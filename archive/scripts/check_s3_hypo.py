import subprocess, json
from pathlib import Path

SISSY = Path(r"C:\Users\hyper\Videos\sissymaker")
OUT = SISSY / "framecheck" / "s3"
OUT.mkdir(parents=True, exist_ok=True)

src = SISSY / "Music Video - Emperorhypnos - Sissymaker Iii (1).mp4"
for t in [0, 3, 6, 9, 12, 15, 18, 21, 24, 30, 40, 60]:
    out = OUT / f"s3_t{t:03d}.png"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", str(src),
         "-frames:v", "1", str(out)],
        capture_output=True,
    )
print("frames done")

HYPO = Path(r"C:\Users\hyper\Videos\hypnoshit")
rows = []
for p in sorted(HYPO.iterdir()):
    if p.suffix.lower() not in (".mp3", ".m4a"):
        continue
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(p)],
        capture_output=True, text=True,
    )
    dur = float(r.stdout.strip()) if r.stdout.strip() else 0
    rows.append((p.name, dur))
    print(f"{dur:9.1f}s  half_start={dur/2:9.1f}  {p.name[:70]}")

total_half = sum(d / 2 for _, d in rows)
print(f"\ntotal second-half duration: {total_half:.1f}s")
