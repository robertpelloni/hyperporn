import subprocess, sys, time
from pathlib import Path

SISSY = Path(r"C:\Users\hyper\Videos\sissymaker")
SRC = SISSY / "Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps_FADE_v2b.mp4"
OUT = SISSY / "Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps_FADE_v2b_2GB.mp4"

def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)

if not SRC.exists():
    sys.exit(f"missing {SRC}")
if OUT.exists():
    OUT.unlink()

# 10774 s target < 2 GB => ~1500 kbps total
# video 1350k + audio 128k leaves headroom for container
log("encoding 2GB copy (libx264 1350k / aac 128k) ...")
r = subprocess.run(
    ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
     "-i", str(SRC),
     "-c:v", "libx264", "-preset", "medium",
     "-b:v", "1350k", "-maxrate", "1400k", "-bufsize", "2800k",
     "-vf", "scale=1280:720",
     "-c:a", "aac", "-b:a", "128k",
     "-movflags", "+faststart",
     str(OUT)],
    capture_output=True, text=True,
)
log(f"rc={r.returncode}")
if r.returncode != 0:
    log(r.stderr[-600:])
    sys.exit(1)
sz = OUT.stat().st_size / 1e6
log(f"DONE {OUT.name} {sz:.1f}MB")
