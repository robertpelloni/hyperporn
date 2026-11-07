# ハイパーポルノ 4K60 — Topaz AI Upscale Runbook

How to take the finished 720p60 strobe mashup to **3840×2160, 60 fps** with the
**free Topaz ffmpeg build** (no Topaz GUI licence purchase, no install), in very
short segments that can be rendered on a GPU machine, verified frame-exact, and
reassembled with any audio bed.

**Status (2026-11-07): proven end-to-end at test scale on an Intel HD 520 laptop.**

| Proof | Result |
|---|---|
| 320×180 → 1280×720, 1 s | `topaz_test_small3_720p.mp4`, HEVC, 60 frames, exit 0 |
| 1280×720 → 3840×2160, 1 s | `topaz_test_real1s_4k.mp4`, HEVC, 60 frames, 1.000 s, 9.6 MB, exit 0 |

The full 3-hour job was **not** run on the laptop (see speed numbers in §8 — it is
a GPU-machine job). Everything needed to run it there is in this repo plus the
manual-copy list in §10.

> Personal / local use only. Do not commit the media, the extracted Topaz
> binaries, downloaded models, or extracted frames to this (public) repo — see
> §11.

---

## 1. The one big idea

The video stream is **identical in every mix** (Ajja / Jumpstreet / Space Tribe /
combined differ only in audio). So:

```
master (720p60, video+audio)
  │  cut video-only into short segments        (cut_for_upscale.py)
  ▼
seg_0000.mp4 … seg_1077.mp4   (10 s each, stream copy, frame-exact)
  │  Topaz tvai_up per segment, batch          (upscale_topaz.py)
  ▼
seg_*.mp4 at 3840×2160 60 fps (video-only)
  │  verify frame counts, concat, remux bed    (reassemble_upscaled.py)
  ▼
hyperporn_4k60.mp4  (+ whichever beds/*.m4a you choose)
```

Upscale **once**, remux audio at the end. Never upscale per-mix.

### Master facts (verified by ffprobe)

| Fact | Value |
|---|---|
| Resolution / fps | 1280×720, 60/1 |
| Frames | **646,461** (the number every stage must reproduce) |
| Duration | 10,774.35 s (2:59:34) |
| Keyframes | every 26 frames (0.4333 s) → lossless, frame-exact segment cuts |
| Video codec | H.264 High, ~1.34 Mbps |

### Segment maths

| Segment length | Files | Notes |
|---:|---:|---|
| 10 s | 1,078 | default; proven in pilot (6 files, 3,602 frames, 60.03 s) |
| 30 s | 360 | fewer files, longer per-file loss if a render dies |
| 60 s | 180 | only if the renderer is rock solid |

Cutting is `-c:v copy` against the 26-frame keyframe grid, so segments are
frame-exact with zero re-encode and total ≈ the master's video stream (~1.7 GB).

---

## 2. Get the free Topaz ffmpeg (no install)

You do **not** need to buy or install Topaz Video. You need three things Topaz
gives away, assembled by hand:

1. **The redistributable is not enough.** `TopazLabs/FFmpeg` releases
   ("Topaz Video AI Redistributables", e.g. v8.0.1.2 win.zip, 75 MB) ship DLLs
   and headers but **no `ffmpeg.exe`**, no `topaz_rlm.dll`, and no models.
2. **Download the app MSI and extract it** (installing needs admin; extracting
   does not):

   ```
   https://downloads.topazlabs.com/deploy/TopazVideoStudio/1.2.1/TopazVideo-1.2.1.msi   (298 MB)
   msiexec /a TopazVideo-1.2.1.msi TARGETDIR=<repo>\topaz-extract /qn
   ```

   You get `topaz-extract\PFiles\Topaz Labs LLC\Topaz Video\ffmpeg.exe` with
   filters `tvai_up, tvai_fi, tvai_pe, tvai_cpe, tvai_stb`, plus every DLL it
   needs (`topaz_rlm.dll`, TensorRT/OpenVINO runtimes, …). Verified:
   `ffmpeg.exe -hide_banner -filters | findstr tvai`.
3. **Model definitions** live in `topaz-extract\Topaz Labs LLC\Topaz Video\models`
   (86 `.json` files). Model **weights** (`.tz3`) download free on first use —
   `prob-4` (Proteus v4) fetched `prob-v4-fgnet-fp16-384x672-4x-ox.tz3` (41 MB)
   with no account.

### Runtime layout used here (all git-ignored, recreate per §10)

```
topaz-extract\      extracted MSI payload (~1.15 GB)
topaz-models-min\   prob-4.json + tvai.tz ONLY   ← TVAI_MODEL_DIR
topaz-models\       downloaded .tz3 weights      ← TVAI_MODEL_DATA_DIR
```

### Environment (required for every Topaz ffmpeg call)

```bat
set "TVAI_MODEL_DIR=<repo>\topaz-models-min"
set "TVAI_MODEL_DATA_DIR=<repo>\topaz-models"
set "PATH=<repo>\topaz-extract\PFiles\Topaz Labs LLC\Topaz Video;%PATH%"
```

**Why the minimal model dir matters:** pointing `TVAI_MODEL_DIR` at the full
86-file models folder makes the engine scan/validate every JSON on every call
(~35 s per file on a loaded machine — startup took ~5 minutes). With only
`prob-4.json` (+ `tvai.tz`, next section) present, model setup takes ~2 s.

---

## 3. The watermark (licensing) — read this first

Without a Topaz login the engine logs:

```
CRITICAL: Cannot open zip file at: ...\topaz-models-min\auth.tpz
CRITICAL: Invalid auth file
INFO: Auth Check Watermark: 1 1 1 ...
INFO: Adding watermark
```

… and burns a large centred **"Topaz Labs™"** watermark into every frame
(visible in `topaz_A_frame15_preview.png` / the 1 s test frames — kept local,
not committed). Two consequences:

- `topaz-models-min\` **must contain `tvai.tz`** (16 KB, copied from the MSI
  `models` folder). Without it the watermark layer fails with
  `Cannot open zip ...\topaz-models-min\tvai.tz` and the pipeline stalls.
- **Removing the watermark requires a legitimate Topaz login.** Signing in once
  in the Topaz app creates a valid `auth.tpz`, after which
  `tvai_owns_app()` returns true and output is clean. There is no supported
  flag, env var, or filter option to turn it off, and this runbook does not
  bypass it. The ffmpeg plumbing below is identical either way — only the
  auth state changes.

---

## 4. Cut the segments

```bat
python cut_for_upscale.py --seconds 10              :: full run, 1,078 segments
python cut_for_upscale.py --seconds 10 --limit 6    :: pilot (what was verified)
```

- Output: `upscale_segments\seg_0000.mp4 …` (video-only, `-an -c:v copy`,
  `-f segment -reset_timestamps 1`) + `upscale_segments\manifest.csv` with
  **probed** per-file `frames,duration,width,height` — never trust the plan,
  trust the probe.
- Pilot verification: 6 files, 1.32–1.58 MB each, **3,602 frames** total for
  60.03 s (the +2 frames are keyframe snapping on the pilot's `-t` cap; a full
  run must sum to exactly **646,461** — the script prints the total).

## 5. Upscale the segments

```bat
python upscale_topaz.py --input upscale_segments --output upscale_out
python upscale_topaz.py --model ahq-12 --device 0    :: examples
```

Defaults: model `prob-4` (Proteus v4), `device=-1` CPU / `-2` auto / `0` first
GPU, encoder `hevc_qsv`, quality 16. The runner is resumable: a segment whose
output already probes at 3840×2160 with the same frame count as its source is
skipped. Any mismatch aborts the run loudly.

The exact filter chain that works (this cost hours to find — keep it intact):

```
tvai_up=model=prob-4:scale=0:w=3840:h=2160:device=-1,scale=3840:2160:flags=lanczos,format=nv12
```

Rules baked into that string:

- **Proteus only offers 1×/2×/4×.** `scale=0:w/h` makes it run the 4× model
  (1280×720 → 5120×2880) and the following `scale=` brings it to 3840×2160.
  There is no native 3×.
- **`format=nv12` is mandatory before hardware encoders.** The filter outputs
  RGB (`x2rgb10le`); `hevc_qsv` rejects it with
  `Current pixel format is unsupported` / `Error submitting the frame for encoding`
  after silently eating the first frames. On an NVIDIA machine use
  `hevc_nvenc` (also nv12-friendly) or append `format=p010le` for 10-bit.
- **Topaz's ffmpeg has no libx264/libx265.** Only hardware encoders
  (qsv/amf/nvenc/mf) are built in. Plan the encoder around the GPU you have.
- `tvai_up` wants **RGB input**; ffmpeg auto-converts yuv420p → rgb48le with
  software swscale warnings (`No accelerated colorspace conversion found`) —
  expected, harmless, slow. Do not "fix" it by pre-converting; the filter
  graph already does the right thing.

### Model choice

| Model | Use |
|---|---|
| `prob-4` (Proteus v4) | default; manual params possible (`preblur`, `noise`, `details`, … via `tvai_up=...:estimate=1` auto-estimate or explicit keys in the model's JSON param list) |
| `ahq-12` (Artemis HQ) | stronger denoise for noisy sources; worth one A/B segment |
| `iris-3` | face-focused; test before committing — faces here are small/fast |

Whatever you pick, render **one 10 s segment first** and eyeball frames against
the source before launching 1,078 of them.

## 6. Surviving a long render (operational rules)

These were all learned the hard way on the laptop; they matter on any machine:

1. **Topaz sets its own process priority to BelowNormal.** On a busy box the
   render starves (CPU flatlines at ~163 MB, zero frames for 30+ minutes
   while "running"). Fix: a guard loop that re-pins the Topaz `ffmpeg.exe`
   to High every 5 s (`guard_any_topaz.ps1`). On a dedicated GPU machine,
   close everything else instead.
2. **Never wrap long renders in a tool timeout.** A killed wrapper leaves the
   child ffmpeg alive holding model/file locks ("The process cannot access
   the file because it is being used by another process"), and a killed
   ffmpeg leaves an unreadable MP4 (`moov atom not found`). Detach with
   `Start-Process`, poll the log file.
3. **Use fragmented MP4 for renders:**
   `-movflags frag_keyframe+empty_moov+default_base_moof -flush_packets 1`.
   If a render dies, the partial file stays readable frame-by-frame.
4. **End-of-stream frame holdback:** `tvai_up` holds frames back (temporal
   model + preflight). A segment rendered from a **seeked** input
   (`-ss 0.5 -i …`) returned only 19 of 30 frames at EOF. Fixes: cut segments
   as standalone files first (the §4 cutter already does), and if a short
   clip still comes up short, pad its source with cloned tail frames
   (`tpad=stop_mode=clone`) and cap output with `-frames:v N` so the real
   frames flush through. Verify every output's `nb_frames` — always.
5. **Memory:** the engine held ~2.2–2.8 GB on the laptop and died once with
   OpenCV `Insufficient memory` at frame 37/60 when system free RAM fell
   under ~1 GB. Keep ≥4 GB free; splitting renders into halves also halves
   the per-process accumulation.
6. **First frame is the slowest.** Per-process startup = model scan (~2 s
   with the minimal dir) + model load (~7 s) + OpenVINO compile; the first
   output frame at 720p took ~19 minutes on the 2-core laptop (18 tiles of
   672×384 per frame). Budget for it; don't mistake it for a hang. A real
   hang shows zero CPU delta over 30 s — check that before killing anything.

## 7. Reassemble

```bat
python reassemble_upscaled.py --upscaled upscale_out --bed combined
python reassemble_upscaled.py --upscaled upscale_out --bed ajja --check-only
```

- Concats the upscaled segments stream-copy, then muxes `beds\<bed>.m4a`
  (`ajja` | `jumpstreet` | `spacetribe` | `combined`) stream-copy + faststart.
- **Hard gate:** total frames must equal **646,461**. A mismatch means a
  segment is missing, duplicated, or was frame-interpolated — the script
  refuses to ship the join.
- Output 4K at QSV quality 16 ran ~77 Mbps on test content (~9.6 MB for 1 s).
  For the full 3 h, budget **30–90 GB** depending on encoder/quality, plus
  the same again in working space. This laptop had 7.7 GB free — another
  reason the full job belongs on the GPU machine.

---

## 8. Measured performance (Intel HD 520 laptop — the floor, not the target)

| Test | Result |
|---|---|
| Model setup, full 86-JSON dir | ~5 min (do not do this — use the minimal dir) |
| Model setup, minimal dir | ~2 s scan + 7 s load, OpenVINO init ~2 s |
| 320×180 → 720p, 60 frames (prob-4, CPU) | ~2.5 min inference (~2.5 s/frame, 1 tile) |
| 720p → 4K, first frame | ~19 min (18 tiles + compile, busy 2-core CPU) |
| 720p → 4K, steady state | **~1.2–1.5 min/frame** |
| Extrapolated full master | 646,461 frames → **>1 year**. Not a laptop job. |

A mid-range NVIDIA GPU running Topaz natively is typically **two to three
orders of magnitude faster** per frame. Re-measure with one segment on the
target machine before extrapolating anything.

## 9. Troubleshooting (symptom → cause → fix)

| Symptom | Cause | Fix |
|---|---|---|
| `Model not found: prob-4` | `TVAI_MODEL_DIR` has no model JSONs | point it at the minimal dir (§2) |
| Startup takes minutes, no frames | full models dir scan / BelowNormal priority starvation | minimal dir + priority guard (§6.1) |
| `Current pixel format is unsupported`, exit −22 | encoder got RGB from the filter | append `format=nv12` (§5) |
| `Cannot open zip ...\tvai.tz` | watermark asset missing from model dir | copy `tvai.tz` into `topaz-models-min\` (§3) |
| Output has fewer frames than input | tvai end-of-stream holdback (seek/short inputs) | standalone segment files; `tpad` clone padding + `-frames:v` (§6.4) |
| `moov atom not found` on output | ffmpeg killed mid-write | fragmented MP4 flags; never kill renders (§6.2–6.3) |
| "process cannot access the file" | zombie ffmpeg from a killed wrapper holds locks | kill only PIDs whose command line is provably yours; check with `Get-CimInstance Win32_Process` |
| OpenCV `Insufficient memory` mid-render | system RAM exhausted | free RAM (≥4 GB), render in halves (§6.5) |
| Big "Topaz Labs" watermark | no valid `auth.tpz` | sign in once in the Topaz app (§3) |

## 10. GPU machine checklist

**Comes with `git pull` (this repo):** all scripts (`cut_for_upscale.py`,
`upscale_topaz.py`, `reassemble_upscaled.py`, `run_topaz_*.bat`,
`run_*_babysit.ps1`, `guard_*.ps1`, `rebuild_nohyp.py`, `build_combined.py`),
this runbook, `PIPELINE.md`, `PROJECT_BRIEF.md`, pilot manifest.

**Copy manually (git-ignored, will NOT sync):**

| Item | Size | Why manual |
|---|---:|---|
| the master video (`ハイパーポルノ*.mp4` / combined) | ~1.8 GB | media is git-ignored; GitHub rejects >100 MB anyway |
| `beds\*.m4a` (or rebuild via `rebuild_nohyp.py` + source MP3s) | ~200 MB each | audio is git-ignored |
| Topaz MSI (re-download per §2 — easier than copying) | 298 MB | proprietary binary |
| extracted frames / test MP4s from the laptop proofs | small | adult imagery — never commit to this public repo |

**On the GPU machine, in order:**

1. `git clone` / `git pull` this repo.
2. Copy the master video (and `beds\` if not rebuilding) into the repo root.
3. Download + extract the Topaz MSI (§2); build `topaz-models-min\`
   (`prob-4.json` + `tvai.tz` from the MSI `models` folder).
4. Optional but recommended: install Topaz Video once and sign in, so
   `auth.tpz` exists and output has **no watermark** (§3). The ffmpeg path
   works either way.
5. `python cut_for_upscale.py --seconds 10` → check the printed total is
   **646,461**.
6. Set the encoder for your GPU in `upscale_topaz.py` (`hevc_nvenc` +
   `device=0` on NVIDIA), render **one** segment, verify 600 frames at
   3840×2160, eyeball it.
7. `python upscale_topaz.py` for the full batch (resumable — rerun freely).
8. `python reassemble_upscaled.py --upscaled upscale_out --bed combined`
   (repeat per bed you want; video work is shared).

## 11. What is (and is not) in git

Committed: documentation, all pipeline/upscale scripts, batch/PowerShell
runners, probe sources (`topaz_probe*.c`), the pilot segment manifest.

Deliberately **not** committed (see `.gitignore`): all video/audio media,
the extracted Topaz app (1.15 GB, proprietary), the redistributable SDK,
downloaded `.tz3` model weights, probe executables, logs, and extracted
preview frames (adult imagery; this repo is public). Recreate binaries from
§2; models re-download free on first run.

## 12. File inventory for this stage

| File | Role |
|---|---|
| `cut_for_upscale.py` | keyframe-exact video-only segment cutter + manifest |
| `upscale_topaz.py` | resumable per-segment `tvai_up` batch runner w/ verification |
| `reassemble_upscaled.py` | frame-gated concat + audio-bed remux |
| `run_topaz_*.bat` | env setup + exact ffmpeg lines for every test/render |
| `run_*_babysit.ps1`, `guard_*.ps1` | detached launch + priority guard + progress log |
| `topaz_probe.c`, `topaz_probe2.c` | direct `tvai_*` C API probes (device/auth/model diagnostics) |
| `upscale_pilot\` | 6 pilot segments + `manifest.csv` (media ignored, manifest tracked) |
| `TOPAZ_4K_UPSCALE.md` | this runbook |
| `PIPELINE.md` §11 | how this stage plugs into the original build |

