#!/usr/bin/env python3
"""Rebuild STROBE from fixed gop26, then produce FADE variants via RGB-multiply mask.

The previous FADE/STROBE exports were sliced from sissy_gop26.mp4 that had
timestamp-gap freeze padding (21570s instead of 3164s). That intermediate is
now rebuilt. Fades use a looping black-edge mask blended in RGB so chroma
stays intact (YUV multiply was tinting green).
"""
import subprocess, sys, time
from pathlib import Path

SISSY_DIR = Path(r"C:\Users\hyper\Videos\sissymaker")
AUDIO = Path(r"C:\Users\hyper\Music\Ajja 2026 (Modern Psytrance of Today) @DimensionFestivalNZ.mp3")

JOBS = {
    # name: (source non-fade liveset, period_frames, fade_in_frames, fade_out_frames)
    "14BEATS": (
        SISSY_DIR / "Ajja_Liveset3h_Sissymaker_WetDream_14BEATS_60fps.mp4",
        360, 4, 6,
    ),
    "14bpm": (
        SISSY_DIR / "Ajja_Liveset3h_Sissymaker_WetDream_14bpm_60fps.mp4",
        257, 4, 6,
    ),
    "STROBE140": (
        SISSY_DIR / "Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps.mp4",
        26, 2, 4,
    ),
}

def run(cmd, label):
    print("START", label, time.strftime("%H:%M:%S"), flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    print("END", label, "rc", r.returncode, time.strftime("%H:%M:%S"), flush=True)
    if r.returncode != 0:
        print((r.stderr or "")[-600:], flush=True)
    return r.returncode == 0

def make_mask(period, fi, fo, path):
    """One period: white body, black fade at both edges."""
    if path.exists():
        path.unlink()
    fo_start = period - fo
    vf = (
        f"fade=t=in:st=0:d={fi}:color=black,"
        f"fade=t=out:st={fo_start}:d={fo}:color=black,"
        f"format=gbrp"
    )
    # generate exact frame count at 60fps, solid white source
    ok = run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "lavfi", "-i", f"color=white:s=1280x720:r=60:d={period/60:.6f}",
        "-vf", vf, "-frames:v", str(period),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
        str(path),
    ], f"mask_p{period}")
    return ok

def fade_variant(tag, src, period, fi, fo):
    out = SISSY_DIR / f"Ajja_Liveset3h_Sissymaker_WetDream_{tag}_60fps_FADE.mp4"
    mask = SISSY_DIR / f"mask_p{period}.mp4"
    if not make_mask(period, fi, fo, mask):
        return False
    if out.exists():
        out.unlink()
    # RGB multiply keeps chroma (white mask = no change; black = fade to black)
    fc = (
        "[0:v]format=gbrp[a];"
        "[1:v]format=gbrp[m];"
        "[a][m]blend=all_mode=multiply:shortest=1,format=yuv420p[v]"
    )
    return run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(src),
        "-stream_loop", "-1", "-i", str(mask),
        "-filter_complex", fc,
        "-map", "[v]", "-map", "0:a:0",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
        "-c:a", "copy",
        str(out),
    ], f"fade_{tag}")

def main():
    # 1) rebuild STROBE liveset from fixed gop26 (stream-copy slices)
    strobe_script = SISSY_DIR / "strobe_fast_60fps.py"
    if not run([sys.executable, str(strobe_script)], "strobe_rebuild"):
        sys.exit(1)

    # 2) FADE variants from the (now clean) non-fade livesets
    for tag, (src, period, fi, fo) in JOBS.items():
        if not src.exists():
            print("MISSING SRC", src, flush=True)
            sys.exit(1)
        if not fade_variant(tag, src, period, fi, fo):
            sys.exit(1)
        p = SISSY_DIR / f"Ajja_Liveset3h_Sissymaker_WetDream_{tag}_60fps_FADE.mp4"
        print("DONE", p.name, f"{p.stat().st_size/1e6:.1f}MB", flush=True)

    print("REBUILD_ALL_OK", flush=True)

if __name__ == "__main__":
    main()
