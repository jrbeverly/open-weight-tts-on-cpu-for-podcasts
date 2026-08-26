# Personas

Two speakers, deliberately **not** treated the same way. The female voice can carry emotional
inflection and the male voice cannot. Running one house style across both is what produced the flat,
robotic delivery that took five rounds to diagnose.

Everything on this page is settled. Change it only with a listening test that says otherwise.

---

## The expert — `af_heart`

Carries the explanations and about 75% of the words. The stronger voice always gets the explaining job;
the reverse arrangement was tried and is audibly worse.

### Audio settings — locked

| | |
|---|---|
| voice | `af_heart` (Kokoro-82M) |
| pitch | **none.** Never shift this voice |
| high pass | 80 Hz |
| de-ess | `deesser=i=0.30:m=0.5:f=0.5` |
| EQ | &minus;2.5 dB @ 320 Hz (Q 1.2) · +2.5 dB @ 3.2 kHz (Q 0.9) · +2 dB shelf @ 9 kHz |
| compression | `acompressor=threshold=-20dB:ratio=2:attack=15:release=250:makeup=1` |
| chorus | `chorus=0.8:0.9:2:0.15:0.12:1.0` — the **2 ms** setting. Not 3 ms, not 12 ms |
| room | `aecho=1:0.88:13|21:0.04|0.025` — short and close |
| flat-span treatment | **off.** She does not need it and it makes her worse |

Order matters. The chain is exactly:

```
highpass 80 → de-ess → EQ 320 → EQ 3.2k → shelf 9k → compressor → chorus 2ms → room (close)
```

The chorus is the one setting arrived at by ear rather than measurement. It does not make her sound
more human; it makes her more pleasant to listen to. 12 ms was audible as doubling, 2 ms is not.

### Writing rules — permissive

She can carry meaning in delivery, so the writing does not have to defend against her.

- **Fillers are wanted**, not tolerated: *you know*, *I mean*, *look*, *so*, *though*, *yeah*.
  Roughly one every two or three turns. More than that reads as padding.
- **Short reactions are safe.** *"Yeah, no problem."* lands.
- **Understatement is safe.** *"It usually isn't."* lands.
- **Fragments for emphasis are safe.** *"Who issues it. How long it lives."*
- She measures flat on roughly **21% of phrases** and it does not matter, because she has the range to
  carry them. Do not treat those spans and do not rewrite around them.

---

## The host — `am_michael`

Asks, frames, and hands over. About 25% of the words. He is the weaker voice, which is precisely why he
gets the smaller job.

### Audio settings — locked

| | |
|---|---|
| voice | `am_michael` (Kokoro-82M) |
| pitch | **none.** Never shift this voice |
| high pass | 110 Hz — thinner than the expert, deliberately |
| EQ | &minus;2 dB @ 300 Hz (Q 1.2) · +1.5 dB @ 4 kHz (Q 1.0) |
| de-ess | `deesser=i=0.30:m=0.5:f=0.5` |
| room | `aecho=1:0.86:29|43:0.07|0.05` — longer and further back |
| compression | none |
| chorus | none |
| flat-span treatment | **on** |

The different high pass and the longer room are not cosmetic. They are what make the two speakers read
as two microphones in one space rather than one voice with two settings. Voice separation now rests
entirely on tone, position and writing, because pitch shifting is forbidden.

### Flat-span treatment

`flatness.py` splits each prepared host turn on silence and measures the 10th-to-90th-percentile pitch
range of every phrase. Anything under **5.0 semitones** reads as robotic. Each such span gets:

- **+2.5 dB** level, plus a matching **+2 dB at 2.8 kHz** presence bump
- **250 ms** of silence inserted immediately before it

Nothing touches pitch. This adds **weight and timing, not inflection** — the measured flatness barely
moves. It is a safety net for lines the writing failed to save, not a fix in its own right. Slowing the
span was tried and made the measurement slightly worse.

The renderer logs every span it treats, with the turn number, timestamp and measured range, so you can
always see what it changed.

### Writing rules — restrictive

This is where most of the quality comes from. He cannot put emotional weight into a statement, so the
writing must make the meaning explicit and never depend on tone.

1. **Prefer questions.** Interrogatives measured **10.20 semitones** of pitch movement against **4.25**
   for a bare declarative. This is the single most effective rule in the whole system.
2. **No bare evaluative fragments.** Never *"That sounds worse."* or *"That's a good one."* Attach an
   explicit stance clause: *"Because on the face of it, that looks like a straight downgrade."*
3. **No understatement or irony.** Say it outright. The delivery will not imply anything.
4. **Contrast by repeating structure**, never by stressing a word. *"The question is rarely X. The
   question is Y."*
5. **Never end a turn on a short declarative.** That position is where flatness concentrates.
6. **No lists of fragments.** *"Start at the edge. Identity in the certificate. Log the handshake."*
   becomes one sentence with grammatical momentum.
7. **Fillers are riskier here.** One mid-sentence is fine. Never open a turn with one.

Applying these took him from flat on most turns to **1 of 28 phrases below 5.0 semitones (4%)**,
against 21% for the expert under permissive rules. That one survivor is caught by the treatment above.

---

## Programme level

The room-tone bed belongs to the whole episode, never to a voice. Per-turn it would breathe in and out
with the speakers, which is worse than having none.

| | |
|---|---|
| bed | `anoisesrc=c=pink:a=0.003`, band limited 120 Hz to 7 kHz |
| level | about &minus;69 dBFS in the gaps |
| mix | `amix=inputs=2:duration=first:normalize=0` — **normalize must be off** or the voice drops 6 dB |
| loudness | one measured static gain to &minus;16 LUFS |
| ceiling | `alimiter=limit=0.75:level=false` |
| result | about &minus;17 LUFS and &minus;1.1 dBTP |
| never | `loudnorm` as a mastering stage |

The bed sits low deliberately, leaving headroom for background music to be added later.

---

## Why these voices

| | |
|---|---|
| `af_heart` + `am_michael` | 8.35 semitones apart. No separation work needed |
| `af_heart` + `Tiffany` (Polly) | 0.8 semitones apart. Both strong, but they blur together |
| Polly `Brian`, `Matthew`, `Patrick` | rejected on listening |
| Polly `Gregory` | workable, not chosen |

Pairing a male with a female sidesteps the separation problem rather than solving it, and is the
cheaper answer. Both chosen voices are Kokoro, so nothing in the audio path touches AWS.
