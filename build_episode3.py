#!/usr/bin/env python3
"""Ultramix episode 3: batch-4 SM (2026-11-23 late) x remaining AI.

SM: sgas, ley1..ley5, drip1 (trimmed per trims_v2.json).
AI: ext07..ext11 (ep1/2 consumed ext01..ext06; ext06's 27 s tail
skipped). Same build as build_episodes.py: GOP26 1080p60
intermediates, frame-exact 26f alternating clips, strobe mask,
AutoDJ bed (seeked to 8540 s for continuity). Resumable.
Output: ultramix_ep3_1080p60.mp4 (C: checkout if G: is low).
"""
import json, subprocess, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import build_episodes as be

WORK = be.WORK
FF, FP = be.FF, be.FP
OUTDIR = be.OUTDIR
CLIP_F, FPS = be.CLIP_F, be.FPS
SM3 = ["sgas", "ley1", "ley2", "ley3", "ley4", "ley5", "drip1"]

def log(m): print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)

def main():
    OUTDIR.mkdir(exist_ok=True)
    trims = json.loads((WORK / "trims_v2.json").read_text(encoding="utf-8"))
    sm_items, sm_secs = [], 0.0
    for stem in SM3:
        src = WORK / "_sm" / f"{stem}.mp4"
        d, _ = be.probe(src)
        t = trims[f"{stem}.mp4"]
        keep = d - t["head_trim_s"] - t["tail_trim_s"]
        sm_items.append((src, t["head_trim_s"], keep)); sm_secs += keep
    log(f"SM3 pool: trimmed {sm_secs:.0f}s")
    sm_frames = be.build_intermediate(OUTDIR / "ep3_sm_parts",
                                      "ep3_sm_all_1080_gop26.mp4", sm_items)
    if sm_frames <= 0: return 1
    sm_path = OUTDIR / "ep3_sm_all_1080_gop26.mp4"
    ai_items, ai_secs = [], 0.0
    for i in range(7, 16):
        if ai_secs >= sm_secs: break
        src = WORK / "_ai" / f"ext{i:02d}.mp4"
        t = trims[f"ext{i:02d}.mp4"]
        d, _ = be.probe(src)
        keep = min(d - t["head_trim_s"] - t["tail_trim_s"], sm_secs - ai_secs)
        ai_items.append((src, t["head_trim_s"], keep)); ai_secs += keep
    log(f"AI pool (ep3): trimmed {ai_secs:.0f}s from {len(ai_items)} files")
    ai_frames = be.build_intermediate(OUTDIR / "ep3_ai_parts",
                                      "ep3_ai_all_1080_gop26.mp4", ai_items)
    if ai_frames <= 0: return 1
    ai_path = OUTDIR / "ep3_ai_all_1080_gop26.mp4"
    mask = OUTDIR / "mask_1080.mp4"
    pairs = sm_frames // CLIP_F
    total_clips = pairs * 2
    out = WORK / "ultramix_ep3_v2_1080p60.mp4"  # v2: mask-timestamp fix (2026-11-25)
    alt = Path(r"C:\Users\hyper\workspace\hyperporn") / out.name
    if not out.exists() and not alt.exists():
        import shutil as _sh
        if _sh.disk_usage(WORK).free / 1e9 < 22:
            out = alt; log(f"G: low, final goes to {out}")
    elif alt.exists():
        out = alt
    want = total_clips * CLIP_F
    if out.exists() and be.nframes(out) == want:
        log("ep3 exists, skip"); return 0
    clips_dir = OUTDIR / "ep3_clips"; clips_dir.mkdir(exist_ok=True)
    fade_chunks = []
    for ci in range(0, total_clips, be.CHUNK_CLIPS):
        hi = min(ci + be.CHUNK_CLIPS, total_clips); n = hi - ci
        fade = OUTDIR / f"ep3_fade_{ci:06d}.mp4"; fade_chunks.append(fade)
        if fade.exists() and be.nframes(fade) == n * CLIP_F: continue
        log(f"ep3 chunk {ci}: cutting {n} clips")
        with ThreadPoolExecutor(max_workers=8) as ex:
            fails = sum(ex.map(be.cut_one, [(i, 0, sm_path, ai_path,
                                             sm_frames, ai_frames, clips_dir)
                                            for i in range(ci, hi)]))
        if fails: log(f"CUT FAILS={fails}"); return 1
        lst = OUTDIR / "ep3_chunk_list.txt"
        with lst.open("w") as f:
            for i in range(ci, hi):
                f.write(f"file '{(clips_dir / f'clip_{i:06d}.mp4').resolve().as_posix()}'\n")
        copy_out = OUTDIR / "ep3_chunk_copy.mp4"
        r = subprocess.run([str(FF), "-y", "-hide_banner", "-loglevel", "error",
                            "-f", "concat", "-safe", "0", "-i", str(lst),
                            "-c", "copy", str(copy_out)], capture_output=True, text=True)
        if r.returncode != 0 or be.nframes(copy_out) != n * CLIP_F:
            log("concat FAIL"); return 1
        fc = ("[1:v]setpts=N/FRAME_RATE/TB,format=gbrp[m];"
              "[0:v]setpts=N/60/TB,format=gbrp[a];"
              "[a][m]blend=all_mode=multiply,format=yuv420p,"
              "tpad=stop_mode=clone:stop_duration=2[v]")
        r = subprocess.run([str(FF), "-y", "-hide_banner", "-loglevel", "error",
                            "-i", str(copy_out), "-stream_loop", "-1", "-i", str(mask),
                            "-filter_complex", fc, "-map", "[v]", "-an",
                            "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr",
                            "-cq", "22", "-b:v", "0", "-frames:v", str(n * CLIP_F),
                            str(fade)], capture_output=True, text=True)
        got = be.nframes(fade) if fade.exists() else -1
        log(f"ep3 chunk {ci} fade rc={r.returncode} frames={got}")
        if r.returncode != 0 or got != n * CLIP_F: return 1
        copy_out.unlink(missing_ok=True)
        for i in range(ci, hi):
            (clips_dir / f"clip_{i:06d}.mp4").unlink(missing_ok=True)
    lst = OUTDIR / "ep3_fade_list.txt"
    with lst.open("w") as f:
        for c in fade_chunks: f.write(f"file '{c.resolve().as_posix()}'\n")
    video_only = OUTDIR / "ep3_video.mp4"
    r = subprocess.run([str(FF), "-y", "-hide_banner", "-loglevel", "error",
                        "-f", "concat", "-safe", "0", "-i", str(lst),
                        "-c", "copy", str(video_only)], capture_output=True, text=True)
    if r.returncode != 0 or be.nframes(video_only) != want:
        log("final concat FAIL"); return 1
    dur = want / FPS
    r = subprocess.run([str(FF), "-y", "-hide_banner", "-loglevel", "error",
                        "-i", str(video_only), "-ss", "8540", "-i",
                        str(WORK / "autodj_mix.flac"),
                        "-filter_complex",
                        f"[1:a]apad,atrim=0:{dur:.3f},asetpts=N/SR/TB,aresample=48000[a]",
                        "-map", "0:v", "-map", "[a]", "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                        str(out)], capture_output=True, text=True)
    got = be.nframes(out) if out.exists() else -1
    log(f"EP3 DONE frames={got} want={want} dur={dur:.0f}s rc={r.returncode} -> {out}")
    if r.returncode != 0 or got != want: return 1
    for c in fade_chunks: c.unlink(missing_ok=True)
    video_only.unlink(missing_ok=True)
    return 0

if __name__ == "__main__":
    sys.exit(main())
