#!/usr/bin/env python3
import subprocess, sys
from pathlib import Path

video = Path(r"C:\Users\hyper\Videos\sissymaker\liveset60_14beats\video_copy.mp4")
audio = Path(r"C:\Users\hyper\Music\Ajja 2026 (Modern Psytrance of Today) @DimensionFestivalNZ.mp3")
final = Path(r"C:\Users\hyper\Videos\sissymaker\Ajja_Liveset3h_Sissymaker_WetDream_14BEATS_60fps.mp4")

print("video", video.exists(), video.stat().st_size if video.exists() else 0, flush=True)
print("audio", audio.exists(), flush=True)

if final.exists():
    final.unlink()

cmd = [
    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
    "-i", str(video), "-i", str(audio),
    "-map", "0:v:0", "-map", "1:a:0",
    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
    "-t", "10774.3",
    str(final),
]
print("muxing...", flush=True)
r = subprocess.run(cmd, capture_output=True, text=True)
print("rc", r.returncode, flush=True)
if r.stderr:
    print(r.stderr[-500:], flush=True)
if r.returncode == 0:
    print("SIZE_MB", final.stat().st_size / 1e6, flush=True)
    pr = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(final)],
        capture_output=True, text=True,
    )
    print("DURATION", pr.stdout.strip(), flush=True)
