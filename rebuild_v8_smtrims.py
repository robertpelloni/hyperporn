#!/usr/bin/env python3
"""v8: stronger SM intro/outro removal.

Extra cuts (seconds, relative to intermediates/sissy_parts4/p_*.mp4) were set by
1s-resolution head/tail contact-sheet inspection (framecheck/trimcheck/):
branding/title cards and credit tails that survived the v4 luma detectors.
Wet-dream B-roll is untouched. Cuts are rounded outward to the 26-frame GOP
grid and applied by stream copy (no re-encode, no quality loss), then the
parts are re-concatenated into intermediates/sissy_all_gop26_v2.mp4.
"""
import subprocess, sys, math, json
from pathlib import Path

WORK = Path(__file__).resolve().parent
PARTS4 = WORK / "intermediates" / "sissy_parts4"
PARTS5 = WORK / "intermediates" / "sissy_parts5"
OUT = WORK / "intermediates" / "sissy_all_gop26_v2.mp4"
NAMES = ["bost","csd2","sm6","smx","sm1","scs","sm2","sm3","sm9","sm7","sm8","sm5p1","sm5p2","scds","sm4"]
# name: (extra_head_s, extra_tail_s) beyond the v4 trims already in parts4
EXTRA = {
    "bost": (1, 0), "csd2": (0, 1), "sm6": (9, 3), "smx": (8, 2), "sm1": (13, 0),
    "scs": (6, 0), "sm2": (17, 0), "sm3": (2, 0), "sm9": (3, 7), "sm7": (0, 0),
    "sm8": (8, 2), "sm5p1": (26, 0), "sm5p2": (0, 2), "scds": (0, 25), "sm4": (11, 0),
}
GOP = 26
FPS = 60

def probe_frames(p):
    r = subprocess.run(["ffprobe","-v","error","-select_streams","v:0",
                        "-show_entries","stream=nb_frames","-of","csv=p=0",str(p)],
                       capture_output=True, text=True, check=True)
    return int(r.stdout.strip())

def gop_ceil(sec):
    return int(math.ceil(sec * FPS / GOP)) * GOP

def main():
    PARTS5.mkdir(parents=True, exist_ok=True)
    report = []
    for i, name in enumerate(NAMES):
        src = PARTS4 / f"p_{i:02d}.mp4"
        dst = PARTS5 / f"p_{i:02d}.mp4"
        total = probe_frames(src)
        head_s, tail_s = EXTRA[name]
        start = gop_ceil(head_s)
        keep = (total - start - gop_ceil(tail_s)) // GOP * GOP
        if keep <= 0:
            print(f"FAIL {name}: keep={keep}", flush=True); return 1
        if dst.exists() and probe_frames(dst) == keep:
            print(f"skip {name} frames={keep}", flush=True)
        else:
            cmd = ["ffmpeg","-y","-hide_banner","-loglevel","error",
                   "-ss", f"{start/FPS:.6f}", "-i", str(src),
                   "-frames:v", str(keep), "-an", "-c:v", "copy",
                   "-avoid_negative_ts","make_zero", str(dst)]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0:
                print(f"FAIL {name}: {r.stderr[-300:]}", flush=True); return 1
            got = probe_frames(dst)
            if got != keep:
                print(f"FAIL {name}: got {got} want {keep}", flush=True); return 1
            print(f"ok {name}: {total} -> {keep} (head {start/FPS:.2f}s tail {(total-start-keep)/FPS:.2f}s)", flush=True)
        report.append({"name": name, "part": i, "src_frames": total,
                       "head_cut_s": start/FPS, "keep_frames": keep,
                       "tail_cut_s": (total-start-keep)/FPS})
    listf = PARTS5 / "list.txt"
    with listf.open("w", encoding="utf-8") as f:
        for i in range(len(NAMES)):
            f.write(f"file 'p_{i:02d}.mp4'\n")
    r = subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error",
                        "-f","concat","-safe","0","-i",str(listf),
                        "-c","copy",str(OUT)], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"concat FAIL {r.stderr[-300:]}", flush=True); return 1
    total_keep = sum(x["keep_frames"] for x in report)
    got = probe_frames(OUT)
    print(f"sissy_all_gop26_v2 frames={got} expected={total_keep} dur={got/FPS:.2f}s", flush=True)
    (WORK / "sm_trim_report_v8.json").write_text(json.dumps(report, indent=2))
    if got != total_keep:
        print("FRAME MISMATCH", flush=True); return 1
    print("DONE", flush=True)
    return 0

if __name__ == "__main__":
    sys.exit(main())
