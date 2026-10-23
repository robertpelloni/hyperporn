#!/usr/bin/env python3
"""Build the 3 FADE variants in parallel via RGB-multiply mask (chroma-safe).

Uses ultrafast preset for speed (the fade is a full 3h re-encode; veryfast was
~0.42x realtime on this 4-core host). Chroma stays intact because the multiply
is done in RGB space (YUV multiply tinted green).
"""
import subprocess, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

SISSY_DIR = Path(r"C:\Users\hyper\Videos\sissymaker")

JOBS = {
    "14BEATS":   ("Ajja_Liveset3h_Sissymaker_WetDream_14BEATS_60fps.mp4",   360, 4, 6),
    "14bpm":     ("Ajja_Liveset3h_Sissymaker_WetDream_14bpm_60fps.mp4",     257, 4, 6),
    "STROBE140": ("Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps.mp4",  26, 2, 4),
}

def log(msg):
    print(msg, flush=True)

def run(cmd, label):
    log(f"START {label} {time.strftime('%H:%M:%S')}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    log(f"END {label} rc={r.returncode} {time.strftime('%H:%M:%S')}")
    if r.returncode != 0:
        log((r.stderr or "")[-500:])
    return r.returncode == 0

def make_mask(period, fi, fo, path):
    if path.exists():
        path.unlink()
    # NOTE: ffmpeg fade filter's st/d are in SECONDS. fi/fo are frame counts,
    # so convert to seconds at 60fps. (Previously d=fi was read as fi seconds,
    # which made fade_in span most of the clip and fade_out never fire.)
    fi_s = fi / 60.0
    fo_s = fo / 60.0
    fo_start_s = (period - fo) / 60.0
    vf = (
        f"fade=t=in:st=0:d={fi_s:.6f}:color=black,"
        f"fade=t=out:st={fo_start_s:.6f}:d={fo_s:.6f}:color=black,"
        f"format=gbrp"
    )
    return run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "lavfi", "-i", f"color=white:s=1280x720:r=60:d={period/60:.6f}",
        "-vf", vf, "-frames:v", str(period),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", str(path),
    ], f"mask_p{period}")

def fade_one(tag, src_name, period, fi, fo):
    src = SISSY_DIR / src_name
    out = SISSY_DIR / f"Ajja_Liveset3h_Sissymaker_WetDream_{tag}_60fps_FADE.mp4"
    if out.exists() and out.stat().st_size > 100_000_000:
        log(f"SKIP (exists): {out.name}")
        return True
    mask = SISSY_DIR / f"mask_p{period}.mp4"
    if not make_mask(period, fi, fo, mask):
        return False
    if out.exists():
        out.unlink()
    fc = (
        "[0:v]format=gbrp[a];"
        "[1:v]format=gbrp[m];"
        "[a][m]blend=all_mode=multiply:shortest=1,format=yuv420p[v]"
    )
    ok = run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(src),
        "-stream_loop", "-1", "-i", str(mask),
        "-filter_complex", fc,
        "-map", "[v]", "-map", "0:a:0",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
        "-c:a", "copy", str(out),
    ], f"fade_{tag}")
    if ok:
        log(f"DONE {out.name} {out.stat().st_size/1e6:.1f}MB")
    return ok

def main():
    log("=== fades_parallel.py (ultrafast, 3-way parallel) ===")
    # pre-build masks first (fast, serial)
    masks_ok = True
    for tag, (_, period, fi, fo) in JOBS.items():
        m = SISSY_DIR / f"mask_p{period}.mp4"
        if m.exists() and m.stat().st_size > 1000:
            continue
        if not make_mask(period, fi, fo, m):
            masks_ok = False
    if not masks_ok:
        log("mask build failed")
        sys.exit(1)

    ok = True
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(fade_one, tag, *rest): tag for tag, rest in JOBS.items()}
        for fut in as_completed(futs):
            tag = futs[fut]
            if not fut.result():
                log(f"FAILED {tag}")
                ok = False
    log("FADES_DONE" if ok else "FADES_FAILED")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
