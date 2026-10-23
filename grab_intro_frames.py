import subprocess
from pathlib import Path

SISSY = Path(r"C:\Users\hyper\Videos\sissymaker")
OUT = SISSY / "framecheck" / "intro"
OUT.mkdir(parents=True, exist_ok=True)

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

def grab(video, t, tag):
    video = Path(video)
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in video.stem)[:36]
    out = OUT / f"{safe}__{tag}.png"
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-ss", f"{t:.2f}", "-i", str(SISSY / video.name),
           "-frames:v", "1", "-vf", "scale=800:-1", str(out)]
    r = subprocess.run(cmd, capture_output=True, timeout=90)
    return out if r.returncode == 0 and out.exists() else None

for name in SOURCES:
    print(f"\n=== {name[:60]} ===")
    for t in (0.3, 2.0, 5.0, 8.0, 12.0, 20.0):
        p = grab(name, t, f"t{int(t*10):03d}")
        print(f"  t={t:5.1f}s -> {p.name if p else 'FAIL'}")
print("\nDONE", len(list(OUT.glob('*.png'))), "frames")
