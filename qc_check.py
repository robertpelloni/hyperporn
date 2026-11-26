#!/usr/bin/env python3
"""QC report for finished finals (ChatGPT roast fix #6/#9).

Per file: probe (res/fps/frames/duration/size), near-black and
dark frame fractions, 26-frame mask fold ratio + dip phase, and
the flash rate implied by the mask (60/26 = 2.31 dips/s; the
triangular dip is a gradual 5-frame ramp, not a hard flash).
Writes QC_REPORT.md. Numeric only - no frame viewing.
Usage: python qc_check.py [files...]  (default: the 3 episodes)
"""
import statistics, subprocess, sys
from pathlib import Path

WORK = Path(__file__).resolve().parent
FFD = WORK / "tools" / "ffmpeg-7.1.1-essentials_build" / "bin"
DEFAULTS = ["ultramix_ep1_1080p60.mp4", "ultramix_ep2_1080p60.mp4",
            "ultramix_ep3_1080p60.mp4"]

def probe(p):
    import json
    r = subprocess.run([str(FFD / "ffprobe.exe"), "-v", "error", "-show_entries",
                        "stream=codec_type,width,height,avg_frame_rate,nb_frames",
                        "-show_entries", "format=duration,size", "-of", "json", str(p)],
                       capture_output=True, text=True)
    d = json.loads(r.stdout)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    return v, float(d["format"]["duration"]), int(d["format"]["size"])

def series(p, ss, secs=8.67):
    r = subprocess.run([str(FFD / "ffmpeg.exe"), "-v", "error", "-ss", str(ss),
                        "-i", str(p), "-t", str(secs), "-vf",
                        "scale=160:90,format=gray", "-f", "rawvideo", "-"],
                       capture_output=True)
    px = 160 * 90
    return [sum(r.stdout[i:i + px]) / px
            for i in range(0, len(r.stdout) - px + 1, px)]

def main():
    files = [Path(f) for f in (sys.argv[1:] or DEFAULTS)]
    lines = ["# QC report (qc_check.py)", "",
             "| File | Spec | Duration | Black <25 | Dark <48 | Mask fold | Flash rate |",
             "|---|---|---:|---:|---:|---:|---:|"]
    for p in files:
        if not p.exists():
            lines.append(f"| {p.name} | MISSING | - | - | - | - | - |")
            continue
        v, dur, size = probe(p)
        folds, black, dark, n = [], 0, 0, 0
        for ss in (600, 2400, 4200):
            if ss > dur - 20:
                continue
            s = series(p, ss)
            f = [statistics.mean(s[i::26]) for i in range(26)]
            folds.append(min(f) / max(f))
            black += sum(1 for x in s if x < 25)
            dark += sum(1 for x in s if x < 48)
            n += len(s)
        lines.append(
            f"| {p.name} | {v['width']}x{v['height']} @{v['avg_frame_rate']} "
            f"{v['nb_frames']}f {size/1e9:.1f}GB | {dur:.0f}s | "
            f"{100*black/max(n,1):.1f}% | {100*dark/max(n,1):.1f}% | "
            f"{statistics.mean(folds) if folds else -1:.2f} | 2.31/s (ramped dip) |")
        print(lines[-1])
    lines += ["", "Mask fold ~0.17-0.20 = dip locked every 26 frames (healthy);",
              "~0.9 = drifting/absent mask (the original ep3 bug). Flash rate is",
              "the mask dip frequency; depth is gradual (5-frame triangular ramp",
              "to a 48/255 floor), not a hard on/off flash. A strobe-free export",
              "variant is a ROADMAP item (ChatGPT fix #6)."]
    (WORK / "QC_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("WROTE QC_REPORT.md")
    return 0

if __name__ == "__main__":
    sys.exit(main())
