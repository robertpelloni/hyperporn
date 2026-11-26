#!/usr/bin/env python3
"""Rebuild sissy_gop26.mp4 with normalized timestamps.

The previous build used the concat demuxer on mixed-fps sources (20/25/30/VFR),
which produced timestamp gaps. fps=60 then filled those gaps with duplicate
frames, stretching 3164s of content into 21570s of mostly-frozen video.
Per-file setpts=N/FPS/TB forces exact CFR; then concat -c copy.
"""
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
W, H, FPS = 1280, 720, 60
KEYINT = 26

def run(cmd, label):
    print("START", label, flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    print("END", label, "rc", r.returncode, flush=True)
    if r.returncode != 0:
        print((r.stderr or "")[-800:], flush=True)
        sys.exit(1)

def dur(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout.strip())

tmp = OUT / "sissy_norm"
tmp.mkdir(exist_ok=True)
parts = []
for i, src in enumerate(SISSY):
    part = tmp / f"part_{i:02d}.mp4"
    parts.append(part)
    if part.exists() and part.stat().st_size > 100_000:
        print("skip", part.name, flush=True)
        continue
    vf = (
        f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
        f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,"
        f"fps={FPS},setpts=N/{FPS}/TB,format=yuv420p"
    )
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(src), "-an",
        "-vf", vf,
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
        "-g", str(KEYINT), "-keyint_min", str(KEYINT), "-sc_threshold", "0",
        "-r", str(FPS), "-pix_fmt", "yuv420p",
        str(part),
    ], f"part_{i:02d}")
    print("  dur", dur(part), flush=True)

listf = tmp / "list.txt"
with listf.open("w", encoding="utf-8") as f:
    for p in parts:
        f.write("file '%s'\n" % p.as_posix())

sissy_int = OUT / "sissy_gop26.mp4"
if sissy_int.exists():
    sissy_int.unlink()
run([
    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
    "-f", "concat", "-safe", "0", "-i", str(listf),
    "-c", "copy",
    str(sissy_int),
], "concat_copy")

d = dur(sissy_int)
print("sissy_dur", d, "MB", sissy_int.stat().st_size / 1e6, flush=True)
if not (3100 < d < 3250):
    print("UNEXPECTED DURATION", d, flush=True)
    sys.exit(1)
print("GOP26_REBUILD_OK", flush=True)
