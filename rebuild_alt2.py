import subprocess
import sys
import time
from pathlib import Path

SISSY = Path(r"C:\Users\hyper\Videos\sissymaker")
MUSIC = SISSY / "alt_audio" / "music_bed.m4a"
HYPO = SISSY / "hypo_mix_v3.m4a"
SRC_FULL = SISSY / "Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps_FADE_v3.mp4"
OUT_FULL = SISSY / "ハイパーポルノ_altaudio_full.mp4"
OUT_2GB = SISSY / "ハイパーポルノ_altaudio_2GB.mp4"
RUN_TIME = 10774.336


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def probe(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(p)],
        capture_output=True, check=True,
    )
    return float(r.stdout.decode("utf-8", errors="replace").strip())


def mux_full():
    if OUT_FULL.exists() and OUT_FULL.stat().st_size > 10_000_000_000:
        log(f"full exists {OUT_FULL.stat().st_size/1e9:.2f}GB")
        return True
    if OUT_FULL.exists():
        OUT_FULL.unlink()
    log("mux full-size altaudio (video copy, aac 320k)...")
    fc = (
        "[1:a]volume=0.70[mus];"
        "[2:a]volume=0.95[hyp];"
        "[mus][hyp]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
        "alimiter=limit=0.95[aout]"
    )
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(SRC_FULL),
         "-i", str(MUSIC),
         "-i", str(HYPO),
         "-filter_complex", fc,
         "-map", "0:v", "-map", "[aout]",
         "-c:v", "copy",
         "-c:a", "aac", "-b:a", "320k",
         "-t", f"{RUN_TIME:.6f}",
         str(OUT_FULL)],
        capture_output=True, text=True,
    )
    size = OUT_FULL.stat().st_size / 1e6 if OUT_FULL.exists() else 0
    log(f"full rc={r.returncode} size={size:.1f}MB")
    if r.returncode != 0:
        log((r.stderr or "")[-600:])
        return False
    return True


def compress():
    if OUT_2GB.exists():
        OUT_2GB.unlink()
    # 1200k video + 192k aac -> ~1.9 GB over 10774 s (under 2 GB)
    log("compress sub-2GB (veryfast 1200k + aac 192k)...")
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(OUT_FULL),
         "-c:v", "libx264", "-preset", "veryfast",
         "-b:v", "1200k", "-maxrate", "1300k", "-bufsize", "2400k",
         "-vf", "scale=1280:720",
         "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart",
         str(OUT_2GB)],
        capture_output=True, text=True,
    )
    size = OUT_2GB.stat().st_size / 1e6 if OUT_2GB.exists() else 0
    log(f"compress rc={r.returncode} size={size:.1f}MB")
    if r.returncode != 0:
        log((r.stderr or "")[-600:])
        return False
    if size >= 2000:
        log(f"WARNING size {size:.1f}MB not under 2000MB")
        return False
    return True


def main():
    for p in (SRC_FULL, MUSIC, HYPO):
        if not p.exists():
            sys.exit(f"missing {p}")
    if not mux_full():
        sys.exit("full mux failed")
    log(f"full dur={probe(OUT_FULL):.2f}s")
    if not compress():
        sys.exit("compress failed")
    log(f"out2 dur={probe(OUT_2GB):.2f}s size={OUT_2GB.stat().st_size/1e6:.1f}MB")
    log("REBUILD_ALT2_OK")


if __name__ == "__main__":
    main()
