#!/usr/bin/env python3
"""Numeric intro/outro detection for csd1 + ext01..ext15 (no frame viewing).

Same luma method as detect_intros.py/detect_outros.py (160x90 gray proxy):
- intro end: first t (0..45 s, 1 s steps) where 3 consecutive samples
  have mean>55 (content-like), else 0.
- outro tail: walk from end (2 s steps over last 90 s) while
  mean>235 or mean<12 or sd<5, tolerating one content frame, else 0.
Conservative: caps head at 45 s and tail at 90 s. Writes trims_v2.json.
Logos on these sources live in the intro/outro cards, so trimming
these regions is the logo removal (no in-content watermark was ever
observed in the cataloged sources).
"""
import json, subprocess, sys
from pathlib import Path

WORK = Path(__file__).resolve().parent
FFD = WORK / "tools" / "ffmpeg-7.1.1-essentials_build" / "bin"
W, H, PX = 160, 90, 160 * 90
NEW_SM = ["csd1", "wct", "bcwt", "sas", "smb1", "bost2", "smb3",
          "bcst", "uys", "cw", "sgas", "ley1", "ley2", "ley3", "ley4",
          "ley5", "drip1"]  # scs2/scds2v deduped to _sm/_dup/
FILES = ([WORK / "_sm" / f"{s}.mp4" for s in NEW_SM] +
         [WORK / "_ai" / f"ext{i:02d}.mp4" for i in range(1, 16)])

def dur(p):
    r = subprocess.run([str(FFD / "ffprobe.exe"), "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def luma(p, ss):
    r = subprocess.run([str(FFD / "ffmpeg.exe"), "-v", "error", "-ss", f"{ss:.2f}",
                        "-i", str(p), "-frames:v", "1", "-vf", f"scale={W}:{H}",
                        "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                       capture_output=True)
    if len(r.stdout) < PX:
        return None
    ch = r.stdout[:PX]
    mean = sum(ch) / PX
    var = sum((b - mean) ** 2 for b in ch) / PX
    return mean, var ** 0.5

def main():
    out = {}
    prev = WORK / "trims_v2.json"
    if prev.exists():  # merge: keep already-detected entries, skip them
        out = json.loads(prev.read_text(encoding="utf-8"))
    for p in FILES:
        if p.name in out:
            print(f"{p.name}: cached, skip"); continue
        d = dur(p)
        head_samples = []
        for t in range(0, 46):
            s = luma(p, t)
            head_samples.append((t, s[0] if s else None))
        head = 0
        for i in range(len(head_samples) - 2):
            if all((head_samples[i + k][1] or 0) > 55 for k in range(3)):
                head = head_samples[i][0]; break
        tail_samples = []
        t = max(0.0, d - 90)
        while t < d - 0.2:
            s = luma(p, t)
            if s:
                tail_samples.append((round(d - t, 1), s[0], s[1]))
            t += 2.0
        def is_outro(m, sd): return m > 235 or m < 12 or sd < 5
        cut = 0
        for back, m, sd in reversed(tail_samples):
            if is_outro(m, sd):
                cut = max(cut, back)
            elif cut > 0:
                break
        out[p.name] = {"dur": round(d, 3), "head_trim_s": head, "tail_trim_s": cut}
        print(f"{p.name}: dur={d:.1f} head={head}s tail={cut}s", flush=True)
    (WORK / "trims_v2.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("WROTE trims_v2.json")
    return 0

if __name__ == "__main__":
    sys.exit(main())
