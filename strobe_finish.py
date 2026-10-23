#!/usr/bin/env python3
"""Finish missing strobe clips then concat + mux."""
import subprocess, sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

SISSY_DIR = Path(r"C:\Users\hyper\Videos\sissymaker")
MUSIC = Path(r"C:\Users\hyper\Music")
out_dir = SISSY_DIR / "clips_strobe140_fixed"
FINAL = SISSY_DIR / "Ajja_Bazinga_Sissymaker_WetDream_STROBE140.mp4"
AUDIO = MUSIC / "Ajja - Bazinga (2023 Revamp).mp3"
WET = SISSY_DIR / "JPVT1109 - Wet Dreams AI Goon Therapy (parts 1-15).mp4"
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
CLIP_DUR = 60.0 / 140.0
FRAMES = 13
W, H, FPS = 1280, 720, 30

def probe(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout.strip())

def sissy_at(sissy_dur, sissy_total, t):
    t = t % sissy_total
    acc = 0.0
    for p, d in sissy_dur:
        if t < acc + d:
            return p, t - acc
        acc += d
    p, d = sissy_dur[-1]
    return p, 0.0

def main():
    sissy_dur = [(p, probe(p)) for p in SISSY]
    wet_dur = probe(WET)
    audio_dur = probe(AUDIO)
    sissy_total = sum(d for _, d in sissy_dur)
    n_clips = int(audio_dur / (FRAMES / FPS)) + 2
    print("n_clips", n_clips, flush=True)

    jobs = []
    for i in range(n_clips):
        out = out_dir / f"clip_{i:05d}.mp4"
        if out.exists() and out.stat().st_size > 2000:
            continue
        if i % 2 == 0:
            src, start = sissy_at(sissy_dur, sissy_total, (i // 2) * CLIP_DUR)
        else:
            start = ((i // 2) * CLIP_DUR) % wet_dur
            src = WET
        jobs.append((i, src, start, out))
    print("missing", len(jobs), [j[0] for j in jobs], flush=True)

    def render(job):
        i, src, start, out = job
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-ss", f"{start:.6f}", "-i", str(src), "-an",
            "-vf", (
                f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
                f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},format=yuv420p,"
                f"tpad=stop_mode=clone:stop_duration=1"
            ),
            "-frames:v", str(FRAMES),
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
            "-g", str(FRAMES), str(out),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            cmd = [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:d={FRAMES/FPS}:r={FPS}",
                "-frames:v", str(FRAMES),
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23", str(out),
            ]
            r = subprocess.run(cmd, capture_output=True, text=True)
        return i, r.returncode, (r.stderr or "")[-150:]

    if jobs:
        with ThreadPoolExecutor(max_workers=4) as ex:
            for fut in as_completed([ex.submit(render, j) for j in jobs]):
                i, rc, err = fut.result()
                print(("ok" if rc == 0 else "FAIL"), i, err if rc else "", flush=True)

    listf = out_dir / "list.txt"
    with listf.open("w", encoding="utf-8") as f:
        for i in range(n_clips):
            f.write("file 'clip_%05d.mp4'\n" % i)
    print("list written", n_clips, flush=True)

    concat_mp4 = out_dir / "video_only.mp4"
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(listf),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
         "-r", str(FPS), "-pix_fmt", "yuv420p", str(concat_mp4)],
        capture_output=True, text=True,
    )
    print("concat rc", r.returncode, (r.stderr or "")[-300:], flush=True)
    if r.returncode != 0:
        sys.exit(1)

    vid_len = n_clips * (FRAMES / FPS)
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(concat_mp4), "-i", str(AUDIO),
         "-map", "0:v:0", "-map", "1:a:0",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-t", "%.6f" % min(vid_len, audio_dur),
         "-movflags", "+faststart", str(FINAL)],
        capture_output=True, text=True,
    )
    print("mux rc", r.returncode, (r.stderr or "")[-300:], flush=True)
    if r.returncode == 0:
        print("DONE", FINAL, FINAL.stat().st_size / 1e6, "MB", flush=True)

if __name__ == "__main__":
    main()
