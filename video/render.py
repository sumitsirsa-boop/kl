"""Renders the full video: background, scenes/B-roll, presenter, captions, transitions.

Usage:
  python3 video/build_audio.py           # once, makes build/mix.wav + build/voice_env.npy
  python3 video/render.py                # full render -> output/punjab_dear_1000_ticket.mp4
  python3 video/render.py --still 28.5   # single frame preview PNG at t=28.5s
  Add `--project diwali` (to both scripts) to build the Diwali Bumper video instead.
"""
import argparse
import math
import os
import subprocess
import sys
from functools import lru_cache
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gfx import (GOLD, NAVY, RED, ROOT, WHITE, clamp, ease_in_out, ease_out_back, ease_out_cubic, font, glow_sprite,
                 gradient_box, lerp, paste, prog, rounded_box, text_img, wrap_words)
from presenter import PH, PW, presenter_img, presenter_shadow, presenter_state
from project import load

T, SC = load("timeline"), load("scenes")
SCENE_FUNCS = SC.SCENE_FUNCS
DURATION, FPS, H, LINES, SCENES, W, scene_at = T.DURATION, T.FPS, T.H, T.LINES, T.SCENES, T.W, T.scene_at

# Per-project look and layout (the Dear 1000 video uses the defaults)
BG_COLORS = getattr(T, "BG_COLORS", ((18, 30, 120), (40, 70, 200), (70, 20, 140)))
RAY_COLOR = getattr(T, "RAY_COLOR", (255, 220, 90))
HEADER_SPAN = getattr(T, "HEADER_SPAN", (5.55, 65.4))
SHAKES = getattr(T, "SHAKES", ((27.2, 18), (10.3, 10), (28.95, 12)))
BOOST_SCENES = getattr(T, "BOOST_SCENES", ("jackpot",))
CAPTION_BOTTOM = getattr(T, "CAPTION_BOTTOM", 1880)

BUILD = os.path.join(ROOT, "build", getattr(T, "BUILD_NAME", ""))
OUT = os.path.join(ROOT, "output")

# ------------------------------------------------------------------ background
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
_ANG = np.arctan2(_yy - 760, _xx - W / 2)
_RAD = np.sqrt((_xx - W / 2) ** 2 + (_yy - 760) ** 2)
_FALL = np.clip(1 - _RAD / 1500, 0, 1)
_BASE = np.zeros((H, W, 3), np.float32)
_top, _mid, _bot = (np.array(c, np.float32) for c in BG_COLORS)
_k = (_yy / H)[..., None]
_BASE[:] = np.where(_k < 0.5, _top + (_mid - _top) * (_k / 0.5), _mid + (_bot - _mid) * ((_k - 0.5) / 0.5))
_BASE *= (1 - 0.35 * np.clip(_RAD / 1400, 0, 1) ** 2)[..., None]  # vignette


def background(t, intensity=1.0):
    rays = np.clip(np.sin(_ANG * 14 + t * 0.35) * 4, 0, 1) * _FALL
    amt = (0.10 * intensity)
    img = _BASE + rays[..., None] * amt * np.array(RAY_COLOR, np.float32)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def bokeh(canvas, t):
    import random
    rnd = random.Random(2)
    for i in range(22):
        x = rnd.uniform(0, W)
        sp = rnd.uniform(25, 60)
        y = (rnd.uniform(0, H) - t * sp) % (H + 200) - 100
        r = int(rnd.uniform(20, 60)) // 4 * 4 + 4
        paste(canvas, glow_sprite(r, (255, 230, 150), 0.35), x + math.sin(t * 0.7 + i) * 20, y)


# ------------------------------------------------------------------ header
@lru_cache(maxsize=None)
def default_header_img():
    w, h = 1000, 120
    img = gradient_box(w, h, 26, (235, 40, 50), (150, 10, 30), outline=GOLD + (255,), width=4, shadow=10, horizontal=True)
    off = 20
    t1 = text_img("PUNJAB STATE DEAR 1000", "anton", 54, fill=WHITE)
    img.alpha_composite(t1, (off + 30, off + 4))
    t2 = text_img("QUARTERLY LOTTERY • GOVT. OF PUNJAB", "semi", 26, fill=(255, 230, 160))
    img.alpha_composite(t2, (off + 34, off + 72))
    chip = rounded_box(250, 84, 20, GOLD + (255,))
    d = ImageDraw.Draw(chip)
    d.text((125, 26), "5th DRAW", font=font("anton", 30), fill=NAVY, anchor="mm")
    d.text((125, 60), "09-01-2027", font=font("anton", 34), fill=RED, anchor="mm")
    img.alpha_composite(chip, (off + w - 270, off + 18))
    return img


def draw_header(c, t):
    a, b = HEADER_SPAN
    if t < a or t > b:
        return
    p = ease_out_cubic(prog(t, a, 0.5)) * (1 - prog(t, b - 0.4, 0.4))
    img = SC.header_img() if hasattr(SC, "header_img") else default_header_img()
    paste(c, img, W / 2, lerp(-120, 100, p))


# ------------------------------------------------------------------ presenter
# big host for intro and the closing scenes, picture-in-picture otherwise
BIG_MODE = getattr(T, "BIG_MODE", [(0.0, 5.55), (65.5, DURATION)])


def presenter_mode(t):
    """0 = big centre, 1 = picture-in-picture; blended over 0.5s transitions."""
    for a, b in BIG_MODE:
        if a <= t < b:
            return 1 - ease_in_out(clamp((t - a) / 0.5)) if a > 0 else 0.0
    # in PIP span: shrink in over 0.5s after the most recent big span ended
    last_end = max((b for a, b in BIG_MODE if b <= t), default=0.0)
    return ease_in_out(clamp((t - last_end) / 0.5))


@lru_cache(maxsize=None)
def pip_ring():
    s = 340
    img = Image.new("RGBA", (s + 40, s + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((20, 20, 20 + s, 20 + s), outline=GOLD + (255,), width=10)
    return img


@lru_cache(maxsize=None)
def pip_bg():
    s = 330
    g = gradient_box(s, s, s // 2, (250, 245, 230), (200, 215, 255))
    return g


@lru_cache(maxsize=None)
def host_tag():
    return text_img(" HOST ", "anton", 34, fill=WHITE)


def draw_presenter(c, t, frame, env):
    mouth, blink, brow = presenter_state(frame, env)
    img = presenter_img(mouth, blink, brow)
    level = env[min(frame, len(env) - 1)]
    bob = math.sin(t * 2.2) * 4 + level * 6
    tilt = math.sin(t * 1.3) * 1.5
    m = presenter_mode(t)
    intro = ease_out_back(prog(t, 0.0, 0.6))
    if m < 1:
        scale_big = 1.35
        cx_big, cy_big = W / 2, 1665 - PH * scale_big / 2 + (1 - intro) * 800
    if m > 0:
        cy_pip = 1505
        cx_pip = W - 200
    if m <= 0.001:
        paste(c, presenter_shadow(), cx_big + 12, cy_big + 20 + bob, scale_big)
        paste(c, img, cx_big, cy_big + bob, scale_big, rot=tilt)
        return
    if m >= 0.999:
        # circular PIP with studio backdrop
        size = 330
        frame_img = pip_bg().copy()
        face = presenter_img(mouth, blink, brow).resize((int(PW * 0.62), int(PH * 0.62)), Image.BICUBIC)
        face = face.rotate(tilt, resample=Image.BICUBIC)
        frame_img.alpha_composite(face, (int(size / 2 - face.width / 2), int(size - face.height + 40 + bob * 0.5)))
        mask = Image.new("L", frame_img.size, 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
        out = Image.new("RGBA", frame_img.size, (0, 0, 0, 0))
        out.paste(frame_img, (0, 0), mask)
        paste(c, glow_sprite(220, (255, 220, 120), 0.4), cx_pip, cy_pip)
        paste(c, out, cx_pip, cy_pip)
        paste(c, pip_ring(), cx_pip, cy_pip)
        tag = rounded_box(150, 50, 25, RED + (255,), outline=WHITE + (255,), width=3)
        tg = host_tag()
        tag.alpha_composite(tg, ((tag.width - tg.width) // 2, (tag.height - tg.height) // 2))
        paste(c, tag, cx_pip, cy_pip + 170)
        return
    # transition: shrink/grow between big and PIP
    scale = lerp(1.35, 0.62, m)
    cx = lerp(cx_big, cx_pip, m)
    cy = lerp(cy_big, cy_pip + 40, m)
    paste(c, img, cx, cy + bob, scale, rot=tilt, alpha=1.0)


# ------------------------------------------------------------------ captions
@lru_cache(maxsize=None)
def caption_layout(idx):
    text = LINES[idx][2]
    words = text.split()
    lines = wrap_words(words, "semi", 50, 920)
    return lines


@lru_cache(maxsize=512)
def caption_img(idx, hi):
    lines = caption_layout(idx)
    f = font("semi", 50)
    lh = 72
    box_h = lh * len(lines) + 40
    img = rounded_box(1000, box_h, 30, (8, 12, 40, 215), outline=(255, 205, 40, 160), width=3)
    d = ImageDraw.Draw(img)
    k = 0
    for li, ws in enumerate(lines):
        line_w = f.getlength(" ".join(ws))
        x = (1000 - line_w) / 2
        y = 20 + li * lh + lh / 2
        for w in ws:
            col = GOLD if k == hi else WHITE
            d.text((x, y), w, font=f, fill=col, anchor="lm", stroke_width=2 if k == hi else 0, stroke_fill=(90, 40, 0))
            x += f.getlength(w + " ")
            k += 1
    return img


def caption_word_index(idx, t):
    s, e, text = LINES[idx]
    words = text.split()
    weights = np.array([len(w) + 2 for w in words], float)
    cum = np.cumsum(weights) / weights.sum()
    k = (t - s) / max(0.01, e - s)
    return int(np.searchsorted(cum, k))


def draw_captions(c, t):
    for i, (s, e, _) in enumerate(LINES):
        if s - 0.05 <= t < e + 0.35:
            hi = caption_word_index(i, t) if t < e else -1
            img = caption_img(i, hi)
            p = ease_out_cubic(prog(t, s - 0.05, 0.2))
            out = prog(t, e + 0.15, 0.2)
            paste(c, img, W / 2, CAPTION_BOTTOM - img.height / 2 + (1 - p) * 30, alpha=p * (1 - out))
            return


# ------------------------------------------------------------------ transitions
def draw_transition(c, t):
    for name, s in SCENES[1:]:
        k = (t - s + 0.18) / 0.4
        if 0 < k < 1:
            x = lerp(-W * 1.6, W * 1.6, ease_in_out(k))
            band = Image.new("RGBA", (W * 2, H * 3), (0, 0, 0, 0))
            d = ImageDraw.Draw(band)
            d.rectangle((W - 260, 0, W - 140, H * 3), fill=GOLD + (255,))
            d.rectangle((W - 130, 0, W + 260, H * 3), fill=RED + (255,))
            d.rectangle((W + 270, 0, W + 320, H * 3), fill=WHITE + (255,))
            band = band.rotate(15, resample=Image.BILINEAR)
            paste(c, band, W / 2 + x, H / 2)


def render_frame(frame, env):
    t = frame / FPS
    name, s, e = scene_at(t)
    intensity = 2.5 if name in BOOST_SCENES else 1.0
    c = background(t, intensity)
    bokeh(c, t)
    # screen shake on impacts
    shake = 0.0
    for ts, amp in SHAKES:
        if 0 <= t - ts < 0.4:
            shake = max(shake, amp * (1 - (t - ts) / 0.4))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)) if shake else c
    SCENE_FUNCS[name](layer, t, s, e)
    if shake:
        dx, dy = int(math.sin(t * 90) * shake), int(math.cos(t * 77) * shake)
        c.alpha_composite(layer, (max(0, dx), max(0, dy)), (max(0, -dx), max(0, -dy)))
    draw_header(c, t)
    draw_presenter(c, t, frame, env)
    if hasattr(SC, "overlay"):
        SC.overlay(c, t)
    draw_captions(c, t)
    draw_transition(c, t)
    # fade in/out
    fade = min(clamp(t / 0.3), clamp((DURATION - t) / 0.6))
    if fade < 1:
        c.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - fade)))))
    return c.convert("RGB")


def render_chunk(args):
    idx, f0, f1 = args
    env = np.load(os.path.join(BUILD, "voice_env.npy"))
    path = os.path.join(BUILD, f"part_{idx:02d}.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fr in range(f0, f1):
        proc.stdin.write(render_frame(fr, env).tobytes())
        if (fr - f0) % 150 == 0:
            print(f"  chunk {idx}: frame {fr}/{f1}", flush=True)
    proc.stdin.close()
    proc.wait()
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--still", type=float, nargs="*")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--project", default="")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    env = np.load(os.path.join(BUILD, "voice_env.npy"))
    if a.still:
        for ts in a.still:
            p = os.path.join(BUILD, f"still_{ts:05.2f}.png")
            render_frame(int(ts * FPS), env).save(p)
            print(p)
        return
    total = int(DURATION * FPS)
    n = a.jobs * 2
    bounds = [(i, total * i // n, total * (i + 1) // n) for i in range(n)]
    with Pool(a.jobs) as pool:
        parts = pool.map(render_chunk, bounds)
    lst = os.path.join(BUILD, "parts.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in parts)
    final = os.path.join(OUT, getattr(T, "OUTPUT_FILE", "punjab_dear_1000_ticket.mp4"))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-i", os.path.join(BUILD, "mix.wav"), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", final], check=True)
    print("done:", final)


if __name__ == "__main__":
    main()
