# STROBE Fade Mashup — Full Pipeline Documentation

**Deliverables (v7 / current — NO hypnoshit):**
- `ハイパーポルノ_ajja.mp4` — video + **Ajja** 2026 Dimension Festival NZ liveset (1.91 GB)
- `ハイパーポルノ_jumpstreet.mp4` — video + **Jumpstreet** livesets chained (1.90 GB)
- `ハイーポルノ_spacetribe.mp4` — video + **Space Tribe / Mad Tribe** singles + Ajja remainder (1.91 GB)
- `rebuild_nohyp.py` — builds the 3 audio beds + muxes them onto the reused video
- `beds/*.m4a` — RG-levelled audio beds (kept for cheap audio remuxes)

The video (strobe cut + mask) is unchanged and reused — stream-copied from the old 2 GB deliverable; only the audio bed differs per mix. Audio is a plain music bed (no Emperor-Hypnos vocal/instruction layer).

**Deliverables (v6 / previous — superseded):**
- `ハイパーポルノ_full.mp4` — Ajja BGM + hypnoshit (full size)
- `ハイパーポルノ_altaudio_full.mp4` — **Space Tribe singles mix** + Ajja remainder + hypnoshit (full size)
- `ハイパーポルノ_altaudio_2GB.mp4` — sub-2 GB of the Space Tribe mix only

**Status (superseded v6):** — ReplayGain applied everywhere; hypnoshit normalized together; hyp at normal volume 0.95
**Status:** v7 — hypnoshit removed; 3 music-bed porn mixes (Ajja / Jumpstreet / Space Tribe-Mad Tribe). Video stream reused, audio re-bedded (ReplayGain per track).
**Date:** 2026-10-25

---

## 1. What this is

A 3-hour (10,774 s) beat-synced video mashup at **60 fps / 720p**:

- **Video:** two adult-studio sources cut on every psytrance kick (**140 BPM strobe** = one clip every **26 frames / 0.4333 s**), alternating sissymaker scenes with wet-dream scenes, with a **one-period triangular-dip white/black mask** multiplied over the whole timeline (soft strobe/fade look).
- **Audio:** one continuous **Ajja** liveset as BGM, mixed with an **Emperor Hypnos ("hypnoshit")** vocal/instruction bed that runs for the full runtime with no cutouts.
- Source audio from the video clips is **always muted** (user adds ambience/sex-noise in their own editor later).

---

## 2. Source materials

### 2.1 Video — sissymaker set (15 files, user-renamed to short codes)

All in `C:\Users\hyper\Videos\sissymaker\`. Long original filenames are gone; **short codes are canonical**.

| Code | Original title | Duration (s) | Intro trim (s) | Outro trim (s) |
|------|----------------|-------------:|---------------:|---------------:|
| `bost` | Black Owned Slut Trainer | 494.8 | 19 | 12 |
| `csd2` | Cum Slut Destiny 2 | 335.1 | 11 | 12 |
| `sm1` | Sissy Maker 1 HD upscale | 234.1 | 3 | 2 |
| `sm2` | Sissymaker II | 442.1 | 4 | 0 |
| `sm3` | Sissymaker III | 408.1 | **25** | 6 |
| `sm4` | Sissy Maker IV | 171.0 | 4 | 4 |
| `sm5p1` | SSMK5 part I | 248.8 | 2 | 3 |
| `sm5p2` | SSMK5 part II | 432.5 | 8 | 18 |
| `sm6` | Sissymaker 6 | 369.6 | 15 | 8 |
| `sm7` | Ssm7 Caption HQ | 580.2 | 8 | 12 |
| `sm8` | SSM8 CANDY | 576.2 | 5 | 16 |
| `sm9` | SM9 CAP | 592.0 | 14 | 4 |
| `smx` | fbj2233 SMX | 514.0 | 20 | 10 |
| `scs` | Sissy Cocksucking Submission | 429.1 | 3 | 0 |
| `scds` | Sissy Cum Dumpster | 238.4 | 14 | 2 |

- **Intros** are Emperor Hypnos title cards; **outros** are credit/flash tails.
- `sm3` is the special case: its title runs to ~20 s (YAVG auto-detect falsely stopped at 9 s) → trim **25 s**.
- Outro values came from a programmatic luma detector (`detect_outros.py`); sm5p1's false 60 s outlier was manually corrected to 3 s.

### 2.2 Video — wet-dream set (1 source)

- `JPVT1109 - Wet Dreams AI Goon Therapy (parts 1-15).mp4` → used as the alternating B-roll stream (`wet_gop26.mp4` intermediate, 5967 MB).

### 2.3 Audio

| Track | Role | Duration (s) |
|-------|------|-------------:|
| `C:\Users\hyper\Music\Ajja - 2026 - Dimension Festival NZ (live).mp3` | BGM (liveset length driver) | 10,774.3 |
| `C:\Users\hyper\Music\Space Tribe - 2016/2017/2018 - ….mp3` (3 sets) | Optional alt BGM variant (user canceled this variant) | 3,441 / 5,081 / 3,058 |
| `C:\Users\hyper\Videos\hypnoshit\` (9 tracks) | Hypnoshit voice bed | see §4.2 |

---

## 3. Stage-by-stage pipeline

```
[0] trims        intro/outro-trimmed sources
[1] normalize    720p60, fps=60, setpts=N/60/TB, GOP=26  →  sissy_all_gop26.mp4 + wet_gop26.mp4
[2] cut          24,864 clips × EXACTLY 26 frames, alternating sissy/wet
[3] concat       clip list → video_copy.mp4   (-c copy)
[4] fade         loop 1-period triangular mask (floor 48/255) × RGB video → video_fade.mp4
[5] audio        Ajja BGM + continuous hypnoshit mix
[6] mux          video_fade + audio  (-c:v copy, one AAC encode)  → _FADE_v3.mp4
[7] compress     libx264 1350k veryfast + faststart              → _FADE_v3_2GB.mp4
```

Runtime is driven by the Ajja track (10,774.3 s). Clip count: 10,774.3 / (26/60) ≈ **24,864 clips**.

---

## 4.2 Space Tribe singles mix (alternate audio, current)

The "alternate audio" / Space Tribe mix is built from the 7 ReplayGain'd single MP3s in `sissymaker\`:

| # | Track | Duration (s) |
|---|-------|-------------:|
| 1 | Mad Tribe - 2017 - Alien's Slave | 499.5 |
| 2 | Mad Tribe - 2017 - Drop the Bomb | 487.7 |
| 3 | Mad Tribe - 2017 - Out of This World | 522.6 |
| 4 | Mad Tribe - 2017 - They Came from Uranus | 499.0 |
| 5 | Space Tribe & Dickster - 2017 - Alien's Fiend | 531.0 |
| 6 | Space Tribe & Laughing Buddha - 2017 - Atom Bombs | 516.1 |
| 7 | Stryker & Space Tribe - 2017 - S, D and Rock 'n Roll | 456.9 |

**Shuffle:** seeded `random.Random(140)` → fixed order (reproducible):
Drop the Bomb → They Came from Uranus → Alien's Fiend → Out of This World → Atom Bombs → Alien's Slave → Sex, Drugs and Rock 'n Roll

Total singles = **3,512.7 s** (the "first part"). Then **Ajja fills the remainder** (7,261.7 s) to reach the full 10,774.3 s runtime. Hypnoshit is mixed over the whole thing.

---

## 4. Audio design

### 4.0 v7 — No-hypnoshit beds (current)

The v7 rebuild drops the hypnoshit vocal bed entirely. Audio = a single psytrance music bed per mix, ReplayGain-levelled per track (`volume=<rg>dB`) then concatenated to the exact video length (10,774.35 s). No `amix`, no `loudnorm`, no limiter (sources are mastered + RG-normalised). Bed audio is AAC 192 kbps, stream-copied into the mux (`-c:a copy`). Built by `rebuild_nohyp.py`:

| Mix | Bed contents |
|-----|--------------|
| `ajja` | Ajja 2026 Dimension Festival NZ (live) — full set (10,774.336 s ≈ video) |
| `jumpstreet` | Jumpstreet livesets chained to fill 3 h — Sunlight Festival 2025 → Dimension Festival DJ Set 2026 (trimmed). Edit the `JUMPSTREET` list in the script to change which sets. |
| `spacetribe` | Space Tribe / Mad Tribe singles in the established seeded order (~3,513 s) + Ajja remainder (~7,261 s) — same pattern as the old "altaudio", minus hypnoshit |

Space Tribe / Mad Tribe singles order (unchanged from v6):
`Drop the Bomb → They Came from Uranus → Alien's Fiend → Out of This World → Atom Bombs → Alien's Slave → Sex, Drugs and Rock 'n Roll`.

**Reuse trick:** because hypnoshit was audio-only, the finished masked video is identical across versions — so v7 copies the video stream from the old 2 GB deliverable (`ハイパーポルノ.mp4`, `-c:v copy`) and swaps only the audio. No re-cut, no re-fade, no video re-encode. To re-bed audio later, rebuild the bed and remux (`python rebuild_nohyp.py mux-one <name>`).

### 4.0b Combined mix + 10-minute chunks (personal use)

`build_combined.py` makes **one combined mix** with all three sources on a single timeline, then slices it into 10-minute files:

- `ハイーポルノ_combined.mp4` — 3:00:00, video reused (`-c:v copy`). Audio bed = Space Tribe/Mad Tribe singles (58 min) → Jumpstreet Sunlight 2025 + Dimension DJ 2026 (30 min each) → Ajja (61 min). ReplayGain per track, AAC 192 kbps.
- `chunks/hyperporn_combined_c01.mp4 … c18.mp4` — 18 standalone 720p60+AAC files, each ~600 s (last = 574 s remainder), stream-copied (keyframe-aligned, `+faststart`). ASCII filenames for upload-tool safety.

Proportions are configurable at the top of `build_combined.py` (`JS_EACH`, the `contrib` list). Re-run `python build_combined.py combined` / `chunks` / `all`.

> These outputs are for **personal / local use**. The assistant built + segmented the media but does not publish, upload, or automate any platform (X, tube sites, self-hosted WordPress, muse.ai, etc.).

### 4.1 BGM (Ajja)

- Full liveset, no trimming.
- Mixed at `volume=0.70`.

### 4.2 Hypnoshit bed (the "full mix")

Order of tracks (each contributes its **second half minus its last 60 s**):

1. You Cant Stop Me
2. Milking Time
3. Ultimate Cuckold
4. Drop for Teacher
5. BeatrixVale
6. Submissive Sissy Slut
7. Obey-Submit
8. Take Your Medicine
9. Penelope (only if earlier tracks don't fill)

- Each part is `loudnorm=I=-16:TP=-1.5:LRA=11` together as a set, then concatenated.
- Target length = full runtime (~10,774 s); the last used track is trimmed to fill exactly.
- Mixed at `volume=0.95` (user asked for "a little louder than Ajja"; 0.80 was "almost perfect").

### 4.3 Final mix (v6 — current)

```
[1:a]volume=0.70[mus];
[2:a]volume=0.95[hyp];
[mus][hyp]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,
alimiter=limit=0.95[aout]
```

Hypnoshit is at the **normal** volume 0.95 (the earlier 1.15 raised mix is retired).
Music bed at 0.70. Both feed `amix normalize=0` + limiter.

**Why hypnoshit cut out ~1/3 of the way in (v3/v4):** two compounding bugs —

1. **AAC `concat -c copy` on many short `.m4a` parts leaves timestamp/gap artifacts** at every part boundary (each part was encoded separately). The fix is to concatenate the parts **once** with the `concat` *filter* into a single continuous encode (`hypo_mix_v4.m4a`), never the concat demuxer with `-c copy`.
2. **`amix` defaults `normalize=1`**, which rescales by the number of active inputs and **renormalizes when an input is considered "dropped"** (`dropout_transition=0` makes that renormalization instantaneous/harsh). The fix is `normalize=0` (plain sum) + `alimiter` for peak safety.

Verification method: `scan_hypo_level.py` measures RMS level every 30 s of the mix file vs the final mux. A healthy mix stays at −17…−21 dB the whole way; gap artifacts show up as brief level collapses at part boundaries.

### 4.3b Hypnoshit v4 build (ReplayGain, normalized together)

All 9 hypnoshit tracks, **same order and truncation as before**:
`You Cant Stop Me → Milking Time → Ultimate Cuckold → Drop for Teacher → BeatrixVale → Submissive Sissy Slut → Obey-Submit → Take Your Medicine → Penelope`

Each track contributes **`[duration/2, duration−60 s]`** (second half minus its last minute). The last track is clipped to fill exactly 10,774.3 s.

Render steps (`rebuild_v6.py`):
1. Extract each truncated part **raw** (no per-part processing).
2. Concat all parts with the `concat` *filter* → one continuous `hypo_raw.m4a`.
3. Measure **album ReplayGain** on the whole raw mix (`ffmpeg -af replaygain`).
4. Re-render once: `volume=<rg>dB,loudnorm=I=-16:TP=-1.5:LRA=11` → `hypo_mix_v4.m4a`.

So the hypnoshit is **normalized together as one piece** (not per-part), with ReplayGain applied first so tracks sit level before the final loudnorm.

### 4.3c Music ReplayGain

Source MP3s (singles + Ajja) carry ReplayGain tags from the user. Before mixing, each is re-encoded with its measured `replaygain_track_gain` applied (`volume=<rg>dB`) so every song sits at the same loudness. This applies to:
- `Ajja - 2026 - Dimension Festival NZ (live).mp3` (normal BGM)
- All 7 Space Tribe / Mad Tribe singles (alternate mix)

---

## 5. Video techniques (the hard-won rules)

### 5.1 Frame-exact strobe cuts — THE critical lesson

- Strobe clip length = 26 frames @ 60 fps (= 140 BPM kick grid).
- **`ffmpeg -c:v copy -t 0.433` is NOT frame-exact** — measured 433/498 clips landing 29/34/36/40/41/5 frames instead of 26 → mask desync → black flashes across the whole timeline.
- **`-frames:v 26 -c:v copy` from GOP=26 intermediates IS frame-exact** (24,864/24,864 correct, zero re-encodes). Always force frame count, never duration.
- **Verify every clip** with `ffprobe -show_entries stream=nb_frames` (container header, fast). Accept only `nb_frames==26`; else delete and recut (re-encode fallback with `tpad=stop_mode=clone` at source end).
- Tiny H.264 clips must not be concatenated with `-c copy` blindly for duration math — but once each clip is verified 26 frames, the concat is clean.

### 5.2 Intermediates

- Build **per-file** 720p60 intermediates: `fps=60,setpts=N/60/TB`, GOP/keyint **26**, then concat.
- Never `concat -c copy` of mixed-fps sources followed by `fps=` (fills gaps with frozen frames).
- Always `ffprobe` the intermediate duration against the sum of source durations before slicing.

### 5.3 Fade / mask

- `mask_p26_fixed.mp4`: one period (26 frames) of a **triangular dip to a non-zero floor (48/255)** in white — NOT `fade=t=in` (frame 0 pure black = a flash every period).
- Loop the mask over the whole video with the **mandatory** `setpts=N/FRAME_RATE/TB` on the looped mask, then multiply in **RGB** (`format=gbrp`), never YUV (UV halves → green):

```
[0:v]format=gbrp[a];
[1:v]setpts=N/FRAME_RATE/TB,format=gbrp[m];
[a][m]blend=all_mode=multiply:shortest=1,format=yuv420p[v]
```

- `-stream_loop -1` resets mask PTS; without `setpts`, `blend` pairs by timestamp and produces long black runs.

### 5.4 Intro/outro detection without viewing frames

When adult content can't be inspected via image tools (safety filters), use **numeric luma stats**:

- Sample 160×90 gray luma mean/std every 2 s.
- Intro end = first stable run of `mean>55` content frames.
- Outro tail = walk backward while `mean>235` or `<12` or `sd<5`.
- Isolated mid-window black samples are mid-video flashes, not outros — the walk-from-end rule must tolerate one content frame.

Script: `detect_outros.py` → `outro_trims.json`.

---

## 6. Compression (sub-2 GB copy)

```
libx264 -preset veryfast -b:v 1350k -maxrate 1400k -bufsize 2800k
  -vf scale=1280:720 -c:a aac -b:a 128k -movflags +faststart
```

- `preset medium` only runs at ~0.5× realtime here → 14 h. **`veryfast` is plenty at this bitrate** and runs ~1.5–2 h.
- Target: ~2,016 MB (1.9 GiB). Always keep the full-size original; the 2 GB is a copy.

---

## 7. Operational rules

- **Detach every multi-hour job** (`Start-Process` + Python argv-list script + log file). Tool timeouts kill ffmpeg mid-write and leave `moov atom not found` MP4s.
- **Resume-safe cutting:** skip clips that already exist (trust size on resume); verify all frame counts at the end. Delete `clip_*.mp4` + `video_copy.mp4` before any re-cut after an intermediate rebuild (resume-skip trap).
- **Disk:** the clip store + concat intermediate peak at ~20 GB. Free them before the final mux/compress stages if C: is tight.
- **Audio-only tweaks after a bake are remuxes** (`-map video -c:v copy`), never video re-encodes.
- PowerShell: write `.py` files via the Write tool (heredoc/nested-quote `python -c` fails). Avoid `Get-Content -Tail` on huge logs.

---

## 8. Script inventory (`C:\Users\hyper\Videos\sissymaker\`)

| Script | Purpose |
|--------|---------|
| `rebuild_v6.py` | **Current:** ReplayGain-aware rebuild — hypnoshit v4 (together + RG), music RG, both full videos (hyp 0.95), 2 GB of Space Tribe mix only |
| `rebuild_v5.py` | Continuous hypnoshit mix + Ajja mux (`normalize=0`) — superseded |
| `rebuild_rg.py` | RG music-bed build — superseded by v6 |
| `rebuild_v4.py` | Full pipeline: trims → GOP26 → 26-frame cut → concat → audio → fade → mux → compress (built the v3 files) |
| `finish_v4.py` | Post-disk-full finisher: ST mux + 2 GB compressions |
| `detect_outros.py` | Programmatic outro detector (luma mean/std) |
| `check_clipframes.py` | Frame-count scanner — proved the `-t` cut bug |
| `scan_hypo_level.py` | RMS-over-time scanner for diagnosing audio dropouts |
| `probe_rg.py` / `probe_hyp_rg.py` | ReplayGain tag/gain measurement |
| `remix_hyp.py` | v2b audio remux (Ajja 0.75 / hyp 0.80) |
| `compress_2gb.py` | Standalone sub-2 GB encoder |
| `fade_fix.py` | Fade/mask construction |
| `mask_p26_fixed.mp4` | The 26-frame triangular dip mask (reused) |
| `intro_trims.json` / `outro_trims.json` | Trim data |
| `performers.txt` | 30 unique performer names (credit list, closed) |

---

## 9. Version history

| File | Notes |
|------|-------|
| `…_FADE_v1.mp4` (10.18 GB) | First fade bake. Keep. |
| `…_FADE_v2.mp4` (10881 MB) | Mask-floor + setpts fix. Keep. |
| `…_FADE_v2b.mp4` (10881 MB) | Audio remix (hyp 0.80). Keep. |
| `…_FADE_v3.mp4` (11.09 GB) | Frame-exact 26-frame cut (black flashes fixed) + hyp second-halves. |
| `ハイパーポルノ.mp4` / `…_2GB.mp4` | User-renamed 2 GB deliverables (superseded by v6). |
| **v6 (current)** | ReplayGain on all audio; hypnoshit normalized together (album RG + loudnorm); hyp at normal 0.95. Full Ajja + full Space Tribe mix + 2 GB of Space Tribe mix only. |

**Space Tribe variant:** reintroduced as the "altaudio" / singles mix (7 ReplayGain'd single MP3s + Ajja remainder). The 2 GB render is **only** for this Space Tribe mix. Older 3-set `spacetribe_mix.m4a` approach is retired.

---

## 10. Parameter cheat-sheet

```
FPS                60
Resolution         1280×720
BPM                140 (strobe = 26 frames / 0.4333 s per clip)
Clip frames        26 EXACTLY  (-frames:v 26, verify nb_frames==26)
Clip count         24,864
Runtime            10,774.336 s  (Ajja liveset length)
Pattern            alternate sissymaker ↔ wet-dream
Mask               triangular dip, floor 48/255, period 26 frames, RGB multiply
BGM                Ajja 2026 Dimension Festival NZ (live), volume 0.70
Hypnoshit          2nd half − 60 s tail of each of 9 tracks, loudnorm I=-16 TP=-1.5 LRA=11, volume 0.95
Mix                amix normalize=0 dropout_transition=0, alimiter 0.95, aac 320k
2GB encode         libx264 veryfast 1200k/1300k/2400k, aac 192k, faststart (measured 1,904 MB)
```
