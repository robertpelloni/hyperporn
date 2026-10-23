import re
import subprocess
from pathlib import Path

s = Path(r"C:\Users\hyper\Videos\sissymaker")
files = [p for p in s.iterdir() if p.is_file() and p.suffix.lower() == ".mp3"]
for p in sorted(files):
    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(p), "-af", "replaygain", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    gain = re.search(r"replaygain_track_gain:\s*([-\d.]+)", r.stderr)
    r2 = subprocess.run(
        ["ffmpeg", "-hide_banner", "-ss", "0", "-t", "60", "-i", str(p),
         "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    mean = re.search(r"mean_volume:\s*([-\d.]+)", r2.stderr)
    g = gain.group(1) if gain else "?"
    m = mean.group(1) if mean else "?"
    print(f"{p.name[:52]:52} rg={g:>7}dB mean60s={m}dB")
