# Episode structure

An episode is a **conversation with a shape**, not a Q&A list. The shape below is what the current
episode uses and what new scripts should follow.

## Target numbers

| | |
|---|---|
| length | 3 to 4 minutes |
| turns | 12 to 16 |
| words | 500 to 700 |
| speaking rate | about 172 words per minute, measured, not assumed |
| speaker split | expert roughly 75% of the words, host 25% |
| host turns | 20 to 45 words, almost always ending in a question |
| cold open | up to 70 words — the one host turn allowed to run long |
| expert turns | 55 to 105 words |
| closing turns | short, and only for the expert |

The expert must carry the majority. She is the stronger voice and the one with something to say. A host
who talks as much as the expert makes the episode worse in two ways at once: less content, more exposure
for the weaker voice.

## The arc

Seven beats. Each is one host turn and one expert turn unless noted.

**1. Cold open and hand-off** — host only.
Welcome, name the topic in one sentence, say why it is being covered, then hand over with a question.
Do not have the host explain anything; his job is to open the door. This turn is the longest the host
gets and the one most at risk of flat delivery, because it is unavoidably declarative. Write it with
long clauses and end it on a question.

**2. Definition.**
The expert defines the central term once, in plain language, and then says she will use the short form
from here. This is the only place the term is spelled out. See `docs/04-pronunciation.md` for why that
matters.

**3. The problem.**
What was actually being solved. Concrete and specific: real endpoints, real constraints, real numbers if
there are any. This beat earns the listener's attention or loses it.

**4. The obvious alternative, and why not.**
The host raises the approach the listener is already thinking of. The expert explains why it was not
taken. This is the beat that makes the episode feel like it comes from experience rather than a
documentation page, and it is the one most often missing from a first draft.

**5. The mechanism.**
How the thing actually works. One or two beats. Stay at the level of "what does this component check and
when" — resist configuration detail, parameter names, and console walkthroughs. Audio is a bad medium for
anything the listener would need to write down.

**6. The payoff.**
What it buys, in operational terms. What is easier now. What you look at when it breaks. Ideally a short
enumeration the listener can hold in their head, delivered by the expert, who can carry a list.

**7. Close.**
Host thanks the guest in one sentence with grammatical momentum. Expert answers with something short and
warm. End there. No summary, no outro copy, no call to action.

## Rules about shape

- **Alternate strictly.** Host, expert, host, expert. Two consecutive turns by the same speaker read as
  an editing mistake.
- **Never open on the expert.** The listener needs to be told what they are about to hear.
- **The host never explains.** If the host is delivering information, it belongs in an expert turn.
- **One idea per expert turn.** A turn covering three things will be read at one pitch across all
  three.
- **Do not end the episode on the host.** The expert gets the last word because she can land it.

## Pacing

Gaps are handled by the renderer and rarely need overriding:

| | |
|---|---|
| between turns | 260 ms |
| after the final turn | 700 ms |
| topic shift | set `gap_after_ms` to 420-480 on the turn *before* the shift |

Use `gap_after_ms` twice per episode at most, on genuine section boundaries. It is a punctuation mark,
not a pacing dial. Everything else about pace comes from sentence length in the writing.

## What does not belong

- Intro or outro music beds. The programme has a room-tone bed at -69 dBFS with headroom left
  deliberately for music to be added afterwards, outside this system.
- Sponsor reads, episode numbers, "don't forget to subscribe".
- Recaps. Four minutes does not need one.
- Anything the listener would have to write down: exact IAM actions, CLI flags, ARNs, code.
- Banter that does not carry information. Two synthetic voices being charming is the fastest route
  to the uncanny valley.
