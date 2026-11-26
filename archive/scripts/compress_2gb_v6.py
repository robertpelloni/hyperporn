"""Compress alt full to 2GB (standalone — rebuild_v6 stalled mid-encode)."""
import subprocess
import sys
import time
from pathlib import Path

SISSY = Path(r"C:\Users\hyper\Videos\sissymaker")
SRC = SISSY / "ハイパーポルノ_altaudio_full.mp4"
OUT = SISSY / "ハイパーポルノ_altaudio_2GB.mp4"


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def probe(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(p)],
        capture_output=True, check=True,
    )
    return float(r.stdout.decode("utf-8", errors="replace").strip())


def main():
    if not SRC.exists():
        sys.exit(f"missing {SRC}")
    log(f"compress {OUT.name} from {SRC.name} ({SRC.stat().st_size/1e6:.1f}MB)")
    if OUT.exists():
        OUT.unlink()
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(SRC),
         "-c:v", "libx264", "-preset", "veryfast",
         "-b:v", "1200k", "-maxrate", "1300k", "-bufsize", "2400k",
         "-vf", "scale=1280:720",
         "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", str(OUT)],
        capture_output=True, text=True,
    )
    size = OUT.stat().st_size / 1e6 if OUT.exists() else 0
    log(f"rc={r.returncode} size={size:.1f}MB")
    if r.returncode != 0:
        log((r.stderr or "")[-500:])
        sys.exit(1)
    log(f"OUT {OUT.name} {probe(OUT):.2f}s {size:.1f}MB")
    log("COMPRESS_2GB_V6_OK")


if __name__ == "__main__":
    main()
