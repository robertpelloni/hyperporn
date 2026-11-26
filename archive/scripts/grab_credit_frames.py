import subprocess, os
from pathlib import Path

SISSY = Path(r"C:\Users\hyper\Videos\sissymaker")
OUT = SISSY / "framecheck" / "credits"
OUT.mkdir(parents=True, exist_ok=True)

# source videos only (skip Ajja outputs, masks)
sources = []
for f in sorted(SISSY.glob("*.mp4")):
    if f.name.startswith(("Ajja_", "mask_", "fade_")):
        continue
    if f.stat().st_size < 10_000_000:
        continue
    sources.append(f)

def grab(video, t, tag):
    out = OUT / f"{video.stem[:40]}_{tag}.png".replace(" ", "_").replace(",", "")
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1",
           "-vf", "scale=960:-1", str(out)]
    r = subprocess.run(cmd, capture_output=True, timeout=60)
    return out if r.returncode == 0 and out.exists() else None

def dur(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(video)],
                       capture_output=True, text=True, timeout=30)
    try:
        return float(r.stdout.strip())
    except Exception:
        return 0.0

for v in sources:
    d = dur(v)
    print(f"\n{v.name[:60]}  dur={d:.1f}s")
    for t, tag in [(0.5, "start"), (min(3.0, d * 0.05), "early"),
                   (max(0, d - 5), "end"), (max(0, d - 60), "end60")]:
        if t < 0:
            continue
        p = grab(v, t, tag)
        print(f"  {tag:6s} t={t:.1f} -> {p.name if p else 'FAIL'}")

print("\nOUT:", OUT)
print("files:", len(list(OUT.glob('*.png'))))
