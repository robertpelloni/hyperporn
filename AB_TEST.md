# A/B: is the maximal tier worth it? (ChatGPT roast fix #1)

Sample: `sm4.mp4` (720p30, 171 s), 20 s window at 60 s.
Reference for VMAF: source scaled lanczos to 1920x1080, fps=60
(duplication) — i.e. "do almost nothing" at the same spec.

| Version | VMAF vs lanczos ref | Encode cost (measured) |
|---|---:|---|
| `_up1080` (ESRGAN x2 -> 1080, dup 60) | **77.77** | ~2.3 min per 10 s segment |
| `_max1080` (ESRGAN x4 -> down 1080, interpolated 60) | **43.35** | ~15-19 min per 10 s segment |

Caveat (important): VMAF compares against a *duplicated-frame*
reference, so interpolated in-between frames are penalized for
differing temporally even when they look smoother to a viewer.
43.35 therefore does NOT prove the max tier looks worse; it
proves it diverges far more from the cheap version while
costing ~7x more per segment.

Decision gate (recorded in ROADMAP): the max queue continues
(it was an explicit user directive and its motion is the one
thing the x2 tier cannot do), but any *future* tier change
requires a fairer test first: VMAF-motion + a no-reference
sharpness metric on at least 3 content types, or a rented-GPU
trial. No new enhancement stage gets a multi-week queue on
extrapolation alone again.
