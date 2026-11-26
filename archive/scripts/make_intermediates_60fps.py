#!/usr/bin/env python3
"""Build all-intra 60fps intermediates for fast clip extraction."""
import subprocess, sys
from pathlib import Path

SISSY_DIR = Path(r"C:\Users\hyper\Videos\sissymaker")
OUT = SISSY_DIR / "intermediates"
OUT.mkdir(exist_ok=True)

SISSY = [
    SISSY_DIR / "Sissy Maker 1 by Emperor Hypnos (1).mp4",
    SISSY_DIR / "Emperor Hypnos Sissymaker II (1).mp4",
    SISSY_DIR / "EmperorHypnos - Sissy Maker III [720p].mp4",
    SISSY_DIR / "Sissy Maker IV by Emperor Hypnos (1).mp4",
    SISSY_DIR / "Sissymaker 5 - EmperorHypnos.mp4",
    SISSY_DIR / "Sissy Maker 6 by Emperor Hypnos (1).mp4",
    SISSY_DIR / "Sissymaker 7 BBC edition.mp4",
    SISSY_DIR / "Sissymaker 8 - Rapture PMV (1).mp4",
    SISSY_DIR / "SissyMaker 9 - Breed Black PMV (1).mp4",
]
WET = SISSY_DIR / "JPVT1109 - Wet Dreams AI Goon Therapy (parts 1-15).mp4"
W, H, FPS = 1280, 720, 60

def run(cmd):
    print("RUN", " ".join(str(c) for c in cmd)[:200], flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-800:], flush=True)
        sys.exit(1)

# concat sissymaker 1-9 into one all-intra file
listf = OUT / "sissy_list.txt"
with listf.open("w", encoding="utf-8") as f:
    for p in SISSY:
        # concat demuxer needs escaped quotes; use absolute path with forward slashes
        f.write("file '%s'\n" % p.as_posix())

sissy_int = OUT / "sissy_all_60fps.mkv"
if not sissy_int.exists() or sissy_int.stat().st_size < 1000:
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(listf),
        "-an",
        "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},format=yuv420p",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
        "-g", "1", "-x264-params", "keyint=1:min-keyint=1:scenecut=0",
        str(sissy_int),
    ])
print("sissy_int", sissy_int.stat().st_size / 1e6, "MB", flush=True)

wet_int = OUT / "wet_all_60fps.mkv"
if not wet_int.exists() or wet_int.stat().st_size < 1000:
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(WET),
        "-an",
        "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},format=yuv420p",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
        "-g", "1", "-x264-params", "keyint=1:min-keyint=1:scenecut=0",
        str(wet_int),
    ])
print("wet_int", wet_int.stat().st_size / 1e6, "MB", flush=True)

def dur(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout.strip())

print("sissy_dur", dur(sissy_int), flush=True)
print("wet_dur", dur(wet_int), flush=True)
print("INTERMEDIATES_DONE", flush=True)
