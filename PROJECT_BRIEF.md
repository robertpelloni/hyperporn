# Hyperporn — Art, Strategy, Hosting & Fair-Use Brief
_A working document for the project. Analysis/advice only — not legal advice. Consolidates the_
_four threads: artistic direction, strategy, hosting, and fair-use/remix status._

**Date:** 2026-10-25 · **Media:** `ハイパーポルノ_*` mashup (140 BPM strobe, 60 fps, 720p)

---

## 1. Artistic direction

**The identity is the mask.** The triangular-dip white/black mask welded two unlike source bodies
into one hypnotic rave texture. That's the brand — protect and develop it.

**Forks to decide:**
- **Music-video vs. guided-erotic.** Post-hypnoshit it reads as pure visual music. Argue for the
  music-driven identity: more coherent as art, no voice fighting the rhythm.
- **3-hour "live set" vs. 35-min "radio edit."** Argue for *both*: the 3h as the endurance/loop
  format, a tight ~35-min structured cut as the flagship.

**Develop the craft:**
- **Musical structure → edit structure.** Map the psytrance arrangement (intro/build/drop/
  breakdown/outro) to edit intensity: hold 2–4 bars on strong scenes at breakdowns, frenetic on
  drops. Relentless 26-frame chopping should be the *default texture*, not the only texture.
- **Mask vocabulary.** Evolve 3–4 mask treatments over the runtime (triangular dip, trapezoid,
  chromatic-channel offset, per-source masks) so a 3h piece has visual chapters.
- **Source intercutting as motif.** Studio (A) vs AI wetdream (B) is thematically loaded (authentic
  vs synthetic). Accelerate A/B intercutting into drops; hold single-source on breakdowns.
- **Unify the grade.** Cool cyan/magenta rave palette across both sources to force coherence.
- **Thematic through-line.** Trance / surrender / loop / hypnagogia. The strobe + repetition is
  thematically apt — lean in rather than hide it.
- **Audio.** Clean psytrance now. Optional: a low sub-pulse / ambient bed for immersion without
  re-introducing a "guided" voice. Or keep it pure. (Direction choice.)
- **Credits / ethos.** If it ever leaves your drive: tasteful credit to performers + sources is
  artistic integrity *and* basic respect for the people on screen.

---

## 2. Strategic options (goal-dependent)

Strategy hinges on the goal — they diverge completely:

| Goal | Strategy | Risk |
|------|----------|------|
| Personal enjoyment | Done. Optimize for loop-ability, add the foley/ambience layer you mentioned. | None |
| Artistic recognition | Reframe as critical/essay work; submit to remix/net-art/adult-art contexts. | Medium (rights) |
| Audience-building | Series branding (the JP title is strong), consistency, platform selection. | Copyright is the ceiling |
| Monetization | Highest legal exposure, lowest defensibility. **Recommend against without rights.** | High |

**Highest-leverage play: the transformative reframe.** Add a genuine critical/narrative layer that
*comments on* the material (an essay on hypnotic media, trance states, AI vs filmed porn aesthetics).
This (a) makes it a real art piece, and (b) is the only route to a defensible fair-use posture. It
changes the work — that's the point.

**Licensing play.** Approach the rightsholders (Sissymaker / Wet Dreams). Some studios have fan/
remix policies or will license clips. Even one or two licensed key sources can anchor the piece.

---

## 3. Hosting analysis

| Option | Trade-off |
|---|---|
| **Local / NAS (personal)** | Best for private use. Zero exposure. Use Jellyfin/Plex. |
| Semi-private (unlisted/password self-host) | Reduces "distribution" optics; **does not fix infringement**. |
| Adult-friendly hosts/CDNs | Built for adult media; still require you to hold rights; DMCA applies. |
| Mainstream cloud (S3/GCS/Azure/CF-R2) | Often prohibit adult + infringing content; termination risk. (R2 zero-egress is technically attractive but policy-problematic.) |
| Offshore / "DMCA-proof" | Jurisdictional theater; US-facing takedowns still land. |
| P2P/IPFS | Censorship-resistant; no safe harbor; content still infringing. |

**Honest core:** hosting location does **not** cure the copyright problem. If it infringes, every
host is a takedown target and liability is yours. The *uploader/rightsholder relationship* is the
real variable, not the server.

**Technical notes:** the 18×600 s chunks are already well-formed for HLS segmentation (faststart,
keyframe-aligned). For public delivery you'd want an HLS playlist + adaptive bitrate ladder; current
video ≈1.2 Mbps. 3h set + chunks ≈ 19 GB storage + real egress cost.

---

## 4. Fair use / remix status — honest verdict

**Steelman (your side):** mashups can be transformative; the strobe/mask creates new aesthetic
meaning; non-commercial; no one watches it *instead of* the originals.

**Four factors:**
1. **Purpose/character** — transformative in *technique*, but courts ask for new *meaning/message*.
   A porn mashup that stays porn, for arousal, is same-purpose → weak. Non-commercial helps.
2. **Nature** — published, highly creative films → strong protection. Against.
3. **Amount** — uses essentially the *entire* sources (chopped, but comprehensive) incl. their
   core. Strongly against.
4. **Market effect** — a free full-length mashup substitutes for buying/licensing and harms the
   clip-licensing market. Against.

**Counter to the steelman:** *Warhol v. Goldsmith* (2023) narrowed transformativeness — re-styling
for the *same purpose* isn't transformative. A porn remix for arousal is same-purpose. *Google v.
Oracle* is distinguishable (functional/API context).

**Bottom line:** as it stands this is a **weak fair-use case**. "Completely derivative" is the
hallmark of a work needing a license. Fair use is an *affirmative defense* — you only win it by
being sued and prevailing. DMCA safe harbor protects *hosts* who honor takedowns, not the uploader.
US publication adds **§2257** record-keeping (performer age/consent) exposure.

**Defensible paths:** (a) license/permission, (b) genuine critical/parody reframe, (c) build from
owned/CC adult content, (d) keep private. — _Consult an IP attorney for anything public._

---

## 5. Next actions (owner split)

**I can do (local / analysis):**
- Build the 35-min "radio edit" art cut from the sources (present in the workspace) per §1.
- Apply the mask-vocabulary / color-grade experiments.
- Package the chunks as HLS (playlist + ladder) for smooth playback.
- Draft the transformative-reframe outline (voiceover/narrative script).
- Audio-bed variants (foley/ambience layer, sub-pulse).

**Yours (I hand back the wheel):**
- Any actual publishing / platform operation / upload automation (X, WordPress, muse.ai, tube sites).
- Rights clearance and legal decisions.
