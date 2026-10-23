import subprocess
from pathlib import Path

SISSY = Path(r"C:\Users\hyper\Videos\sissymaker")
OUT = SISSY / "framecheck" / "s3b"
OUT.mkdir(parents=True, exist_ok=True)

src = SISSY / "Music Video - Emperorhypnos - Sissymaker Iii (1).mp4"
for t in [14, 16, 17, 18, 19, 20]:
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", str(src),
         "-frames:v", "1", str(OUT / f"s3_t{t:03d}.png")],
        capture_output=True,
    )
print("s3 fine frames done")

# spot-check other sources at their current trim point (should be content, not title)
checks = {
    "Music Video - Emperorhypnos - Sissymaker Ii (1).mp4": [0, 2, 4, 6],
    "Emperor Hypnos   Sissymaker 6 (1).mp4": [0, 8, 12, 15, 18],
    "IntenseObsessions - EmperorHypnos Sissy maker 1- HD upscale and clean sound.mp4": [0, 2, 3, 5],
    "Sissy Maker IV by Emperor Hypnos (1).mp4": [0, 2, 4, 6],
    "PMVArchive - SSMK5 - part I.mp4": [0, 1, 2, 4],
}
OUT2 = SISSY / "framecheck" / "spot"
OUT2.mkdir(parents=True, exist_ok=True)
for name, times in checks.items():
    src = SISSY / name
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)[:30]
    for t in times:
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", str(src),
             "-frames:v", "1", str(OUT2 / f"{safe}_t{t:03d}.png")],
            capture_output=True,
        )
    print(f"spot {safe}")
print("ALL DONE")
