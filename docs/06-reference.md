# Complete reference

Everything determined while building this, including the dead ends. If you are an AI picking this up
cold, reading this document and `03-authoring-a-script.md` is enough to work on the system without
rediscovering any of it.

Written after six rounds of listening tests. Every claim below is either a measurement or a recorded
human listening judgement, and the two are labelled differently on purpose, because several times the
measurement and the ear disagreed and **the ear won every time**.

---

## 1. Orientation

The system turns a technical write-up into a 3-4 minute two-voice audio explainer. It runs entirely
locally on CPU with Kokoro-82M. It creates no cloud resources.

| file | what it is |
|---|---|
| `script.json` | the current episode's dialogue |
| `render.py` | synthesis, per-persona processing, flat-span treatment, mastering |
| `lint.py` | checks a script against the writing rules, no model needed |
| `flatness.py` | measures per-phrase pitch range; imported by the renderer |
| `docs/` | this documentation |

```
python3 lint.py script.json
.venv/bin/python render.py script.json
```

---

## 2. How the current design was reached

Six rounds, each driven by a human listening and reporting.

**Round 1 — Polly baseline.** Five variants on Amazon Polly generative, neural and long-form. Verdict:
*all five sound terrible, immediately.* This was the most useful single piece of feedback in the
project, because it forced measurement rather than more variants.

**Round 2 — diagnosis.** Two real defects found by measurement, not taste: `loudnorm` was gain-riding
the programme, and the source codec was the wrong one. Fixing those was the largest quality jump in
the whole project. Also established that Polly offers only three English generative males.

**Round 3 — voice selection.** Of five Polly males, four were rejected outright on listening.
`Brian` was the strongest candidate *on paper* — the only new English male in the same March 2026
expressive batch as `Tiffany` — and was rejected as "absolutely terrible". Paper reasoning about voices
is worthless.

**Round 4 — open weights.** Kokoro-82M introduced. `am_michael` and `af_heart` both beat every Polly
male. The two-female pairing was tested and the similar-pitch problem surfaced.

**Round 5 — the flat line.** The human identified that "That sounds worse" sounded robotic. This was
measurable, and the investigation produced the single most important finding in the system: **writing
that depends on emotional inflection fails, and no amount of post-processing fixes it.**

**Round 6 — personas.** The two speakers stopped sharing a house style. Different chains, different
writing rules, flat-span treatment on the male only.

---

## 3. The central finding

**The male voice cannot carry emotional inflection. The female can. Therefore they need different
writing, not just different EQ.**

Everything else follows from this. The evidence:

| phrase | pitch range | verdict |
|---|---|---|
| "And passthrough?" (question) | 10.20 st | moving |
| "If the load balancer isn't checking anything…" | 7.45 st | moving |
| **"That sounds worse."** | **4.25 st** | **flat** |
| "Because on the face of it, that looks like a straight downgrade." | 5.99 st | moving |

Under permissive writing the male was flat on most turns. Under restrictive writing he is flat on
**1 phrase in 28 (4%)**. The female, under permissive writing, is flat on **9 in 42 (21%)** and it does
not matter, because she has the range to carry those phrases.

Pitch range is measured as the 10th-to-90th-percentile spread of the autocorrelation pitch track, per
phrase, where phrases are split on silence. Under 5.0 semitones reads as robotic.

**Why it happens structurally:** each turn is synthesized with no knowledge of its neighbours, so every
turn starts cold. Turn-final short declaratives are where flatness concentrates — which is exactly
where reaction lines get written.

---

## 4. What post-processing can and cannot do

Tried on the same flat span, measured:

| treatment | 4.25 st becomes | verdict |
|---|---|---|
| slow to 90% (tempo only) | 3.83 st | worse. Rejected on listening too |
| +2.5 dB level and presence bump | unchanged | **works on listening.** Adds weight |
| 250 ms pause before | unchanged | **works on listening.** Adds timing |
| all combined | 4.20 st | unchanged |
| **rewrite the line** | **5.99 st** | **works** |

**Nothing in the audio chain touches pitch, so nothing in the audio chain can add inflection.** Level
and timing read as emphasis, which is a real and useful effect, but a different one. The shipped
treatment is +2.5 dB plus a 250 ms pause, applied only to the male, as a safety net for lines the
writing failed to save.

---

## 5. Mastering

### The loudnorm trap

`loudnorm` silently ignores `linear=true` and falls back to `Normalization Type: Dynamic` whenever the
required gain would breach the true-peak ceiling. Synthesized speech sits near &minus;24 LUFS, so
reaching &minus;16 needs about +8 dB and it **always** fell back.

Measured damage against the raw clip: **+8.7 dB at 100 Hz** (mud) and **+3 dB in the sibilance band**
(harshness), plus audible pumping in the gaps.

Replacement: measure integrated loudness once, apply one constant `volume` gain, catch peaks with
`alimiter`. Same loudness, none of the damage.

### Limiter ceiling

MP3 adds roughly **1.4 dB of inter-sample overshoot** on dense material.

| ceiling | result |
|---|---|
| 0.89 | decoded peak **1.002** — actual clipping |
| 0.82 | &minus;0.2 to &minus;0.3 dBTP — hotter than podcast spec |
| **0.75** | &minus;0.8 to &minus;1.1 dBTP — correct |

Final loudness lands about &minus;17 LUFS, roughly 1 LU under target, because the limiter works after
the gain is calculated. Consistent between episodes; platforms normalise anyway.

### Room tone

`anoisesrc=c=pink:a=0.003`, band limited 120 Hz to 7 kHz, about &minus;69 dBFS in the gaps, mixed under
the **whole programme**. Per-turn it breathes in and out with the speakers.

`amix=inputs=2:duration=first:normalize=0` — **normalize must be off.** With it on, `amix` scales each
input by 1/n and the voice drops 6 dB, which silently invalidates any A/B against a version without the
bed. This bug produced a variant 5.8 dB quiet before it was caught.

Also watch `aecho` output gain: at `out_gain=0.35` the makeup needed jumped to **+19.7 dB**, which would
have slammed the limiter. Use `aecho=1:0.9:...`.

---

## 6. The voices

### Chosen

| | `af_heart` | `am_michael` |
|---|---|---|
| role | expert, ~75% of words | host, ~25% |
| median F0 | 200 Hz | 131 Hz |
| separation | 8.35 semitones apart — no work needed | |
| pace | — | 138 wpm on a fixed 26-word line |

### Pitch separation, measured

| pair | separation |
|---|---|
| `am_michael` + `af_heart` | 8.35 st |
| `am_michael` + `Tiffany` | 5.14 st |
| **`af_heart` + `Tiffany`** | **0.8 st** |

Two same-gender voices 0.8 semitones apart are genuinely hard to tell apart — confirmed in the most
direct way possible, when the human evaluating them attributed a set of Tiffany clips to `af_heart`.
Pairing a male with a female sidesteps the problem instead of solving it, and is the cheaper answer.

### Rejected, all on listening

| voice | engine | verdict |
|---|---|---|
| `Brian` | Polly generative en-GB | "absolutely terrible", despite being the strongest paper candidate |
| `Matthew` | Polly generative | "terrible, complete removal" |
| `Patrick` | Polly long-form | "a no-go" |
| `Gregory` | Polly long-form | workable, not chosen |
| `Stephen` | Polly generative | usable but grates |
| `bm_george` | Kokoro | good as an asker; not chosen once `am_michael` won |

### Polly pace on identical text (26 words)

Brian 120 wpm · Patrick 139 · Gregory 143 · Stephen 158 · Matthew 174. A 45% spread.

---

## 7. Kokoro-82M

| | |
|---|---|
| licence | Apache 2.0 |
| size | about 330 MB |
| output | 24 kHz, mono |
| speed | RTF ~0.55 on 4 CPU cores, no GPU. A 3-4 min episode is ~90 s |
| voices | `af_*` 11, `am_*` 9, `bf_*` 4, `bm_*` 4 |

**Brightness varies enormously by voice.** At 11 kHz against 1 kHz: `am_michael` &minus;17 dB,
`bm_george` &minus;60 dB — almost no top end at all. Per-voice EQ is not optional.

**The G2P front end is the fragile part, not the model.** `misaki` calls `spacy.cli.download`, which
shells out to `pip` without `--break-system-packages`. On a Debian-managed Python that fails at
*synthesis* time with `externally-managed-environment` and produces **no audio and no useful error**.
Use a virtualenv.

`KPipeline` yields `.phonemes` alongside audio — this is the pronunciation-checking mechanism, see
`04-pronunciation.md`.

---

## 8. Amazon Polly, for the record

No longer used, but expensive to rediscover.

### SSML support by engine

| tag | generative | long-form | neural | standard |
|---|---|---|---|---|
| `break`, `sub`, `phoneme` (IPA), `say-as`, `p`/`s`, `lang`, `w`, `mark` | yes | yes | yes | yes |
| `prosody rate` | quantised, see below | continuous | continuous | continuous |
| `prosody pitch` | **no** | no | no | yes |
| `emphasis` | **no** | no | no | yes |
| `amazon:effect drc` | **no** | yes | yes | yes |
| `amazon:effect whispered`, `amazon:breath`, `amazon:auto-breaths` | **no** | no | no | yes |
| `amazon:domain news`/`conversational` | no | no | Matthew and Joanna only | no |
| `phoneme` x-sampa | no | no | no | no |

### Generative quantises prosody rate into three buckets

Byte-identical MP3s prove it. 60%, 70%, 80%, 85%, `x-slow`, `slow` all return the identical file.
90%, 95%, 100%, 105%, 110%, `medium` and no tag all return a different identical file. Only `fast`
differs again. **Percentage rate tuning is a no-op on generative.**

### Other Polly facts

- Max input 3000 characters on generative; 6000 fails.
- Word and sentence speech marks are unsupported on generative.
- `pcm` caps at 16 kHz, so there is no lossless 24 kHz path.
- **`ogg_vorbis` at 24 kHz beats `mp3`.** Scored against the lossless 16 kHz PCM of the same
  utterance: Vorbis **14.8 dB SNR**, MP3 **11.4 dB**. Vorbis still carries content at 11.5 kHz where
  the 48 kbps MP3 has brick-walled.
- Synthesis is **deterministic across output formats** — the same request returns the same waveform,
  differently encoded. This is what makes the codec comparison above possible.
- Clips ship with ~300 ms leading and ~250 ms trailing silence, close to the inter-turn gap you want.
- Output sits near &minus;24 LUFS, peak about &minus;8.4 dBFS.
- English generative voices are limited: males are only `Stephen`, `Matthew`, `Brian`.
- On generative, `AWS`, `S3`, `SAN` and `x509` synthesize **byte-identically** to a hand-written
  `<sub>` alias — the model already says them correctly.
- `<say-as interpret-as="characters">AWS</say-as>` is 36% longer and spells it out with pauses.
- Em dash, hyphen and comma produce **byte-identical** audio on generative. Ellipsis is longer. An
  explicit `<break>` is far longer than any punctuation. Punctuation is a weak pacing lever there.
- `<sub alias="C A">CA</sub>` inserted a phrase break: "AWS Private CA you control" came back as
  "AWS Private. **CA** you control". **Wrapping a short acronym in `<sub>` costs a phrase break.**

### CloudFront viewer mTLS, as of August 2026

Real, and the current script relies on it. Three modes: **required** (validates against a trust store
and rejects), **optional** (validates if presented, forwards for authorization), **passthrough**
(verifies the client holds the private key, forwards the chain to the origin). Trust store is a bundle
of CAs. Validation happens at the edge. Announced November 2025; passthrough mode May 2026. No
additional cost.

---

## 9. Measurement methods, and where they lied

Three objective methods were used. Two of them produced a confidently wrong answer at least once.

### Phoneme inspection — reliable

`KPipeline` returns the phoneme string. Instant, free, offline, deterministic, and it explains the
fault rather than just flagging it. **This is the right tool for pronunciation.** See
`04-pronunciation.md`.

### Byte and hash comparison of synthesized audio — reliable

Because Polly is deterministic, identical MD5s prove two inputs produce identical audio. This is how
the prosody-rate quantisation and the redundant `<sub>` aliases were proven rather than guessed.

### Amazon Transcribe round trip — useful but not an oracle

Caught real defects: untreated `mTLS` comes back as "MTLS", `SPIFFE` as "spiff", and both Kokoro `ALB`
failures.

**But it is not deterministic.** Two episodes containing a **byte-identical** clip transcribed `403`
correctly in one and as "40. 3" in the other, purely because the surrounding context differed. Confirm
any miss against the audio before acting on it.

### Short-term RMS dynamic range — abandoned, it was wrong

Proposed as a proxy for expressiveness. It ranked `Tiffany` **last** among voices, which is the exact
reverse of how she was heard. Dropped before it influenced anything. Recorded here because it is an
attractive-looking metric that does not measure what it appears to.

### The general lesson

Twice a metric was satisfied while the listening test got worse: the dynamic-range proxy, and pitch
shifting for voice separation. **A measurement is for diagnosis and regression-checking, never for
deciding whether something sounds good.**

---

## 10. Everything rejected

| approach | why |
|---|---|
| `loudnorm` as a mastering stage | silent dynamic fallback, gain-rides the programme |
| Pitch shifting for voice separation | `rubberband` at ±1.4 st is audible on speech even with `formant=preserved`. Moved the metric 0.8 → 3.36 st and made both voices worse |
| Slowing a flat span | 4.25 → 3.83 st, and audibly worse |
| Haas stereo widening | at `side_gain` 0.12 the mono downmix peaked at 1.15. Clips wherever a player sums to mono |
| Explicit `<break>` pauses throughout a script | "terrible", introduced more problems than solved |
| Shortening sentences for pacing | same verdict |
| Heavy EQ curves | barely distinguishable from flat. Small lever |
| Short-term RMS dynamic range as an expressiveness metric | ranks the best voice last |
| Spelling acronyms out with spaces | slower and usually worse than the acronym as written |
| MP3 as the Polly source format | Vorbis is 3.4 dB cleaner at the same rate |
| 192 kbps for web embedding | transparent at 80 kbps on 24 kHz mono, a third of the size |

---

## 11. Environment and tooling

Every one of these cost real time.

- **`ffmpeg` is not installed by default.** `sudo apt-get install -y ffmpeg`.
- **`numpy` via apt**, `sudo apt-get install -y python3-numpy`, or in the venv.
- **`python3-venv` is not installed by default** and `python3 -m venv` fails confusingly without it.
- **Use a virtualenv with `--system-site-packages`.** Kokoro's G2P shells out to `pip` at runtime and
  PEP 668 blocks it otherwise, producing no audio and a misleading error.
- **Python 3.11 f-strings cannot contain a backslash** in the expression part.
- **Key any synthesis cache on the post-substitution string.** Keying on source text means editing the
  pronunciation table silently changes nothing. This hid a real fix for a full round.

---

## 12. Numbers, all in one place

| quantity | value |
|---|---|
| flat threshold | 5.0 semitones, 10th-to-90th percentile |
| flat-span lift | +2.5 dB, plus +2 dB at 2.8 kHz |
| flat-span pause | 250 ms before |
| loudness target | &minus;16 LUFS, lands at about &minus;17 |
| limiter ceiling | 0.75 |
| true peak achieved | &minus;0.8 to &minus;1.1 dBTP |
| room-tone bed | pink, `a=0.003`, 120 Hz-7 kHz, ~&minus;69 dBFS |
| inter-turn gap | 260 ms |
| final gap | 700 ms |
| section-boundary gap | 420-480 ms, twice per episode at most |
| edge trim | &minus;60 dB threshold, 150 ms kept |
| fade in | 8 ms |
| sample rate | 24 kHz mono throughout |
| master encode | 192 kbps; 80 kbps for web embedding |
| speaking rate | 172 wpm, measured |
| episode target | 12-16 turns, 500-700 words, 3-4 minutes |
| current episode | 14 turns, 649 words, 3:46, &minus;17.2 LUFS, &minus;1.1 dBTP |
| host flat rate | 1 phrase in 28 (4%) |
| expert flat rate | 9 phrases in 42 (21%), untreated by design |

---

## 13. What to try next

Ordered by expected value.

1. **Dialogue-native open models — VibeVoice, Dia.** These generate *both speakers in one pass* with
   real turn-taking, instead of synthesizing each turn cold. That cold-turn problem is the root cause
   of flat delivery, and it is the only known approach that addresses the cause rather than the
   symptom. They need a GPU, which means a running instance rather than a local process — a different
   cost and teardown story than anything here.
2. **Synthesize with lookahead context.** If a future Kokoro release accepts preceding text as
   context without voicing it, turn-initial flatness should drop without changing anything else.
3. **Per-voice brightness calibration.** Kokoro voices differ by 40 dB at 11 kHz. A measured
   per-voice shelf, rather than the current hand-set one, would make voice swapping safe.
4. **Music bed.** The room tone deliberately leaves headroom. This is explicitly out of scope for this
   system and expected to be added downstream.

Not worth revisiting: EQ curves, general audio transformations, pitch manipulation, stereo width. All
were explored across 21 measured variants and none moved the needle compared to the writing.
