#!/usr/bin/env python3
"""Dedupe _sm by (1) duration grouping, (2) perceptual frame-sequence match.

Length is only a candidate filter: sas/bost2 share 317.1 s but are
different content. Verification: 64-bit aHash of a 160x90 gray frame
every 5 s, sequence-aligned with offsets -60..+60 s; a pair is the
same content if the best offset averages <8/64 differing bits over
>=10 compared frames. Losers (lower resolution, then smaller file)
move to _sm/_dup/ (never deleted). Writes dedupe_report.json.
"""
import json, subprocess, sys
from pathlib import Path

WORK = Path(__file__).resolve().parent
FFD = WORK / "tools" / "ffmpeg-7.1.1-essentials_build" / "bin"
NEW = ["sgas", "ley1", "ley2", "ley3", "ley4", "ley5", "drip1"]
OLD = ["bost", "csd2", "csd1", "scds", "scs", "sm1", "sm2", "sm3", "sm4",
       "sm5p1", "sm5p2", "sm6", "sm7", "sm8", "sm9", "smx",
       "wct", "bcwt", "sas", "bost2", "smb1", "smb3", "bcst", "uys", "cw"]

def probe(p):
    r = subprocess.run([str(FFD / "ffprobe.exe"), "-v", "error", "-show_entries",
                        "stream=width,height", "-show_entries", "format=duration",
                        "-of", "json", str(p)], capture_output=True, text=True)
    d = json.loads(r.stdout)
    v = d["streams"][0]
    return {"dur": float(d["format"]["duration"]), "w": v["width"], "h": v["height"],
            "mb": p.stat().st_size / 1e6}

def hashes(p, dur):
    # one 64-bit aHash (8x8) per 5 s, from 160x90 gray raw frames
    out = []
    r = subprocess.run([str(FFD / "ffmpeg.exe"), "-v", "error", "-i", str(p),
                        "-vf", "fps=1/5,scale=8:8,format=gray",
                        "-f", "rawvideo", "-"], capture_output=True)
    raw = r.stdout
    for i in range(0, len(raw) - 63, 64):
        ch = raw[i:i + 64]
        mean = sum(ch) / 64
        h = 0
        for j, b in enumerate(ch):
            if b > mean:
                h |= 1 << j
        out.append(h)
    return out

def best_match(a, b):
    best = (999.0, 0, 0)
    for off in range(-12, 13):
        diffs, n = 0, 0
        for i, ha in enumerate(a):
            j = i + off
            if 0 <= j < len(b):
                diffs += bin(ha ^ b[j]).count("1"); n += 1
        if n >= 10:
            avg = diffs / n
            if avg < best[0]:
                best = (avg, off, n)
    return best  # avg bits differing, offset (5 s units), compared frames

def main():
    files = {}
    for stem in OLD + NEW:
        p = WORK / "_sm" / f"{stem}.mp4"
        if p.exists():
            files[stem] = {**probe(p), "new": stem in NEW}
    for stem, info in files.items():
        info["hashes"] = hashes(WORK / "_sm" / f"{stem}.mp4", info["dur"])
        print(f"{stem}: dur={info['dur']:.1f} {info['w']}x{info['h']} "
              f"frames_hashed={len(info['hashes'])}", flush=True)
    # candidate pairs: new files vs everything, duration within 120 s
    # (same content can differ by intro length), verified by hash match
    parent = {s: s for s in files}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    pairs = []
    stems = list(files)
    for i, a in enumerate(stems):
        for b in stems[i + 1:]:
            if not (files[a]["new"] or files[b]["new"]):
                continue
            if abs(files[a]["dur"] - files[b]["dur"]) > 120:
                continue
            avg, off, n = best_match(files[a]["hashes"], files[b]["hashes"])
            same = avg < 8
            pairs.append({"a": a, "b": b, "avg_bit_diff": round(avg, 2),
                          "offset_s": off * 5, "compared": n, "same_content": same})
            print(f"{a} vs {b}: avgdiff={avg:.2f} off={off*5}s n={n} "
                  f"{'SAME' if same else 'different'}", flush=True)
            if same:
                parent[find(a)] = find(b)
    groups = {}
    for s in files:
        groups.setdefault(find(s), []).append(s)
    dup_dir = WORK / "_sm" / "_dup"
    moved = []
    for root, members in groups.items():
        if len(members) < 2:
            continue
        # keep highest resolution (w*h), then largest file
        keep = max(members, key=lambda s: (files[s]["w"] * files[s]["h"], files[s]["mb"]))
        for s in members:
            if s != keep:
                dup_dir.mkdir(exist_ok=True)
                src = WORK / "_sm" / f"{s}.mp4"
                src.rename(dup_dir / f"{s}.mp4")
                moved.append({"moved": s, "kept": keep, "reason": "same content, lower/equal quality"})
                print(f"MOVE {s} -> _dup/ (kept {keep})", flush=True)
    report = {"pairs": pairs, "moved_to_dup": moved,
              "kept_pool": sorted(s for s in files
                                  if not any(m["moved"] == s for m in moved))}
    (WORK / "dedupe_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"WROTE dedupe_report.json moved={len(moved)} kept={len(report['kept_pool'])}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
