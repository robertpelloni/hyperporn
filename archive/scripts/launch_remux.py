import subprocess, sys
from pathlib import Path

log = Path(r"C:\Users\hyper\Videos\sissymaker\remux_pmv.log")
err = Path(r"C:\Users\hyper\Videos\sissymaker\remux_pmv.err.log")

with open(log, "w", encoding="utf-8") as lo, open(err, "w", encoding="utf-8") as er:
    p = subprocess.Popen(
        [sys.executable, r"C:\Users\hyper\Videos\sissymaker\remux_pmv.py"],
        stdout=lo, stderr=er,
    )
    print(f"launched PID {p.pid}")
