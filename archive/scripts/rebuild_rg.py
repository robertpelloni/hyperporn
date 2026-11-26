import random
import subprocess
import sys
import time
from pathlib import Path

SISSY = Path(r"C:\Users\hyper\Videos\sissymaker")
WORK = SISSY / "alt_audio_rg"
VIDEO = SISSY / "liveset60_strobe" / "video_fade.mp4"
HYPO = SISSY / "hypo_mix_v3.m4a"

SINGLES = [
    "Mad Tribe - 2017 - Alien's Slave.mp3",
    "Mad Tribe - 2017 - Drop the Bomb.mp3",
    "Mad Tribe - 2017 - Out of This World.mp3",
    "Mad Tribe - 2017 - They Came from Uranus.mp3",
    "Space Tribe & Dickster - 2017 - Alien's Fiend.mp3",
    "Space Tribe & Laughing Buddha - 2017 - Atom Bombs.mp3",
    "Stryker & Space Tribe - 2017 - S, D and Rock 'n Roll.mp3",
]
AJJA = "Ajja - 2026 - Dimension Festival NZ (live).mp3"
SHUFFLE_SEED = 140

OUT_NORM_FULL = SISSY / "ハイパーポルノ_full.mp4"
OUT_ALT_FULL = SISSY / "ハイパーポルノ_altaudio_full.mp4"
OUT_NORM_2GB = SISSY / "ハイパーポルノ_2GB.mp4"
OUT_ALT_2GB = SISSY / "ハイパーポルノ_altaudio_2GB.mp4"

RUN_TIME = 10774.336
MUS_VOL = "0.70"
HYP_VOL = "1.15"


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def probe(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(p)],
        capture_output=True, check=True,
    )
    return float(r.stdout.decode("utf-8", errors="replace").strip())


def run(cmd, label):
    log(label)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        log(f"FAIL {label} rc={r.returncode}")
        log((r.stderr or "")[-500:])
        sys.exit(1)
    return r


def concat_filter(inputs, out, label):
    if out.exists() and out.stat().st_size > 10_000:
        log(f"{out.name} exists {probe(out):.1f}s")
        return out
    n = len(inputs)
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for p in inputs:
        cmd += ["-i", str(p)]
    labels = "".join(f"[{i}:a]" for i in range(n))
    fc = (f"{labels}concat=n={n}:v=0:a=1,"
          "aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[aout]")
    cmd += ["-filter_complex", fc, "-map", "[aout]",
            "-c:a", "aac", "-b:a", "192k", str(out)]
    run(cmd, label)
    log(f"  {out.name} {probe(out):.1f}s")
    return out


def build_music_bed():
    WORK.mkdir(exist_ok=True)
    single_paths = [SISSY / n for n in SINGLES]
    for p in single_paths:
        if not p.exists():
            sys.exit(f"missing single {p}")
    ajja = SISSY / AJJA
    if not ajja.exists():
        sys.exit(f"missing ajja {ajja}")

    total_singles = sum(probe(p) for p in single_paths)
    log(f"singles total {total_singles:.1f}s (ReplayGain MP3s)")

    order = list(single_paths)
    random.Random(SHUFFLE_SEED).shuffle(order)
    log("shuffle order:")
    for p in order:
        log(f"  {p.name} {probe(p):.1f}s")

    singles_mix = concat_filter(order, WORK / "singles_mix.m4a", "concat shuffled singles")
    singles_dur = probe(singles_mix)
    ajja_need = RUN_TIME - singles_dur
    log(f"ajja slice needed {ajja_need:.1f}s")

    ajja_part = WORK / "ajja_part.m4a"
    if not ajja_part.exists() or ajja_part.stat().st_size < 10_000:
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-ss", "0", "-t", f"{ajja_need:.6f}", "-i", str(ajja),
             "-ac", "2", "-ar", "44100",
             "-c:a", "aac", "-b:a", "192k", str(ajja_part)],
            "slice ajja")
    log(f"  ajja_part {probe(ajja_part):.1f}s")

    music_bed = concat_filter([singles_mix, ajja_part], WORK / "music_bed.m4a",
                              "concat singles + ajja")
    log(f"music bed {probe(music_bed):.1f}s")
    return music_bed


def mux_full(music_src, out):
    if out.exists() and out.stat().st_size > 9_000_000_000:
        log(f"full exists {out.name}")
        return True
    if out.exists():
        out.unlink()
    log(f"mux full {out.name} (mus={MUS_VOL} hyp={HYP_VOL})...")
    fc = (
        f"[1:a]volume={MUS_VOL}[mus];"
        f"[2:a]volume={HYP_VOL}[hyp];"
        "[mus][hyp]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
        "alimiter=limit=0.95[aout]"
    )
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(VIDEO),
         "-i", str(music_src),
         "-i", str(HYPO),
         "-filter_complex", fc,
         "-map", "0:v", "-map", "[aout]",
         "-c:v", "copy",
         "-c:a", "aac", "-b:a", "320k",
         "-t", f"{RUN_TIME:.6f}",
         str(out)],
        capture_output=True, text=True,
    )
    size = out.stat().st_size / 1e6 if out.exists() else 0
    log(f"  rc={r.returncode} size={size:.1f}MB")
    if r.returncode != 0:
        log((r.stderr or "")[-500:])
        return False
    return True


def compress(src, out):
    if out.exists():
        out.unlink()
    log(f"compress {out.name} (veryfast 1200k + aac 192k)...")
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(src),
         "-c:v", "libx264", "-preset", "veryfast",
         "-b:v", "1200k", "-maxrate", "1300k", "-bufsize", "2400k",
         "-vf", "scale=1280:720",
         "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart",
         str(out)],
        capture_output=True, text=True,
    )
    size = out.stat().st_size / 1e6 if out.exists() else 0
    log(f"  rc={r.returncode} size={size:.1f}MB")
    if r.returncode != 0:
        log((r.stderr or "")[-500:])
        return False
    if size >= 2000:
        log(f"  WARNING {size:.1f}MB not under 2000MB")
        return False
    return True


def main():
    for p in (VIDEO, HYPO):
        if not p.exists():
            sys.exit(f"missing {p}")

    music_bed = build_music_bed()
    ajja = SISSY / AJJA

    if not mux_full(ajja, OUT_NORM_FULL):
        sys.exit("norm full failed")
    if not mux_full(music_bed, OUT_ALT_FULL):
        sys.exit("alt full failed")
    if not compress(OUT_NORM_FULL, OUT_NORM_2GB):
        sys.exit("norm 2GB failed")
    if not compress(OUT_ALT_FULL, OUT_ALT_2GB):
        sys.exit("alt 2GB failed")

    for p in (OUT_NORM_FULL, OUT_ALT_FULL, OUT_NORM_2GB, OUT_ALT_2GB):
        log(f"OUT {p.name} {probe(p):.2f}s {p.stat().st_size/1e6:.1f}MB")
    log("REBUILD_RG_OK")


if __name__ == "__main__":
    main()
