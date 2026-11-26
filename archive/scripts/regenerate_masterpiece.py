#!/usr/bin/env python3
"""Regenerate the sissymaker x wet-dream liveset masterpiece with CORRECT pieces.

Uses ALL 13 Emperor Hypnos videos in order (Sissymaker 1-9, then the 4 others),
alternating with the wet-dream compilation, cut to the beat grid of the
DimensionFestivalNZ 2026 liveset (longest Ajja set, ~3h), 60fps.

Produces three cut rates, plus an RGB-multiply fade variant of each:
  - 14bpm   : one clip = one beat @ 14 BPM   (257 frames @60fps)
  - 14BEATS : one clip = 14 beats @ 140 BPM  (360 frames @60fps)
  - STROBE140: one clip = one kick @ 140 BPM (26 frames @60fps, stream-copy)

Resumable: skips already-built parts/clips/finals.
"""
import subprocess, sys, time, shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

SISSY_DIR = Path(r"C:\Users\hyper\Videos\sissymaker")
MUSIC = Path(r"C:\Users\hyper\Music")
INTER = SISSY_DIR / "intermediates"

AUDIO = MUSIC / "Ajja 2026 (Modern Psytrance of Today) @DimensionFestivalNZ.mp3"
WET = SISSY_DIR / "JPVT1109 - Wet Dreams AI Goon Therapy (parts 1-15).mp4"

# All Emperor Hypnos videos in order: Sissymaker 1-9, then the others.
EMPEROR = [
    "Sissy Maker 1 by Emperor Hypnos (1).mp4",
    "Music Video - Emperorhypnos - Sissymaker Ii (1).mp4",
    "Music Video - Emperorhypnos - Sissymaker Iii (1).mp4",
    "Sissy Maker IV by Emperor Hypnos (1).mp4",
    "Emperor Hypnos   Sissymaker 5 (1).mp4",
    "Emperor Hypnos   Sissymaker 6 (1).mp4",
    "Emperor Hypnos   Sissymaker 7 (1).mp4",
    "Emperor Hypnos Sissymaker 8 (1).mp4",
    "Emperor Hypnos   Sissymaker 9 (1).mp4",
    "Black Owned Slut Trainer Emperor Hypnos (1).mp4",
    "Cum Slut Destiny 2 EmperorHypnos (1).mp4",
    "Music Video - Emperorhypnos - Sissy Cocksucking Submission (1).mp4",
    "Sissy Cum Dumpster Submission by EmperorHypnos (1).mp4",
]

SISSY_ALL_INT = INTER / "sissy_all_gop26.mp4"
WET_INT = INTER / "wet_gop26.mp4"
NORM_DIR = INTER / "sissy_all_norm"

W, H, FPS = 1280, 720, 60
PSY_BPM = 140.0
KEYINT = 26

def log(msg):
    print(msg, flush=True)

def run(cmd, label):
    log(f"START {label} {time.strftime('%H:%M:%S')}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    log(f"END {label} rc={r.returncode} {time.strftime('%H:%M:%S')}")
    if r.returncode != 0:
        log((r.stderr or "")[-800:])
    return r

def probe(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(p)],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout.strip())

def emperor_at(emps_dur, total, t):
    t = t % total
    acc = 0.0
    for p, d in emps_dur:
        if t < acc + d:
            return p, t - acc
        acc += d
    p, d = emps_dur[-1]
    return p, 0.0

# ---------------------------------------------------------------- step 1
def build_intermediate():
    """Normalize all 13 Emperor Hypnos videos to CFR 60fps 720p GOP26,
    then concat -c copy into a single clean intermediate."""
    log("=== STEP 1: build sissy_all_gop26.mp4 ===")
    emps = [SISSY_DIR / n for n in EMPEROR]
    for p in emps:
        if not p.exists():
            log(f"MISSING SOURCE: {p}")
            sys.exit(1)

    NORM_DIR.mkdir(parents=True, exist_ok=True)
    parts = []
    for i, src in enumerate(emps):
        part = NORM_DIR / f"part_{i:02d}.mp4"
        parts.append(part)
        if part.exists() and part.stat().st_size > 100_000:
            log(f"skip part {i:02d}")
            continue
        vf = (
            f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,"
            f"fps={FPS},setpts=N/{FPS}/TB,format=yuv420p"
        )
        r = run([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", str(src), "-an", "-vf", vf,
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
            "-g", str(KEYINT), "-keyint_min", str(KEYINT),
            "-sc_threshold", "0", "-r", str(FPS), "-pix_fmt", "yuv420p",
            str(part),
        ], f"part_{i:02d}")
        if r.returncode != 0:
            log(f"part {i:02d} FAILED")
            sys.exit(1)
        log(f"  part {i:02d} dur {probe(part):.1f}s")

    listf = NORM_DIR / "list.txt"
    with listf.open("w", encoding="utf-8") as f:
        for p in parts:
            f.write("file '%s'\n" % p.as_posix())

    if SISSY_ALL_INT.exists():
        SISSY_ALL_INT.unlink()
    r = run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(listf),
        "-c", "copy", str(SISSY_ALL_INT),
    ], "concat_copy")
    if r.returncode != 0:
        log("concat FAILED")
        sys.exit(1)

    d = probe(SISSY_ALL_INT)
    log(f"sissy_all dur={d:.1f}s MB={SISSY_ALL_INT.stat().st_size/1e6:.1f}")
    total = sum(probe(p) for p in emps)
    if not (total * 0.99 < d < total * 1.01):
        log(f"UNEXPECTED DURATION {d} vs sum {total}")
        sys.exit(1)
    log("INTERMEDIATE_OK")

# ---------------------------------------------------------------- step 2/3
def build_liveset(clip_dur, frames, tag, out_name, workers):
    """Slice 60fps clips straight from the 13 originals, alternate with wet
    dream, concat, and mux the liveset audio."""
    log(f"=== STEP {tag}: clip={clip_dur:.6f}s frames={frames} ===")
    out_dir = SISSY_DIR / f"liveset60_{tag}"
    final = SISSY_DIR / out_name

    emps = [SISSY_DIR / n for n in EMPEROR]
    emps_dur = [(p, probe(p)) for p in emps]
    wet_dur = probe(WET)
    audio_dur = probe(AUDIO)
    emp_total = sum(d for _, d in emps_dur)
    n_clips = int(audio_dur / clip_dur) + 1
    log(f"audio={audio_dur:.1f}s emp_total={emp_total:.1f}s wet={wet_dur:.1f}s n_clips={n_clips}")

    if final.exists() and final.stat().st_size > 100_000_000:
        log(f"SKIP (final exists): {out_name}")
        return

    if out_dir.exists():
        shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    def render(i):
        if i % 2 == 0:
            src, start = emperor_at(emps_dur, emp_total, (i // 2) * clip_dur)
        else:
            start = ((i // 2) * clip_dur) % wet_dur
            src = WET
        out = out_dir / f"clip_{i:06d}.mp4"
        if out.exists() and out.stat().st_size > 2000:
            return i, 0, ""
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-ss", f"{start:.6f}", "-i", str(src), "-an",
            "-vf", (
                f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
                f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},format=yuv420p,"
                f"tpad=stop_mode=clone:stop_duration=1"
            ),
            "-frames:v", str(frames),
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "25",
            "-g", str(frames), str(out),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        return i, r.returncode, (r.stderr or "")[-200:]

    log(f"rendering {n_clips} clips, {workers} workers...")
    done = fails = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(render, i) for i in range(n_clips)]
        for fut in as_completed(futs):
            i, rc, err = fut.result()
            done += 1
            if rc != 0:
                fails += 1
                if fails <= 8:
                    log(f"FAIL {i}: {err}")
            if done % 100 == 0 or done == n_clips:
                log(f"  {done}/{n_clips} fails={fails}")

    missing = [i for i in range(n_clips)
               if not (out_dir / f"clip_{i:06d}.mp4").exists()
               or (out_dir / f"clip_{i:06d}.mp4").stat().st_size <= 2000]
    if missing:
        log(f"retrying {len(missing)} missing...")
        with ThreadPoolExecutor(max_workers=4) as ex:
            list(ex.map(render, missing))
        missing = [i for i in missing
                   if not (out_dir / f"clip_{i:06d}.mp4").exists()
                   or (out_dir / f"clip_{i:06d}.mp4").stat().st_size <= 2000]
        if missing:
            log(f"STILL MISSING {len(missing)}: {missing[:10]}")
            sys.exit(1)

    listf = out_dir / "list.txt"
    with listf.open("w", encoding="utf-8") as f:
        for i in range(n_clips):
            f.write("file 'clip_%06d.mp4'\n" % i)

    concat_mp4 = out_dir / "video_copy.mp4"
    log("concat copy...")
    r = run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-f", "concat", "-safe", "0", "-i", str(listf),
             "-c", "copy", str(concat_mp4)], "concat")
    if r.returncode != 0:
        sys.exit(1)

    log("mux audio...")
    r = run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-i", str(concat_mp4), "-i", str(AUDIO),
             "-map", "0:v:0", "-map", "1:a:0",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
             "-t", "%.6f" % min(n_clips * clip_dur, audio_dur),
             str(final)], "mux")
    if r.returncode != 0:
        sys.exit(1)
    log(f"DONE {final.name} {final.stat().st_size/1e6:.1f}MB")

    shutil.rmtree(out_dir, ignore_errors=True)
    log("cleaned clips")

# ---------------------------------------------------------------- step 4
def build_strobe():
    """Stream-copy 26-frame strobe clips from the GOP26 intermediates."""
    log("=== STEP strobe: stream-copy from intermediates ===")
    OUT = SISSY_DIR / "liveset60_strobe"
    FINAL = SISSY_DIR / "Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps.mp4"
    CLIP_FRAMES = 26
    CLIP_DUR = CLIP_FRAMES / 60.0

    if FINAL.exists() and FINAL.stat().st_size > 100_000_000:
        log(f"SKIP (final exists): {FINAL.name}")
        return

    sissy_dur = probe(SISSY_ALL_INT)
    wet_dur = probe(WET_INT)
    audio_dur = probe(AUDIO)
    n_clips = int(audio_dur / CLIP_DUR) + 1
    log(f"sissy={sissy_dur:.1f} wet={wet_dur:.1f} audio={audio_dur:.1f} n_clips={n_clips}")

    if OUT.exists():
        shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir(exist_ok=True)

    def cut(i):
        out = OUT / f"clip_{i:06d}.mp4"
        if out.exists() and out.stat().st_size > 1500:
            return i, 0, ""
        if i % 2 == 0:
            src, total = SISSY_ALL_INT, sissy_dur
            start = ((i // 2) * CLIP_DUR) % total
        else:
            src, total = WET_INT, wet_dur
            start = ((i // 2) * CLIP_DUR) % total
        start = round(start / CLIP_DUR) * CLIP_DUR
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-ss", f"{start:.6f}", "-i", str(src),
            "-t", f"{CLIP_DUR:.6f}", "-an",
            "-c:v", "copy", "-avoid_negative_ts", "make_zero", str(out),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0 or not out.exists() or out.stat().st_size <= 1500:
            cmd = [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-ss", f"{start:.6f}", "-i", str(src),
                "-t", f"{CLIP_DUR:.6f}", "-an",
                "-vf", "fps=60,format=yuv420p", "-frames:v", str(CLIP_FRAMES),
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "25", str(out),
            ]
            r = subprocess.run(cmd, capture_output=True, text=True)
        return i, r.returncode, (r.stderr or "")[-150:]

    log(f"cutting {n_clips} clips...")
    done = fails = 0
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = [ex.submit(cut, i) for i in range(n_clips)]
        for fut in as_completed(futs):
            i, rc, err = fut.result()
            done += 1
            if rc != 0:
                fails += 1
                if fails <= 5:
                    log(f"FAIL {i}: {err}")
            if done % 500 == 0 or done == n_clips:
                log(f"  {done}/{n_clips} fails={fails}")

    missing = [i for i in range(n_clips)
               if not (OUT / f"clip_{i:06d}.mp4").exists()
               or (OUT / f"clip_{i:06d}.mp4").stat().st_size <= 1500]
    log(f"missing {len(missing)}")
    if missing:
        with ThreadPoolExecutor(max_workers=6) as ex:
            list(ex.map(cut, missing))
        missing = [i for i in missing
                   if not (OUT / f"clip_{i:06d}.mp4").exists()
                   or (OUT / f"clip_{i:06d}.mp4").stat().st_size <= 1500]
        if missing:
            log(f"STILL MISSING {len(missing)}")
            sys.exit(1)

    listf = OUT / "list.txt"
    with listf.open("w", encoding="utf-8") as f:
        for i in range(n_clips):
            f.write("file 'clip_%06d.mp4'\n" % i)

    copy_mp4 = OUT / "video_copy.mp4"
    log("concat copy...")
    r = run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-f", "concat", "-safe", "0", "-i", str(listf),
             "-c", "copy", str(copy_mp4)], "concat")
    if r.returncode != 0:
        sys.exit(1)

    log("mux audio...")
    if FINAL.exists():
        FINAL.unlink()
    r = run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-i", str(copy_mp4), "-i", str(AUDIO),
             "-map", "0:v:0", "-map", "1:a:0",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
             "-t", "%.6f" % min(n_clips * CLIP_DUR, audio_dur),
             str(FINAL)], "mux")
    if r.returncode != 0:
        sys.exit(1)
    log(f"DONE {FINAL.name} {FINAL.stat().st_size/1e6:.1f}MB")
    shutil.rmtree(OUT, ignore_errors=True)
    log("cleaned strobe clips")

# ---------------------------------------------------------------- step 5
def make_mask(period, fi, fo, path):
    if path.exists():
        path.unlink()
    fo_start = period - fo
    vf = (
        f"fade=t=in:st=0:d={fi}:color=black,"
        f"fade=t=out:st={fo_start}:d={fo}:color=black,"
        f"format=gbrp"
    )
    r = run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "lavfi", "-i", f"color=white:s=1280x720:r=60:d={period/60:.6f}",
        "-vf", vf, "-frames:v", str(period),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", str(path),
    ], f"mask_p{period}")
    return r.returncode == 0

def fade_variant(tag, src, period, fi, fo):
    out = SISSY_DIR / f"Ajja_Liveset3h_Sissymaker_WetDream_{tag}_60fps_FADE.mp4"
    if out.exists() and out.stat().st_size > 100_000_000:
        log(f"SKIP (fade exists): {out.name}")
        return
    mask = SISSY_DIR / f"mask_p{period}.mp4"
    if not make_mask(period, fi, fo, mask):
        log(f"mask failed for {tag}")
        sys.exit(1)
    if out.exists():
        out.unlink()
    fc = (
        "[0:v]format=gbrp[a];"
        "[1:v]format=gbrp[m];"
        "[a][m]blend=all_mode=multiply:shortest=1,format=yuv420p[v]"
    )
    r = run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(src),
        "-stream_loop", "-1", "-i", str(mask),
        "-filter_complex", fc,
        "-map", "[v]", "-map", "0:a:0",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
        "-c:a", "copy", str(out),
    ], f"fade_{tag}")
    if r.returncode != 0:
        sys.exit(1)
    log(f"DONE {out.name} {out.stat().st_size/1e6:.1f}MB")

# ---------------------------------------------------------------- main
FADES = {
    "14BEATS": ("Ajja_Liveset3h_Sissymaker_WetDream_14BEATS_60fps.mp4", 360, 4, 6),
    "14bpm":   ("Ajja_Liveset3h_Sissymaker_WetDream_14bpm_60fps.mp4",   257, 4, 6),
    "STROBE140": ("Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps.mp4", 26, 2, 4),
}

def main():
    step = sys.argv[1] if len(sys.argv) > 1 else "all"
    log(f"=== regenerate_masterpiece.py step={step} ===")

    if step in ("all", "intermediate"):
        build_intermediate()

    if step in ("all", "14bpm"):
        build_liveset(60.0 / 14.0, 257, "14bpm",
                      "Ajja_Liveset3h_Sissymaker_WetDream_14bpm_60fps.mp4", 8)

    if step in ("all", "14beats"):
        build_liveset(14.0 * (60.0 / PSY_BPM), 360, "14beats",
                      "Ajja_Liveset3h_Sissymaker_WetDream_14BEATS_60fps.mp4", 8)

    if step in ("all", "strobe"):
        build_strobe()

    if step in ("all", "fade"):
        for tag, (src_name, period, fi, fo) in FADES.items():
            src = SISSY_DIR / src_name
            if not src.exists():
                log(f"MISSING SRC {src}")
                sys.exit(1)
            fade_variant(tag, src, period, fi, fo)

    log("ALL_REQUESTED_STEPS_DONE")

if __name__ == "__main__":
    main()
