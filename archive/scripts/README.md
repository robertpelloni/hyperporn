# Archived scripts (2026-11-26, nondestructive)

76 one-off/iterated scripts moved here from the repo root during
the ChatGPT-roast cleanup (fix #2/#10). Nothing was deleted; git
history also preserves every version. They are grouped by era:

- `rebuild_v2..v6`, `rebuild_alt*`, `rebuild_final/fixed/rg/nohyp`,
  `regenerate_masterpiece`, `finish_v4`, `remix_hyp`, `remux_*`,
  `compress_2gb*`, `launch_remux` — superseded master-build
  iterations. Canonical now: `build_v8_full.py` + `mux_v8*.py`
  (v8), `build_v9_extend.py` (v9), `build_episodes.py` /
  `build_episode3.py` (ultramix).
- `fade_*`, `fades_parallel`, `strobe_*`, `test_*fade/geq/oneshot`,
  `freeze_test`, `audit_freeze`, `check_*`, `grab_*`, `scan_*`,
  `probe_*` (except canonical probes in the builders) — the
  fade/strobe/GOP26 experiments that produced the hard rules in
  `PIPELINE.md` sections 5-6. Their findings live on in the docs;
  the scripts are reference only.
- `detect_intros/outros`, `make_trim_sheets*`, `verify_trim_sheets`
  (root copies) — v1 trim detection. Canonical: `detect_trims_v2.py`.
- `beat_mashup*`, `build_combined`, `build_hypo_v5`, `mux_14beats`,
  `mux_strobe`, `liveset_60fps`, `find_longest_ajja`, `write_remix`
  — audio-bed and early liveset experiments (see `PIPELINE.md` 4).
- `cdp_*`, `parse_pi` — Edge CDP coordination probes from the
  Nov 2026 sessions; current coordination uses TEMP scripts per
  session against `localhost:9222` (see `HANDOFF.md`).

If a canonical builder ever needs a flag or trick from here,
copy the snippet forward — do not resurrect whole files.
