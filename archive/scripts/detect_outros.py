import subprocess, json
from pathlib import Path

SISSY = Path(r"C:\Users\hyper\Videos\sissymaker")
W, H = 160, 90  # tiny proxy for stats only
PX = W * H

def probe_dur(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(p)],
        capture_output=True, text=True,
    )
    return float(r.stdout.strip())

def luma_stats(src, ss, n=1):
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{ss:.3f}", "-i", str(src),
           "-frames:v", str(n), "-vf", f"scale={W}:{H}",
           "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    r = subprocess.run(cmd, capture_output=True)
    data = r.stdout
    out = []
    got = len(data) // PX
    for i in range(got):
        ch = data[i * PX:(i + 1) * PX]
        mean = sum(ch) / PX
        var = sum((b - mean) ** 2 for b in ch) / PX
        out.append((mean, var ** 0.5))
    return out

TRIM = json.loads((SISSY / "intro_trims.json").read_text())
results = {}

for name in TRIM:
    src = SISSY / name
    if not src.exists():
        continue
    dur = probe_dur(src)
    # sample every 2s over the last 60s
    samples = []
    t = max(0, dur - 60)
    while t < dur - 0.2:
        st = luma_stats(src, t, 1)
        if st:
            samples.append((round(dur - t, 1), st[0][0], st[0][1]))
        t += 2.0
    # find outro start: sustained near-black or near-white flash or low-variance logo
    outro_start = None
    for back, mean, sd in samples:  # back = seconds before end
        # flash/near-white or black or flat logo
        if mean > 235 or mean < 12 or (sd < 6 and back < 40):
            if outro_start is None or back < outro_start:
                pass
    # simpler: walk from end backward while frames look like outro
    def is_outro(mean, sd):
        return mean > 235 or mean < 12 or sd < 5
    seq = list(reversed(samples))  # from end backward
    cut_back = 0
    for back, mean, sd in seq:
        if is_outro(mean, sd):
            cut_back = max(cut_back, back)
        else:
            # allow one content frame to end the streak if we already saw outro
            if cut_back > 0:
                break
    results[name] = {"dur": dur, "outro_tail": cut_back}
    print(f"{dur:7.1f}s outro_tail={cut_back:5.1f}s  {name[:52]}")
    for back, mean, sd in samples[-12:]:
        tag = "OUT" if is_outro(mean, sd) else "   "
        print(f"    -{back:5.1f}s mean={mean:6.1f} sd={sd:5.1f} {tag}")

(SISSY / "outro_trims.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
print("WROTE outro_trims.json")
