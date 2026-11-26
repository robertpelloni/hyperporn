#!/usr/bin/env python3
"""Detect intro-end for each source: first stable run of content-like frames.

Title cards here are dark purple glitter / neon logo sequences.
Content is brighter with skin tones and higher detail.
"""
import subprocess, json
from pathlib import Path

SISSY = Path(r"C:\Users\hyper\Videos\sissymaker")
SOURCES = [
    "Black Owned Slut Trainer Emperor Hypnos (1).mp4",
    "Cum Slut Destiny 2 EmperorHypnos (1).mp4",
    "Emperor Hypnos   Sissymaker 6 (1).mp4",
    "fbj2233 - SMX.mp4",
    "IntenseObsessions - EmperorHypnos Sissy maker 1- HD upscale and clean sound.mp4",
    "Music Video - Emperorhypnos - Sissy Cocksucking Submission (1).mp4",
    "Music Video - Emperorhypnos - Sissymaker Ii (1).mp4",
    "Music Video - Emperorhypnos - Sissymaker Iii (1).mp4",
    "PMVArchive - SM9 CAP.mp4",
    "PMVArchive - Ssm7 Caption HQ.mp4",
    "PMVArchive - SSM8 CANDY.mp4",
    "PMVArchive - SSMK5 - part I.mp4",
    "PMVArchive - SSMK5 - part II.mp4",
    "Sissy Cum Dumpster Submission by EmperorHypnos (1).mp4",
    "Sissy Maker IV by Emperor Hypnos (1).mp4",
]

def stats_window(path, start, dur=0.5):
    """Mean YAVG/UAVG/VAVG and scene score over a short window."""
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-ss", f"{start:.2f}", "-t", f"{dur:.2f}", "-i", str(path),
        "-vf", "signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-",
        "-f", "null", "-",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    ys = []
    for line in r.stdout.splitlines():
        if "YAVG=" in line:
            try:
                ys.append(float(line.split("YAVG=")[1].strip()))
            except ValueError:
                pass
    return sum(ys) / len(ys) if ys else None

def detect(name):
    p = SISSY / name
    # sample every 1s up to 45s
    samples = []
    for t in range(0, 46):
        y = stats_window(p, t)
        samples.append((t, y))
        # print(f"    {name[:30]} t={t} y={y}")
    # content-like: YAVG typically > 60 for these; intro logos sit ~5-40
    # find first t where next 3 consecutive samples all > 55
    trim = 0
    for i, (t, y) in enumerate(samples):
        if y is None:
            continue
        nxt = samples[i:i + 3]
        if len(nxt) == 3 and all(yy is not None and yy > 55 for _, yy in nxt):
            trim = t
            break
    else:
        # fallback: first sample > 55, else 0
        for t, y in samples:
            if y is not None and y > 55:
                trim = t
                break
    return trim, samples

print("=== intro detection (YAVG-based) ===")
results = {}
for name in SOURCES:
    trim, samples = detect(name)
    results[name] = trim
    ys = " ".join(f"{t}:{int(y) if y is not None else '-'}" for t, y in samples[:25])
    print(f"\n{name[:60]}")
    print(f"  TRIM={trim}s")
    print(f"  y0-24: {ys}")

out = SISSY / "intro_trims.json"
out.write_text(json.dumps(results, indent=2))
print("\nWROTE", out)
print("SUM", sum(results.values()), "seconds of intro total")
