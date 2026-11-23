#!/usr/bin/env python3
"""Ultramix episodes: SM x AI overlapping (the original effect) at 1080p60.

Two episodes, from the deduped pools:
- SM: _sm kept pool (dedupe_report.json), intro/outro trimmed
  (old 15: PIPELINE table; new: trims_v2.json numeric detection).
  Logos live in those cards, so trimming is the logo removal.
- AI: _ai/ext01.. in order, trimmed per trims_v2.json, only as much
  as the SM pool can pair with (1:1 alternating 26-frame clips).

Intermediates: per-source 1920x1080, fps=60, GOP 26 (lanczos;
_up1080 ESRGAN versions replace these in a later rebuild - see
UPSCALE_1080.md). Then: frame-exact 26f clips alternating SM/AI,
26f triangular strobe mask scaled to 1080 (RGB multiply), chunked
resumable fade, autodj bed per episode (AAC 192k).

Outputs: ultramix_ep1_1080p60.mp4, ultramix_ep2_1080p60.mp4
Outdir: liveset60_ultra/ (chunks + intermediates, resumable).
"""
import json, subprocess, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

WORK = Path(__file__).resolve().parent
FFD = WORK / "tools" / "ffmpeg-7.1.1-essentials_build" / "bin"
FF, FP = FFD / "ffmpeg.exe", FFD / "ffprobe.exe"
OUTDIR = Path(r"C:\hyperporn_ultra_work")  # scratch on C: (G: too small for intermediates)
CLIP_F, FPS = 26, 60
CHUNK_CLIPS = 1036  # ~449 s per chunk; frames divisible by 26

SM_ORDER = ["bost", "csd2", "csd1", "sm6", "smx", "sm1", "scs", "sm2",
            "sm3", "sm9", "sm7", "sm8", "sm5p1", "sm5p2", "scds", "sm4",
            "wct", "bcwt", "sas", "bost2", "smb1", "smb3", "bcst", "uys", "cw"]
SM_TRIM_OLD = {  # PIPELINE 2.1 (head, tail) seconds
    "bost": (19, 12), "csd2": (11, 12), "sm1": (3, 2), "sm2": (4, 0),
    "sm3": (25, 6), "sm4": (4, 4), "sm5p1": (2, 3), "sm5p2": (8, 18),
    "sm6": (15, 8), "sm7": (8, 12), "sm8": (5, 16), "sm9": (14, 4),
    "smx": (20, 10), "scs": (3, 0), "scds": (14, 2)}

def log(m): print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)

def probe(p):
    r = subprocess.run([str(FP), "-v", "error", "-show_entries",
                        "stream=nb_frames", "-show_entries", "format=duration",
                        "-of", "json", str(p)], capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
        return float(d["format"]["duration"]), int(d["streams"][0].get("nb_frames") or 0)
    except Exception:
        return 0.0, -1

def nframes(p): return probe(p)[1]

def build_intermediate(parts_dir, out_name, items):
    """items: (src, head_s, keep_s). Per-source normalize, concat copy."""
    parts_dir.mkdir(parents=True, exist_ok=True)
    total_frames = 0
    parts = []
    for i, (src, head, keep) in enumerate(items):
        part = parts_dir / f"p_{i:02d}.mp4"
        parts.append(part)
        want = round(keep * FPS)
        if part.exists() and abs(nframes(part) - want) <= 600:
            total_frames += nframes(part); continue
        vf = ("scale=1920:1080:force_original_aspect_ratio=decrease:flags=lanczos,"
              "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=60,format=yuv420p")
        cmd = [str(FF), "-y", "-hide_banner", "-loglevel", "error",
               "-ss", f"{head:.3f}", "-i", str(src), "-t", f"{keep:.3f}",
               "-vf", vf, "-an", "-c:v", "h264_nvenc", "-preset", "p5",
               "-rc", "vbr", "-cq", "20", "-b:v", "0", "-g", "26",
               "-keyint_min", "26", "-sc_threshold", "0", str(part)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        got = nframes(part) if part.exists() else -1
        log(f"part {part.name} rc={r.returncode} frames={got} want~{want}")
        if r.returncode != 0 or abs(got - want) > 600:  # fps-convert rounding at tails
            return -1
        total_frames += got
    out = OUTDIR / out_name
    listf = parts_dir / "list.txt"
    with listf.open("w") as f:
        for p in parts:
            f.write(f"file '{p.resolve().as_posix()}'\n")
    if out.exists() and nframes(out) == total_frames:
        log(f"{out_name} exists frames={total_frames}, skip concat")
        return total_frames
    r = subprocess.run([str(FF), "-y", "-hide_banner", "-loglevel", "error",
                        "-f", "concat", "-safe", "0", "-i", str(listf),
                        "-c", "copy", str(out)], capture_output=True, text=True)
    got = nframes(out) if out.exists() else -1
    log(f"{out_name} frames={got} expected={total_frames} rc={r.returncode}")
    return got if got == total_frames else -1

def cut_one(args):
    idx, ep_start, sm_path, ai_path, sm_total, ai_total, clips_dir = args
    out = clips_dir / f"clip_{idx:06d}.mp4"
    if out.exists() and nframes(out) == CLIP_F:
        return 0
    if out.exists():
        out.unlink()
    pair = idx // 2
    src, total = (sm_path, sm_total) if idx % 2 == 0 else (ai_path, ai_total)
    start_f = (pair * CLIP_F) % total
    cmd = [str(FF), "-y", "-hide_banner", "-loglevel", "error",
           "-ss", f"{start_f/FPS:.6f}", "-i", str(src),
           "-frames:v", str(CLIP_F), "-an", "-c:v", "copy",
           "-avoid_negative_ts", "make_zero", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0 and nframes(out) == CLIP_F:
        return 0
    if out.exists():
        out.unlink()
    cmd = [str(FF), "-y", "-hide_banner", "-loglevel", "error",
           "-ss", f"{start_f/FPS:.6f}", "-i", str(src), "-an",
           "-vf", "fps=60,tpad=stop_mode=clone:stop_duration=1,format=yuv420p",
           "-frames:v", str(CLIP_F), "-c:v", "libx264", "-preset", "ultrafast",
           "-crf", "25", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return 0 if (r.returncode == 0 and nframes(out) == CLIP_F) else 1

def main():
    OUTDIR.mkdir(exist_ok=True)
    (WORK / "intermediates").mkdir(exist_ok=True)
    trims = json.loads((WORK / "trims_v2.json").read_text(encoding="utf-8"))
    kept = set(json.loads((WORK / "dedupe_report.json").read_text(encoding="utf-8"))["kept_pool"])
    # --- SM intermediate ---
    sm_items, sm_secs = [], 0.0
    for stem in SM_ORDER:
        if stem not in kept:
            continue
        src = WORK / "_sm" / f"{stem}.mp4"
        d, _ = probe(src)
        if stem in SM_TRIM_OLD:
            head, tail = SM_TRIM_OLD[stem]
        else:
            t = trims[f"{stem}.mp4"]
            head, tail = t["head_trim_s"], t["tail_trim_s"]
        keep = d - head - tail
        sm_items.append((src, head, keep)); sm_secs += keep
    log(f"SM pool: {len(sm_items)} files, trimmed {sm_secs:.0f}s")
    sm_path = OUTDIR / "sm_all_1080_gop26.mp4"
    sm_frames = build_intermediate(OUTDIR / "sm_parts", "sm_all_1080_gop26.mp4", sm_items)
    if sm_frames <= 0:
        return 1
    # --- AI intermediate (only what SM can pair with) ---
    ai_items, ai_secs = [], 0.0
    for i in range(1, 16):
        if ai_secs >= sm_secs:
            break
        src = WORK / "_ai" / f"ext{i:02d}.mp4"
        t = trims[f"ext{i:02d}.mp4"]
        d, _ = probe(src)
        keep = min(d - t["head_trim_s"] - t["tail_trim_s"], sm_secs - ai_secs)
        ai_items.append((src, t["head_trim_s"], keep)); ai_secs += keep
    log(f"AI pool: {len(ai_items)} files, trimmed {ai_secs:.0f}s")
    ai_path = OUTDIR / "ai_all_1080_gop26.mp4"
    ai_frames = build_intermediate(OUTDIR / "ai_parts", "ai_all_1080_gop26.mp4", ai_items)
    if ai_frames <= 0:
        return 1
    # --- mask at 1080 ---
    mask = OUTDIR / "mask_1080.mp4"
    if not mask.exists():
        r = subprocess.run([str(FF), "-y", "-hide_banner", "-loglevel", "error",
                            "-i", str(WORK / "mask_p26_fixed.mp4"),
                            "-vf", "scale=1920:1080,format=yuv420p",
                            "-c:v", "libx264", "-crf", "10", str(mask)],
                           capture_output=True, text=True)
        log(f"mask_1080 rc={r.returncode} frames={nframes(mask) if mask.exists() else -1}")
    # --- episodes ---
    pairs = sm_frames // CLIP_F
    total_clips = pairs * 2
    half = (pairs // 2) * 2  # clips in ep1 (even)
    episodes = [(1, 0, half), (2, half, total_clips)]
    for ep, c0, c1 in episodes:
        out = WORK / f"ultramix_ep{ep}_1080p60.mp4"
        want_frames = (c1 - c0) * CLIP_F
        if out.exists() and nframes(out) == want_frames:
            log(f"ep{ep} exists, skip"); continue
        clips_dir = OUTDIR / f"ep{ep}_clips"
        clips_dir.mkdir(exist_ok=True)
        fade_chunks = []
        for ci in range(c0, c1, CHUNK_CLIPS):
            hi = min(ci + CHUNK_CLIPS, c1)
            n = hi - ci
            fade = OUTDIR / f"ep{ep}_fade_{ci:06d}.mp4"
            fade_chunks.append(fade)
            if fade.exists() and nframes(fade) == n * CLIP_F:
                continue
            log(f"ep{ep} chunk {ci}: cutting {n} clips")
            with ThreadPoolExecutor(max_workers=8) as ex:
                fails = sum(ex.map(cut_one, [(i, c0, sm_path, ai_path,
                                               sm_frames, ai_frames, clips_dir)
                                              for i in range(ci, hi)]))
            if fails:
                log(f"ep{ep} CUT FAILS={fails}"); return 1
            lst = OUTDIR / f"ep{ep}_chunk_list.txt"
            with lst.open("w") as f:
                for i in range(ci, hi):
                    f.write(f"file '{(clips_dir / f'clip_{i:06d}.mp4').resolve().as_posix()}'\n")
            copy_out = OUTDIR / f"ep{ep}_chunk_copy.mp4"
            r = subprocess.run([str(FF), "-y", "-hide_banner", "-loglevel", "error",
                                "-f", "concat", "-safe", "0", "-i", str(lst),
                                "-c", "copy", str(copy_out)], capture_output=True, text=True)
            if r.returncode != 0 or nframes(copy_out) != n * CLIP_F:
                log(f"ep{ep} concat FAIL"); return 1
            fc = ("[1:v]setpts=N/FRAME_RATE/TB,format=gbrp[m];[0:v]format=gbrp[a];"
                  "[a][m]blend=all_mode=multiply:shortest=1,format=yuv420p[v]")
            r = subprocess.run([str(FF), "-y", "-hide_banner", "-loglevel", "error",
                                "-i", str(copy_out), "-stream_loop", "-1", "-i", str(mask),
                                "-filter_complex", fc, "-map", "[v]", "-an",
                                "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr",
                                "-cq", "22", "-b:v", "0", "-t", f"{n*CLIP_F/FPS:.6f}",
                                str(fade)], capture_output=True, text=True)
            got = nframes(fade) if fade.exists() else -1
            log(f"ep{ep} chunk {ci} fade rc={r.returncode} frames={got}")
            if r.returncode != 0 or got != n * CLIP_F:
                return 1
            copy_out.unlink(missing_ok=True)
            for i in range(ci, hi):
                (clips_dir / f"clip_{i:06d}.mp4").unlink(missing_ok=True)
        lst = OUTDIR / f"ep{ep}_fade_list.txt"
        with lst.open("w") as f:
            for c in fade_chunks:
                f.write(f"file '{c.resolve().as_posix()}'\n")
        video_only = OUTDIR / f"ep{ep}_video.mp4"
        r = subprocess.run([str(FF), "-y", "-hide_banner", "-loglevel", "error",
                            "-f", "concat", "-safe", "0", "-i", str(lst),
                            "-c", "copy", str(video_only)], capture_output=True, text=True)
        if r.returncode != 0 or nframes(video_only) != want_frames:
            log(f"ep{ep} final concat FAIL"); return 1
        dur = want_frames / FPS
        r = subprocess.run([str(FF), "-y", "-hide_banner", "-loglevel", "error",
                            "-i", str(video_only), "-i", str(WORK / "autodj_mix.flac"),
                            "-filter_complex",
                            f"[1:a]apad,atrim=0:{dur:.3f},asetpts=N/SR/TB,aresample=48000[a]",
                            "-map", "0:v", "-map", "[a]", "-c:v", "copy",
                            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                            str(out)], capture_output=True, text=True)
        got = nframes(out) if out.exists() else -1
        log(f"EP{ep} DONE frames={got} want={want_frames} dur={dur:.0f}s rc={r.returncode}")
        if r.returncode != 0 or got != want_frames:
            return 1
        for c in fade_chunks:
            c.unlink(missing_ok=True)
        video_only.unlink(missing_ok=True)
    log("ALL DONE")
    return 0

if __name__ == "__main__":
    sys.exit(main())
