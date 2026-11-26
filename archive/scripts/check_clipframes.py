import subprocess
from pathlib import Path

OUTDIR = Path(r"C:\Users\hyper\Videos\sissymaker\liveset60_strobe")

def nframes(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-count_frames",
         "-select_streams", "v:0",
         "-show_entries", "stream=nb_read_frames",
         "-of", "csv=p=0", str(p)],
        capture_output=True, text=True,
    )
    s = (r.stdout or "").strip()
    try:
        return int(s)
    except ValueError:
        return -1

# sample clips across the timeline
idxs = [0, 1, 100, 500, 1000, 2000, 4000, 8000, 12000, 16000, 20000, 22000, 24000, 24800, 24863]
print("idx  frames  size")
for i in idxs:
    p = OUTDIR / f"clip_{i:06d}.mp4"
    if not p.exists():
        print(f"{i:6d}  MISSING")
        continue
    print(f"{i:6d}  {nframes(p):5d}  {p.stat().st_size}")

# bulk scan: count how many clips != 26 frames (sample every 50th for speed)
bad = []
total = 0
for i in range(0, 24864, 50):
    p = OUTDIR / f"clip_{i:06d}.mp4"
    if not p.exists():
        continue
    total += 1
    n = nframes(p)
    if n != 26:
        bad.append((i, n))
print(f"\nsampled {total} clips, bad frame counts: {len(bad)}")
for i, n in bad[:40]:
    print(f"  clip {i}: {n} frames")
