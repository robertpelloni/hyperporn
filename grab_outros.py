import subprocess, json
from pathlib import Path

SISSY = Path(r"C:\Users\hyper\Videos\sissymaker")
OUT = SISSY / "framecheck" / "outro"
OUT.mkdir(parents=True, exist_ok=True)

def probe_dur(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(p)],
        capture_output=True, text=True,
    )
    return float(r.stdout.strip())

TRIM = json.loads((SISSY / "intro_trims.json").read_text())

for name in TRIM:
    src = SISSY / name
    if not src.exists():
        print("MISSING", name)
        continue
    dur = probe_dur(src)
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)[:36]
    # grab last 90s at 10s steps
    for dt in [0, 10, 20, 30, 45, 60, 75, 85]:
        t = max(0, dur - dt)
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", str(src),
             "-frames:v", "1", str(OUT / f"{safe}_end{dt:03d}.png")],
            capture_output=True,
        )
    print(f"{dur:8.1f}s  {name[:55]}")
print("DONE")
