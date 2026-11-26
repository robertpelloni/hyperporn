# Roast synthesis & fix status (2026-11-26)

Roasts harvested via Edge CDP :9222, identity
"[muse-wonder-1.0 in Muse Code in G:\hyperporn on laptop]",
marker `HPN-ROAST-1126`. ChatGPT: full roast captured.
Gemini: full roast captured. muse.ai (Bobbi): prompt posted,
reply still pending at writing (thread interleaves projects;
harvest later from the same marker).

## ChatGPT - "KEEP the project. KILL the uncontrolled optimization loop."
| # | Fix | Status |
|---|---|---|
| 1 | A/B test before multi-week queues | DONE - `AB_TEST.md` (VMAF 77.8 x2 vs 43.3 max vs lanczos ref, caveat recorded); decision gate in ROADMAP |
| 2 | One manifest pipeline, archive 40 scripts | DONE (archive) - 76 scripts to `archive/scripts/`, 15 canonical left; manifest driver = ROADMAP next |
| 3 | Content-addressed resumable cache | PARTIAL - segment/clips already hash-named + frame-verified skips; true content-hash cache = ROADMAP |
| 4 | Correct beat sync (not fixed 26f) | ELEVATED by Gemini measurement (below) |
| 5 | Automated tests | DONE - `tests/test_pipeline.py`, 5 passing |
| 6 | Flash-safety assessment + safer variant | MEASURED - `QC_REPORT.md` (fold, black%, 2.31 Hz ramped dip); strobe-free variant = TODO |
| 7 | Storage manifest, no hardcoded drives | DONE - `STORAGE.md`, `DEPLOY.md` |
| 8 | Resolve git lock ownership | OPEN - holder is external (IDE git pollers); per policy not killed; temp-index until it clears, then `git reset --mixed HEAD` |
| 9 | Objective/visual QC reports | DONE - `qc_check.py`/`QC_REPORT.md` |
| 10 | Archive obsolete + define DONE | DONE - archive + Definition of DONE in ROADMAP |

## Gemini - "multi-week Pascal GPU torture chamber"
| # | Fix | Status |
|---|---|---|
| 1 | Stop 4x supersampling full sources; 2x on scene-safe segments | GATE RECORDED - max queue continues per user directive + AB_TEST caveat; segment-only processing already the design (10 s scene-safe segments; PMV internal cuts are within segments, interpolation is per-segment so flow never crosses segment joins, though it can cross cuts *inside* a segment - noted) |
| 2 | **140 BPM phase drift**: 26f = 138.46 BPM; use Bresenham [26,26,25,...] | **VERIFIED REAL, WORSE**: measured beds are NOT 140 - Ajja ~146-147 BPM, AutoDJ ~138-143 varying (`bpm` autocorrelation estimates, 3 windows each, 2026-11-26). The 26f grid was never kick-locked to either bed. Bresenham helps only against a bed warped/measured to a fixed tempo. Proper fix = per-section tempo measurement + frame-accumulator boundaries on the NEXT episode build; finished episodes would need a rebuild to change (user decision, TODO). |
| 3 | Pre-bake atoms, assemble by concat copy | ALREADY the episode design (26f atoms -> chunk concat -> fade); finals are not re-rendered per mix |
| 4 | Kill index.lock squatter in 60 s | NOT DONE by policy - no killing unknown processes; see ChatGPT #8 |
| 5 | 1 CLI + manifest, archive rest | archive DONE; CLI = ROADMAP |
| 6 | Preflight junction/drive guard + real QA | DONE - `preflight.py` (drives/junctions/space/binaries/pools), QC probes in `qc_check.py`; freezedetect/blackdetect sweeps = TODO extension |
| 7 | VRAM guard around GPU queue | DONE - `vram_wait()` in `upscale_max.py` (backs off below 900 MiB free) |

## What the roasts got wrong / overstated
- "Upscaling intros/dead air that gets cut": trims happen
  before intermediates in episode builds, but the *libraries*
  do upscale full sources on purpose (per-clip deliverables).
- "Re-encoding identical clips dozens of times": atoms are
  cut once per build; libraries and episodes are separate
  deliverables, not the same render repeated.
- Gemini's 5m13s drift figure assumes a true 140.00 bed for
  7.92 h; measured beds aren't 140, so the real statement is
  stronger and messier: cuts were never beat-locked at all.

RESOLVED 2026-11-26: .git/index.lock was a stale 0-byte file from 2026-11-23 23:46 (proven unheld by exclusive-open test, user confirmed nothing running). Renamed to .git/index.lock.stale-20261126, git reset --mixed HEAD resynced the main index, status clean. Temp-index commits retired; normal git flow restored (ChatGPT #8 / Gemini #4 DONE).
