# VISION

Hyperporn is a single-machine, frame-exact PMV construction
system: studio sissymaker sources and AI-generated PMVs are cut
into 26-frame clips on a 140 BPM grid, alternated, fused with a
triangular strobe mask, and married to continuous psytrance
beds. The identity is the mask and the grid - everything else
serves them.

Ultimate goal: a finished, verified, *finite* library of
long-form mixes at the highest quality this hardware (or one
rented GPU day) can honestly produce, where every deliverable
is frame-counted, timestamp-true, and reproducible from
documented stages - and where "done" is defined in advance,
not discovered after another enhancement tier appears.

Foundational concepts:
- Frame-exactness over convenience (`-frames:v 26`, GOP 26,
  verify `nb_frames`; never `-t` cutting).
- The mask is applied in RGB, period 26, floor 48/255, and its
  health is a measurable number (fold ratio ~0.18), not a vibe.
- Quality claims require measurements (VMAF, fold, luma),
  and cost claims require benchmarks on this machine.
- Sources are cataloged (hash + trims) before processing;
  duplicates are verified perceptually, never by name/length.
- Adult material is processed locally and numerically; the
  public repo carries code and docs, never media or frames.

User-satisfaction design: deliverables play start-to-finish
without black flashes, drift, or timestamp lies; every file's
composition is documented; remaining work is always listed
with honest time estimates instead of optimism.
