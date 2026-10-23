import subprocess, os, json
from pathlib import Path

SISSY = Path(r"C:\Users\hyper\Videos\sissymaker")

def probe(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration:stream=codec_type,width,height,r_frame_rate",
         "-of", "json", str(p)],
        capture_output=True, text=True, timeout=60,
    )
    d = json.loads(r.stdout)
    dur = float(d["format"]["duration"])
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    return {
        "dur": dur,
        "w": v.get("width"),
        "h": v.get("height"),
        "fps": v.get("r_frame_rate"),
    }

sources = []
for f in sorted(SISSY.glob("*.mp4")):
    if f.name.startswith(("Ajja_", "mask_", "fade_")):
        continue
    if f.stat().st_size < 20_000_000:
        continue
    try:
        info = probe(f)
    except Exception as e:
        print(f"ERR {f.name}: {e}")
        continue
    sources.append((f, info))
    print(f"{info['dur']:8.1f}s  {info['w']}x{info['h']} @{info['fps']}  {f.name}")

print(f"\nTOTAL files={len(sources)}  sum_dur={sum(i['dur'] for _, i in sources):.1f}s")
