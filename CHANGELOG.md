# CHANGELOG

## 1.1.0 — 2026-11-07 — Repository sync & v8 pipeline consolidation
- Merged v8 sissy pipeline into `main`: `build_v8_full.py`, `mux_v8.py`,
  `rebuild_v8_smtrims.py`, `make_trim_sheets(2).py`, `probe_sm_trims.py`,
  `verify_trim_sheets.py`, plus `sm_trim_report_v8.json` and
  `framecheck/trimcheck/` verification sheets.
- Retired `intermediates/sissy_parts4/` (consumed into `sissy_all_gop26_v2.mp4`);
  current parts live in `intermediates/sissy_parts5/`.
- Policy: databases (`catalog.db`, `hypernexus.db`) and memory/sessions are now
  tracked; machine-local `.stfolder/` markers are ignored.
- Batch scripts (`run_topaz_*.bat`) verified — absolute paths match current layout.
- `backup/wip-leader-sync-20261107` reviewed: only a Syncthing marker, not merged.

## 1.0.0 — 2026-11-07 and earlier
- Full creation pipeline documented (`PIPELINE.md`, `PROJECT_BRIEF.md`).
- Topaz 4K60 upscale stage (`TOPAZ_4K_UPSCALE.md`, `upscale_topaz.py`).
- Hypo v5 audio builds, GOP26 intermediates, strobe/liveset-60fps tooling.
