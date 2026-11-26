#!/usr/bin/env python3
import hashlib, subprocess
from pathlib import Path

src = Path(r"C:\Users\hyper\Videos\sissymaker\intermediates\sissy_gop26.mp4")
tmp = Path(r"C:\Users\hyper\Videos\sissymaker\sg.png")

for t in (100, 800, 1500, 2200, 3000, 3100):
    hs = []
    for dt in (0, 0.15, 0.4):
        subprocess.run(
            ["ffmpeg", "-y", "-ss", f"{t+dt}", "-i", str(src), "-frames:v", "1", str(tmp)],
            capture_output=True,
        )
        hs.append(hashlib.md5(tmp.read_bytes()).hexdigest()[:8])
    print(f"t={t:5} frozen={len(set(hs)) == 1} {hs}", flush=True)
print("FREEZE_CHECK_DONE", flush=True)
