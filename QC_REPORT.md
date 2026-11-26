# QC report (qc_check.py)

| File | Spec | Duration | Black <25 | Dark <48 | Mask fold | Flash rate |
|---|---|---:|---:|---:|---:|---:|
| ultramix_ep1_1080p60.mp4 | 1920x1080 @1537224/25621 512408f 18.6GB | 8540s | 4.6% | 20.0% | 0.17 | 2.31/s (ramped dip) |
| ultramix_ep2_1080p60.mp4 | 1920x1080 @30744480/512417 512408f 15.9GB | 8540s | 3.3% | 8.6% | 0.18 | 2.31/s (ramped dip) |
| ultramix_ep3_1080p60.mp4 | 1920x1080 @7051980/117529 470132f 17.8GB | 7836s | 3.2% | 8.0% | 0.18 | 2.31/s (ramped dip) |

Mask fold ~0.17-0.20 = dip locked every 26 frames (healthy);
~0.9 = drifting/absent mask (the original ep3 bug). Flash rate is
the mask dip frequency; depth is gradual (5-frame triangular ramp
to a 48/255 floor), not a hard on/off flash. A strobe-free export
variant is a ROADMAP item (ChatGPT fix #6).
