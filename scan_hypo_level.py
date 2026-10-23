import subprocess
from pathlib import Path

HYPO = Path(r"C:\Users\hyper\Videos\sissymaker\hypo_mix_v2.m4a")
DUR = 10798.8

print("t_start  mean_vol  peak_vol  (hypnoshit mix scan)")
t = 0.0
while t < DUR - 30:
    win = 60.0
    r = subprocess.run(
        ["ffmpeg", "-v", "info", "-ss", f"{t:.1f}", "-t", f"{win:.1f}",
         "-i", str(HYPO), "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    mean = peak = None
    for line in (r.stderr or "").splitlines():
        if "mean_volume" in line:
            mean = line.split(":")[-1].strip()
        if "max_volume" in line:
            peak = line.split(":")[-1].strip()
    print(f"{t:8.0f}  {mean}  {peak}")
    t += 300.0
