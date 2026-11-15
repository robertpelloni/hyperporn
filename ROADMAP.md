# ROADMAP

## Done
- v8 sissy rebuild with SM trim sheets (`rebuild_v8_smtrims.py`, verified via `verify_trim_sheets.py`)
- Full creation pipeline documented (`PIPELINE.md`, `PROJECT_BRIEF.md`)
- Topaz 4K60 upscale stage defined (`TOPAZ_4K_UPSCALE.md`, `upscale_topaz.py`)
- Hypo v5 audio iteration (`hypo_mix_v5.m4a`, `build_hypo_v5.py`)

## Next
1. Finish `liveset60_v8` — `fade_chunk_01.mp4` is 0 bytes (stalled/failed); resume from `chunk_list.txt`
2. Lock v8: review `sm_trim_report_v8.json` against `framecheck/trimcheck/verify_v8.jpg`
3. Topaz 4K60 upscale of finished masters
4. Compress-to-2GB distribution variants (`compress_2gb_v6.py`)

## Submodule / layout map
- No submodules (no `.gitmodules`). Single-repo layout:
  - `intermediates/` — GOP26 intermediates, `sissy_parts5/`, concat lists
  - `liveset60_v8/`, `liveset60_strobe/` — liveset builds
  - `framecheck/` — intro/outro/spot/trimcheck verification frames
  - `topaz-extract/`, `topaz-redist/`, `topaz-models*/` — Topaz binaries/models (untracked, rebuilt from MSI)
  - `.hypernexus/` — agent memory/sessions (tracked); `catalog.db`, `hypernexus.db` — tracked
