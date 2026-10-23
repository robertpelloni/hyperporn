#!/usr/bin/env python3
"""Beat-synced mashup: sissymaker 1-9 alternating with wet dream compilation.
Clip length = one beat at 14 BPM (60/14 s). Audio = AJJA track only."""
import os, subprocess, sys, math
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

SISSY_DIR = Path(r"C:\Users\hyper\Videos\sissymaker")
MUSIC = Path(r"C:\Users\hyper\Music")
OUT_DIR = Path(r"C:\Users\hyper\Videos\sissymaker\beat_mashup_clips")
FINAL = Path(r"C:\Users\hyper\Videos\sissymaker\Ajja_Bazinga_Sissymaker_WetDream_14bpm.mp4")

# sissymaker 1-9 (Emperor Hypnos numbered series)
SISSY = [
    SISSY_DIR / "Sissy Maker 1 by Emperor Hypnos (1).mp4",
    SISSY_DIR / "Emperor Hypnos Sissymaker II (1).mp4",
    SISSY_DIR / "EmperorHypnos - Sissy Maker III [720p].mp4",
    SISSY_DIR / "Sissy Maker IV by Emperor Hypnos (1).mp4",
    SISSY_DIR / "Sissymaker 5 - EmperorHypnos.mp4",
    SISSY_DIR / "Sissy Maker 6 by Emperor Hypnos (1).mp4",
    SISSY_DIR / "Sissymaker 7 BBC edition.mp4",
    SISSY_DIR / "Sissymaker 8 - Rapture PMV (1).mp4",
    SISSY_DIR / "SissyMaker 9 - Breed Black PMV (1).mp4",
]
WET = SISSY_DIR / "JPVT1109 - Wet Dreams AI Goon Therapy (parts 1-15).mp4"
AUDIO = MUSIC / "Ajja - Bazinga (2023 Revamp).mp3"

BPM = 14.0
CLIP_DUR = 60.0 / BPM  # 4.285714...
W, H, FPS = 1280, 720, 30
CRF, PRESET = "23", "ultrafast"

def probe(p: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout.strip())

def main():
    for p in SISSY + [WET, AUDIO]:
        if not p.exists():
            print("MISSING:", p); sys.exit(1)

    sissy_dur = [(p, probe(p)) for p in SISSY]
    wet_dur = probe(WET)
    audio_dur = probe(AUDIO)
    print(f"audio={audio_dur:.2f}s  wet={wet_dur:.2f}s  sissy_total={sum(d for _,d in sissy_dur):.2f}s")
    print(f"clip_dur={CLIP_DUR:.6f}s ({BPM} BPM)")

    n_clips = int(audio_dur // CLIP_DUR)
    # leave a little headroom so video >= audio
    n_clips = max(n_clips, 2)
    print(f"n_clips={n_clips}  video_dur={n_clips*CLIP_DUR:.2f}s")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # clean old clips
    for f in OUT_DIR.glob("clip_*.mp4"):
        f.unlink()

    # sequential cursor helpers (wrap around)
    sissy_total = sum(d for _, d in sissy_dur)
    jobs = []  # (idx, source, start, path)

    def sissy_at(t: float):
        t = t % sissy_total
        acc = 0.0
        for p, d in sissy_dur:
            if t < acc + d:
                return p, t - acc
            acc += d
        p, d = sissy_dur[-1]
        return p, 0.0

    for i in range(n_clips):
        if i % 2 == 0:
            # sissymaker sequential
            t = (i // 2) * CLIP_DUR
            src, start = sissy_at(t)
        else:
            t = ((i // 2) + 0.5) * CLIP_DUR
            # wet dream sequential (independent cursor so both sources progress)
            start = (((i // 2)) * CLIP_DUR) % wet_dur
            src = WET
        out = OUT_DIR / f"clip_{i:04d}.mp4"
        jobs.append((i, src, start, out))

    def render(job):
        i, src, start, out = job
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-ss", f"{start:.6f}",
            "-i", str(src),
            "-t", f"{CLIP_DUR:.6f}",
            "-an",
            "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},format=yuv420p",
            "-c:v", "libx264", "-preset", PRESET, "-crf", CRF,
            "-g", str(FPS * 2),
            str(out),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        return i, r.returncode, r.stderr[-400:] if r.stderr else ""

    print(f"rendering {len(jobs)} clips with 6 workers...")
    done = 0
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = [ex.submit(render, j) for j in jobs]
        for fut in as_completed(futs):
            i, rc, err = fut.result()
            done += 1
            if rc != 0:
                print(f"FAIL clip {i}: {err}")
                sys.exit(1)
            if done % 10 == 0 or done == len(jobs):
                print(f"  rendered {done}/{len(jobs)}")

    # concat
    listf = OUT_DIR / "list.txt"
    with listf.open("w", encoding="utf-8") as f:
        for i in range(n_clips):
            f.write(f"file 'clip_{i:04d}.mp4'\n")

    concat_mp4 = OUT_DIR / "video_only.mp4"
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(listf),
        "-c", "copy",
        str(concat_mp4),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("concat failed, re-encoding:", r.stderr[-500:])
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", str(listf),
            "-c:v", "libx264", "-preset", PRESET, "-crf", CRF,
            str(concat_mp4),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stderr); sys.exit(1)

    # mux AJJA audio (trim/pad to video length)
    vid_len = n_clips * CLIP_DUR
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(concat_mp4),
        "-i", str(AUDIO),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-t", f"{vid_len:.6f}",
        "-movflags", "+faststart",
        str(FINAL),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr); sys.exit(1)

    print("DONE:", FINAL)
    print(f"size={FINAL.stat().st_size/1e6:.1f} MB  dur={vid_len:.2f}s  clips={n_clips}")

if __name__ == "__main__":
    main()
