#!/usr/bin/env python3
"""Resume strobe clips then concat + mux AJJA audio."""
import subprocess, sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

SISSY_DIR = Path(r"C:\Users\hyper\Videos\sissymaker")
MUSIC = Path(r"C:\Users\hyper\Music")
out_dir = SISSY_DIR / "clips_strobe140"
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
    print("probing sources...", flush=True)
    sissy_dur = [(p, probe(p)) for p in SISSY]
    wet_dur = probe(WET)
    audio_dur = probe(AUDIO)
    sissy_total = sum(d for _, d in sissy_dur)
    n_clips = max(int(audio_dur // CLIP_DUR), 2)
    print(f"n_clips={n_clips} audio={audio_dur:.2f}s clip={CLIP_DUR:.6f}s", flush=True)

    out_dir.mkdir(parents=True, exist_ok=True)
    jobs = []
    for i in range(n_clips):
        out = out_dir / f"clip_{i:05d}.mp4"
        if out.exists() and out.stat().st_size > 1000:
            continue
        if i % 2 == 0:
            src, start = sissy_at(sissy_dur, sissy_total, (i // 2) * CLIP_DUR)
        else:
            start = ((i // 2) * CLIP_DUR) % wet_dur
            src = WET
        jobs.append((i, src, start, out))
    print(f"missing clips: {len(jobs)}", flush=True)

    def render(job):
        i, src, start, out = job
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-ss", f"{start:.6f}", "-i", str(src),
            "-t", f"{CLIP_DUR:.6f}", "-an",
            "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},format=yuv420p",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
            "-g", str(FPS * 2), str(out),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        return i, r.returncode, (r.stderr or "")[-200:]

    if jobs:
        done = 0
        fails = 0
        with ThreadPoolExecutor(max_workers=8) as ex:
            futs = [ex.submit(render, j) for j in jobs]
            for fut in as_completed(futs):
                i, rc, err = fut.result()
                done += 1
                if rc != 0:
                    fails += 1
                    print(f"FAIL {i}: {err}", flush=True)
                if done % 40 == 0 or done == len(jobs):
                    print(f"rendered {done}/{len(jobs)} fails={fails}", flush=True)
        if fails > 10:
            print("too many failures", flush=True)
            sys.exit(1)

    # verify all clips exist
    missing = [i for i in range(n_clips) if not (out_dir / f"clip_{i:05d}.mp4").exists() or (out_dir / f"clip_{i:05d}.mp4").stat().st_size <= 1000]
    if missing:
        print("still missing", missing[:20], "count", len(missing), flush=True)
        sys.exit(1)

    listf = out_dir / "list.txt"
    with listf.open("w", encoding="utf-8") as f:
        for i in range(n_clips):
            f.write(f"file 'clip_{i:05d}.mp4'\n")
    concat_mp4 = out_dir / "video_only.mp4"
    print("concat...", flush=True)
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(listf), "-c", "copy", str(concat_mp4)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print("concat copy failed, re-encode:", r.stderr[-300:], flush=True)
        r = subprocess.run(
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-f", "concat", "-safe", "0", "-i", str(listf),
             "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23", str(concat_mp4)],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            print(r.stderr, flush=True)
            sys.exit(1)

    vid_len = n_clips * CLIP_DUR
    print("mux audio...", flush=True)
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(concat_mp4), "-i", str(AUDIO),
         "-map", "0:v:0", "-map", "1:a:0",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-t", f"{vid_len:.6f}", "-movflags", "+faststart", str(FINAL)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(r.stderr, flush=True)
        sys.exit(1)
    print(f"DONE {FINAL} size={FINAL.stat().st_size/1e6:.1f}MB dur={vid_len:.2f}s clips={n_clips}", flush=True)

if __name__ == "__main__":
    main()
