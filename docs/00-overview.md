# What this system is

A reproducible way to turn a finished technical write-up into a two-voice audio explainer that a person
will actually listen to for three or four minutes without wanting to stop.

It is not a story generator. The intelligence comes from the source article. This system's only job is
to make that material **sound excellent**, and most of that job turns out to be writing, not audio.

## The pipeline

```
technical write-up          recording (VTT) + supporting materials
      │                                   │
      │                                   │  docs/07-from-a-recording.md
      │                                   ▼
      │                         claims, anchors, one question
      │                                   │
      └──────────────┬────────────────────┘
                     │  docs/03-authoring-a-script.md      ← an AI does this
                     ▼
   script.json          two speakers, persona-specific writing
      │
      │  lint.py                            ← catches rule violations before synthesis
      ▼
   validated script
      │
      │  render.py                          ← Kokoro-82M, local CPU, no credentials
      ▼
  per-turn audio  ──►  per-persona chain  ──►  flat-span treatment (asker only)
      │
      │  concat, one static gain, limiter, room-tone bed
      ▼
   episode.mp3          ~-17 LUFS, -1 dBTP, 24 kHz mono
```

Every stage leaves an inspectable artifact on disk: the synthesized clip, the prepared per-turn WAV,
the treated WAV where treatment fired, and the master.

## What "good" means here

The bar is a **deliberately produced internal technical briefing**. Not documentation read aloud, and
not an over-produced AI podcast with two voices performing enthusiasm at each other. The expert carries
the depth. The host creates pacing and gives the listener somewhere to stand.

Concretely, the failure modes that matter, in the order they were found to matter:

1. **Mastering that damages the audio.** Fixed once, stays fixed. See `docs/05-audio-chain.md`.
2. **Writing that needs a tone of voice the model cannot produce.** This is the largest remaining
   lever and the one that needs attention on every new script. See `docs/03-authoring-a-script.md`.
3. **Voice and role assignment.** Settled. See `docs/02-personas.md`.
4. **Pronunciation.** Mechanical, verifiable, cheap. See `docs/04-pronunciation.md`.
5. **Tonal shaping.** Real but small. Already set; do not spend effort here.

## Constraints that shape everything

- **24 kHz is the ceiling.** Kokoro outputs 24 kHz, so there is nothing above 12 kHz, ever. Presence
  has to be built at 3-4 kHz. Do not try to add "air".
- **Each turn is synthesized alone.** The model has no knowledge of the surrounding turns, so every
  turn starts cold. This is why short reaction lines land flat, and it cannot be fixed in post.
- **Pitch must never be shifted.** Tried, measured, rejected. It wrecks both voices.
- **No AWS in the audio path.** Rendering is entirely local and needs no credentials.

## Running it

```
python3 -m venv --system-site-packages .venv
.venv/bin/pip install kokoro "misaki[en]" soundfile torch
.venv/bin/python -m spacy download en_core_web_sm

python3 lint.py script.json          # check the writing rules first
.venv/bin/python render.py script.json
# -> build/episodes/script.mp3, plus every intermediate WAV alongside it
```

A three to four minute episode costs about 90 seconds of CPU on four cores with no GPU. Kokoro-82M is
Apache 2.0 and about 330 MB.

## The documents

| | |
|---|---|
| `01-episode-structure.md` | the shape an episode takes, turn by turn |
| `02-personas.md` | the two voices: settings and writing rules, locked |
| `03-authoring-a-script.md` | **the AI-facing spec**: article in, `script.json` out |
| `04-pronunciation.md` | what the model says wrong, and how to check without listening |
| `05-audio-chain.md` | the signal chain and mastering, with the reasoning |
| `06-reference.md` | everything learned, including the dead ends |
| `07-from-a-recording.md` | the other AI-facing spec: rambled VTT plus source material in, beat sheet out |

`example-episode.mp3` in this directory is a rendered episode: 3:46, 14 turns, the current target.
