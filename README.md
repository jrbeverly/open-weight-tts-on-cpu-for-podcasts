# Open Weight TTS on CPU for Technical Podcasts

> [!WARNING]
> **AI-authored:** This change was autonomously planned and implemented by an AI software factory from a human-authored specification, with possible subsequent human review or modification.

Turns a technical write-up into a 3–4 minute, two-voice audio explainer. Exploration centers around whether it is possible to create something that provides technical overview of git repositories, software components or architectures in-use within the organization.

Runs Kokoro-82M locally on CPU. No GPU, cloud resources, or credentials required.

```sh
python3 -m venv --system-site-packages .venv
.venv/bin/pip install kokoro "misaki[en]" soundfile torch
.venv/bin/python -m spacy download en_core_web_sm

python3 lint.py script.json
.venv/bin/python render.py script.json
```

`docs/example-episode.mp3` is a rendered example.

## Notes

- Script quality is the main quality lever. Good TTS does not rescue a bad podcast script. Earlier versions sounded materially worse mostly because the writing itself was unpleasant to listen to.
- Newer scripts aren't really _great_ but they show that even just minor improvements can realize notable quality jumps.
- The two voices need different writing, not just different audio treatment. The male voice carries less emotional inflection, so lines depending on delivery tend to land flat. The female voice tolerates looser/more expressive writing.
- That script/voice matching mattered more than the audio-processing experiments.
- Still missing a proper opening sting/jingle. Current episodes start too abruptly.
- Also want a low-key background music/ambience layer through most or all of the episode. Soft rhythmic/game-like music seems to make this format considerably easier to listen to and gives the dialogue something to sit on.
- Likely worth treating the audio bed as part of the format rather than post-processing: intro sting + looping/sectional background cues + outro.
- Kokoro exposes generated phonemes, which makes pronunciation problems easy to inspect offline. Known issues include `terminate` using the wrong vowel and hyphenated words getting fused.
- Pitch shifting for stronger voice separation tested well numerically and sounded worse. Dropped.
- Loudness processing needs care. `loudnorm` can fall back to dynamic behaviour when the requested gain conflicts with the peak ceiling.
- MP3 encoding can introduce inter-sample overshoot, so limiter headroom needs to account for the final encode rather than only the pre-encode waveform.
- Existing documentation could feed both simple TTS versions and more conversational AI-generated explainers.
- Human-led explainer/video sessions could also become source material for additional supporting audio content.
- Probably not most users’ first choice for learning technical systems, but meaningfully expands the number of approachable learning formats available; potentially valuable for onboarding.
