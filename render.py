"""Persona-driven renderer. Each speaker has its own chain, its own writing rules, and its own
answer to flat delivery. See personas.md."""
import hashlib
import json
import re
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

from flatness import pitch_track, segments

ROOT = Path(__file__).parent
OUT = ROOT / "build" / "episodes"
SRC = ROOT / "build" / "src"
TARGET_LUFS = -16.0
SR = 24000

DEESS = "deesser=i=0.30:m=0.5:f=0.5"
CHORUS_2MS = "chorus=0.8:0.9:2:0.15:0.12:1.0"
ROOM_TONE = 0.003

EXPERT_CHAIN = [
    "highpass=f=80", DEESS,
    "equalizer=f=320:width_type=q:w=1.2:g=-2.5",
    "equalizer=f=3200:width_type=q:w=0.9:g=2.5",
    "highshelf=f=9000:g=2",
    "acompressor=threshold=-20dB:ratio=2:attack=15:release=250:makeup=1",
    CHORUS_2MS,
    "aecho=1:0.88:13|21:0.04|0.025",
]
ASKER_CHAIN = [
    "highpass=f=110",
    "equalizer=f=300:width_type=q:w=1.2:g=-2",
    "equalizer=f=4000:width_type=q:w=1.0:g=1.5", DEESS,
    "aecho=1:0.86:29|43:0.07|0.05",
]

# Checked against the phonemes misaki actually produces, not by ear.
#   terminate  -> tˈɛɹmənˌAt, the wrong vowel; the override gives tˈɜɹmɪnˌAt
#   you know   -> ju nˈO, unstressed and rushed; stressing both words gives it room
#   execute-api-> the hyphen fuses it into ˈɛksᵻkjˌutˌApˌiˈI, one word
# mTLS and TLS are left alone: bare mTLS is already ˌɛmtˌiˌɛlˈɛs, and spelling it "mutual T L S"
# stresses all three letters separately, which is what made it drag.
SPOKEN = [
    (r"\bterminate\b", "[terminate](/t\u02c8\u025c\u0279m\u026an\u02ccAt/)"),
    (r"\byou know\b", "[you know](/j\u02c8u n\u02c8O/)"),
    (r"\bexecute-api\b", "execute API"),
]

# Anything under this much pitch movement reads as robotic. "That sounds worse." measured 4.25.
FLAT_SEMITONES = 5.0
LIFT_DB = 2.5
PAUSE_S = 0.25

PERSONAS = {
    "expert": {"voice": "af_heart", "chain": EXPERT_CHAIN, "treat": False},
    "asker": {"voice": "am_michael", "chain": ASKER_CHAIN, "treat": True},
}

_kokoro = None


def kokoro():
    global _kokoro
    if _kokoro is None:
        from kokoro import KPipeline
        _kokoro = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")
    return _kokoro


def ff(args):
    subprocess.run(["ffmpeg", "-y", "-v", "error"] + args, check=True)


def synthesize(persona, text):
    voice = PERSONAS[persona]["voice"]
    body = text
    for pattern, spoken in SPOKEN:
        body = re.sub(pattern, spoken, body)
    # keyed on the spoken string, so editing SPOKEN actually invalidates the cache
    path = SRC / ("%s-%s.wav" % (voice, hashlib.md5(body.encode()).hexdigest()[:8]))
    if path.exists():
        return path
    audio = np.concatenate([np.asarray(r.audio, dtype=np.float32)
                            for r in kokoro()(body, voice=voice)])
    handle = wave.open(str(path), "wb")
    handle.setnchannels(1)
    handle.setsampwidth(2)
    handle.setframerate(SR)
    handle.writeframes((np.clip(audio, -1, 1) * 32767).astype("<i2").tobytes())
    handle.close()
    return path


def prepare(clip, wav, chain, gap_ms):
    edge = "silenceremove=start_periods=1:start_threshold=-60dB:start_silence=0.15"
    steps = [edge, "areverse", edge, "areverse", "afade=t=in:d=0.008"] + chain
    steps.append("apad=pad_dur=%s" % (gap_ms / 1000))
    ff(["-i", str(clip), "-af", ",".join(steps), "-ar", str(SR), "-ac", "1",
        "-c:a", "pcm_s16le", str(wav)])


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1",
                          "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def flat_spans(wav):
    x = load(wav)
    found = []
    for a, b in segments(x):
        f = pitch_track(x[int(a * SR):int(b * SR)])
        if len(f) < 4:
            continue
        span = 12 * np.log2(np.percentile(f, 90) / np.percentile(f, 10))
        if span < FLAT_SEMITONES:
            found.append((a, b, span))
    return found


def piece(wav, out, start, end=None, lift=0.0):
    chain = ["atrim=start=%s%s" % (start, "" if end is None else ":end=%s" % end),
             "asetpts=PTS-STARTPTS"]
    if lift:
        chain.append("volume=%.2fdB" % lift)
        chain.append("equalizer=f=2800:width_type=q:w=1.0:g=%.1f" % (lift * 0.8))
    ff(["-i", str(wav), "-af", ",".join(chain), "-ar", str(SR), "-ac", "1",
        "-c:a", "pcm_s16le", str(out)])
    return out


def treat_flat(work, wav):
    """Lift each flat span and put a short pause in front of it. No pitch is touched, so this
    adds weight and timing rather than inflection; the writing has to do the rest."""
    spans = flat_spans(wav)
    if not spans:
        return wav, []
    parts = []
    cursor = 0.0
    for index, (a, b, _) in enumerate(spans):
        if a - cursor > 0.02:
            parts.append(piece(wav, work / ("p%02da.wav" % index), cursor, a))
        gap = work / ("p%02dgap.wav" % index)
        ff(["-f", "lavfi", "-i", "anullsrc=r=%d:cl=mono" % SR, "-t", str(PAUSE_S),
            "-c:a", "pcm_s16le", str(gap)])
        parts.append(gap)
        parts.append(piece(wav, work / ("p%02db.wav" % index), a, b, LIFT_DB))
        cursor = b
    parts.append(piece(wav, work / "ptail.wav", cursor))
    listing = work / "join.txt"
    listing.write_text("".join("file '%s'\n" % p.resolve() for p in parts))
    out = work / "treated.wav"
    ff(["-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(out)])
    return out, spans


def graph(count, tail):
    return "".join("[%d:a]" % i for i in range(count)) + \
        "concat=n=%d:v=0:a=1[cat];[cat]%s[out]" % (count, tail)


def loudness(wavs):
    command = ["ffmpeg", "-hide_banner"]
    for wav in wavs:
        command += ["-i", str(wav)]
    command += ["-filter_complex",
                graph(len(wavs), "loudnorm=I=%s:TP=-1.5:print_format=json" % TARGET_LUFS),
                "-map", "[out]", "-f", "null", "-"]
    err = subprocess.run(command, capture_output=True, text=True).stderr
    return float(json.loads(err[err.rindex("{"):err.rindex("}") + 1])["input_i"])


def master(wavs, name, bed=ROOM_TONE):
    """The bed runs under the whole programme. Per-turn it would breathe in and out."""
    gain = TARGET_LUFS - loudness(wavs)
    command = ["ffmpeg", "-y", "-v", "error"]
    for wav in wavs:
        command += ["-i", str(wav)]
    if bed:
        command += ["-f", "lavfi", "-i", "anoisesrc=c=pink:r=%d:a=%s" % (SR, bed)]
        tail = ("volume=%.2fdB[v];[%d:a]highpass=f=120,lowpass=f=7000[n];"
                "[v][n]amix=inputs=2:duration=first:normalize=0,"
                "alimiter=limit=0.75:level=false,aresample=%d" % (gain, len(wavs), SR))
        full = "".join("[%d:a]" % i for i in range(len(wavs))) + \
            "concat=n=%d:v=0:a=1[cat];[cat]%s[out]" % (len(wavs), tail)
    else:
        full = graph(len(wavs),
                     "volume=%.2fdB,alimiter=limit=0.75:level=false,aresample=%d" % (gain, SR))
    command += ["-filter_complex", full, "-map", "[out]", "-ar", str(SR), "-ac", "1",
                "-c:a", "libmp3lame", "-b:a", "192k", str(OUT / (name + ".mp3"))]
    subprocess.run(command, check=True, capture_output=True)
    print("  %-24s gain %+.2f dB" % (name, gain))


def build(name, turns):
    work = OUT / name
    work.mkdir(parents=True, exist_ok=True)
    wavs = []
    for index, turn in enumerate(turns, 1):
        persona = "expert" if turn["speaker"] == "expert" else "asker"
        spec = PERSONAS[persona]
        wav = work / ("%03d-%s.wav" % (index, spec["voice"]))
        gap = turn.get("gap_after_ms", 700 if index == len(turns) else 260)
        prepare(synthesize(persona, turn["text"]), wav, spec["chain"], gap)
        if spec["treat"]:
            wav, spans = treat_flat(work, wav)
            for a, b, s in spans:
                print("    turn %d flat at %.2f-%.2f (%.2f st) -> lifted" % (index, a, b, s))
        wavs.append(wav)
    master(wavs, name)


OUT.mkdir(parents=True, exist_ok=True)
SRC.mkdir(parents=True, exist_ok=True)
source = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "script.json"
script = json.loads(source.read_text())
build(sys.argv[2] if len(sys.argv) > 2 else source.stem, script["turns"])
