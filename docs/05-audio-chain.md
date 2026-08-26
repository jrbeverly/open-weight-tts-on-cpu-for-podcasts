# The audio chain

Every stage, in order, with the reason it exists. Settings live in `render.py`; this explains them.

```
Kokoro 24 kHz WAV
   ↓  trim edges, 8 ms fade in
   ↓  persona chain          (different per speaker — see 02-personas.md)
   ↓  pad with the inter-turn gap
   ↓  flat-span treatment    (host only)
   ↓
concat all turns
   ↓  one static gain to -16 LUFS
   ↓  pink room-tone bed mixed under the whole programme
   ↓  alimiter at 0.75
   ↓  encode 192 kbps mono 24 kHz
episode.mp3
```

## Per-turn preparation

```
silenceremove(start, -60dB, keep 150ms) → areverse → silenceremove → areverse
→ afade=t=in:d=0.008 → [persona chain] → apad=pad_dur=<gap>
```

**Edge trimming** keeps 150 ms rather than cutting to the waveform. An aggressive trim clips word
onsets and leaves hard cuts that click at the joins. Kokoro already ships about 300 ms of leading and
250 ms of trailing silence, which is close to the gap you want anyway.

**The 8 ms fade** exists solely to stop the join clicking.

## Mastering

**One measured static gain, then a limiter.** Never `loudnorm` as a mastering stage.

This is the single most important thing on this page. `loudnorm` silently ignores `linear=true` and
falls back to `Normalization Type: Dynamic` whenever the required gain would breach the true-peak
ceiling. Synthesized speech sits near &minus;24 LUFS, so reaching &minus;16 needs about +8 dB and it
**always** fell back. Dynamic mode gain-rides the entire programme: measured against the raw clip it
added **+8.7 dB at 100 Hz** and **+3 dB in the sibilance band**, and it pumps audibly in the gaps
between turns.

The replacement measures integrated loudness once, applies a single constant `volume` gain, and catches
peaks with a limiter. Same &minus;16.6 LUFS, none of the damage.

**Limiter ceiling is 0.75, not 0.89.** MP3 encoding adds roughly 1.4 dB of inter-sample overshoot on
dense material. At 0.89 the episodes decoded at a peak of **1.002** — actual clipping. At 0.75 they land
at &minus;0.8 to &minus;1.1 dBTP, inside podcast spec.

Measured loudness comes out about &minus;17 LUFS, roughly 1 LU under target, because the limiter works
after the gain is calculated. It is consistent between episodes and platforms normalise anyway.

## The room-tone bed

`anoisesrc=c=pink:a=0.003`, band limited 120 Hz to 7 kHz, mixed under the **whole programme**.

Per-turn it would breathe in and out with the speakers, which is worse than having none at all.

`amix=inputs=2:duration=first:normalize=0` — **normalize must be off.** With it on, `amix` scales each
input by 1/n and the voice drops 6 dB, which quietly ruins any A/B against a version without the bed.

The bed lands around &minus;69 dBFS in the gaps. That is 6 dB below the first version tried, left low
deliberately so background music can be added underneath later.

## Source format

Kokoro outputs 24 kHz. That is the hard ceiling: **nothing exists above 12 kHz**, so presence must be
built at 3-4 kHz and "air" shelves do very little.

Intermediates are `pcm_s16le` WAV so there is exactly one lossy encode, at the end, at 192 kbps.

For embedding in a web page, re-encode to 80 kbps — on 24 kHz mono that is transparent against the
source and roughly a third of the size.

## Flat-span treatment (host only)

`flatness.py` splits a prepared turn on silence, then measures the 10th-to-90th-percentile pitch range
of each phrase by autocorrelation. Under **5.0 semitones** reads as robotic.

Each flagged span gets **+2.5 dB**, a **+2 dB bump at 2.8 kHz**, and **250 ms of silence in front**. The
turn is rebuilt by cutting it into pieces and concatenating, so only the flagged span is touched.

**This adds weight and timing, not inflection.** Measured, the flatness barely moves: 4.25 → 4.20
semitones with everything applied. Nothing in the chain touches pitch, so nothing in the chain can add
contour. It is a safety net; the writing does the real work.

## Rejected

| approach | why |
|---|---|
| pitch shifting for voice separation | `rubberband` at ±1.4 semitones is audible on speech even with `formant=preserved`. Moved the metric 0.8 → 3.36 semitones and made both voices worse |
| slowing a flat span | 4.25 → 3.83 semitones. Slightly worse, and audibly so |
| Haas stereo widening | at `side_gain` 0.12 the mono downmix peaked at 1.15. Clips on any player that sums to mono |
| `loudnorm` mastering | see above |
| heavy EQ curves | barely distinguishable from flat in listening tests. Small lever, not worth effort |
| explicit `<break>` pauses in the script | rejected on listening; introduced more problems than they solved |
| shortening sentences for pacing | same |

## Settings that came from the ear, not the meter

Almost everything here was decided by measurement. Two things were not, and should be changed only by
listening:

- **The 2 ms chorus on the expert.** It does not make her more human. It makes her more pleasant.
- **The room-tone bed.** It masks the digital sterility of a perfectly silent gap.
