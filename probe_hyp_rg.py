import re
import subprocess
from pathlib import Path

h = Path(r"C:\Users\hyper\Videos\hypnoshit")
for p in sorted(h.iterdir()):
    if p.suffix.lower() not in (".mp3", ".m4a", ".wav", ".flac"):
        continue
    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(p), "-af", "replaygain", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    g = re.search(r"replaygain_track_gain:\s*([-\d.]+)", r.stderr)
    pk = re.search(r"replaygain_track_peak:\s*([-\d.]+)", r.stderr)
    gs = g.group(1) if g else "NONE"
    ps = pk.group(1) if pk else "?"
    print(f"{p.name[:58]:58} rg={gs:>8} peak={ps}")
