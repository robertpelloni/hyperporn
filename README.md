# hyperporn

A video-processing pipeline workspace: Python/ffmpeg tooling that cuts,
grades, and assembles long-form beat-synced music videos from source
clips — 140 BPM psytrance audio, 26-frame strobe cuts, 60 fps output,
with a Topaz Video AI 4K upscale stage. The finished piece is a ~3-hour
"live set" cut (plus a planned ~35-minute edit). This repo holds the
pipeline scripts and documentation only; video files are excluded.

**Version:** 1.1.0

## Pipeline

```
source clips → trim detection → strobe/fade cutting → mux → 60 fps
conversion → Topaz 4K upscale → reassembly → final render
```

- **Trim/cut** — `detect_intros.py`, `detect_outros.py`,
  `probe_sm_trims.py`, `make_trim_sheets.py` — intro/outro detection
  and trim sheets
- **Cutting** — `rebuild_v2.py`–`rebuild_v8_smtrims.py`,
  `regenerate_masterpiece.py` — successive rebuild versions of the
  full edit; `strobe_*.py` — strobe-cut variants and 60 fps
  conversion (`liveset_60fps.py`, `strobe_fast_60fps.py`)
- **Fades** — `fade_*.py`, `fades_parallel.py` — fade/blend variant
  testing and fixes
- **Audio** — `beat_mashup.py`, `beat_mashup_variants.py` — beat-matched
  audio assembly; `mux_*.py` — audio/video muxing
- **Upscale** — `upscale_topaz.py`, `cut_for_upscale.py`,
  `reassemble_upscaled.py`, `TOPAZ_4K_UPSCALE.md` — Topaz 4K60
  upscale stage (chunked, with babysitter scripts for long runs)
- **Checks** — `check_black*.py`, `check_clipframes.py`,
  `audit_freeze.py` — black-frame, freeze, and GOP checks
- **Docs** — `PIPELINE.md` (full creation pipeline),
  `PROJECT_BRIEF.md` (artistic direction, hosting, and rights
  analysis), `TOPAZ_4K_UPSCALE.md`

## Rights note

The project's own brief (`PROJECT_BRIEF.md`) is explicit: the source
material is third-party, the fair-use case for the finished piece is
weak, and public distribution would need licenses or a genuine
transformative reframe. This repo contains no video — only the
tooling and the analysis.

## Status

Active workspace, v1.1.0 (last commit 2026-11-07, staging the v8
pipeline). Single-developer project; the pipeline is iterated by
versioned rebuild scripts rather than a single stable tool.
