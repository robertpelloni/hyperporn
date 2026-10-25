#!/usr/bin/env python3
"""
rebuild_nohyp.py — Rebuild the hyperporn mashup WITHOUT any hypnoshit.

Video stream is copied from the existing 2 GB deliverable (already strobe-cut +
masked); only the audio bed changes. Three porn mixes:
  1. ajja       — Ajja 2026 Dimension Festival NZ (live)
  2. jumpstreet — Jumpstreet livesets chained to fill the runtime
  3. spacetribe — Space Tribe / Mad Tribe singles (seeded order) + Ajja remainder

Each bed is ReplayGain-levelled (volume=<rg>dB per track) then limited; no
hypnoshit vocal bed is mixed anywhere.

Usage:
    python rebuild_nohyp.py beds      # build audio beds only (fast)
    python rebuild_nohyp.py mux       # mux beds onto the video -> 3 mp4s
    python rebuild_nohyp.py all       # beds + mux
"""
import os, subprocess, sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

WORK = os.path.dirname(os.path.abspath(__file__))
os.chdir(WORK)

VIDEO_SRC = "ハイパーポルノ.mp4"          # existing 2 GB deliverable (video reused)
BEDS = os.path.join(WORK, "beds")
os.makedirs(BEDS, exist_ok=True)

AJJA = "Ajja - 2026 - Dimension Festival NZ (live).mp3"

# Jumpstreet livesets chained to fill the runtime (order matters).
JUMPSTREET = [
    "~/Music/Jumpstreet - 2025 - Sunlight Festival (live).mp3",
    "~/Music/Jumpstreet - 2026 - Dimension Festival DJ Set (live).mp3",
]

# Space Tribe / Mad Tribe singles, in the established seeded order.
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


def video_dur():
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", VIDEO_SRC],
        capture_output=True, text=True).stdout.strip()
    return float(out)


def replaygain(path):
    """Return (gain_db, found) from the replaygain_track_gain tag."""
    out = subprocess.run(
        ["ffprobe", "-v", "error",
         "-show_entries", "format_tags=replaygain_track_gain",
         "-of", "default=nw=1:nk=1", sh(path)],
        capture_output=True, text=True).stdout.strip()
    if not out:
        return 0.0, False
    # e.g. "-0.87 dB"
    tok = out.replace("dB", "").split()[0]
    try:
        return float(tok), True
    except ValueError:
        return 0.0, False


def build_bed(name, tracks, dur):
    """
    tracks: list of file paths, concatenated in order, each RG-levelled,
            output trimmed to exactly `dur` seconds.
    Writes beds/<name>.m4a (AAC 320k) and prints measured duration.
    """
    out = os.path.join(BEDS, f"{name}.m4a")
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for t in tracks:
        cmd += ["-i", sh(t)]
    # per-input RG volume + concat filter
    parts, labels = [], []
    for i, t in enumerate(tracks):
        g, found = replaygain(t)
        parts.append(f"[{i}:a]volume={g:+.2f}dB,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[a{i}]")
        labels.append(f"[a{i}]")
        print(f"    [{name}] in{i}: rg={g:+.2f}dB{' (no tag)' if not found else ''}  {os.path.basename(sh(t))}", flush=True)
    n = len(tracks)
    # No alimiter (RG already levels each track & sources are mastered);
    # concat + trim to the exact video length.
    fc = ";".join(parts) + f";{''.join(labels)}concat=n={n}:v=0:a=1[cat]" \
         + f";[cat]atrim=0:{dur:.3f},asetpts=N/SR/TB[out]"
    cmd += ["-filter_complex", fc, "-map", "[out]",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", out]
    print(f"  -> building beds/{name}.m4a ({n} tracks, target {dur:.1f}s)", flush=True)
    subprocess.run(cmd, check=True)
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", out],
                       capture_output=True, text=True).stdout.strip()
    print(f"  -> beds/{name}.m4a done, duration {float(d):.2f}s")
    return out


def mux(bed, outname):
    out = os.path.join(WORK, outname)
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-i", VIDEO_SRC, "-i", bed,
           "-map", "0:v", "-map", "1:a",
           "-c:v", "copy", "-c:a", "copy",
           "-movflags", "+faststart", "-shortest", out]
    print(f"  -> muxing {outname} (video stream copied, no re-encode)")
    subprocess.run(cmd, check=True)
    sz = os.path.getsize(out) / 1e9
    print(f"  -> {outname} done ({sz:.2f} GB)")


BED_TRACKS = {
    "ajja": [AJJA],
    "jumpstreet": JUMPSTREET,
    "spacetribe": ST_SINGLES + [AJJA],
}
MIX_NAME = {
    "ajja": "ハイパーポルノ_ajja.mp4",
    "jumpstreet": "ハイパーポルノ_jumpstreet.mp4",
    "spacetribe": "ハイーポルノ_spacetribe.mp4",
}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    which = sys.argv[2] if len(sys.argv) > 2 else None
    dur = video_dur()
    print(f"Video: {VIDEO_SRC}  duration={dur:.2f}s", flush=True)

    if mode == "bed":
        # Build a single bed (for parallel launch): python rebuild_nohyp.py bed ajja
        build_bed(which, BED_TRACKS[which], dur)
        print(f"\nBed '{which}' complete.", flush=True)
        return

    if mode in ("beds", "all"):
        for k in ("ajja", "jumpstreet", "spacetribe"):
            print(f"\n[{k}] bed", flush=True)
            build_bed(k, BED_TRACKS[k], dur)

    if mode == "mux-one":
        b = os.path.join(BEDS, f"{which}.m4a")
        mux(b, MIX_NAME[which])
        return

    if mode in ("mux", "all"):
        print("\n[MUX] Building the three porn mixes", flush=True)
        for k in ("ajja", "jumpstreet", "spacetribe"):
            mux(os.path.join(BEDS, f"{k}.m4a"), MIX_NAME[k])

    print("\nAll requested work complete.", flush=True)


if __name__ == "__main__":
    main()
