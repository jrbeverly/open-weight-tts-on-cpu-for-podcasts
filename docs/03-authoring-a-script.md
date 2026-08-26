# Authoring a script

**This is the document to hand an AI along with a technical write-up.** Everything it needs to produce a
compliant `script.json` is here or linked from here.

Read `01-episode-structure.md` for the arc and `02-personas.md` for the voices before writing.

---

## The job

Turn one finished technical write-up into a `script.json`: a two-speaker conversation of 12 to 16 turns
and 500 to 700 words that explains the material to a competent engineer who has not read it.

You are not summarising the article. You are finding the **story** in it: what was being solved, what
the obvious approach was, why it was not taken, how the chosen thing actually works, and what it bought.
If the article does not contain that story, extract what it does have and say less rather than padding.

---

## The file

```json
{
  "title": "Securing internal endpoints with mTLS on CloudFront",
  "note": "optional, free text, for humans",
  "turns": [
    { "speaker": "host",   "text": "..." },
    { "speaker": "expert", "text": "...", "gap_after_ms": 420 }
  ]
}
```

- `speaker` is exactly `"host"` or `"expert"`.
- Turns strictly alternate, starting with `host` and ending with `expert`.
- `gap_after_ms` is optional, 420-480, at most twice per episode, on genuine section boundaries.
- `text` is plain prose. No SSML, no markup, no stage directions, no speaker names inside the text.

---

## The two personas, in one line each

**Host — `am_michael`.** Cannot carry emotional inflection. Write defensively.
**Expert — `af_heart`.** Can carry it. Write loosely, and give her most of the words.

### Host rules — follow these literally

| rule | why |
|---|---|
| **End almost every turn on a question mark** | questions measure 10.20 semitones of pitch movement, bare declaratives 4.25 |
| **Never a bare evaluation** — no *"That sounds worse."*, *"That's a good one."*, *"Interesting."* | needs a tone the voice cannot produce |
| **Never understatement or irony** | it will be read literally and flatly |
| **Never end a turn on a short declarative** | flatness concentrates in that position |
| **Never a list of fragments** | each fragment is read at the same pitch |
| **Contrast by repeated structure**, not stressed words | *"The question is rarely X. The question is Y."* |
| **Attitude goes in the words** | *"Because on the face of it, that looks like a straight downgrade."* |
| 20-45 words per turn, cold open up to 70 | longer clauses give the model contour to build |
| At most one filler, mid-sentence, never opening | fillers are riskier on this voice |

The only host turn that may be substantially declarative is the cold open, because it has to be. Write
it with long clauses and end it on a question handing over.

### Expert rules — permissive

- Fillers are wanted: *you know*, *I mean*, *look*, *so*, *though*, *yeah*. About one every two or
  three turns.
- Short reactions, understatement, and fragments for emphasis are all safe.
- 55-105 words per turn. One idea per turn.
- She gets the last word, and it should be short and warm.

---

## Writing for the ear

- **Contractions everywhere.** *it's*, *you're*, *doesn't*, *we'd*.
- **No parentheticals.** A parenthesis is a visual device. Split the sentence.
- **No numbered or bulleted structure.** "Two things." then two sentences is fine; "firstly, secondly"
  is not.
- **Nothing the listener would need to write down.** No ARNs, CLI flags, exact IAM actions, code,
  or configuration keys.
- **Spell out the central acronym once**, at its definition, then use the short form for the rest of
  the episode. See `04-pronunciation.md`.
- **Read every line aloud.** If you need a particular tone of voice to make it mean what it means, and
  it is a host line, rewrite it.

---

## Forbidden spellings

These are known to synthesize wrong. `lint.py` will reject them.

| do not write | write instead |
|---|---|
| `mutual T L S`, `m T L S` | `mutual TLS` at the definition, `mTLS` after |
| `execute-api` | `execute API` |
| `ALB` | `the load balancer` or `Application Load Balancer` |
| `A W S`, spaced-out acronyms generally | the acronym as normally written |

The full reasoning, and the method for checking a new word, is in `04-pronunciation.md`. Any acronym not
already listed there should be checked before it goes in a script.

---

## Worked example

The source material said, in effect: *passthrough mode means the load balancer does not validate the
client certificate, which seems worse, but it lets your application make the authorization decision.*

**First draft, which failed:**

```
host:   "And the other mode?"
expert: "Passthrough. The ALB doesn't validate anything. That sounds worse,
         but it's often what you want."
host:   "That sounds worse."
```

Three separate violations. The host turn is a two-word fragment with nothing for the model to shape.
`ALB` is mispronounced. And *"That sounds worse."* is a bare evaluation that needs a skeptical tone —
it measured 4.25 semitones and was the line that triggered this entire rule set.

**Rewritten:**

```
host:   "And passthrough? If the load balancer isn't checking anything, what am
         I actually getting from it? Because on the face of it, that looks like
         a straight downgrade."
expert: "It does look like a downgrade, and in most cases it turns out to be the
         opposite. The load balancer forwards the whole certificate chain to your
         application in a header, and, you know, your code decides. The question
         you actually care about is rarely whether the certificate is valid. The
         question is which service is calling, and whether that service is
         allowed to."
```

The skepticism moved into the words. The host turn ends on a clause with momentum instead of a
fragment. `ALB` became *the load balancer*. The expert answers directly, uses one filler, and builds
the contrast by repeating *"The question…"* rather than needing stress on a word.

That phrase measured **5.99 semitones**, up from 4.25, and removed every flat span from the turn.

---

## Before you hand it over

Run the linter. It is fast and catches most rule violations mechanically:

```
python3 lint.py script.json
```

Then render. The renderer reports every flat span it had to treat:

```
.venv/bin/python render.py script.json          # -> build/episodes/script.mp3
.venv/bin/python render.py cloudfront.json ep-04  # -> build/episodes/ep-04.mp3
```

**One or two treated spans in an episode is normal.** Four or more means the host writing is not
following the rules, and the fix is the script, not the audio. Go back and look at which turns were
flagged; they will be the ones that end on a declarative.
