# Authoring from a recording

**Hand an AI this document, the VTT, and the supporting materials.**

This document covers one stage: getting from a rambling spoken explanation to a beat sheet with a
source behind every beat. From there `03-authoring-a-script.md` is the writing spec and produces the
`script.json`.

Read `01-episode-structure.md`, `02-personas.md` and `03-authoring-a-script.md` first. Nothing in them
is relaxed here.

---

## The failure mode, first

**The recording is not a draft of the script.**

Handed a transcript, a model will remove the disfluencies, split it across two speakers, and return
something that tracks the recording turn for turn. The result wanders exactly where the speaker
wandered, runs as long as the speaker happened to talk, and asserts whatever the speaker happened to
remember correctly. It reads as a cleaned-up transcript because it is one.

The recording supplies judgement, emphasis and experience. The materials supply mechanism and fact.
The episode is built out of both and resembles neither.

---

## Inputs

### The recording

A VTT of one person explaining a technical topic out loud, unscripted.

Expect no ordering, repetition, self-correction, abandoned sentences, tangents and asides. Expect it to
be three to ten times longer than the episode. Expect it to be wrong in places, because it is somebody
talking from memory. Expect the technical terms to be the words the transcription got wrong, because
they are the rarest words in the audio.

### The supporting materials

Paths or URLs handed over alongside the VTT.

| material | what it is good for |
|---|---|
| design write-up, ADR | the decision, and the alternative that was rejected |
| vendor or product documentation | how the mechanism works, and what it is actually called |
| repository — IaC, config | what was deployed, as opposed to what was intended |
| repository — README, module layout | boundaries, and the vocabulary the team uses |
| repository — commit and PR history | the "why not", when it was never written down anywhere else |
| ticket thread, incident notes | the problem beat, with real constraints |

**Nothing from a repository is quoted into the script.** A repository is read to verify claims and to
understand mechanism. The listener cannot write anything down, so identifiers, flags, parameters and
code never reach the audio. See `01-episode-structure.md`.

---

## Authority

**The recording decides what the episode is about. The materials decide what is true.**

| question | decided by |
|---|---|
| what this episode is about | the recording |
| which parts matter most | the recording |
| why the obvious approach was rejected | the recording, verified against the materials |
| how the mechanism works | the materials |
| what a thing is called, and what the number is | the materials |
| whether a claim is in the episode at all | verification, below |

When the recording and the materials disagree on a fact, the materials win and the script states the
correct thing plainly. Never narrate the correction, never write around it, never hedge it into "some
people think". The listener was not in the room for the mistake.

---

## Six passes

### 1. Flatten

Strip cue numbers and per-line timestamps. Keep one timestamp at each topic shift, so every later claim
can be anchored back to a point in the recording.

**Keep the disfluencies at this stage.** "…so it goes to the queue, uh, no, it goes to the queue *after*
the check" is a self-correction, and the second half is the claim. A cleaned transcript loses which
half the speaker meant.

### 2. Claim inventory

Every technical assertion, one line each, with its timestamp. Sort each into one of four kinds, because
they are verified differently and they are worth different amounts:

| kind | example | verifiable against materials |
|---|---|---|
| **mechanism** | "the edge validates the certificate before it reaches the origin" | yes |
| **decision** | "we didn't want to own that much networking" | rarely |
| **experience** | "the first version fell over the moment we added the second region" | no |
| **background** | "TLS normally only authenticates the server" | yes, trivially |

Decision and experience claims are the ones that exist **only** in the recording. They are the reason
the episode will not sound like documentation read aloud. Background claims are the ones most likely
to be misremembered and the cheapest to check.

### 3. Emphasis map

Rank the topics by how much of the recording they occupy, using the timestamps. Then adjust for verbal
marking: a point the speaker returned to after moving on, or introduced with *the thing people get
wrong is*, *the reason we actually did this*, *honestly*, *the tricky part*.

Distinguish **dwelling** from **struggling**. Returning to a point after covering other ground is
emphasis. Circling the same sentence three times is someone trying to remember a detail, and it is
worth no more than the sentence.

The top of that ranking is almost always the episode's spine.

### 4. Verification

Take every claim to the materials.

| outcome | action |
|---|---|
| **confirmed** | keep; record where it was confirmed |
| **corrected** | keep the corrected version; record the source |
| **unsupported, and checkable** — a mechanism or background claim the materials neither confirm nor contradict | **cut it** |
| **unsupported, and not checkable** — a decision or experience claim | keep, and flag it on handover for the human to confirm |

That last row is the one to get right. The speaker is the authority on what their team did and why, and
no document will ever confirm it. Everything else has to be backed.

Terms are part of verification. **A term that appears in the VTT and nowhere in the materials is
probably a transcription error, not a term.** Resolve it against the materials before it goes anywhere
near a script.

### 5. One question

Write down, in a single sentence, the one question this episode answers, phrased the way a competent
engineer who has not seen the system would ask it.

Everything that does not serve that question is out, however good it is.

The arithmetic is unforgiving. 500 to 700 words is roughly seven expert turns, which is seven ideas. A
thirty-minute recording is around four thousand words and a dozen topics. Under a fifth survives, and
the survivors are **chosen, not trimmed evenly**. Cutting every topic by 80% produces four minutes of
nothing in particular.

If the recording genuinely contains two episodes, make one and say which one in the handover.

### 6. Beat sheet

Map the surviving claims onto the seven beats in `01-episode-structure.md`. One line per beat: the
claim, and the anchor it came from.

Two checks before writing a word of dialogue:

- **Beat 4 must have real content.** `01-episode-structure.md` records that "the obvious alternative,
  and why not" is the beat most often missing from a first draft. From a recording it should be the
  easiest one, because people rambling about their own systems volunteer rejected alternatives
  constantly. If the recording did not, look in ADRs and commit history. If it is nowhere, say so on
  handover rather than inventing a counterargument.
- **Beat 3 must be concrete.** Real constraints, real scale, real failure. This beat is where the
  recording's experience claims belong, and it is the beat that earns the next three minutes.

Then write the script against `03-authoring-a-script.md`.

---

## Fidelity

Hard rules. Each of these is a way of sounding authoritative about something nobody said.

- **No number that is not in the materials or the recording.** If the speaker said "I think it was
  about a second", find the real figure or drop the figure.
- **No anecdote that was not told.** Illustrative examples are inventions.
- **No decision attributed to anyone who did not state it.** "We chose this because" requires that
  somebody actually said why.
- **Do not promote a hedge.** *Probably*, *I think*, *something like* in the recording means the claim
  gets verified or cut, never stated flatly.
- **The expert is an AI subject matter expert on the implementation.** She can say what the system does
  and why it was built that way. She cannot claim to have been there.
- **Do not import vendor marketing.** Documentation describes capabilities in the vendor's voice; the
  episode describes what this team uses and why.

---

## Terms, before writing

Collect every product name, service name, acronym and identifier from both the VTT and the materials.
Check each against the "deliberately absent" table in `04-pronunciation.md` — most are already correct
and adding a substitution makes things worse.

Anything not on that list gets a phoneme check **before** the script is written, not after:

```python
from kokoro import KPipeline
p = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")
for r in p("The gateway forwards it to the collector.", voice="af_heart"):
    print(r.phonemes)
    break
```

Repository-sourced terms are the highest risk in this whole input path, because repositories are full
of exactly the shapes that break: hyphenated identifiers, `snake_case`, `CamelCase`, version suffixes.
`execute-api` is the recorded case. **Rewrite rather than patch** — that rule is in
`04-pronunciation.md` and it applies with more force here, because a repository will supply fifty such
strings and none of them belong in speech anyway.

---

## Handing it over

Return the `script.json`, and with it, in the response rather than as files:

1. **Traceability** — one line per expert turn: the claim, and the timestamp or source it came from.
2. **Corrections** — anything the recording got wrong, and what the materials said instead.
3. **Unconfirmed** — the decision and experience claims that were kept on the speaker's authority
   alone. This is the list the human actually needs to read.
4. **Cut** — the topics that did not serve the one question, in a line each. This is the raw material
   for a second episode.

Then run the checks:

```
python3 lint.py script.json
.venv/bin/python render.py script.json
```

---

## When it comes back wrong

| symptom | where it actually went wrong |
|---|---|
| "that isn't what I said" | pass 4 or 5 — a claim drifted, or a cut removed the qualifier that made it true |
| "this sounds like the documentation" | the decision and experience claims were dropped; they are the whole difference |
| "it's shallow" | pass 5 — breadth was kept instead of choosing one question |
| "it's in the wrong order" | the beat sheet followed the recording's order instead of the arc in `01-episode-structure.md` |
| `lint.py` errors | the writing, not the material. Fix against `03-authoring-a-script.md` |
| four or more treated flat spans | host turns are ending on short declaratives. See `02-personas.md` |
| a term is mispronounced | it skipped the phoneme check above |
