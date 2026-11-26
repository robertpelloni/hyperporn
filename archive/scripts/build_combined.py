#!/usr/bin/env python3
"""
build_combined.py — One combined mix (Space Tribe/Mad Tribe + Jumpstreet + Ajja,
all in a single timeline) on the reused strobe video, sliced into 10-minute chunks.

Stages:
    python build_combined.py combined   # build combined audio bed + mux -> 3h mp4
    python build_combined.py chunks     # slice the combined mp4 into 10-min chunks
    python build_combined.py all        # combined + chunks

No hypnoshit. Video stream copied from the existing deliverable.
"""
import os, subprocess, sys, math

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

WORK = os.path.dirname(os.path.abspath(__file__))
os.chdir(WORK)
BEDS = os.path.join(WORK, "beds")
os.makedirs(BEDS, exist_ok=True)

VIDEO_SRC = "ハイパーポルノ.mp4"           # reuse the finished strobe video
OUT_MIX = "ハイーポルノ_combined.mp4"
CHUNK_DIR = "chunks"
CHUNK_PREFIX = "hyperporn_combined_c"     # ASCII names for upload-tool safety
CHUNK_SEC = 600

AJJA = "Ajja - 2026 - Dimension Festival NZ (live).mp3"
JS_A = os.path.expanduser("~/Music/Jumpstreet - 2025 - Sunlight Festival (live).mp3")
JS_B = os.path.expanduser("~/Music/Jumpstreet - 2026 - Dimension Festival DJ Set (live).mp3")
JS_EACH = 1800   # 30 min from each of two Jumpstreet livesets (plural)

ST_SINGLES = [
    "Mad Tribe - 2017 - Drop the Bomb.mp3",
    "Mad Tribe - 2017 - They Came from Uranus.mp3",
    "Space Tribe & Dickster - 2017 - Alien's Fiend.mp3",
    "Mad Tribe - 2017 - Out of This World.mp3",
    "Space Tribe & Laughing Buddha - 2017 - Atom Bombs.mp3",
    "Mad Tribe - 2017 - Alien's Slave.mp3",
    "Stryker & Space Tribe - 2017 - S, D and Rock 'n Roll.mp3",
]


def sh(p):
    return os.path.expanduser(p)


def dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", sh(path)],
                         capture_output=True, text=True).stdout.strip()
    return float(out)


def rg(path):
    out = subprocess.run(["ffprobe", "-v", "error",
                          "-show_entries", "format_tags=replaygain_track_gain",
                          "-of", "default=nw=1:nk=1", sh(path)],
                         capture_output=True, text=True).stdout.strip()
    if not out:
        return 0.0
    try:
        return float(out.replace("dB", "").split()[0])
    except ValueError:
        return 0.0


def video_dur():
    return dur(VIDEO_SRC)


def build_combined():
    target = video_dur()
    st_total = sum(dur(t) for t in ST_SINGLES)
    js_total = JS_EACH * 2
    ajja_len = target - st_total - js_total
    print(f"target={target:.1f}s  ST={st_total:.1f}s  JS={js_total:.1f}s  Ajja={ajja_len:.1f}s",
          flush=True)

    # (file, clip_seconds or None for full)
    contrib = [(t, None) for t in ST_SINGLES] \
        + [(JS_A, JS_EACH), (JS_B, JS_EACH)] \
        + [(AJJA, ajja_len)]

    out = os.path.join(BEDS, "combined.m4a")
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for f, _ in contrib:
        cmd += ["-i", sh(f)]

    parts, labels = [], []
    for i, (f, clip) in enumerate(contrib):
        g = rg(f)
        chain = f"[{i}:a]volume={g:+.2f}dB,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo"
        if clip is not None:
            chain += f",atrim=0:{clip:.3f},asetpts=N/SR/TB"
        chain += f"[a{i}]"
        parts.append(chain)
        labels.append(f"[a{i}]")
        print(f"    in{i}: rg={g:+.2f}dB clip={clip}  {os.path.basename(sh(f))}", flush=True)

    n = len(contrib)
    fc = ";".join(parts) + f";{''.join(labels)}concat=n={n}:v=0:a=1[cat]" \
         + f";[cat]atrim=0:{target:.3f},asetpts=N/SR/TB[out]"
    cmd += ["-filter_complex", fc, "-map", "[out]",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", out]
    print(f"  -> building beds/combined.m4a ({n} inputs)", flush=True)
    subprocess.run(cmd, check=True)
    print(f"  -> combined bed done ({dur(out):.2f}s)", flush=True)


def mux():
    print("  -> muxing combined video (stream copy)", flush=True)
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-i", VIDEO_SRC, "-i", os.path.join(BEDS, "combined.m4a"),
           "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "copy",
           "-movflags", "+faststart", OUT_MIX]
    subprocess.run(cmd, check=True)
    print(f"  -> {OUT_MIX} done ({os.path.getsize(OUT_MIX)/1e9:.2f} GB, {dur(OUT_MIX):.1f}s)",
          flush=True)


def chunks():
    os.makedirs(CHUNK_DIR, exist_ok=True)
    d = dur(OUT_MIX)
    n = math.ceil(d / CHUNK_SEC)
    print(f"  -> slicing {d:.1f}s into {n} x {CHUNK_SEC}s chunks", flush=True)
    for i in range(n):
        ss = i * CHUNK_SEC
        out = os.path.join(CHUNK_DIR, f"{CHUNK_PREFIX}{i+1:02d}.mp4")
        cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
               "-ss", str(ss), "-t", str(CHUNK_SEC), "-i", OUT_MIX,
               "-map", "0", "-c", "copy", "-movflags", "+faststart", out]
        subprocess.run(cmd, check=True)
        print(f"    chunk {i+1:02d}/{n}: {out}  ({os.path.getsize(out)/1e6:.1f} MB)",
              flush=True)
    print(f"  -> {n} chunks in {CHUNK_DIR}/", flush=True)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("combined", "all"):
        build_combined()
        mux()
    if mode in ("chunks", "all"):
        chunks()
    print("\nDone.", flush=True)


if __name__ == "__main__":
    main()
