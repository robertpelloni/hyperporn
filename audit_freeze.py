#!/usr/bin/env python3
"""Freeze-check second-half sissymaker clips across all six livesets."""
import hashlib, subprocess
from pathlib import Path

work = Path(r"C:\Users\hyper\Videos\sissymaker")
files = {
    "BEATS-orig": work / "Ajja_Liveset3h_Sissymaker_WetDream_14BEATS_60fps.mp4",
    "BEATS-FADE": work / "Ajja_Liveset3h_Sissymaker_WetDream_14BEATS_60fps_FADE.mp4",
    "14bpm-orig": work / "Ajja_Liveset3h_Sissymaker_WetDream_14bpm_60fps.mp4",
    "14bpm-FADE": work / "Ajja_Liveset3h_Sissymaker_WetDream_14bpm_60fps_FADE.mp4",
    "STROBE-orig": work / "Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps.mp4",
    "STROBE-FADE": work / "Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps_FADE.mp4",
}

def grab(f, t):
    png = work / "gz.png"
    subprocess.run(["ffmpeg", "-y", "-ss", f"{t:.3f}", "-i", str(f), "-frames:v", "1", str(png)], capture_output=True)
    return hashlib.md5(png.read_bytes()).hexdigest()[:10]

# For each file sample 5 frames spanning one full clip at a second-half timestamp
# 14BEATS clip=6s at t=8000 (clip index 1333, sissy if even? 1333 odd=wet). use 8004 => 1334 even sissy
# 14bpm clip=4.2857 at t=8000
# strobe clip=0.4333
tests = {
    "BEATS-orig": (8004.0, 6.0),
    "BEATS-FADE": (8004.0, 6.0),
    "14bpm-orig": (8001.0, 4.2857),
    "14bpm-FADE": (8001.0, 4.2857),
    "STROBE-orig": (8001.0, 0.4333),
    "STROBE-FADE": (8001.0, 0.4333),
}

for name, f in files.items():
    if not f.exists():
        print(name, "MISSING", flush=True)
        continue
    t0, dur = tests[name]
    hs = [grab(f, t0 + i * dur / 5) for i in range(5)]
    frozen = len(set(hs)) == 1
    half_frozen = len(set(hs[:2])) == 1 or len(set(hs[-2:])) == 1
    print(f"{name:12s} t0={t0} frozen={frozen} half_or_more_dup={len(set(hs))<5} hashes={hs}", flush=True)

print("FREEZE_AUDIT_DONE", flush=True)
