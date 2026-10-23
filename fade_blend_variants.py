#!/usr/bin/env python3
"""Soft-cut fade variants: loop a one-period fade mask and multiply-blend."""
import subprocess, sys
from pathlib import Path

SISSY_DIR = Path(r"C:\Users\hyper\Videos\sissymaker")
W, H, FPS = 1280, 720, 60

# name, source, clip_seconds, fade_in, fade_out
JOBS = [
    (
        "Ajja_Liveset3h_Sissymaker_WetDream_14BEATS_60fps_FADE.mp4",
        "Ajja_Liveset3h_Sissymaker_WetDream_14BEATS_60fps.mp4",
        6.0, 0.07, 0.10,
    ),
    (
        "Ajja_Liveset3h_Sissymaker_WetDream_14bpm_60fps_FADE.mp4",
        "Ajja_Liveset3h_Sissymaker_WetDream_14bpm_60fps.mp4",
        60.0 / 14.0, 0.07, 0.10,
    ),
    (
        "Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps_FADE.mp4",
        "Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps.mp4",
        26.0 / 60.0, 0.035, 0.05,
    ),
]

def make_mask(clip: float, fi: float, fo: float, dest: Path):
    # one loopable period: fade-in from black, hold white, fade-out to black
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "lavfi", "-i", f"color=c=white:s={W}x{H}:r={FPS}:d={clip}",
        "-vf", f"fade=t=in:st=0:d={fi}:color=black,fade=t=out:st={clip - fo}:d={fo}:color=black",
        "-frames:v", str(max(int(round(clip * FPS)), 2)),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        str(dest),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print("mask rc", r.returncode, dest.name, dest.stat().st_size if dest.exists() else 0, flush=True)
    if r.returncode != 0:
        print(r.stderr[-300:], flush=True)
        sys.exit(1)

def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    for out_name, src_name, clip, fi, fo in JOBS:
        if which != "all":
            key = which.lower()
            if key not in out_name.lower() and key not in src_name.lower():
                continue
        src = SISSY_DIR / src_name
        out = SISSY_DIR / out_name
        if not src.exists():
            print("missing", src_name, flush=True)
            continue
        if out.exists() and out.stat().st_size > 1_000_000:
            print("exists", out_name, flush=True)
            continue
        mask = SISSY_DIR / f"mask_{int(clip*1000)}ms.mp4"
        make_mask(clip, fi, fo, mask)
        print("BLEND", src_name, "->", out_name, flush=True)
        r = subprocess.run(
            [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-i", str(src),
                "-stream_loop", "-1", "-i", str(mask),
                "-filter_complex",
                "[0:v][1:v]blend=all_mode=multiply[v]",
                "-map", "[v]", "-map", "0:a?",
                "-shortest",
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "24",
                "-c:a", "copy",
                str(out),
            ],
            capture_output=True, text=True,
        )
        print("blend rc", r.returncode, flush=True)
        if r.stderr:
            print(r.stderr[-400:], flush=True)
        if r.returncode == 0:
            print("SIZE_MB", out.stat().st_size / 1e6, flush=True)
            pr = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)],
                capture_output=True, text=True,
            )
            print("DURATION", pr.stdout.strip(), flush=True)
        else:
            sys.exit(1)
    print("FADE_ALL_DONE", flush=True)

if __name__ == "__main__":
    main()
