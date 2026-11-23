#!/usr/bin/env python3
"""Catalog the 2026-11-19/20 added videos, then rename to short neutral names.

Mapping is written BEFORE any rename (NEW_VIDEOS.md + new_videos.json),
so the original titles are never lost. Rename is idempotent: if an
extNN.mp4 already exists and the original is gone, that entry is skipped.
"""
import hashlib, json, subprocess, sys
from pathlib import Path

WORK = Path(__file__).resolve().parent
PROBE = WORK / "tools" / "ffmpeg-7.1.1-essentials_build" / "bin" / "ffprobe.exe"

# Deterministic order: alphabetical by original name (JPVT part 1 < part 2).
ORIGINALS = [
    "777REMIX - AI LOVES ANAL - Another Anal Gooning PMV.mp4",
    "Dom8natriX - AI GOONING MIX COMPILATION BIG ASS BIG TITS by Dom8natriX.mp4",
    "Dom8natriX - AI GOONING MIX COMPILATION BIG ASS BIG TITS by Dom8natriX(1).mp4",
    "Dom8natriX - AI GOONING MIX COMPILATION BIG ASS BIG TITS by Dom8natriX(2).mp4",
    "JPVT1109 - OurDream AI Generated Splitscreen PMV (part 1).mp4",
    "JPVT1109 - OurDream AI-Generated PMV (part 2).mp4",
    "Piqazzo - AI Gooning Cum Countdown.mp4",
    "Piqazzo - AI Gooning to the MAX Encouragement Hetero, Trans, Gangbang.mp4",
    "Piqazzo - Drain your Balls - Edge Therapy.mp4",
    "YourVideosCouldLookBetter - Ai Gen PMV 4k60 Ai Upscale.mp4",
    "famousALYX - mommys cum countdown.mp4",
    "fhtagn_322 - Crazy - monicafetishista partial remix 4k60fps +ai enhanced.mp4",
    "monicafetishista - Prayer (Enhanced) - All Anal AI PMV.mp4",
    "monicafetishista - Prayer for Gooning - Anal Only AI MegaMix.mp4",
    "monicafetishista - Satisfaction Extended 1 Hour Gigamix.mp4",
]

def probe(p):
    r = subprocess.run([str(PROBE), "-v", "error", "-show_entries",
                        "stream=codec_type,codec_name,width,height,avg_frame_rate",
                        "-show_entries", "format=duration,size,bit_rate",
                        "-of", "json", str(p)], capture_output=True, text=True)
    d = json.loads(r.stdout)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    a = next((s for s in d["streams"] if s["codec_type"] == "audio"), {})
    return {"duration_s": round(float(d["format"]["duration"]), 3),
            "width": v.get("width"), "height": v.get("height"),
            "fps": v.get("avg_frame_rate"), "vcodec": v.get("codec_name"),
            "acodec": a.get("codec_name"), "size_bytes": p.stat().st_size}

def sha256(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        while b := f.read(8 * 1024 * 1024):
            h.update(b)
    return h.hexdigest()

def main():
    entries = []
    for i, name in enumerate(ORIGINALS, 1):
        new = f"ext{i:02d}.mp4"
        src, dst = WORK / name, WORK / new
        if dst.exists() and not src.exists():
            entries.append({"new_name": new, "original_name": name, "status": "already-renamed"})
            continue
        if not src.exists():
            print(f"MISSING {name}"); return 1
        info = probe(src)
        entries.append({"new_name": new, "original_name": name,
                        "sha256": sha256(src), **info, "status": "cataloged"})
        print(new, info)
    (WORK / "new_videos.json").write_text(json.dumps(entries, indent=2), encoding="utf-8")
    total = sum(e.get("duration_s", 0) for e in entries)
    lines = ["# New videos added 2026-11-19/20 — catalog & rename map", "",
             "Saved before renaming. Original titles are preserved here only;",
             "on disk the files now use the short neutral names in the first column.",
             "These are finished PMVs (not raw studio sources), so — like",
             "`wet_gop26.mp4` before them — they are used whole: no intro/outro",
             "trim. Prior processes applied in `build_v9_extend.py`: normalize to",
             "1280x720 / 60 fps / GOP 26, 26-frame triangular strobe mask",
             "(`mask_p26_fixed.mp4`, RGB multiply), own audio kept (AAC 48 kHz),",
             "then concat after the v8 master.", "",
             "| New name | Original name | Duration (s) | Size (MB) | Video | Audio | SHA-256 (first 16) |",
             "|---|---|---:|---:|---|---|---|"]
    for e in entries:
        if "duration_s" in e:
            lines.append(f"| `{e['new_name']}` | {e['original_name']} | {e['duration_s']:.1f} | "
                         f"{e['size_bytes']/1e6:.0f} | {e['vcodec']} {e['width']}x{e['height']} @{e['fps']} | "
                         f"{e['acodec']} | `{e['sha256'][:16]}` |")
    lines += ["", f"Total new duration: **{total:.1f} s** ({total/3600:.2f} h). "
              f"v8 master is 10774.4 s, so the extended cut is ~{10774.4+total:.0f} s "
              f"({(10774.4+total)/3600:.2f} h).", "",
              "Note: the three Dom8natriX files have identical duration/resolution "
              "but different SHA-256 hashes (re-encodes/variants), so all three are kept."]
    (WORK / "NEW_VIDEOS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if "--rename" in sys.argv:
        for e in entries:
            src, dst = WORK / e["original_name"], WORK / e["new_name"]
            if src.exists():
                src.rename(dst); print(f"renamed -> {dst.name}")
    print(f"total={total:.1f}s entries={len(entries)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
