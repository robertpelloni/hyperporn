#!/usr/bin/env python3
"""Preflight guard (Gemini roast fix #6): fail fast before a batch.

Checks every drive/junction the builders touch resolves and has
free space, the ffmpeg/ESRGAN binaries exist, and no source pool
file vanished. Exit 1 with a clear list on any failure.
Usage: python preflight.py
"""
import shutil, subprocess, sys
from pathlib import Path

WORK = Path(__file__).resolve().parent
CHECKS = [
    ("G: repo+sources", WORK, 10),
    ("C: checkout+scratch link", Path(r"C:\hyperporn_ultra_work"), 5),
    ("M: media libraries", Path(r"M:\hyperporn_media"), 10),
]
BINARIES = [
    WORK / "tools" / "ffmpeg-7.1.1-essentials_build" / "bin" / "ffmpeg.exe",
    WORK / "tools" / "ffmpeg-7.1.1-essentials_build" / "bin" / "ffprobe.exe",
    Path(r"C:\Users\hyper\workspace\hyperporn\comfy-pipeline\tools\realesrgan\realesrgan-ncnn-vulkan.exe"),
]

def main():
    bad = []
    for label, path, min_gb in CHECKS:
        if not path.exists():
            bad.append(f"{label}: MISSING {path}"); continue
        free = shutil.disk_usage(path).free / 1e9
        resolved = path.resolve()
        status = "OK" if free >= min_gb else "LOW"
        print(f"{status} {label}: {path} -> {resolved} free={free:.1f}GB (min {min_gb})")
        if free < min_gb:
            bad.append(f"{label}: only {free:.1f}GB free")
    for b in BINARIES:
        print(("OK  " if b.exists() else "MISS") + f" binary {b}")
        if not b.exists():
            bad.append(f"binary missing: {b}")
    for pool in ("_sm", "_ai"):
        n = len(list((WORK / pool).glob("*.mp4")))
        print(f"OK  pool {pool}: {n} files" if n else f"MISS pool {pool}")
        if not n:
            bad.append(f"pool empty: {pool}")
    if bad:
        print("PREFLIGHT FAIL:"); [print(" -", b) for b in bad]
        return 1
    print("PREFLIGHT PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
