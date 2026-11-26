#!/usr/bin/env python3
"""One-pass periodic luma fade test — try several filter entry points."""
import subprocess
from pathlib import Path

src = Path(r"C:\Users\hyper\Videos\sissymaker\intermediates\wet_gop26.mp4")
work = Path(r"C:\Users\hyper\Videos\sissymaker")
expr = (
    "lutyuv=y='val*if(lt(mod(n\\,60)\\,4)\\,mod(n\\,60)/4\\,"
    "if(gt(mod(n\\,60)\\,52)\\,(60-mod(n\\,60))/8\\,1))'"
)

attempts = [
    ("vf_direct", ["-vf", expr]),
    ("filter_complex", ["-filter_complex", expr + "[v]", "-map", "[v]"]),
    ("filter_script_v", ["-filter_script:v", str(work / "vf_oneshot.txt")]),
]

(work / "vf_oneshot.txt").write_text(expr)

for name, opts in attempts:
    out = work / f"fade_try_{name}.mp4"
    if out.exists():
        out.unlink()
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-t", "3", "-i", str(src),
        *opts,
        "-frames:v", "60",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
        str(out),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(name, "rc", r.returncode, "size", out.stat().st_size if out.exists() else 0, flush=True)
    if r.returncode != 0:
        print("  err", (r.stderr or "").strip().splitlines()[-3:], flush=True)
        continue
    # YAVG at mid (should be bright) and near end (fade-out -> dark)
    for label, t in (("mid", 0.5), ("end", 0.95)):
        png = work / "fo_t.png"
        subprocess.run(["ffmpeg", "-y", "-ss", str(t), "-i", str(out), "-frames:v", "1", str(png)], capture_output=True)
        r2 = subprocess.run(
            ["ffmpeg", "-v", "info", "-i", str(png), "-vf",
             "signalstats,metadata=print:key=lavfi.signalstats.YAVG", "-f", "null", "-"],
            capture_output=True, text=True,
        )
        y = [ln.split("=")[-1] for ln in (r2.stderr + r2.stdout).splitlines() if "YAVG" in ln]
        print(" ", label, "YAVG", y, flush=True)

print("ATTEMPTS_DONE", flush=True)
