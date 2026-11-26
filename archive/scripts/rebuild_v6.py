"""rebuild_v6: ReplayGain-aware audio rebuild.

Phases:
  1. hypo_mix_v4.m4a  - same 9-track order, same truncation (2nd half - 60s),
                        concatenated THEN normalized together + ReplayGain applied.
  2. Music beds       - Ajja and singles MP3s get ReplayGain measured + applied.
  3. Both full videos - hypnoshit at NORMAL volume 0.95 (not the raised 1.15).
  4. 2GB render       - ONLY the Space Tribe singles mix (altaudio).
"""
import re
import subprocess
import random
import sys
import time
from pathlib import Path

SISSY = Path(r"C:\Users\hyper\Videos\sissymaker")
HYPO_DIR = Path(r"C:\Users\hyper\Videos\hypnoshit")
WORK = SISSY / "alt_audio_rg"
HYPO_WORK = SISSY / "hypo_v4"
VIDEO = SISSY / "liveset60_strobe" / "video_fade.mp4"

HYPO_MIX = SISSY / "hypo_mix_v4.m4a"
AJJA = SISSY / "Ajja - 2026 - Dimension Festival NZ (live).mp3"
SINGLES = [
    "Mad Tribe - 2017 - Alien's Slave.mp3",
    "Mad Tribe - 2017 - Drop the Bomb.mp3",
    "Mad Tribe - 2017 - Out of This World.mp3",
    "Mad Tribe - 2017 - They Came from Uranus.mp3",
    "Space Tribe & Dickster - 2017 - Alien's Fiend.mp3",
    "Space Tribe & Laughing Buddha - 2017 - Atom Bombs.mp3",
    "Stryker & Space Tribe - 2017 - S, D and Rock 'n Roll.mp3",
]
SHUFFLE_SEED = 140

HYPO_ORDER = [
    "You Cant Stop Me", "Milking Time", "Ultimate Cuckold",
    "Drop for Teacher", "BeatrixVale", "Submissive Sissy Slut",
    "Obey-Submit", "Take Your Medicine", "Penelope",
]

OUT_NORM_FULL = SISSY / "ハイパーポルノ_full.mp4"
OUT_ST_FULL = SISSY / "ハイパーポルノ_altaudio_full.mp4"
OUT_ST_2GB = SISSY / "ハイパーポルノ_altaudio_2GB.mp4"

RUN_TIME = 10774.336
MUS_VOL = "0.70"
HYP_VOL = "0.95"   # normal volume from before, NOT 1.15


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


def measure_rg(path):
    """Return replaygain_track_gain in dB (computed)."""
    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(path),
         "-af", "replaygain", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    m = re.search(r"replaygain_track_gain:\s*([-\d.]+)", r.stderr or "")
    return float(m.group(1)) if m else 0.0


def find_hypo(keyword):
    key = keyword.lower().replace("-", " ").replace("_", " ")
    for p in HYPO_DIR.iterdir():
        if p.suffix.lower() not in (".mp3", ".m4a", ".wav", ".flac"):
            continue
        name = p.name.lower().replace("-", " ").replace("_", " ")
        if key in name:
            return p
    return None


def build_hypo_mix_v4():
    """Same order/truncation as before, but normalize TOGETHER + apply ReplayGain."""
    if HYPO_MIX.exists() and HYPO_MIX.stat().st_size > 500_000:
        log(f"hypo v4 exists {HYPO_MIX.stat().st_size/1e6:.1f}MB")
        return True
    HYPO_WORK.mkdir(exist_ok=True)

    # Phase A: extract truncated parts RAW (no per-part loudnorm)
    parts = []
    filled = 0.0
    for key in HYPO_ORDER:
        src = find_hypo(key)
        if not src:
            log(f"missing hypo {key}")
            continue
        dur = probe(src)
        ss = dur / 2.0
        end = dur - 60.0
        if end <= ss:
            continue
        take = end - ss
        if filled + take > RUN_TIME:
            take = RUN_TIME - filled
        if take < 5:
            break
        out = HYPO_WORK / f"{len(parts):02d}_raw.m4a"
        if not (out.exists() and out.stat().st_size > 100_000):
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                 "-ss", f"{ss:.3f}", "-t", f"{take:.3f}", "-i", str(src),
                 "-ac", "2", "-ar", "44100",
                 "-c:a", "aac", "-b:a", "192k", str(out)],
                f"hypo raw part {key}")
        parts.append(out)
        filled += take
        log(f"  raw part {key} +{take:.1f}s total={filled:.1f}s")
        if filled >= RUN_TIME - 1:
            break

    # Phase B: concat all parts as ONE continuous stream
    raw_mix = HYPO_WORK / "hypo_raw.m4a"
    if not (raw_mix.exists() and raw_mix.stat().st_size > 500_000):
        n = len(parts)
        cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
        for p in parts:
            cmd += ["-i", str(p)]
        labels = "".join(f"[{i}:a]" for i in range(n))
        fc = (f"{labels}concat=n={n}:v=0:a=1,"
              "aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[aout]")
        cmd += ["-filter_complex", fc, "-map", "[aout]",
                "-c:a", "aac", "-b:a", "192k", str(raw_mix)]
        run(cmd, f"concat {n} hypo parts (continuous)")
    log(f"hypo raw mix {probe(raw_mix):.1f}s")

    # Phase C: measure ReplayGain on the WHOLE mix (album/normalized-together)
    rg = measure_rg(raw_mix)
    log(f"hypo album ReplayGain = {rg:+.2f} dB")

    # Phase D: render final with ReplayGain applied + normalize together
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(raw_mix),
         "-af", f"volume={rg:+.2f}dB,loudnorm=I=-16:TP=-1.5:LRA=11",
         "-ac", "2", "-ar", "44100",
         "-c:a", "aac", "-b:a", "192k", str(HYPO_MIX)],
        "hypo v4: apply ReplayGain + loudnorm together")
    log(f"hypo_mix_v4 {probe(HYPO_MIX):.1f}s {HYPO_MIX.stat().st_size/1e6:.1f}MB")
    return True


def apply_rg_encode(src, out, label):
    """Re-encode audio with its ReplayGain applied."""
    if out.exists() and out.stat().st_size > 100_000:
        log(f"{out.name} exists")
        return out
    rg = measure_rg(src)
    log(f"  RG {src.name} = {rg:+.2f} dB")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(src),
         "-af", f"volume={rg:+.2f}dB",
         "-ac", "2", "-ar", "44100",
         "-c:a", "aac", "-b:a", "192k", str(out)],
        label)
    return out


def build_music_beds():
    WORK.mkdir(exist_ok=True)

    # Ajja with RG applied
    ajja_rg = apply_rg_encode(AJJA, WORK / "ajja_rg.m4a", "ajja + ReplayGain")
    ajja_dur = probe(ajja_rg)
    log(f"ajja_rg {ajja_dur:.1f}s")

    # Singles with RG applied
    single_paths = []
    for n in SINGLES:
        src = SISSY / n
        if not src.exists():
            sys.exit(f"missing single {src}")
        dst = WORK / (src.stem + "_rg.m4a")
        apply_rg_encode(src, dst, f"single RG {n[:40]}")
        single_paths.append(dst)

    total = sum(probe(p) for p in single_paths)
    log(f"singles total {total:.1f}s")

    # Space Tribe mix = shuffled singles then Ajja remainder
    order = list(single_paths)
    random.Random(SHUFFLE_SEED).shuffle(order)
    log("shuffle order:")
    for p in order:
        log(f"  {p.name} {probe(p):.1f}s")

    singles_mix = WORK / "singles_mix.m4a"
    if not (singles_mix.exists() and singles_mix.stat().st_size > 100_000):
        n = len(order)
        cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
        for p in order:
            cmd += ["-i", str(p)]
        labels = "".join(f"[{i}:a]" for i in range(n))
        fc = (f"{labels}concat=n={n}:v=0:a=1,"
              "aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[aout]")
        cmd += ["-filter_complex", fc, "-map", "[aout]",
                "-c:a", "aac", "-b:a", "192k", str(singles_mix)]
        run(cmd, "concat shuffled singles")
    sd = probe(singles_mix)
    log(f"singles_mix {sd:.1f}s")

    ajja_need = RUN_TIME - sd
    log(f"ajja remainder {ajja_need:.1f}s")
    ajja_part = WORK / "ajja_part.m4a"
    if not (ajja_part.exists() and ajja_part.stat().st_size > 100_000):
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-ss", "0", "-t", f"{ajja_need:.6f}", "-i", str(ajja_rg),
             "-c:a", "aac", "-b:a", "192k", str(ajja_part)],
            "slice ajja remainder")
    log(f"ajja_part {probe(ajja_part):.1f}s")

    st_bed = WORK / "music_bed.m4a"
    if not (st_bed.exists() and st_bed.stat().st_size > 100_000):
        cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
               "-i", str(singles_mix), "-i", str(ajja_part),
               "-filter_complex",
               "[0:a][1:a]concat=n=2:v=0:a=1,"
               "aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[aout]",
               "-map", "[aout]", "-c:a", "aac", "-b:a", "192k", str(st_bed)]
        run(cmd, "concat singles + ajja = space tribe bed")
    log(f"st_bed {probe(st_bed):.1f}s")

    return ajja_rg, st_bed


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
         "-i", str(VIDEO), "-i", str(music_src), "-i", str(HYPO_MIX),
         "-filter_complex", fc,
         "-map", "0:v", "-map", "[aout]",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
         "-t", f"{RUN_TIME:.6f}", str(out)],
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
         "-movflags", "+faststart", str(out)],
        capture_output=True, text=True,
    )
    size = out.stat().st_size / 1e6 if out.exists() else 0
    log(f"  rc={r.returncode} size={size:.1f}MB")
    if r.returncode != 0:
        log((r.stderr or "")[-500:])
        return False
    return True


def main():
    for p in (VIDEO, AJJA):
        if not p.exists():
            sys.exit(f"missing {p}")

    if not build_hypo_mix_v4():
        sys.exit("hypo v4 failed")

    ajja_rg, st_bed = build_music_beds()

    if not mux_full(ajja_rg, OUT_NORM_FULL):
        sys.exit("ajja full failed")
    if not mux_full(st_bed, OUT_ST_FULL):
        sys.exit("st full failed")

    # 2GB ONLY for the Space Tribe mix
    if not compress(OUT_ST_FULL, OUT_ST_2GB):
        sys.exit("st 2GB failed")

    for p in (OUT_NORM_FULL, OUT_ST_FULL, OUT_ST_2GB):
        log(f"OUT {p.name} {probe(p):.2f}s {p.stat().st_size/1e6:.1f}MB")
    log("REBUILD_V6_OK")


if __name__ == "__main__":
    main()
