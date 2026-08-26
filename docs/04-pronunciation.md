# Pronunciation

## Check phonemes, do not listen

`misaki`, the grapheme-to-phoneme front end Kokoro uses, returns the phoneme string alongside the audio.
That makes pronunciation **objectively checkable, instantly, offline, and deterministically** — before
any audio is rendered.

```python
from kokoro import KPipeline
p = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")
for r in p("It's where you terminate.", voice="af_heart"):
    print(r.phonemes)      # ˌɪts wˌɛɹ ju tˈɛɹmənˌAt.
    break
```

That output is the bug: `tˈɛɹmənˌAt` is "TAIR-min-ate". The correct form is `tˈɜɹmɪnˌAt`.

This replaced an Amazon Transcribe round-trip that had been used for the same purpose. The comparison
is not close:

| | Transcribe round trip | phoneme inspection |
|---|---|---|
| cost | S3 bucket, one job per episode | free |
| speed | about a minute | instant |
| needs AWS | yes | no |
| deterministic | **no** — it wrote "40. 3" for audio it had already read as "403" | yes |
| explains the fault | no, only that it sounded wrong | yes, the wrong vowel is right there |

Transcribe still has a use: confirming that a whole episode is *intelligible* end to end. It is the
wrong tool for a single word.

## Fixing a word

Kokoro accepts an inline phoneme override in the text itself:

```
[terminate](/tˈɜɹmɪnˌAt/)
```

Use **misaki's own symbol set**, not textbook IPA. Read the symbols off a working example first — the
inventory is compressed, and getting it wrong produces silence or garbage rather than an error:

| symbol | sound | as in |
|---|---|---|
| `A` | /eɪ/ | g**a**te |
| `O` | /oʊ/ | c**o**de |
| `I` | /aɪ/ | d**i**ce |
| `W` | /aʊ/ | cl**ou**d |
| `Y` | /ɔɪ/ | p**oi**nt |
| `ˈ` | primary stress | precedes the syllable |
| `ˌ` | secondary stress | precedes the syllable |

## The active table

Held in `SPOKEN` in `render.py`, applied as word-boundary regexes before synthesis.

| written | renders as | fix | why |
|---|---|---|---|
| `terminate` | `tˈɛɹmənˌAt` | `[terminate](/tˈɜɹmɪnˌAt/)` | wrong vowel |
| `you know` | `ju nˈO` | `[you know](/jˈu nˈO/)` | neither word stressed, so it rushes |
| `execute-api` | `ˈɛksᵻkjˌutˌApˌiˈI` | rewrite to `execute API` | the hyphen fuses it into one word |

## Deliberately absent

Adding entries here is not free. A substitution that is not needed makes things worse.

| term | renders as | verdict |
|---|---|---|
| `mTLS` | `ˌɛmtˌiˌɛlˈɛs` | correct as written. **Never** spell it `mutual T L S` |
| `mutual TLS` | `mjˈuʧəwəl tˌiˌɛlˈɛs` | one fluid unit, correct |
| `mutual T L S` | `mjˈuʧəwəl tˈi ˈɛl ˈɛs` | **wrong** — three separately stressed letters, drags badly |
| `TLS` | `tˌiˌɛlˈɛs` | correct |
| `CloudFront` | `klˌWdfɹˈʌnt` | correct |
| `APIs` | `ˌApˌiˈIz` | correct |
| `VPNs` | `vˌipˌiˈɛnz` | correct |
| `DNS` | `dˌiˌɛnˈɛs` | correct |
| `IP` | `ˌIpˈi` | correct |
| `allowlist` | `əlˈWlɪst` | correct |
| `certificate authority` | `səɹtˈɪfəkət əθˈɔɹəTi` | correct |

## Acronyms the model gets wrong per-voice

`ALB` is the known case. Kokoro says it as "AB" in `bm_george` and "LB" in `af_heart` — it drops a
different letter depending on the voice. Amazon Polly says it correctly, and gets *worse* if you force
a spaced alias on it.

**The rule that came out of this: do not patch such words, write them out.** "the load balancer's
access logs" fixed it on every voice and every engine at once, and reads better aloud anyway.

## Rules of thumb

- **Hyphens fuse words.** Any hyphenated identifier is suspect. Write it as separate words.
- **Spacing out an acronym's letters slows it down** and usually sounds worse, not clearer. Try the
  acronym as normally written first.
- **Check before you add.** Most acronyms are already correct. Run the phoneme check and only add a
  substitution when the output is genuinely wrong.
- **Fixes do not transfer between engines**, and on Kokoro they do not even transfer between voices.
  Rewriting the script beats patching the table.
- **Key the clip cache on the post-substitution string.** Keying it on the source text means editing
  the table silently changes nothing — this bug hid a pronunciation fix for a full round.
