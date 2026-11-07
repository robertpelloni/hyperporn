#!/usr/bin/env python3
"""v8 full rebuild: re-cut 26f clips from sissy_all_gop26_v2 (SM intros/outros
removed) + wet_gop26 (untouched), re-apply the 26f triangular strobe fade,
in 6 disk-bounded chunks. Resumable: finished chunks are skipped.
Output: liveset60_v8/video_fade_v8.mp4 (646461 frames, 10774.35s, no audio).
"""
import subprocess, sys, time, os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

WORK = Path(__file__).resolve().parent
SISSY = WORK / "intermediates" / "sissy_all_gop26_v2.mp4"
WET = WORK / "intermediates" / "wet_gop26.mp4"
MASK = WORK / "mask_p26_fixed.mp4"
OUTDIR = WORK / "liveset60_v8"
CLIPS = OUTDIR / "clips_tmp"
N_CLIPS, CLIP_F, FPS = 24864, 26, 60
CHUNK = 4144  # clips per chunk; 6 chunks; chunk frames divisible by 26 (mask phase)

def log(m): print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)

def nframes(p):
    r = subprocess.run(["ffprobe","-v","error","-select_streams","v:0",
                        "-show_entries","stream=nb_frames","-of","csv=p=0",str(p)],
                       capture_output=True, text=True)
    try: return int((r.stdout or "").strip())
    except ValueError: return -1

def cut_one(args):
    i, s_frames, w_frames = args
    out = CLIPS / f"clip_{i:06d}.mp4"
    if out.exists() and nframes(out) == CLIP_F: return 0
    if out.exists(): out.unlink()
    src, total = (SISSY, s_frames) if i % 2 == 0 else (WET, w_frames)
    start_f = ((i // 2) * CLIP_F) % total
    cmd = ["ffmpeg","-y","-hide_banner","-loglevel","error",
           "-ss", f"{start_f/FPS:.6f}", "-i", str(src),
           "-frames:v", str(CLIP_F), "-an", "-c:v", "copy",
           "-avoid_negative_ts","make_zero", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0 and nframes(out) == CLIP_F: return 0
    if out.exists(): out.unlink()
    cmd = ["ffmpeg","-y","-hide_banner","-loglevel","error",
           "-ss", f"{start_f/FPS:.6f}", "-i", str(src), "-an",
           "-vf","fps=60,tpad=stop_mode=clone:stop_duration=1,format=yuv420p",
           "-frames:v", str(CLIP_F), "-c:v","libx264","-preset","ultrafast","-crf","25", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return 0 if (r.returncode == 0 and nframes(out) == CLIP_F) else 1

def main():
    OUTDIR.mkdir(exist_ok=True); CLIPS.mkdir(exist_ok=True)
    s_frames, w_frames = nframes(SISSY), nframes(WET)
    log(f"sissy={s_frames} wet={w_frames} mask={MASK.exists()}")
    chunks = []
    for ci in range(0, N_CLIPS, CHUNK):
        hi = min(ci + CHUNK, N_CLIPS); n = hi - ci
        fade_out = OUTDIR / f"fade_chunk_{ci//CHUNK:02d}.mp4"
        chunks.append(fade_out)
        if fade_out.exists() and nframes(fade_out) == n * CLIP_F:
            log(f"chunk {ci//CHUNK} exists, skip"); continue
        log(f"chunk {ci//CHUNK}: cutting clips {ci}..{hi-1}")
        with ThreadPoolExecutor(max_workers=8) as ex:
            fails = sum(ex.map(cut_one, [(i, s_frames, w_frames) for i in range(ci, hi)]))
        log(f"chunk {ci//CHUNK}: cut done fails={fails}")
        if fails: log("CUT FAILS - abort"); return 1
        listf = OUTDIR / "chunk_list.txt"
        with listf.open("w") as f:
            for i in range(ci, hi): f.write(f"file 'clips_tmp/clip_{i:06d}.mp4'\n")
        copy_out = OUTDIR / "chunk_copy.mp4"
        r = subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error",
                            "-f","concat","-safe","0","-i",str(listf),"-c","copy",str(copy_out)],
                           capture_output=True, text=True)
        if r.returncode != 0 or nframes(copy_out) != n * CLIP_F:
            log(f"concat FAIL rc={r.returncode} frames={nframes(copy_out)}"); return 1
        fc = "[1:v]setpts=N/FRAME_RATE/TB,format=gbrp[m];[0:v]format=gbrp[a];[a][m]blend=all_mode=multiply:shortest=1,format=yuv420p[v]"
        log(f"chunk {ci//CHUNK}: fade encode start")
        r = subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error",
                            "-i",str(copy_out),"-stream_loop","-1","-i",str(MASK),
                            "-filter_complex",fc,"-map","[v]","-an",
                            "-c:v","libx264","-preset","ultrafast","-crf","23",
                            "-t", f"{n*CLIP_F/FPS:.6f}", str(fade_out)],
                           capture_output=True, text=True)
        got = nframes(fade_out) if fade_out.exists() else -1
        log(f"chunk {ci//CHUNK}: fade rc={r.returncode} frames={got}")
        if r.returncode != 0 or got != n * CLIP_F: return 1
        copy_out.unlink()
        for i in range(ci, hi): (CLIPS / f"clip_{i:06d}.mp4").unlink(missing_ok=True)
    listf = OUTDIR / "fade_list.txt"
    with listf.open("w") as f:
        for c in chunks: f.write(f"file '{c.name}'\n")
    final = OUTDIR / "video_fade_v8.mp4"
    r = subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error",
                        "-f","concat","-safe","0","-i",str(listf),"-c","copy",str(final)],
                       capture_output=True, text=True)
    got = nframes(final) if final.exists() else -1
    log(f"FINAL video_fade_v8 frames={got} expected={N_CLIPS*CLIP_F} rc={r.returncode}")
    if got != N_CLIPS * CLIP_F: return 1
    for c in chunks: c.unlink()
    log("DONE")
    return 0

if __name__ == "__main__":
    sys.exit(main())
