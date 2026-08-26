"""Check a script against the writing rules in docs/03-authoring-a-script.md.

Text only, no model, no audio. Catches what can be caught before spending 90 seconds rendering.
Run: python3 lint.py script.json
"""
import json
import re
import sys
from pathlib import Path

BANNED = [
    (r"mutual\s+T\s+L\s+S", "spell it 'mutual TLS' at the definition, 'mTLS' after"),
    (r"\bm\s+T\s+L\s+S\b", "spell it 'mTLS'"),
    (r"execute-api", "the hyphen fuses it into one word; write 'execute API'"),
    (r"\bALB\b", "Kokoro drops a letter, differently per voice; write 'the load balancer'"),
    (r"\bA\s+W\s+S\b", "write 'AWS'"),
]

# Bare evaluations that need a tone of voice the host cannot produce.
EVALUATIVE = re.compile(
    r"^(that|this|it)('s| is| sounds| looks| seems)\s+(a\s+)?\w+[.!]$", re.I)

FILLERS = ["you know", "i mean", "look,", "yeah", "so,", "though"]
# "So" opening a question is a discourse marker and measures fine; these are the real fillers.
OPENING_FILLERS = ["um", "uh", "you know", "i mean", "yeah", "like,", "well,"]
HOST_MAX_WORDS = 45
HOST_COLD_OPEN_MAX = 70
HOST_MIN_WORDS = 8
EXPERT_MAX_WORDS = 105
WORDS_PER_MINUTE = 172


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def check(path):
    script = json.loads(Path(path).read_text())
    turns = script["turns"]
    errors, warnings = [], []

    def err(i, msg):
        errors.append("turn %2d  %s" % (i, msg))

    def warn(i, msg):
        warnings.append("turn %2d  %s" % (i, msg))

    if turns[0]["speaker"] != "host":
        err(1, "episode must open on the host")
    if turns[-1]["speaker"] != "expert":
        err(len(turns), "episode must end on the expert, who can land it")
    if not 12 <= len(turns) <= 16:
        warnings.append("       %d turns; target is 12 to 16" % len(turns))

    words = {"host": 0, "expert": 0}
    for index, turn in enumerate(turns, 1):
        speaker, text = turn["speaker"], turn["text"]
        count = len(text.split())
        words[speaker] += count

        if index > 1 and turns[index - 2]["speaker"] == speaker:
            err(index, "two consecutive %s turns; speakers must alternate" % speaker)

        for pattern, why in BANNED:
            if re.search(pattern, text, re.I):
                err(index, "forbidden spelling %r: %s" % (pattern, why))

        if re.search(r"[(\[]", text):
            err(index, "parenthetical; a parenthesis is a visual device, split the sentence")

        if speaker == "host":
            if not text.rstrip().endswith("?"):
                if index == len(turns) - 1 or index == len(turns):
                    pass
                elif index == 1:
                    err(index, "the cold open must hand over on a question")
                else:
                    err(index, "host turn does not end on a question")
            cap = HOST_COLD_OPEN_MAX if index == 1 else HOST_MAX_WORDS
            if count > cap:
                warn(index, "%d words; host turns should be under %d" % (count, cap))
            if count < HOST_MIN_WORDS:
                err(index, "%d words; too short to develop any contour" % count)
            for sentence in sentences(text):
                if EVALUATIVE.match(sentence):
                    err(index, "bare evaluation %r needs a tone the voice cannot produce" % sentence)
            last = sentences(text)[-1]
            if not last.endswith("?") and len(last.split()) < 8:
                err(index, "turn ends on a short declarative %r; flatness concentrates there" % last)
            frags = [s for s in sentences(text) if len(s.split()) <= 4]
            if len(frags) >= 2:
                err(index, "list of fragments %s; use one sentence with momentum" % frags)
            lowered = text.lower()
            if any(lowered.startswith(f) for f in OPENING_FILLERS):
                err(index, "host turn opens on a filler")
        else:
            if count > EXPERT_MAX_WORDS:
                warn(index, "%d words; expert turns should be under %d, one idea each"
                     % (count, EXPERT_MAX_WORDS))

        gap = turn.get("gap_after_ms")
        if gap is not None and not 300 <= gap <= 600:
            warn(index, "gap_after_ms %d is outside the useful 420 to 480 range" % gap)

    total = words["host"] + words["expert"]
    share = 100 * words["expert"] / total
    if share < 65:
        warnings.append("       expert carries only %.0f%% of the words; target is about 75%%" % share)
    if not 500 <= total <= 700:
        warnings.append("       %d words; target is 500 to 700 (about %.1f min)"
                        % (total, total / WORDS_PER_MINUTE))

    overrides = sum(1 for t in turns if "gap_after_ms" in t)
    if overrides > 2:
        warnings.append("       %d gap overrides; at most 2, on real section boundaries" % overrides)

    fillers = sum(1 for t in turns if t["speaker"] == "expert"
                  and any(f in t["text"].lower() for f in FILLERS))
    if fillers == 0:
        warnings.append("       expert uses no fillers; one every two or three turns reads warmer")

    print("%s  %d turns, %d words, expert %.0f%%, about %.1f min"
          % (Path(path).name, len(turns), total, share, total / WORDS_PER_MINUTE))
    for line in errors:
        print("  ERROR    %s" % line)
    for line in warnings:
        print("  warning  %s" % line)
    if not errors and not warnings:
        print("  clean")
    return 1 if errors else 0


sys.exit(max(check(p) for p in (sys.argv[1:] or ["script.json"])))
