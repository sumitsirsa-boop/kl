"""Builds the final soundtrack: voiceover + synthesized SFX + background music.

All sound effects and the music bed are synthesized here with numpy, so the
project has no third-party audio licensing to worry about.

Usage: python3 video/build_audio.py [--project diwali]
Writes build/sfx_music.wav (no voice), build/mix.wav (final) and build/voice_env.npy
(per-frame voice loudness, used for the presenter's lip-sync).
"""
import os
import subprocess
import wave

import numpy as np

from project import load

T = load("timeline")
DURATION, FPS, SFX = T.DURATION, T.FPS, T.SFX

SR = 44100
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build", T.BUILD_NAME)
rng = np.random.default_rng(7)


def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def env(n, attack=0.005, decay=0.2):
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    return a * np.exp(-t / decay)


def noise(dur):
    return rng.standard_normal(int(dur * SR))


def lp_fft(x, cutoff):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x))


def hp_fft(x, cutoff):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (cutoff / np.maximum(f, 1)) ** 4)
    return np.fft.irfft(X, len(x))


def bp_fft(x, lo, hi):
    return hp_fft(lp_fft(x, hi), lo)


def norm(x, peak=0.9):
    m = np.max(np.abs(x)) or 1
    return x / m * peak


# ---------------------------------------------------------------- effects
def sfx_whoosh():
    d = 0.7
    n = noise(d)
    t = t_axis(d)
    shape = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    # sweeping band: chunked filtering for a rising-then-falling pitch
    out = np.zeros_like(n)
    chunks = 14
    L = len(n) // chunks
    for c in range(chunks):
        seg = n[c * L:(c + 1) * L + 512]
        centre = 400 + 3200 * np.sin(np.pi * (c + 0.5) / chunks)
        f = bp_fft(seg, centre * 0.5, centre * 1.6)
        w = np.hanning(len(f))
        out[c * L:c * L + len(f)] += (f * w)[: len(out) - c * L]
    return norm(out * shape, 0.8)


def sfx_boom():
    d = 1.6
    t = t_axis(d)
    f = 70 * np.exp(-t * 2.2) + 32
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 2.4)
    click = lp_fft(noise(d), 1800) * np.exp(-t * 40) * 0.6
    return norm(np.tanh((body + click) * 2.0), 0.95)


def sfx_sparkle():
    d = 1.2
    out = np.zeros(int(d * SR))
    for k in range(14):
        st = int(rng.uniform(0, 0.8) * SR)
        fr = rng.uniform(2500, 6500)
        n = int(0.35 * SR)
        tt = np.arange(n) / SR
        tone = np.sin(2 * np.pi * fr * tt) * env(n, 0.002, 0.07)
        out[st:st + n] += tone[: len(out) - st] * rng.uniform(0.3, 1)
    return norm(out, 0.6)


def sfx_ding():
    d = 1.5
    t = t_axis(d)
    x = (np.sin(2 * np.pi * 1318.5 * t) + 0.5 * np.sin(2 * np.pi * 2637 * t)
         + 0.25 * np.sin(2 * np.pi * 3955 * t)) * env(len(t), 0.002, 0.45)
    return norm(x, 0.7)


def sfx_chime():
    d = 2.0
    out = np.zeros(int(d * SR))
    for i, fr in enumerate([784, 988, 1175]):
        st = int(i * 0.12 * SR)
        n = len(out) - st
        tt = np.arange(n) / SR
        out[st:] += np.sin(2 * np.pi * fr * tt) * env(n, 0.003, 0.6)
    return norm(out, 0.6)


def sfx_stamp():
    d = 0.6
    t = t_axis(d)
    thud = np.sin(2 * np.pi * (90 * np.exp(-t * 8) + 50) * t) * np.exp(-t * 14)
    slap = bp_fft(noise(d), 300, 3000) * np.exp(-t * 35)
    return norm(np.tanh(2.5 * (thud + 0.7 * slap)), 0.95)


def sfx_page():
    d = 0.35
    t = t_axis(d)
    x = bp_fft(noise(d), 1500, 7000) * np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.5
    x *= 1 + 0.6 * np.sin(2 * np.pi * 38 * t)
    return norm(x, 0.5)


def sfx_tick():
    d = 0.08
    t = t_axis(d)
    x = bp_fft(noise(d), 2000, 6000) * np.exp(-t * 120) + np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 90)
    return norm(x, 0.6)


def sfx_click():
    d = 0.06
    t = t_axis(d)
    x = np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 140) + 0.4 * bp_fft(noise(d), 2000, 8000) * np.exp(-t * 200)
    return norm(x, 0.6)


def sfx_pop():
    d = 0.18
    t = t_axis(d)
    f = 300 + 900 * np.exp(-t * 40)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.001, 0.05)
    return norm(x, 0.7)


def sfx_check():
    a = sfx_pop()
    t = t_axis(0.5)
    b = (np.sin(2 * np.pi * 1568 * t) + 0.4 * np.sin(2 * np.pi * 2093 * t)) * env(len(t), 0.002, 0.15)
    out = np.zeros(len(t) + int(0.08 * SR))
    out[: len(a)] += a
    out[int(0.08 * SR):] += b * 0.7
    return norm(out, 0.7)


def sfx_notify():
    out = np.zeros(int(0.8 * SR))
    for i, fr in enumerate([880, 1320]):
        st = int(i * 0.13 * SR)
        n = int(0.5 * SR)
        tt = np.arange(n) / SR
        out[st:st + n] += np.sin(2 * np.pi * fr * tt) * env(n, 0.003, 0.12)
    return norm(out, 0.6)


def sfx_cash():
    # "cha-ching": drawer slide + two bell hits
    d = 1.4
    out = np.zeros(int(d * SR))
    slide = bp_fft(noise(0.18), 800, 5000) * np.hanning(int(0.18 * SR))
    out[: len(slide)] += slide * 0.6
    for st, base in [(0.16, 2093), (0.30, 2637)]:
        s = int(st * SR)
        n = len(out) - s
        tt = np.arange(n) / SR
        bell = sum(np.sin(2 * np.pi * base * m * tt) / (k + 1) for k, m in enumerate([1, 1.5, 2.76, 5.4]))
        out[s:] += bell * env(n, 0.001, 0.35)
    return norm(out, 0.85)


def sfx_coins():
    d = 2.2
    out = np.zeros(int(d * SR))
    for k in range(45):
        st = int(rng.uniform(0, 1.8) * SR)
        n = int(0.25 * SR)
        tt = np.arange(n) / SR
        fr = rng.uniform(3500, 7500)
        x = (np.sin(2 * np.pi * fr * tt) + 0.6 * np.sin(2 * np.pi * fr * 1.41 * tt)) * env(n, 0.0005, 0.04)
        out[st:st + n] += x[: len(out) - st] * rng.uniform(0.2, 1)
    return norm(out, 0.6)


def sfx_counter():
    d = 1.5
    out = np.zeros(int(d * SR))
    c = sfx_click()
    tt = 0.0
    gap = 0.03
    while tt < d - 0.1:
        s = int(tt * SR)
        out[s:s + len(c)] += c * 0.6
        tt += gap
        gap *= 1.04
    return norm(out, 0.5)


def sfx_drumroll():
    d = 1.75
    out = np.zeros(int(d * SR))
    tt = 0.0
    while tt < d - 0.05:
        s = int(tt * SR)
        n = int(0.06 * SR)
        hit = bp_fft(noise(0.06), 150, 4000) * env(n, 0.001, 0.02)
        out[s:s + n] += hit * (0.4 + 0.6 * tt / d)
        tt += 0.035
    return norm(out, 0.8)


def sfx_crash():
    d = 2.5
    t = t_axis(d)
    x = hp_fft(noise(d), 3000) * env(len(t), 0.001, 0.7)
    return norm(x, 0.6)


def sfx_dhol():
    d = 0.8
    out = np.zeros(int(d * SR))
    for st, f0, g in [(0.0, 75, 1.0), (0.18, 180, 0.6), (0.27, 180, 0.5), (0.36, 75, 0.9)]:
        s = int(st * SR)
        n = int(0.4 * SR)
        tt = np.arange(n) / SR
        x = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 0.6 * np.exp(-tt * 30))) / SR) * env(n, 0.001, 0.12)
        out[s:s + n] += x[: len(out) - s] * g
    return norm(np.tanh(out * 1.5), 0.9)


def sfx_fire():
    d = 2.0
    t = t_axis(d)
    rumble = lp_fft(noise(d), 500) * 0.5
    crackle = np.zeros(len(t))
    for k in range(60):
        s = int(rng.uniform(0, d - 0.02) * SR)
        n = int(0.01 * SR)
        crackle[s:s + n] += noise(0.01)[:n] * rng.uniform(0.3, 1)
    x = (rumble + hp_fft(crackle, 1500)) * np.minimum(1, np.minimum(t / 0.2, (d - t) / 0.6))
    return norm(x, 0.6)


def sfx_rattle():
    d = 3.5
    out = np.zeros(int(d * SR))
    for k in range(140):
        s = int(rng.uniform(0, d - 0.05) * SR)
        n = int(0.04 * SR)
        tt = np.arange(n) / SR
        fr = rng.uniform(900, 2500)
        out[s:s + n] += np.sin(2 * np.pi * fr * tt) * env(n, 0.0005, 0.01) * rng.uniform(0.2, 1)
    t = t_axis(d)
    out *= np.minimum(1, np.minimum(t / 0.3, (d - t) / 0.5))
    return norm(out, 0.5)


def sfx_rocket():
    """Diwali rocket: rising whistle then a crackling burst."""
    d = 2.2
    t = t_axis(d)
    out = np.zeros(len(t))
    rise = int(0.9 * SR)
    tt = t[:rise]
    f = 900 + 2200 * (tt / 0.9) ** 1.5
    out[:rise] = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.35 * np.minimum(1, tt / 0.1)
    b = len(t) - rise
    tb = np.arange(b) / SR
    boom = np.sin(2 * np.pi * (60 * np.exp(-tb * 5) + 40) * tb) * np.exp(-tb * 5)
    crackle = np.zeros(b)
    for k in range(70):
        s = int(rng.uniform(0.05, 1.1) * SR)
        m = int(0.008 * SR)
        crackle[s:s + m] += noise(0.008)[:m] * rng.uniform(0.2, 1) * np.exp(-s / SR * 1.5)
    out[rise:] = boom + hp_fft(crackle, 2000) * 1.5
    return norm(np.tanh(out * 1.5), 0.9)


def sfx_cracker():
    d = 0.7
    t = t_axis(d)
    bang = noise(d) * np.exp(-t * 18)
    body = np.sin(2 * np.pi * (80 * np.exp(-t * 10) + 45) * t) * np.exp(-t * 9)
    return norm(np.tanh(2.5 * (lp_fft(bang, 4000) + body)), 0.95)


def sfx_bell():
    """Temple bell (ghanti)."""
    d = 2.5
    t = t_axis(d)
    partials = [(1, 1.0), (2.32, 0.6), (4.25, 0.35), (6.63, 0.2)]
    x = sum(a * np.sin(2 * np.pi * 820 * m * t) * np.exp(-t * (1.2 + m * 0.5)) for m, a in partials)
    x *= 1 + 0.15 * np.sin(2 * np.pi * 5 * t)
    return norm(x * np.minimum(1, t / 0.002), 0.7)


def sfx_riser():
    """Rising noise sweep that builds tension before a reveal."""
    d = 1.6
    t = t_axis(d)
    out = np.zeros(len(t))
    chunks = 16
    L = len(t) // chunks
    n = noise(d)
    for c in range(chunks):
        seg = n[c * L:(c + 1) * L + 256]
        centre = 300 + 5000 * (c / chunks) ** 2
        f = bp_fft(seg, centre * 0.6, centre * 1.5) * np.hanning(len(seg))
        out[c * L:c * L + len(f)] += f[: len(out) - c * L]
    tone = np.sin(2 * np.pi * np.cumsum(200 + 900 * (t / d) ** 2) / SR) * 0.3
    return norm((out + tone) * (t / d) ** 1.5, 0.8)


def sfx_laser():
    d = 0.6
    t = t_axis(d)
    f = 2400 * np.exp(-t * 5) + 300
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.4 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR)
    return norm(lp_fft(x, 6000) * env(len(t), 0.005, 0.25), 0.55)


def sfx_glitch():
    d = 0.35
    out = noise(d) * 0
    for k in range(9):
        s = int(rng.uniform(0, d - 0.04) * SR)
        m = int(rng.uniform(0.01, 0.04) * SR)
        fr = rng.uniform(200, 3000)
        tt = np.arange(m) / SR
        out[s:s + m] += np.sign(np.sin(2 * np.pi * fr * tt)) * rng.uniform(0.3, 1)
    return norm(bp_fft(out, 300, 7000), 0.5)


def sfx_reels():
    """Slot-machine reels spinning then stopping."""
    d = 1.8
    out = np.zeros(int(d * SR))
    c = sfx_click()
    tt, gap = 0.0, 0.025
    while tt < d - 0.3:
        s = int(tt * SR)
        out[s:s + len(c)] += c * 0.5
        tt += gap
        gap *= 1.035
    for st in (d - 0.45, d - 0.3, d - 0.15):
        s = int(st * SR)
        th = sfx_stamp()[: int(0.15 * SR)] * 0.6
        out[s:s + len(th)] += th[: len(out) - s]
    return norm(out, 0.7)


def sfx_vault():
    """Heavy metal door: clunk, then a low creak."""
    d = 2.0
    t = t_axis(d)
    clunk = np.sin(2 * np.pi * 70 * t) * np.exp(-t * 12) + bp_fft(noise(d), 400, 2500) * np.exp(-t * 30) * 0.6
    creak_f = 110 + 25 * np.sin(2 * np.pi * 3 * t)
    creak = np.sign(np.sin(2 * np.pi * np.cumsum(creak_f) / SR)) * 0.15
    creak = lp_fft(creak, 1500) * np.clip((t - 0.3) / 0.2, 0, 1) * np.exp(-np.clip(t - 0.5, 0, None) * 1.5)
    return norm(np.tanh(2 * (clunk + creak)), 0.9)


def sfx_cheer():
    """Small crowd cheer: band-limited noise swell with a few claps."""
    d = 2.4
    t = t_axis(d)
    crowd = bp_fft(noise(d), 500, 3000) * np.sin(np.pi * np.clip(t / d, 0, 1)) ** 0.7
    crowd *= 1 + 0.3 * np.sin(2 * np.pi * 4 * t)
    claps = np.zeros(len(t))
    for k in range(40):
        s = int(rng.uniform(0, d - 0.05) * SR)
        m = int(0.02 * SR)
        claps[s:s + m] += hp_fft(noise(0.02), 1200)[:m] * np.exp(-np.arange(m) / SR * 200) * rng.uniform(0.3, 1)
    return norm(crowd * 0.6 + claps, 0.6)


def sfx_swoosh_up():
    d = 0.9
    t = t_axis(d)
    x = bp_fft(noise(d), 800, 6000) * np.sin(np.pi * t / d) ** 2
    tone = np.sin(2 * np.pi * np.cumsum(400 + 1200 * t / d) / SR) * 0.2 * np.sin(np.pi * t / d)
    return norm(x + tone, 0.6)


def sfx_impact():
    """Cinematic hit: sub drop plus bright transient."""
    d = 2.0
    t = t_axis(d)
    sub = np.sin(2 * np.pi * np.cumsum(55 * np.exp(-t * 1.5) + 30) / SR) * np.exp(-t * 1.8)
    hit = hp_fft(noise(d), 2500) * np.exp(-t * 25) * 0.8
    return norm(np.tanh((sub + hit) * 2.2), 0.95)


EFFECTS = {name[4:]: fn for name, fn in globals().items() if name.startswith("sfx_")}


# ---------------------------------------------------------------- music bed
def music_bed_edm(dur):
    """Festive EDM-ish bed: four-on-the-floor kick, off-beat hats, minor pad, bell arpeggio."""
    bpm = 120
    beat = 60 / bpm
    n = int(dur * SR)
    out = np.zeros(n)
    t_all = np.arange(n) / SR
    chords = [[220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [196.0, 246.9, 293.7], [164.8, 207.7, 246.9]]
    bar = beat * 4
    pad = np.zeros(n)
    for i in range(int(dur / bar) + 1):
        s, e = int(i * bar * SR), min(n, int((i + 1) * bar * SR))
        if s >= n:
            break
        tt = np.arange(e - s) / SR
        seg = sum(np.sign(np.sin(2 * np.pi * f * tt)) * 0.3 + np.sin(2 * np.pi * f / 2 * tt) for f in chords[i % 4])
        pad[s:e] += seg * np.minimum(1, np.minimum(tt / 0.08, (bar - tt) / 0.08))
    out += lp_fft(pad, 900) * 0.05
    k = 0
    while k * beat / 2 < dur:
        s = int(k * beat / 2 * SR)
        if k % 2 == 0:  # kick on every beat
            m = int(0.3 * SR)
            tt = np.arange(m) / SR
            x = np.sin(2 * np.pi * np.cumsum(50 + 120 * np.exp(-tt * 30)) / SR) * env(m, 0.001, 0.12)
            out[s:s + m] += x[: n - s] * 0.5
        else:  # off-beat hat
            m = int(0.06 * SR)
            out[s:s + m] += hp_fft(noise(0.06), 7000)[:m][: n - s] * env(m, 0.001, 0.02)[: n - s] * 0.18
        if k % 8 == 4:  # clap
            m = int(0.15 * SR)
            out[s:s + m] += bp_fft(noise(0.15), 900, 4000)[:m][: n - s] * env(m, 0.001, 0.05)[: n - s] * 0.25
        k += 1
    arp = [880.0, 1046.5, 1318.5, 1046.5]
    k = 0
    while k * beat / 2 < dur:
        s = int(k * beat / 2 * SR)
        m = int(0.3 * SR)
        tt = np.arange(m) / SR
        f = arp[k % 4] * (0.75 if (k // 16) % 2 else 1)
        x = (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * 2.76 * f * tt)) * env(m, 0.001, 0.08)
        out[s:s + m] += x[: n - s] * 0.04
        k += 1
    fade = np.minimum(1, np.minimum(t_all / 1.0, (dur - t_all) / 2.0))
    return out * np.clip(fade, 0, 1)


def music_bed(dur):
    """Light upbeat bhangra-flavoured loop: dhol-ish percussion, shaker, pad, pluck."""
    bpm = 112
    beat = 60 / bpm
    n = int(dur * SR)
    out = np.zeros(n)
    # chord roots: C - Am - F - G (2 bars each, 4 beats per bar)
    chords = [[261.6, 329.6, 392.0], [220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [196.0, 246.9, 293.7]]
    bar = beat * 4
    t_all = np.arange(n) / SR
    # pad
    pad = np.zeros(n)
    for i in range(int(dur / bar) + 1):
        ch = chords[(i // 1) % 4]
        s = int(i * bar * SR)
        e = min(n, int((i + 1) * bar * SR))
        if s >= n:
            break
        tt = np.arange(e - s) / SR
        seg = sum(np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * f * 2.003 * tt) for f in ch)
        fade = np.minimum(1, np.minimum(tt / 0.05, (bar - tt) / 0.05))
        pad[s:e] += seg * fade
    out += lp_fft(pad, 1400) * 0.10
    # percussion
    k = 0
    while k * beat / 2 < dur:
        st = k * beat / 2
        s = int(st * SR)
        step = k % 8
        if step in (0, 3, 4, 6):  # dhol bass "dha"
            m = int(0.35 * SR)
            tt = np.arange(m) / SR
            x = np.sin(2 * np.pi * np.cumsum(70 * (1 + 0.8 * np.exp(-tt * 35))) / SR) * env(m, 0.001, 0.1)
            out[s:s + m] += x[: n - s] * 0.55
        if step in (2, 5, 7):  # high "tak"
            m = int(0.12 * SR)
            tt = np.arange(m) / SR
            x = np.sin(2 * np.pi * 380 * tt) * env(m, 0.001, 0.03) + bp_fft(noise(0.12), 1500, 5000)[:m] * env(m, 0.001, 0.02) * 0.5
            out[s:s + m] += x[: n - s] * 0.35
        # shaker on every half beat
        m = int(0.07 * SR)
        x = hp_fft(noise(0.07), 6000)[:m] * env(m, 0.004, 0.02)
        out[s:s + m] += x[: n - s] * (0.12 if step % 2 else 0.07)
        k += 1
    # pluck melody (pentatonic, sparse)
    scale = [523.3, 587.3, 659.3, 784.0, 880.0]
    pattern = [0, 2, 3, 2, 4, 3, 2, 1, 0, 2, 3, 4, 3, 2, 1, 2]
    k = 0
    while k * beat < dur:
        if k % 2 == 0:
            s = int(k * beat * SR)
            f = scale[pattern[(k // 2) % len(pattern)]]
            m = int(0.4 * SR)
            tt = np.arange(m) / SR
            x = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt)) * env(m, 0.002, 0.12)
            out[s:s + m] += x[: n - s] * 0.08
        k += 1
    fade = np.minimum(1, np.minimum(t_all / 1.0, (dur - t_all) / 2.0))
    return out * np.clip(fade, 0, 1)


def decode(rel):
    path = os.path.join(BUILD, os.path.basename(rel) + ".wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(ROOT, "assets", rel),
                    "-ac", "1", "-ar", str(SR), path], check=True)
    with wave.open(path) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768


def read_voice():
    """Lays out the voice clips listed in the timeline's VOICE_CLIPS."""
    out = np.zeros(int(DURATION * SR))
    cache = {}
    for at, rel, src_s, src_e in T.VOICE_CLIPS:
        if rel not in cache:
            cache[rel] = decode(rel)
        x = cache[rel][int(src_s * SR):None if src_e is None else int(src_e * SR)]
        s = int(at * SR)
        e = min(len(out), s + len(x))
        out[s:e] += x[: e - s]
    return out


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    stereo = np.stack([x, x], axis=1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((stereo * 32767).astype(np.int16).tobytes())


def main():
    os.makedirs(BUILD, exist_ok=True)
    n = int(DURATION * SR)
    voice = read_voice()

    cache = {}
    sfx = np.zeros(n)
    for t, name, gain in SFX:
        if name not in cache:
            cache[name] = EFFECTS[name]()
        x = cache[name]
        s = int(t * SR)
        e = min(n, s + len(x))
        sfx[s:e] += x[: e - s] * gain

    music = music_bed_edm(DURATION) if getattr(T, "MUSIC", "") == "edm" else music_bed(DURATION)

    # voice envelope -> ducking for music and per-frame lip-sync data
    win = int(0.05 * SR)
    venv = np.sqrt(np.convolve(voice ** 2, np.ones(win) / win, mode="same"))
    duck = 1 - 0.55 * np.clip(venv / 0.05, 0, 1)
    duck = np.convolve(duck, np.ones(int(0.15 * SR)) / int(0.15 * SR), mode="same")

    music_level = 0.32
    mix = voice * 1.0 + sfx * 0.42 + music * music_level * duck
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)  # gentle soft-clip limiter
    write_wav(os.path.join(BUILD, "mix.wav"), norm(mix, 0.95))

    frames = int(DURATION * FPS)
    hop = SR / FPS
    fr_env = np.array([np.sqrt(np.mean(voice[int(i * hop):int((i + 1) * hop)] ** 2) + 1e-12) for i in range(frames)])
    fr_env = fr_env / (np.percentile(fr_env, 95) or 1)
    np.save(os.path.join(BUILD, "voice_env.npy"), np.clip(fr_env, 0, 1.4))
    print("audio ok:", os.path.join(BUILD, "mix.wav"))


if __name__ == "__main__":
    main()
