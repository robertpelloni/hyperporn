#!/usr/bin/env python3
"""rebuild_v4: fixed frame counts, intro+outro trims, hypnoshit v2, Ajja + Space Tribe.

Fixes vs v3:
  - clips cut with -frames:v 26 (v3 stream-copy -t gave 29/34/40 frame clips -> mask desync -> black flashes)
  - sm3 intro 9s -> 25s (title card runs through t=20)
  - outro tails trimmed per source
  - hypnoshit: second half of each track only, minus last 60s, loudnorm, louder than BGM
  - two BGM variants: Ajja NZ liveset and Space Tribe (3 sets concat)

Outputs:
  Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps_FADE_v3.mp4
  SpaceTribe_Sissymaker_WetDream_STROBE140_60fps_FADE_v3.mp4
  + 2GB compressed copies
"""
import subprocess, sys, time, json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

SISSY = Path(r"C:\Users\hyper\Videos\sissymaker")
INTER = SISSY / "intermediates"
INTER.mkdir(exist_ok=True)
HYPO_DIR = Path(r"C:\Users\hyper\Videos\hypnoshit")
MUSIC = Path(r"C:\Users\hyper\Music")
WET_SRC = SISSY / "JPVT1109 - Wet Dreams AI Goon Therapy (parts 1-15).mp4"

AJJA = MUSIC / "Ajja - 2026 - Dimension Festival NZ (live).mp3"
ST1 = MUSIC / "Space Tribe - 2016 - Sonic Booking Podcast Episode 001 (live).mp3"
ST2 = MUSIC / "Space Tribe - 2017 - The Big Bang (live).mp3"
ST3 = MUSIC / "Space Tribe - 2018 - Psychedelic Rave (NL) (live).mp3"

OUTDIR = SISSY / "liveset60_strobe"
CLIP_FRAMES = 26
CLIP_DUR = CLIP_FRAMES / 60.0
W, H, FPS = 1280, 720, 60

# name: (intro_s, outro_s)  — intros from detection, sm3 bumped to 25 (title through t=20)
TRIMS = {
    "bost":  (19.0, 12.0),
    "csd2":  (11.0, 12.0),
    "sm6":   (15.0,  8.0),
    "smx":   (20.0, 10.0),
    "sm1":   ( 3.0,  2.0),
    "scs":   ( 3.0,  0.0),
    "sm2":   ( 4.0,  0.0),
    "sm3":   (25.0,  6.0),
    "sm9":   (14.0,  4.0),
    "sm7":   ( 8.0, 12.0),
    "sm8":   ( 5.0, 16.0),
    "sm5p1": ( 2.0,  3.0),
    "sm5p2": ( 8.0, 18.0),
    "scds":  (14.0,  2.0),
    "sm4":   ( 4.0,  4.0),
}

SISSY_GOP = INTER / "sissy_all_gop26.mp4"
WET_GOP = INTER / "wet_gop26.mp4"
VIDEO_ONLY = OUTDIR / "video_copy.mp4"
VIDEO_FADE = OUTDIR / "video_fade.mp4"
MASK = SISSY / "mask_p26_fixed.mp4"
HYPO_MIX = SISSY / "hypo_mix_v2.m4a"
ST_MIX = SISSY / "spacetribe_mix.m4a"

OUT_AJJA = SISSY / "Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps_FADE_v3.mp4"
OUT_ST = SISSY / "SpaceTribe_Sissymaker_WetDream_STROBE140_60fps_FADE_v3.mp4"

HYPO_ORDER = [
    "You Cant Stop Me", "Milking Time", "Ultimate Cuckold",
    "Drop for Teacher", "BeatrixVale", "Submissive Sissy Slut",
    "Obey-Submit", "Take Your Medicine", "Penelope",
]


def log(msg):
    print(f"{time.strftime('%H:%M:%S')} {msg}", flush=True)


def probe(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(p)],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout.strip())


def norm_part(src, ss, end, out):
    dur = end - ss
    if out.exists() and out.stat().st_size > 100_000:
        return True
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-ss", f"{ss:.3f}", "-t", f"{dur:.3f}", "-i", str(src),
        "-an",
        "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,"
               "pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=60,setpts=N/60/TB,format=yuv420p",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
        "-g", "26", "-keyint_min", "26", "-sc_threshold", "0",
        str(out),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        log(f"PART FAIL {out.name} {(r.stderr or '')[-200:]}")
    return r.returncode == 0


def build_sissy_intermediate():
    if SISSY_GOP.exists() and SISSY_GOP.stat().st_size > 500_000_000:
        log(f"sissy intermediate exists {SISSY_GOP.stat().st_size/1e6:.0f}MB")
        return True
    parts_dir = INTER / "sissy_parts4"
    parts_dir.mkdir(exist_ok=True)
    log(f"normalizing {len(TRIMS)} sources (intro+outro trimmed)...")
    ok = True
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {}
        for i, (name, (intro, outro)) in enumerate(TRIMS.items()):
            src = SISSY / f"{name}.mp4"
            if not src.exists():
                log(f"MISSING {name}")
                ok = False
                continue
            dur = probe(src)
            end = dur - outro
            if end <= intro + 1:
                log(f"SKIP {name} too short after trim")
                ok = False
                continue
            out = parts_dir / f"p_{i:02d}.mp4"
            futs[ex.submit(norm_part, src, intro, end, out)] = name
        for fut in as_completed(futs):
            n = futs[fut]
            if not fut.result():
                ok = False
            else:
                log(f"  part ok {n}")
    if not ok:
        return False

    listf = parts_dir / "list.txt"
    parts = sorted(parts_dir.glob("p_*.mp4"))
    total = 0.0
    with listf.open("w", encoding="utf-8") as f:
        for p in parts:
            d = probe(p)
            total += d
            f.write(f"file '{p.name}'\n")
    log(f"parts sum dur={total:.1f}s")
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(listf),
         "-c", "copy", str(SISSY_GOP)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        log(f"concat fail {(r.stderr or '')[-300:]}")
        return False
    got = probe(SISSY_GOP)
    log(f"sissy_all_gop26 dur={got:.1f}s (sum {total:.1f}s) size={SISSY_GOP.stat().st_size/1e6:.0f}MB")
    return abs(got - total) <= 2.0


def build_wet_intermediate():
    if WET_GOP.exists() and WET_GOP.stat().st_size > 500_000_000:
        log(f"wet intermediate exists {WET_GOP.stat().st_size/1e6:.0f}MB")
        return True
    log("building wet intermediate...")
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(WET_SRC), "-an",
         "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,"
                "pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=60,setpts=N/60/TB,format=yuv420p",
         "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
         "-g", "26", "-keyint_min", "26", "-sc_threshold", "0",
         str(WET_GOP)],
        capture_output=True, text=True,
    )
    log(f"wet rc={r.returncode} dur={probe(WET_GOP):.1f}s")
    return r.returncode == 0


def nframes(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=nb_frames", "-of", "csv=p=0", str(p)],
        capture_output=True, text=True,
    )
    s = (r.stdout or "").strip()
    try:
        return int(s)
    except ValueError:
        return -1


def cut_one(i, sissy_dur, wet_dur):
    out = OUTDIR / f"clip_{i:06d}.mp4"
    if out.exists() and out.stat().st_size > 1500:
        return i, 0, "skip"
    if out.exists():
        out.unlink()
    if i % 2 == 0:
        src, total = SISSY_GOP, sissy_dur
    else:
        src, total = WET_GOP, wet_dur
    start = round((((i // 2) * CLIP_DUR) % total) / CLIP_DUR) * CLIP_DUR
    # fast path: stream-copy 26 packets from GOP-aligned seek
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-ss", f"{start:.6f}", "-i", str(src),
           "-frames:v", str(CLIP_FRAMES), "-an",
           "-c:v", "copy", "-avoid_negative_ts", "make_zero", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0 and out.exists() and nframes(out) == CLIP_FRAMES:
        return i, 0, "copy"
    # slow path: re-encode exactly 26 frames (clone-pad at source end)
    if out.exists():
        out.unlink()
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-ss", f"{start:.6f}", "-i", str(src),
           "-an", "-vf", "fps=60,tpad=stop_mode=clone:stop_duration=1,format=yuv420p",
           "-frames:v", str(CLIP_FRAMES),
           "-c:v", "libx264", "-preset", "ultrafast", "-crf", "25", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not out.exists() or nframes(out) != CLIP_FRAMES:
        return i, 1, (r.stderr or "")[-150:]
    return i, 0, "reenc"


def cut_clips(n_clips, sissy_dur, wet_dur):
    OUTDIR.mkdir(exist_ok=True)
    log(f"cutting {n_clips} clips (forced {CLIP_FRAMES} frames)...")
    done = fails = copy_n = reenc_n = 0
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = [ex.submit(cut_one, i, sissy_dur, wet_dur) for i in range(n_clips)]
        for fut in as_completed(futs):
            i, rc, how = fut.result()
            done += 1
            if rc != 0:
                fails += 1
                if fails <= 5:
                    log(f"FAIL {i} {how}")
            elif how == "copy":
                copy_n += 1
            elif how == "reenc":
                reenc_n += 1
            if done % 500 == 0 or done == n_clips:
                log(f"  {done}/{n_clips} fails={fails} copy={copy_n} reenc={reenc_n}")
    bad = []
    for i in range(n_clips):
        p = OUTDIR / f"clip_{i:06d}.mp4"
        if not p.exists() or p.stat().st_size <= 1500 or nframes(p) != CLIP_FRAMES:
            bad.append(i)
    log(f"bad clips after pass1: {len(bad)}")
    if bad:
        with ThreadPoolExecutor(max_workers=6) as ex:
            list(ex.map(lambda i: cut_one(i, sissy_dur, wet_dur), bad))
        bad = [i for i in bad
               if not (OUTDIR / f"clip_{i:06d}.mp4").exists()
               or nframes(OUTDIR / f"clip_{i:06d}.mp4") != CLIP_FRAMES]
        if bad:
            log(f"STILL BAD {len(bad)}: {bad[:20]}")
            return False
    return True


def concat_clips(n_clips):
    listf = OUTDIR / "list.txt"
    with listf.open("w", encoding="utf-8") as f:
        for i in range(n_clips):
            f.write("file 'clip_%06d.mp4'\n" % i)
    if VIDEO_ONLY.exists() and VIDEO_ONLY.stat().st_size > 1_000_000_000:
        log(f"concat exists {VIDEO_ONLY.stat().st_size/1e6:.0f}MB")
        return True
    log("concat copy...")
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(listf),
         "-c", "copy", str(VIDEO_ONLY)],
        capture_output=True, text=True,
    )
    log(f"concat rc={r.returncode} size={VIDEO_ONLY.stat().st_size/1e6:.0f}MB")
    return r.returncode == 0


def make_mask():
    if MASK.exists() and MASK.stat().st_size > 1000:
        return True
    n, k, floor = 26, 6, 48
    half = k / 2.0
    frames = bytearray()
    for i in range(n):
        d = min(i, n - i)
        v = 255 if d >= half else int(floor + (255 - floor) * (d / half))
        frames.extend(bytes([v]) * (W * H))
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-frames:v", str(n),
         "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
         "-pix_fmt", "yuv420p", str(MASK)],
        input=bytes(frames), capture_output=True, timeout=120,
    )
    log(f"mask rc={r.returncode}")
    return r.returncode == 0


def fade_video(n_clips, audio_dur):
    if not make_mask():
        return False
    if VIDEO_FADE.exists() and VIDEO_FADE.stat().st_size > 1_000_000_000:
        log(f"fade video exists {VIDEO_FADE.stat().st_size/1e6:.0f}MB")
        return True
    fc = (
        "[1:v]setpts=N/FRAME_RATE/TB,format=gbrp[m];"
        "[0:v]format=gbrp[a];"
        "[a][m]blend=all_mode=multiply:shortest=1,format=yuv420p[v]"
    )
    log("fade encode START...")
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(VIDEO_ONLY),
         "-stream_loop", "-1", "-i", str(MASK),
         "-filter_complex", fc,
         "-map", "[v]", "-an",
         "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
         "-t", f"{min(n_clips * CLIP_DUR, audio_dur):.6f}",
         str(VIDEO_FADE)],
        capture_output=True, text=True,
    )
    log(f"fade rc={r.returncode}")
    return r.returncode == 0


def find_hypo(keyword):
    key = keyword.lower().replace("-", " ").replace("_", " ")
    for p in HYPO_DIR.iterdir():
        if p.suffix.lower() not in (".mp3", ".m4a"):
            continue
        name = p.name.lower().replace("-", " ").replace("_", " ")
        if key in name:
            return p
    return None


def build_hypo_mix(target_dur):
    if HYPO_MIX.exists() and HYPO_MIX.stat().st_size > 500_000:
        log(f"hypo mix exists {HYPO_MIX.stat().st_size/1e6:.1f}MB")
        return True
    parts_dir = SISSY / "hypo_parts_v2"
    parts_dir.mkdir(exist_ok=True)
    parts = []
    filled = 0.0
    for key in HYPO_ORDER:
        src = find_hypo(key)
        if not src:
            log(f"missing hypo {key}")
            continue
        dur = probe(src)
        ss = dur / 2.0
        end = dur - 60.0
        if end <= ss:
            continue
        take = end - ss
        if filled + take > target_dur:
            take = target_dur - filled
        if take < 5:
            break
        out = parts_dir / f"{len(parts):02d}.m4a"
        if not (out.exists() and out.stat().st_size > 100_000):
            r = subprocess.run(
                ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                 "-ss", f"{ss:.3f}", "-t", f"{take:.3f}", "-i", str(src),
                 "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=44100",
                 "-c:a", "aac", "-b:a", "192k", str(out)],
                capture_output=True, text=True,
            )
            if r.returncode != 0:
                log(f"hypo part fail {key} {(r.stderr or '')[-200:]}")
                continue
        parts.append(out)
        filled += take
        log(f"  hypo part {key} +{take:.1f}s total={filled:.1f}s")
        if filled >= target_dur - 1:
            break
    listf = parts_dir / "list.txt"
    with listf.open("w", encoding="utf-8") as f:
        for p in parts:
            f.write(f"file '{p.name}'\n")
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(listf),
         "-c", "copy", str(HYPO_MIX)],
        capture_output=True, text=True,
    )
    log(f"hypo mix rc={r.returncode} dur={probe(HYPO_MIX):.1f}s")
    return r.returncode == 0


def build_st_mix(target_dur):
    if ST_MIX.exists() and ST_MIX.stat().st_size > 500_000:
        log(f"st mix exists {ST_MIX.stat().st_size/1e6:.1f}MB")
        return True
    parts_dir = SISSY / "st_parts"
    parts_dir.mkdir(exist_ok=True)
    parts = []
    filled = 0.0
    for i, src in enumerate([ST1, ST2, ST3]):
        if not src.exists():
            log(f"missing {src}")
            continue
        dur = probe(src)
        take = min(dur, target_dur - filled)
        if take < 5:
            break
        out = parts_dir / f"{i:02d}.m4a"
        if not (out.exists() and out.stat().st_size > 100_000):
            r = subprocess.run(
                ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                 "-t", f"{take:.3f}", "-i", str(src),
                 "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=44100",
                 "-c:a", "aac", "-b:a", "192k", str(out)],
                capture_output=True, text=True,
            )
            if r.returncode != 0:
                log(f"st part fail {src.name} {(r.stderr or '')[-200:]}")
                continue
        parts.append(out)
        filled += take
        log(f"  st part {src.name[:40]} +{take:.1f}s total={filled:.1f}s")
    listf = parts_dir / "list.txt"
    with listf.open("w", encoding="utf-8") as f:
        for p in parts:
            f.write(f"file '{p.name}'\n")
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(listf),
         "-c", "copy", str(ST_MIX)],
        capture_output=True, text=True,
    )
    log(f"st mix rc={r.returncode} dur={probe(ST_MIX):.1f}s")
    return r.returncode == 0


def mux_audio(bgm, out, run_time):
    if out.exists():
        out.unlink()
    fc = (
        "[1:a]volume=0.70[bgm];"
        "[2:a]volume=0.90[hyp];"
        "[bgm][hyp]amix=inputs=2:duration=first:dropout_transition=0,"
        "alimiter=limit=0.95[aout]"
    )
    log(f"mux {out.name} ...")
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(VIDEO_FADE),
         "-i", str(bgm),
         "-i", str(HYPO_MIX),
         "-filter_complex", fc,
         "-map", "0:v", "-map", "[aout]",
         "-c:v", "copy",
         "-c:a", "aac", "-b:a", "320k",
         "-t", f"{run_time:.6f}",
         str(out)],
        capture_output=True, text=True,
    )
    log(f"mux rc={r.returncode} size={out.stat().st_size/1e6:.1f}MB")
    return r.returncode == 0


def compress(src, out):
    if out.exists():
        out.unlink()
    log(f"compress {out.name} ...")
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(src),
         "-c:v", "libx264", "-preset", "medium",
         "-b:v", "1350k", "-maxrate", "1400k", "-bufsize", "2800k",
         "-vf", "scale=1280:720",
         "-c:a", "aac", "-b:a", "128k",
         "-movflags", "+faststart",
         str(out)],
        capture_output=True, text=True,
    )
    log(f"compress rc={r.returncode} size={out.stat().st_size/1e6:.1f}MB")
    return r.returncode == 0


def main():
    log("=== rebuild v4: 26-frame clips, intro+outro trim, hypo v2, Ajja+SpaceTribe ===")
    for p in (WET_SRC, AJJA, ST1, HYPO_DIR):
        if not p.exists():
            sys.exit(f"missing {p}")
    ajja_dur = probe(AJJA)
    n_clips = int(ajja_dur / CLIP_DUR) + 1
    log(f"ajja={ajja_dur:.1f}s n_clips={n_clips}")

    if not build_sissy_intermediate():
        sys.exit("sissy intermediate failed")
    if not build_wet_intermediate():
        sys.exit("wet intermediate failed")
    sissy_dur = probe(SISSY_GOP)
    wet_dur = probe(WET_GOP)
    log(f"sissy={sissy_dur:.1f} wet={wet_dur:.1f}")

    if not cut_clips(n_clips, sissy_dur, wet_dur):
        sys.exit("clip cut failed")
    if not concat_clips(n_clips):
        sys.exit("concat failed")

    if not build_hypo_mix(ajja_dur + 5):
        sys.exit("hypo mix failed")
    if not build_st_mix(ajja_dur + 5):
        sys.exit("st mix failed")

    run_time = min(n_clips * CLIP_DUR, ajja_dur)
    if not fade_video(n_clips, ajja_dur):
        sys.exit("fade failed")

    if not mux_audio(AJJA, OUT_AJJA, run_time):
        sys.exit("ajja mux failed")
    if not mux_audio(ST_MIX, OUT_ST, run_time):
        sys.exit("st mux failed")

    compress(OUT_AJJA, SISSY / OUT_AJJA.name.replace(".mp4", "_2GB.mp4"))
    compress(OUT_ST, SISSY / OUT_ST.name.replace(".mp4", "_2GB.mp4"))
    log("REBUILD_V4_OK")


if __name__ == "__main__":
    main()
