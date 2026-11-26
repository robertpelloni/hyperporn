import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SISSY = Path(r"C:\Users\hyper\Videos\sissymaker")

print("=== files ===")
for f in sorted(SISSY.glob("*.mp4")):
    name = f.name
    if any(k in name for k in ("\u30cf\u30a4", "pmv", "full", "2GB")):
        print(f"  {name} {f.stat().st_size/1e6:.1f} MB")

SRC = SISSY / "\u30cf\u30a4\u30d1\u30fc\u30dd\u30eb\u30ce.mp4"
if not SRC.exists():
    candidates = list(SISSY.glob("*altaudio_2GB*.mp4"))
    if candidates:
        SRC = candidates[0]
    else:
        sys.exit("no source found")

print(f"\nsource: {SRC.name} {SRC.stat().st_size/1e6:.1f} MB")

OUT = SISSY / "\u30cf\u30a4\u30d1\u30fc\u30dd\u30eb\u30ce_pmv2.mp4"
print(f"target: {OUT.name}")

# Main profile + L4.0 + mp42 brand = max compatibility for web transcoders
cmd = [
    "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning",
    "-i", str(SRC),
    "-c:v", "libx264", "-preset", "fast",
    "-profile:v", "main", "-level", "4.0",
    "-b:v", "1200k", "-maxrate", "1300k", "-bufsize", "2400k",
    "-vf", "scale=1280:720",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
    "-movflags", "+faststart",
    "-brand", "mp42",
    str(OUT),
]
print(f"\nlaunching re-encode (Main profile L4.0)...")
t0 = time.time()
r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
elapsed = time.time() - t0
size = OUT.stat().st_size / 1e6 if OUT.exists() else 0
print(f"\nrc={r.returncode} time={elapsed:.0f}s size={size:.1f}MB")
if r.returncode != 0:
    print((r.stderr or "")[-800:])
    sys.exit(1)
print("PMV2_OK")
