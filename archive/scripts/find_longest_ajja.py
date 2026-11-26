#!/usr/bin/env python3
import subprocess
from pathlib import Path

music = Path(r"C:\Users\hyper\Music")
cands = []
for p in music.rglob("*.mp3"):
    if "ajja" not in p.name.lower():
        continue
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
        capture_output=True, text=True,
    )
    try:
        cands.append((float(r.stdout.strip()), p.name, str(p)))
    except Exception:
        pass

print("count", len(cands), flush=True)
for d, n, path in sorted(cands, reverse=True)[:12]:
    print(f"{d:10.1f}s {d/3600:.2f}h  {n}", flush=True)
if cands:
    best = max(cands)
    print("BEST_PATH", best[2], flush=True)
    print("BEST_DUR", best[0], flush=True)
