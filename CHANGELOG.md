# CHANGELOG

## 1.2.0 — 2026-11-23 — Catch-up, new-video catalog/rename, v9 extension
- Reviewed prior Muse sessions plus Antigravity session `5d99ed74` and both
  checkouts (`G:\hyperporn`, `~/workspace/hyperporn`); see
  `CATCHUP_2026-11-23.md`. Fast-forwarded G to `origin/main` (`0e1d2e0`).
- Upscaling corrected: Topaz 4K60 was never run on a full master
  (watermarked, ~42 d on GTX 1060); the settled free path is Real-ESRGAN
  (A/B verified, no watermark, ~110 d at 4K — 1080p/chunks only).
- 15 videos added 2026-11-19/20 cataloged (`NEW_VIDEOS.md`,
  `new_videos.json`, `catalog_new_videos.py`) and renamed to `ext01..ext15.mp4`.
- `build_v9_extend.py`: prior processes applied to the new PMVs (720p60,
  GOP 26, strobe mask, own audio AAC 192k) and appended to the v8 master
  → `hyperporn_v9_extended.mp4` (media git-ignored, local only).
- `.gitignore`: `tools/` (downloaded ffmpeg) now ignored.

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
