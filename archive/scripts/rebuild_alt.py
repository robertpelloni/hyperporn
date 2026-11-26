import random
import subprocess
import sys
import time
from pathlib import Path

VID = Path(r"C:\Users\hyper\Videos")
SISSY = Path(r"C:\Users\hyper\Videos\sissymaker")
WORK = SISSY / "alt_audio"
AJJA = Path(r"C:\Users\hyper\Music\Ajja - 2026 - Dimension Festival NZ (live).mp3")
HYPO = SISSY / "hypo_mix_v3.m4a"
SRC_VIDEO = SISSY / "ハイパーポルノ.mp4"
OUT = SISSY / "ハイパーポルノ_altaudio.mp4"
RUN_TIME = 10774.336

SINGLES = [
    "Mad Tribe - Alien S Slave (Original Mix).webm",
    "Mad Tribe - Drop The Bomb.mkv",
    "Mad Tribe - Out Of This World.webm",
    "Mad Tribe - They Came from Uranus.mkv",
    "Space Tribe & Dickster - Alien S Fiend.mkv",
    "Space Tribe & Laughing Buddha - Atom Bombs.mkv",
    "Stryker & Space Tribe - S, D and Rock 'n Roll.mkv",
]
SHUFFLE_SEED = 140


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def probe(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(p)],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout.strip())


def run(cmd, label):
    log(label)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        log(f"FAIL {label} rc={r.returncode}")
        log((r.stderr or "")[-600:])
        sys.exit(1)
    return r


def extract_singles():
    WORK.mkdir(exist_ok=True)
    outs = []
    for name in SINGLES:
        src = VID / name
        if not src.exists():
            sys.exit(f"missing single: {src}")
        dst = WORK / (src.stem + ".m4a")
        if not dst.exists() or dst.stat().st_size < 10_000:
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                 "-i", str(src), "-vn",
                 "-ac", "2", "-ar", "44100",
                 "-c:a", "aac", "-b:a", "192k", str(dst)],
                f"extract {name}")
        outs.append(dst)
        log(f"  {dst.name} {probe(dst):.1f}s")
    return outs


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


def main():
    for p in (SRC_VIDEO, AJJA, HYPO):
        if not p.exists():
            sys.exit(f"missing {p}")

    extracted = extract_singles()
    total_singles = sum(probe(p) for p in extracted)
    log(f"singles total {total_singles:.1f}s")

    order = list(extracted)
    random.Random(SHUFFLE_SEED).shuffle(order)
    log("shuffle order:")
    for p in order:
        log(f"  {p.name} {probe(p):.1f}s")

    singles_mix = concat_filter(order, WORK / "singles_mix.m4a", "concat shuffled singles")
    singles_dur = probe(singles_mix)

    ajja_need = RUN_TIME - singles_dur
    log(f"ajja slice needed {ajja_need:.1f}s")
    if ajja_need <= 0:
        sys.exit("singles longer than runtime")
    if ajja_need > probe(AJJA):
        sys.exit("ajja too short")

    ajja_part = WORK / "ajja_part.m4a"
    if not ajja_part.exists() or ajja_part.stat().st_size < 10_000:
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-ss", "0", "-t", f"{ajja_need:.6f}", "-i", str(AJJA),
             "-ac", "2", "-ar", "44100",
             "-c:a", "aac", "-b:a", "192k", str(ajja_part)],
            "slice ajja")
    log(f"  ajja_part {probe(ajja_part):.1f}s")

    music_bed = concat_filter([singles_mix, ajja_part], WORK / "music_bed.m4a",
                              "concat singles + ajja")
    log(f"music bed {probe(music_bed):.1f}s")

    if OUT.exists():
        OUT.unlink()
    log("mux alternate-audio 2GB video...")
    fc = (
        "[1:a]volume=0.70[mus];"
        "[2:a]volume=0.95[hyp];"
        "[mus][hyp]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
        "alimiter=limit=0.95[aout]"
    )
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(SRC_VIDEO),
         "-i", str(music_bed),
         "-i", str(HYPO),
         "-filter_complex", fc,
         "-map", "0:v", "-map", "[aout]",
         "-c:v", "copy",
         "-c:a", "aac", "-b:a", "320k",
         "-t", f"{RUN_TIME:.6f}",
         str(OUT)],
        capture_output=True, text=True,
    )
    log(f"mux rc={r.returncode} size={OUT.stat().st_size/1e6:.1f}MB")
    if r.returncode != 0:
        log((r.stderr or "")[-600:])
        sys.exit(1)
    log(f"OUT {OUT.name} {probe(OUT):.1f}s {OUT.stat().st_size/1e6:.1f}MB")
    log("REBUILD_ALT_OK")


if __name__ == "__main__":
    main()
