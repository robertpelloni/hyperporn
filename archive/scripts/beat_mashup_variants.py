#!/usr/bin/env python3
"""Variant mashups: strobe (140 BPM) and 14-beat clips."""
import os, subprocess, sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

SISSY_DIR = Path(r"C:\Users\hyper\Videos\sissymaker")
MUSIC = Path(r"C:\Users\hyper\Music")
OUT_ROOT = Path(r"C:\Users\hyper\Videos\sissymaker")

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

W, H, FPS = 1280, 720, 30
PSY_BPM = 140.0

def probe(p: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout.strip())

def build(clip_dur: float, tag: str, out_name: str, workers: int = 8):
    out_dir = OUT_ROOT / f"clips_{tag}"
    final = OUT_ROOT / out_name
    print(f"\n=== {tag}: clip_dur={clip_dur:.6f}s ===")

    sissy_dur = [(p, probe(p)) for p in SISSY]
    wet_dur = probe(WET)
    audio_dur = probe(AUDIO)
    sissy_total = sum(d for _, d in sissy_dur)

    n_clips = max(int(audio_dur // clip_dur), 2)
    print(f"n_clips={n_clips}  video_dur={n_clips*clip_dur:.2f}s  audio={audio_dur:.2f}s")

    out_dir.mkdir(parents=True, exist_ok=True)
    for f in out_dir.glob("clip_*.mp4"):
        f.unlink()

    def sissy_at(t: float):
        t = t % sissy_total
        acc = 0.0
        for p, d in sissy_dur:
            if t < acc + d:
                return p, t - acc
            acc += d
        p, d = sissy_dur[-1]
        return p, 0.0

    jobs = []
    for i in range(n_clips):
        if i % 2 == 0:
            src, start = sissy_at((i // 2) * clip_dur)
        else:
            start = ((i // 2) * clip_dur) % wet_dur
            src = WET
        out = out_dir / f"clip_{i:05d}.mp4"
        jobs.append((i, src, start, out))

    def render(job):
        i, src, start, out = job
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-ss", f"{start:.6f}",
            "-i", str(src),
            "-t", f"{clip_dur:.6f}",
            "-an",
            "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},format=yuv420p",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
            "-g", str(FPS * 2),
            str(out),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        return i, r.returncode, r.stderr[-300:] if r.stderr else ""

    print(f"rendering {len(jobs)} clips with {workers} workers...")
    done = 0
    fail = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(render, j) for j in jobs]
        for fut in as_completed(futs):
            i, rc, err = fut.result()
            done += 1
            if rc != 0:
                fail += 1
                print(f"FAIL clip {i}: {err}")
                if fail > 5:
                    print("too many failures, abort"); sys.exit(1)
            if done % 50 == 0 or done == len(jobs):
                print(f"  {done}/{len(jobs)}")

    listf = out_dir / "list.txt"
    with listf.open("w", encoding="utf-8") as f:
        for i in range(n_clips):
            f.write(f"file 'clip_{i:05d}.mp4'\n")

    concat_mp4 = out_dir / "video_only.mp4"
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(listf),
        "-c", "copy", str(concat_mp4),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("concat copy failed, re-encoding...")
        cmd[cmd.index("copy")] = "libx264"
        # rebuild properly
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", str(listf),
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
            str(concat_mp4),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stderr); sys.exit(1)

    vid_len = n_clips * clip_dur
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(concat_mp4),
        "-i", str(AUDIO),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-t", f"{vid_len:.6f}",
        "-movflags", "+faststart",
        str(final),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr); sys.exit(1)

    print(f"DONE {final.name}: {final.stat().st_size/1e6:.1f} MB  dur={vid_len:.2f}s  clips={n_clips}")
    return final

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    if which in ("strobe", "both"):
        build(clip_dur=60.0 / PSY_BPM, tag="strobe140",
              out_name="Ajja_Bazinga_Sissymaker_WetDream_STROBE140.mp4",
              workers=10)
    if which in ("14beat", "both"):
        build(clip_dur=14.0 * (60.0 / PSY_BPM), tag="beat14",
              out_name="Ajja_Bazinga_Sissymaker_WetDream_14BEATS.mp4",
              workers=6)
