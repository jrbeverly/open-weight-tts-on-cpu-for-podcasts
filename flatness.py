"""Find spans where the voice is delivering flat, which is where writing that needs
emotional inflection falls over."""
import subprocess
import sys

import numpy as np

SR = 24000


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1",
                          "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def segments(x, floor_db=-42, min_gap=0.18, min_len=0.25):
    hop = int(0.01 * SR)
    frames = len(x) // hop
    rms = np.array([np.sqrt((x[i * hop:(i + 1) * hop] ** 2).mean() + 1e-12) for i in range(frames)])
    db = 20 * np.log10(rms + 1e-12)
    loud = db > (db.max() + floor_db)
    spans = []
    start = None
    gap = 0
    for i, on in enumerate(loud):
        if on:
            if start is None:
                start = i
            gap = 0
        elif start is not None:
            gap += 1
            if gap * 0.01 >= min_gap:
                if (i - gap - start) * 0.01 >= min_len:
                    spans.append((start * 0.01, (i - gap) * 0.01))
                start = None
                gap = 0
    if start is not None:
        spans.append((start * 0.01, frames * 0.01))
    return spans


def pitch_track(x):
    n = int(0.04 * SR)
    lo, hi = int(SR / 320), int(SR / 70)
    out = []
    for i in range(len(x) // n):
        s = x[i * n:(i + 1) * n]
        if np.sqrt((s ** 2).mean()) < 0.02:
            continue
        s = s - s.mean()
        ac = np.correlate(s, s, mode="full")[len(s) - 1:]
        if ac[0] <= 0:
            continue
        ac /= ac[0]
        seg = ac[lo:hi]
        if not len(seg):
            continue
        k = int(np.argmax(seg)) + lo
        if ac[k] > 0.32:
            out.append(SR / k)
    return np.array(out)


def report(path):
    x = load(path)
    print("%-6s %-6s %-7s %-9s %-9s %s" % ("start", "end", "sec", "F0 med", "F0 range", "verdict"))
    for a, b in segments(x):
        seg = x[int(a * SR):int(b * SR)]
        f = pitch_track(seg)
        if len(f) < 4:
            print("%-6.2f %-6.2f %-7.2f %-9s %-9s %s" % (a, b, b - a, "-", "-", "unvoiced"))
            continue
        med = np.median(f)
        span = 12 * np.log2(np.percentile(f, 90) / np.percentile(f, 10))
        verdict = "FLAT" if span < 3.0 else ("narrow" if span < 5.0 else "moving")
        print("%-6.2f %-6.2f %-7.2f %-9.1f %-9.2f %s" % (a, b, b - a, med, span, verdict))


if __name__ == "__main__":
    for path in sys.argv[1:]:
        print("\n== %s" % path)
        report(path)
