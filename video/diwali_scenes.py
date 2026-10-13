"""Scenes for the Punjab State Dear Diwali Bumper 2026 video (Diwali theme).

Reuses the generic widgets from scenes.py (ribbons, pills, prize cards, phone, contact card...)
and adds Diwali elements: fireworks, diyas, rangoli, marigold toran, 12-rashi tiles,
plus an always-on agency ticker and periodic contact pop-ups.
"""
import math
import os
import random
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import scenes as base
from diwali_timeline import CONTACT_POPUPS, CONTACT_START, RASHI_TIMES
from gfx import (DEEP_RED, GOLD, GOLD_LIGHT, GREEN, NAVY, ORANGE, PINK, RED, ROOT, WHITE, clamp, ease_in_out,
                 ease_out_back, ease_out_cubic, ease_out_elastic, font, glow_sprite, grad_text, gradient_box,
                 indian_format, lerp, paste, prog, rounded_box, supersampled, text_img)
from timeline import H, W

CX = W // 2
MAROON = (110, 10, 40)
title_in, pill, ribbon, sparkles = base.title_in, base.pill, base.ribbon, base.sparkles

AGENCY = "SUMIT LOTTERY AGENCY"
ADDRESS = "One Way Traffic Road, Mansa"
PHONES = ("70598 77770", "89688 69862")


def gold_ribbon(text, w=620, h=96, size=58, fname="anton"):
    return ribbon(text, w, h, (200, 30, 60), (110, 10, 40), size, fname)


# ================================================================== ticket
@lru_cache(maxsize=None)
def ticket_full():
    return Image.open(os.path.join(ROOT, "assets", "diwali", "ticket.jpg")).convert("RGBA")


@lru_cache(maxsize=None)
def ticket_front(width=980):
    img = ticket_full().crop((0, 0, 1292, 800))
    h = int(img.height * width / img.width)
    img = img.resize((width, h), Image.LANCZOS)
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, img.width - 1, img.height - 1), 18, fill=255)
    out = Image.new("RGBA", (img.width + 60, img.height + 60), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 170), (30, 42), mask)
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    out.paste(img, (30, 30), mask)
    return out


@lru_cache(maxsize=None)
def ticket_crop(box, width):
    img = ticket_full().crop(box)
    h = int(img.height * width / img.width)
    img = img.resize((width, h), Image.LANCZOS)
    framed = Image.new("RGBA", (width + 16, h + 16), GOLD + (255,))
    framed.paste(img, (8, 8))
    mask = Image.new("L", framed.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, framed.width - 1, framed.height - 1), 20, fill=255)
    out = Image.new("RGBA", framed.size, (0, 0, 0, 0))
    out.paste(framed, (0, 0), mask)
    return out


# ================================================================== Diwali elements
FW_COLS = [(255, 210, 80), (255, 90, 120), (120, 220, 255), (150, 255, 140), (255, 150, 40), (220, 140, 255)]


def firework(c, t, t0, x, y, col, seed=0, n=48, radius=330, rise=0.7):
    """Rocket rises for `rise` seconds from the bottom, then bursts at (x, y)."""
    lt = t - t0
    if lt < 0 or lt > rise + 2.0:
        return
    d = ImageDraw.Draw(c)
    if lt < rise:
        k = ease_out_cubic(lt / rise)
        ry = lerp(H + 50, y, k)
        for j in range(6):
            yy = ry + j * 16
            a = int(255 * (1 - j / 6))
            d.ellipse((x - 4, yy - 4, x + 4, yy + 4), fill=(255, 230, 160, a))
        return
    bt = lt - rise
    fade = clamp(1 - bt / 1.9)
    if bt < 0.25:
        paste(c, glow_sprite(200, col, 0.6), x, y, 1 + bt * 3, alpha=1 - bt / 0.25)
    rnd = random.Random(seed)
    for i in range(n):
        ang = 2 * math.pi * i / n + rnd.uniform(-0.05, 0.05)
        sp = radius * rnd.uniform(0.75, 1.05)
        r = sp * ease_out_cubic(min(1, bt / 0.9))
        px = x + math.cos(ang) * r
        py = y + math.sin(ang) * r + 120 * bt * bt
        for j in range(3):  # short trails
            rr = r * (1 - 0.06 * (j + 1))
            tx = x + math.cos(ang) * rr
            ty = y + math.sin(ang) * rr + 120 * bt * bt
            a = int(255 * fade * (0.6 - j * 0.18))
            d.ellipse((tx - 3, ty - 3, tx + 3, ty + 3), fill=col + (max(0, a),))
        tw = 0.6 + 0.4 * math.sin(t * 30 + i)
        d.ellipse((px - 5, py - 5, px + 5, py + 5), fill=(255, 255, 230, int(255 * fade * tw)))


def firework_show(c, t, t0, bursts, seed=1):
    for i, (dt, x, y) in enumerate(bursts):
        firework(c, t, t0 + dt, x, y, FW_COLS[(i + seed) % len(FW_COLS)], seed=seed * 10 + i)


@lru_cache(maxsize=None)
def diya_base():
    def draw(d, s, img):
        d.pieslice((0, -40 * s, 140 * s, 70 * s), 0, 180, fill=(200, 80, 20))
        d.pieslice((10 * s, -30 * s, 130 * s, 58 * s), 0, 180, fill=(235, 120, 40))
        d.ellipse((0, 0, 140 * s, 22 * s), fill=(150, 50, 10))
        for k in range(5):
            x = 22 + k * 24
            d.ellipse(((x - 5) * s, 34 * s, (x + 5) * s, 44 * s), fill=GOLD)
    return supersampled(140, 70, draw)


@lru_cache(maxsize=None)
def flame_sprite(h):
    def draw(d, s, img):
        w = h * 0.5
        d.ellipse((0, h * 0.35 * s, w * s, h * s), fill=(255, 150, 20))
        d.polygon([(0, h * 0.68 * s), (w * s, h * 0.68 * s), (w / 2 * s, 0)], fill=(255, 150, 20))
        d.ellipse((w * 0.25 * s, h * 0.55 * s, w * 0.75 * s, h * 0.95 * s), fill=(255, 240, 160))
    return supersampled(int(h * 0.5) + 1, int(h), draw)


def diya(c, t, x, y, scale=1.0, seed=0):
    flick = 1 + 0.12 * math.sin(t * 17 + seed) + 0.06 * math.sin(t * 29 + seed * 2)
    paste(c, glow_sprite(90, (255, 170, 60), 0.55), x, y - 55 * scale, scale * flick)
    paste(c, flame_sprite(56), x, y - 48 * scale, scale, sy=flick, rot=math.sin(t * 6 + seed) * 6)
    paste(c, diya_base(), x, y + 10 * scale, scale)


def diya_row(c, t, y, xs, scale=0.8, start=0.0):
    for i, x in enumerate(xs):
        p = prog(t, start + i * 0.08, 0.35)
        if p > 0:
            diya(c, t, x, y + (1 - ease_out_back(p)) * 60, scale, seed=i)


@lru_cache(maxsize=None)
def rangoli(size=640):
    def draw(d, s, img):
        c = size * s / 2
        rings = [(0.48, 16, (255, 120, 30)), (0.40, 12, (230, 30, 110)), (0.31, 10, (255, 205, 40)),
                 (0.22, 8, (40, 180, 200)), (0.13, 6, (255, 255, 255))]
        for r, n, col in rings:
            R = r * size * s
            pr = R * 0.33
            for k in range(n):
                a = 2 * math.pi * k / n
                px, py = c + math.cos(a) * (R - pr), c + math.sin(a) * (R - pr)
                d.ellipse((px - pr, py - pr * 0.7, px + pr, py + pr * 0.7), fill=col + (200,))
        d.ellipse((c - 0.06 * size * s, c - 0.06 * size * s, c + 0.06 * size * s, c + 0.06 * size * s), fill=GOLD)
    return supersampled(size, size, draw)


@lru_cache(maxsize=None)
def toran():
    """Marigold garland swags with mango leaves, across the top of the frame."""
    w, h = W, 190

    def draw(d, s, img):
        swags = 4
        sw = w / swags
        for k in range(swags):
            x0 = k * sw
            for i in range(26):
                u = i / 25
                x = x0 + u * sw
                y = 20 + math.sin(u * math.pi) * 95
                col = (255, 150, 20) if i % 2 else (255, 205, 40)
                r = 15
                d.ellipse(((x - r) * s, (y - r) * s, (x + r) * s, (y + r) * s), fill=col)
            # hanging strand + leaf
            xm = x0 + sw / 2
            for j in range(4):
                y = 130 + j * 14
                d.ellipse(((xm - 10) * s, (y - 10) * s, (xm + 10) * s, (y + 10) * s), fill=(255, 120, 20))
            d.polygon([(xm * s, 180 * s), ((xm - 14) * s, 200 * s), (xm * s, 230 * s), ((xm + 14) * s, 200 * s)],
                      fill=(40, 140, 50))
        for k in range(9):  # leaves along the top
            x = k * w / 8
            d.polygon([(x * s, 0), ((x - 16) * s, 24 * s), (x * s, 56 * s), ((x + 16) * s, 24 * s)], fill=(40, 140, 50))
    return supersampled(w, h + 50, draw)


# ================================================================== header, ticker, pop-ups
@lru_cache(maxsize=None)
def header_img():
    w, h = 1000, 120
    img = gradient_box(w, h, 26, (150, 20, 50), (80, 5, 35), outline=GOLD + (255,), width=4, shadow=10, horizontal=True)
    off = 20
    t1 = text_img("PUNJAB STATE DEAR DIWALI BUMPER 2026", "anton", 44, fill=GOLD_LIGHT)
    img.alpha_composite(t1, (off + 26, off + 10))
    t2 = text_img("1st PRIZE ₹12 CRORE • GOVT. OF PUNJAB", "semi", 26, fill=(255, 230, 190))
    img.alpha_composite(t2, (off + 30, off + 70))
    chip = rounded_box(220, 84, 20, GOLD + (255,))
    d = ImageDraw.Draw(chip)
    d.text((110, 26), "DRAW ON", font=font("anton", 30), fill=MAROON, anchor="mm")
    d.text((110, 60), "16-11-2026", font=font("anton", 34), fill=RED, anchor="mm")
    img.alpha_composite(chip, (off + w - 236, off + 18))
    return img


@lru_cache(maxsize=None)
def ticker_strip():
    item = f"  ★ {AGENCY}  •  {ADDRESS}  •  ☎ {PHONES[0]}  •  ☎ {PHONES[1]}  "
    t = text_img(item, "sym", 30, fill=WHITE)
    return t


def draw_ticker(c, t):
    if t < 1.0 or t > 96.8:
        return
    a = clamp((t - 1.0) / 0.4) * clamp((96.8 - t) / 0.4)
    bar_h, y0 = 56, H - 56
    bar = gradient_box(W, bar_h, 0, (150, 10, 40), (90, 5, 30), horizontal=True)
    d = ImageDraw.Draw(bar)
    d.line((0, 0, W, 0), fill=GOLD, width=4)
    strip = ticker_strip()
    sw = strip.width
    off = -(t * 140) % sw
    x = off - sw
    while x < W:
        bar.alpha_composite(strip, (int(x), (bar_h - strip.height) // 2 + 2), )
        x += sw
    lab = rounded_box(210, bar_h, 0, GOLD + (255,))
    ImageDraw.Draw(lab).text((105, bar_h / 2 + 1), "CONTACT", font=font("anton", 34), fill=MAROON, anchor="mm")
    bar.alpha_composite(lab, (0, 0))
    paste(c, bar, 0, y0, alpha=a, anchor="tl")


@lru_cache(maxsize=None)
def popup_card():
    w, h = 620, 196
    img = gradient_box(w, h, 28, (255, 225, 110), (255, 165, 30), outline=WHITE + (255,), width=5, shadow=12)
    d = ImageDraw.Draw(img)
    off = 24
    d.text((off + 28, off + 44), "टिकट के लिए संपर्क करें", font=font("xbold", 34), fill=MAROON, anchor="lm")
    d.text((off + 28, off + 96), AGENCY, font=font("anton", 56), fill=DEEP_RED, anchor="lm")
    d.text((off + 28, off + 155), f"☎ {PHONES[0]}  |  {PHONES[1]}", font=font("sym", 31), fill=NAVY, anchor="lm")
    return img


def draw_popups(c, t):
    for st in CONTACT_POPUPS:
        lt = t - st
        if 0 <= lt < 4.2:
            p_in = ease_out_back(prog(lt, 0, 0.45))
            p_out = ease_in_out(prog(lt, 3.7, 0.5))
            x = lerp(-420, 345, p_in) - p_out * 800
            paste(c, popup_card(), x, 1515 + math.sin(t * 3) * 4)


def overlay(c, t):
    """Drawn every frame above the scene and presenter (render.py calls this)."""
    draw_popups(c, t)
    draw_ticker(c, t)


# ================================================================== scenes
def scene_intro(c, t, s, e):
    paste(c, rangoli(), CX, 470, 1.0 + 0.03 * math.sin(t * 2), rot=t * 12, alpha=0.55 * prog(t, 0, 0.6))
    firework_show(c, t, 0.15, [(0, 230, 380), (1.75, 850, 300), (3.25, 520, 220)], seed=1)
    paste(c, toran(), CX, 115, alpha=prog(t, 0.0, 0.4))
    title = grad_text("नमस्कार दोस्तों!", "xbold", 116, stroke=8, stroke_fill=MAROON)
    paste(c, title, CX, 400, ease_out_elastic(prog(t, 0.15, 1.0)))
    title_in(c, t, 1.45, grad_text("HAPPY DIWALI", "anton", 130, top=(255, 245, 170), bottom=(255, 120, 20), stroke=7,
                                   stroke_fill=MAROON), CX, 560, "pop")
    title_in(c, t, 3.1, pill("किस्मत चमकाने का सबसे बड़ा मौका!", "xbold", 44, fill=(200, 20, 70, 255), color=WHITE),
             CX, 700, "up")
    sparkles(c, t, CX, 480, (460, 200), 12, seed=11)


def scene_ticket(c, t, s, e):
    lt = t - s
    p = ease_out_cubic(prog(lt, 0, 0.75))
    zoom = 1 + 0.05 * prog(lt, 0.75, 7)
    tk = ticket_front()
    x = lerp(W + 700, CX, p)
    fy = 600 + 10 * math.sin(lt * 2)
    paste(c, glow_sprite(520, (255, 200, 80), 0.35), CX, fy, alpha=p)
    paste(c, tk, x, fy, 0.98 * zoom * lerp(0.7, 1, p), rot=lerp(-25, 0, p))
    title_in(c, t, s + 0.8, grad_text("PUNJAB STATE DEAR", "anton", 100, stroke=6, stroke_fill=MAROON), CX, 1000, "up")
    title_in(c, t, s + 1.1, grad_text("DIWALI BUMPER 2026", "anton", 116, top=(255, 250, 200), bottom=(255, 170, 40),
                                      stroke=7, stroke_fill=MAROON), CX, 1120, "up")
    st = prog(t, 9.75, 0.25)
    if st > 0:
        paste(c, base.official_stamp(), 860, 330, lerp(2.6, 0.9, ease_out_cubic(st)), rot=-12, alpha=min(1, st * 2))
        title_in(c, t, 9.95, pill("पंजाब सरकार की ऑफिशियल लॉटरी", "xbold", 44, fill=(20, 150, 70, 255), color=WHITE),
                 CX, 1260, "pop")


@lru_cache(maxsize=None)
def history_badge():
    def draw(d, s, img):
        c = 300 * s
        pts = []
        for k in range(32):
            r = (290 if k % 2 == 0 else 250) * s
            a = k * math.pi / 16
            pts.append((c + math.cos(a) * r, c + math.sin(a) * r))
        d.polygon(pts, fill=(200, 30, 60))
        d.ellipse((c - 235 * s, c - 235 * s, c + 235 * s, c + 235 * s), fill=GOLD)
        d.ellipse((c - 215 * s, c - 215 * s, c + 215 * s, c + 215 * s), fill=MAROON)
        d.text((c, c - 120 * s), "PUNJAB LOTTERY", font=font("anton", 46 * s), fill=GOLD_LIGHT, anchor="mm")
        d.text((c, c - 20 * s), "FIRST TIME", font=font("anton", 100 * s), fill=WHITE, anchor="mm")
        d.text((c, c + 80 * s), "IN HISTORY", font=font("anton", 70 * s), fill=GOLD, anchor="mm")
        for k in range(5):
            x = c + (k - 2) * 52 * s
            d.text((x, c + 160 * s), "★", font=font("sym", 44 * s), fill=GOLD, anchor="mm")
    return supersampled(600, 600, draw)


def scene_history(c, t, s, e):
    lt = t - s
    paste(c, rangoli(), CX, 640, 1.25, rot=-t * 15, alpha=0.4)
    p = ease_out_elastic(prog(lt, 0.1, 1.0))
    paste(c, history_badge(), CX, 640, p * (1 + 0.02 * math.sin(t * 5)), rot=math.sin(t * 2) * 3)
    title_in(c, t, 13.6, text_img("पंजाब लॉटरी के इतिहास में", "xbold", 58, fill=WHITE, stroke=4, stroke_fill=MAROON,
                                  shadow=4), CX, 290, "up")
    title_in(c, t, 14.3, grad_text("सबसे बड़ा इनाम!", "xbold", 96, stroke=7, stroke_fill=MAROON), CX, 1060, "pop")
    if t > 15.2:  # build-up before the jackpot reveal
        k = prog(t, 15.2, 1.75)
        paste(c, glow_sprite(400, (255, 230, 150), 0.5 * k), CX, 640, 1 + k)
    sparkles(c, t, CX, 640, (380, 330), 14, seed=17)


def scene_jackpot(c, t, s, e):
    lt = t - s
    flash = clamp(1 - lt / 0.35)
    paste(c, rangoli(), CX, 640, 1.5, rot=t * 25, alpha=0.5)
    paste(c, glow_sprite(600, (255, 210, 90), 0.7), CX, 640, 1.2 + 0.05 * math.sin(t * 6))
    firework_show(c, t, s - 0.5, [(0.6, 220, 420), (1.3, 860, 360), (2.0, 540, 280), (2.6, 300, 700)], seed=3)
    base.coin_rain(c, t, s + 0.2, count=40, seed=4, dur=3.6)
    base.confetti(c, t, s, count=120, burst_y=1150)
    title_in(c, t, s + 0.05, gold_ribbon("1st PRIZE", 480, 100), CX, 300, "pop")
    cp = prog(t, 17.2, 1.7)
    val = 120_000_000 if cp >= 1 else int(120_000_000 * ease_out_cubic(cp)) // 100000 * 100000
    num = text_img("₹ " + indian_format(val), "xbold", 112, fill=GOLD_LIGHT, stroke=6, stroke_fill=MAROON, shadow=6)
    paste(c, num, CX, 460)
    if t >= 19.0:
        paste(c, grad_text("12 CRORE", "anton", 230, stroke=10, stroke_fill=MAROON), CX, 690,
              ease_out_elastic(prog(t, 19.0, 0.9)))
    gp = prog(t, 20.1, 0.25)
    if gp > 0:
        stamp = text_img(" GUARANTEED ", "anton", 110, fill=WHITE, stroke=0)
        box = gradient_box(stamp.width + 20, stamp.height + 10, 20, (40, 180, 90), (10, 110, 50), outline=GOLD + (255,),
                           width=8, shadow=10)
        box.alpha_composite(stamp, ((box.width - stamp.width) // 2, (box.height - stamp.height) // 2))
        paste(c, box, CX, 950, lerp(2.4, 1.0, ease_out_cubic(gp)), rot=-6, alpha=min(1, gp * 2))
    sparkles(c, t, CX, 600, (460, 300), 16, seed=41)
    if flash > 0:
        c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * flash))))


@lru_cache(maxsize=None)
def mini_ticket(sold):
    w, h = 300, 190
    img = gradient_box(w, h, 14, (255, 215, 80), (220, 150, 20), outline=MAROON + (255,), width=4, shadow=6)
    d = ImageDraw.Draw(img)
    off = 12
    d.text((off + w / 2, off + 38), "DIWALI BUMPER", font=font("anton", 34), fill=MAROON, anchor="mm")
    d.text((off + w / 2, off + 95), "₹12 CRORE", font=font("anton", 44), fill=DEEP_RED, anchor="mm")
    if sold:
        st = text_img(" SOLD ", "anton", 34, fill=WHITE)
        bx = rounded_box(st.width, st.height, 8, (20, 150, 70, 235), outline=WHITE + (255,), width=3)
        bx.alpha_composite(st)
        bx = bx.rotate(-14, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(bx, ((img.width - bx.width) // 2, img.height - bx.height - 18))
    return img


def scene_sold(c, t, s, e):
    title_in(c, t, s + 0.05, gold_ribbon("ध्यान दीजिए!", 520, 100, size=60, fname="xbold"), CX, 300, "pop")
    for i in range(3):
        x = 200 + i * 340
        p = prog(t, s + 0.4 + i * 0.15, 0.4)
        if p > 0:
            sold = t >= 23.4 + i * 0.3
            paste(c, mini_ticket(sold), x, 540 + math.sin(t * 2 + i) * 6, ease_out_back(p) * 0.95, rot=(i - 1) * 4)
    if t >= 24.6:  # the winning ticket comes from the sold ones
        k = prog(t, 24.6, 0.4)
        paste(c, glow_sprite(220, (255, 230, 120), 0.8), 540, 540, 1 + 0.2 * math.sin(t * 8), alpha=k)
        paste(c, text_img("WINNER!", "anton", 70, fill=GOLD_LIGHT, stroke=4, stroke_fill=MAROON), 540, 680,
              ease_out_back(k))
    msg = gradient_box(980, 220, 30, (40, 180, 90), (10, 110, 50), outline=GOLD + (255,), width=6, shadow=12)
    d = ImageDraw.Draw(msg)
    d.text((514, 100), "1st PRIZE सिर्फ़ बिके हुए", font=font("xbold", 60), fill=WHITE, anchor="mm")
    d.text((514, 176), "टिकटों में से ही निकलेगा!", font=font("xbold", 60), fill=GOLD_LIGHT, anchor="mm")
    title_in(c, t, 22.7, msg, CX, 900, "pop")
    title_in(c, t, 23.2, text_img("1st PRIZE WILL BE DRAWN OUT OF SOLD TICKETS ONLY", "anton", 40, fill=WHITE,
                                  stroke=3, stroke_fill=MAROON), CX, 1100, "up")


@lru_cache(maxsize=None)
def calendar_card(day, weekday):
    w, h = 600, 640
    img = rounded_box(w, h, 40, (255, 250, 240, 255), shadow=16)
    d = ImageDraw.Draw(img)
    pad = 32
    d.rounded_rectangle((pad, pad, pad + w - 1, pad + 170), 40, fill=(200, 30, 60))
    d.rectangle((pad, pad + 120, pad + w - 1, pad + 170), fill=(200, 30, 60))
    d.text((pad + w / 2, pad + 88), "NOVEMBER 2026", font=font("anton", 74), fill=GOLD_LIGHT, anchor="mm")
    for rx in (150, 450):
        d.rounded_rectangle((pad + rx - 14, pad - 30, pad + rx + 14, pad + 40), 12, fill=(60, 40, 40))
    d.text((pad + w / 2, pad + 390), day, font=font("anton", 300), fill=MAROON, anchor="mm")
    d.text((pad + w / 2, pad + 580), weekday, font=font("bold", 48), fill=(150, 110, 110), anchor="mm")
    return img


def scene_draw_date(c, t, s, e):
    lt = t - s
    title_in(c, t, s + 0.05, gold_ribbon("DRAW DATE", 480, 96), CX, 300, "pop")
    flips = [26.2, 26.5, 26.8]
    days = ["13", "14", "15", "16"]
    idx = sum(1 for f in flips if t >= f)
    sy = 1.0
    for f in flips:
        if f - 0.12 <= t < f:
            sy = (f - t) / 0.12
        elif f <= t < f + 0.12:
            sy = (t - f) / 0.12
    paste(c, calendar_card(days[idx], "MONDAY" if idx == 3 else ""), CX, 740, ease_out_back(prog(lt, 0, 0.5)) * 0.92,
          sy=max(0.05, sy))
    lock = prog(t, 27.7, 0.5)
    if lock > 0:
        paste(c, glow_sprite(380, (255, 210, 80), 0.5), CX, 740, 1 + 0.1 * lock, alpha=1 - lock)
        sparkles(c, t, CX, 740, (330, 330), 10, seed=21)
    ct = prog(t, 29.6, 0.4)
    if ct > 0:
        turn = ease_in_out(prog(t, 29.6, 1.2))
        paste(c, base.clock_face(int((turn * 720) % 360), int(lerp(120, 180, turn))), 170, 1200, ease_out_back(ct))
        title_in(c, t, 29.8, grad_text("6:00 PM ONWARDS", "anton", 92, stroke=6, stroke_fill=MAROON), 620, 1200, "right")


@lru_cache(maxsize=None)
def price_tag():
    w, h = 600, 320

    def draw(d, s, img):
        pts = [(90 * s, 10 * s), (w * s - 20 * s, 10 * s), (w * s - 20 * s, h * s - 20 * s), (90 * s, h * s - 20 * s),
               (10 * s, h * s / 2 - 5 * s)]
        d.polygon([(x + 6 * s, y + 10 * s) for x, y in pts], fill=(0, 0, 0, 90))
        d.polygon(pts, fill=(255, 200, 30))
        d.polygon([(100 * s, 26 * s), (w * s - 36 * s, 26 * s), (w * s - 36 * s, h * s - 36 * s), (100 * s, h * s - 36 * s),
                   (30 * s, h * s / 2 - 5 * s)], outline=MAROON, width=5 * s)
        d.ellipse((60 * s, h * s / 2 - 25 * s, 100 * s, h * s / 2 + 15 * s), fill=(255, 255, 255), outline=MAROON, width=5 * s)
        d.text((340 * s, 90 * s), "TICKET MRP", font=font("anton", 54 * s), fill=MAROON, anchor="mm")
        d.text((340 * s, 200 * s), "₹500", font=font("xbold", 150 * s), fill=DEEP_RED, anchor="mm")
    return supersampled(w, h, draw)


def scene_mrp(c, t, s, e):
    lt = t - s
    p = ease_out_cubic(prog(lt, 0, 0.5))
    paste(c, ticket_crop((880, 225, 1225, 305), 880), CX, 400, lerp(1.4, 1.0, p), alpha=p)
    sw = prog(t, 31.7, 0.2)
    if sw > 0:
        k = t - 31.7
        ang = 26 * math.exp(-k * 2.2) * math.cos(k * 7)
        pivot_y = lerp(420, 620, ease_out_back(sw))
        ImageDraw.Draw(c).line((CX + 200, 500, CX + 200, pivot_y + 20), fill=(255, 255, 255, 200), width=5)
        paste(c, price_tag(), CX, pivot_y + 220, 1.0, rot=ang)
        sparkles(c, t, CX, pivot_y + 220, (320, 170), 10, seed=31)
    title_in(c, t, 32.8, pill("सिर्फ़ ₹500 में", "xbold", 62, fill=(200, 20, 70, 255), color=WHITE), CX, 1190, "pop")


RASHIS = [("मेष", "ARIES"), ("वृषभ", "TAURUS"), ("मिथुन", "GEMINI"), ("कर्क", "CANCER"), ("सिंह", "LEO"),
          ("कन्या", "VIRGO"), ("तुला", "LIBRA"), ("वृश्चिक", "SCORPIO"), ("धनु", "SAGITTARIUS"), ("मकर", "CAPRICORN"),
          ("कुंभ", "AQUARIUS"), ("मीन", "PISCES")]
RASHI_COLS = [((255, 90, 80), (170, 20, 40)), ((255, 170, 40), (190, 90, 0)), ((60, 170, 255), (20, 70, 180)),
              ((200, 90, 255), (110, 30, 170))]


@lru_cache(maxsize=None)
def zodiac_wheel():
    def draw(d, s, img):
        c = 320 * s
        d.ellipse((10 * s, 10 * s, 630 * s, 630 * s), fill=MAROON, outline=GOLD, width=10 * s)
        d.ellipse((150 * s, 150 * s, 490 * s, 490 * s), outline=GOLD, width=5 * s)
        for k in range(12):
            a = -math.pi / 2 + k * math.pi / 6
            d.line((c + math.cos(a + math.pi / 12) * 170 * s, c + math.sin(a + math.pi / 12) * 170 * s,
                    c + math.cos(a + math.pi / 12) * 310 * s, c + math.sin(a + math.pi / 12) * 310 * s),
                   fill=GOLD, width=3 * s)
            d.text((c + math.cos(a) * 240 * s, c + math.sin(a) * 240 * s), chr(0x2648 + k), font=font("sym", 62 * s),
                   fill=GOLD_LIGHT, anchor="mm")
        d.text((c, c - 10 * s), "12", font=font("anton", 170 * s), fill=WHITE, anchor="mm")
        d.text((c, c + 100 * s), "राशियाँ", font=font("xbold", 50 * s), fill=GOLD, anchor="mm")
    return supersampled(640, 640, draw)


@lru_cache(maxsize=None)
def rashi_tile(i):
    hi, en = RASHIS[i]
    c1, c2 = RASHI_COLS[i % 4]
    w, h = 236, 250
    img = gradient_box(w, h, 28, c1, c2, outline=GOLD + (255,), width=5, shadow=8)
    d = ImageDraw.Draw(img)
    off = 16
    d.text((off + w / 2, off + 70), chr(0x2648 + i), font=font("sym", 84), fill=WHITE, anchor="mm")
    d.text((off + w / 2, off + 162), hi, font=font("xbold", 46), fill=GOLD_LIGHT, anchor="mm")
    d.text((off + w / 2, off + 216), en, font=font("anton", 30 if len(en) < 10 else 26), fill=WHITE, anchor="mm")
    return img


def scene_rashi(c, t, s, e):
    title_in(c, t, s + 0.05, gold_ribbon("12 राशियों में टिकट", 700, 100, size=58, fname="xbold"), CX, 300, "pop")
    wheel_a = prog(t, s + 0.2, 0.5) * (1 - prog(t, 37.0, 0.4))
    if wheel_a > 0:
        paste(c, zodiac_wheel(), CX, 800, ease_out_back(min(1, wheel_a * 1.2)), rot=-t * 20, alpha=wheel_a)
    for i, st in enumerate(RASHI_TIMES):
        p = prog(t, st - 0.05, 0.35)
        if p > 0:
            r, col = divmod(i, 4)
            x = 150 + col * 260
            y = 520 + r * 285
            lit = st <= t < (RASHI_TIMES[i + 1] if i + 1 < 12 else st + 0.6)
            paste(c, rashi_tile(i), x, y, ease_out_back(p) * (1.08 if lit else 1.0), rot=(1 - p) * 25)


def scene_total(c, t, s, e):
    title_in(c, t, s + 0.05, gold_ribbon("हर राशि में 3 लाख टिकट", 760, 100, size=54, fname="xbold"), CX, 300, "pop")
    title_in(c, t, s + 0.4, pill("No. 700000 – 999999", "anton", 60, fill=(255, 245, 225, 255), color=MAROON), CX, 470, "up")
    title_in(c, t, 46.8, text_img("12 × 3,00,000 =", "anton", 96, fill=WHITE, stroke=4, stroke_fill=MAROON, shadow=4),
             CX, 650, "up")
    if t >= 47.2:
        cp = prog(t, 47.2, 1.6)
        val = 3_600_000 if cp >= 1 else int(3_600_000 * ease_out_cubic(cp)) // 1000 * 1000
        big = grad_text(indian_format(val), "anton", 190, stroke=9, stroke_fill=MAROON)
        paste(c, big, CX, 850, 1.0 + (0.1 * (1 - prog(t, 48.9, 0.3)) if t >= 48.9 else 0))
    if t >= 48.9:
        title_in(c, t, 48.9, grad_text("36 LAKH TICKETS", "anton", 110, top=(255, 250, 200), bottom=(255, 170, 40),
                                       stroke=6, stroke_fill=MAROON), CX, 1060, "pop")
    diya_row(c, t, 1250, [150, 330, 510, 690], 0.8, start=s + 0.5)


def scene_prizes(c, t, s, e):
    card2 = base.prize_card("2nd PRIZE", "₹1 CRORE each", "3 WINNERS", (150, 30, 70), (80, 10, 40), medal_label="2",
                            mc=((225, 230, 240), (130, 140, 160)))
    title_in(c, t, s + 0.1, card2, CX, 420, "left")
    if t >= 53.7:
        card3 = base.prize_card("3rd PRIZE", "₹50 LAKH each", "3 WINNERS", (170, 90, 40), (100, 45, 20),
                                medal_label="3", mc=((235, 160, 100), (140, 80, 30)))
        title_in(c, t, 53.7, card3, CX, 730, "right")
    for row, (st, y) in enumerate(((51.2, 1000), (54.3, 1170))):
        if t < st:
            continue
        for i in range(3):
            p = prog(t, st + i * 0.15, 0.3)
            paste(c, base.winner_icon(), 200 + i * 130, y, ease_out_back(p) * 1.2)
        title_in(c, t, st, text_img(("2nd" if row == 0 else "3rd") + " × 3", "anton", 64, fill=GOLD_LIGHT, stroke=4,
                                    stroke_fill=MAROON), 720, y, "right")


def scene_consolation(c, t, s, e):
    if t < 61.55:
        title_in(c, t, s + 0.05, gold_ribbon("CONSOLATION PRIZE", 760, 100), CX, 300, "pop")
        card = base.prize_card("CONSOLATION", "₹10 LAKH each", "11 WINNERS", (200, 40, 120), (110, 10, 70))
        title_in(c, t, 57.9, card, CX, 520, "pop")
        for i in range(11):
            r, col = divmod(i, 6)
            p = prog(t, 58.4 + i * 0.09, 0.25)
            if p > 0:
                paste(c, base.winner_icon(), 165 + col * 150 + r * 75, 800 + r * 120, ease_out_back(p) * 1.3)
        title_in(c, t, 59.5, text_img("11 × ₹10,00,000", "anton", 90, fill=WHITE, stroke=4, stroke_fill=MAROON),
                 CX, 1080, "up")
        return
    title_in(c, t, 61.55, gold_ribbon("PRIZE TABLE", 560, 96), CX, 290, "pop")
    title_in(c, t, 61.65, base.table_header(), CX, 395, "up")
    rows = [("1st", "1", "12,00,00,000"), ("Cons.", "11", "10,00,000"), ("2nd", "3", "1,00,00,000"),
            ("3rd", "3", "50,00,000"), ("4th", "12", "10,00,000"), ("5th", "12", "5,00,000"), ("6th", "3,600", "9,000"),
            ("7th", "3,600", "5,000"), ("8th", "3,600", "3,000"), ("9th", "1,80,000", "1,000")]
    for i, row in enumerate(rows):
        p = prog(t, 61.9 + i * 0.2, 0.35)
        if p > 0:
            paste(c, base.table_row(i, *row), CX + (1 - ease_out_cubic(p)) * (W if i % 2 else -W), 470 + i * 82, 0.92,
                  alpha=p)
    if t >= 64.0:
        title_in(c, t, 64.0, pill("कुल 1,90,842 इनाम", "xbold", 56, fill=GREEN + (255,), color=WHITE), CX, 1330, "pop")


def scene_live(c, t, s, e):
    lt = t - s
    p = ease_out_back(prog(lt, 0, 0.5))
    py = 740 + (1 - p) * 900
    paste(c, base.phone_frame(), CX, py)
    base.draw_machine(c, t, CX, py - 60, 200)
    blink = 0.6 + 0.4 * abs(math.sin(t * 4))
    live = pill("● LIVE", "anton", 52, fill=(230, 20, 40, 255), color=WHITE, padx=30, pady=10)
    paste(c, live, CX - 140, py - 360, 0.9 * (1 + 0.04 * math.sin(t * 8)), alpha=blink if t > 66.3 else 0)
    paste(c, text_img("HD", "anton", 44, fill=WHITE), CX + 170, py - 360, alpha=p)
    paste(c, text_img("LIVE DRAW", "anton", 60, fill=GOLD), CX, py + 230, alpha=p)
    url = base.typewriter("www.punjablotteries.com/livedraw", t, 67.5, cps=18)
    if url:
        title_in(c, t, 67.5, pill(url, "bold", 44, fill=(255, 255, 255, 245), color=MAROON), CX, 1290, "up")


def scene_contact(c, t, s, e):
    title_in(c, t, s + 0.05, gold_ribbon("टिकट खरीदने के लिए पहुँचें", 860, 104, size=56, fname="xbold"), CX, 290, "pop")
    p = prog(t, CONTACT_START + 0.3, 0.5)
    if p > 0:
        paste(c, base.agency_card(), CX, 530, ease_out_back(p) * (1 + 0.012 * math.sin(t * 3)))
    for i, (num, st, en) in enumerate(((PHONES[0], 76.36, 81.9), (PHONES[1], 82.04, 86.6))):
        q = prog(t, st, 0.45)
        if q > 0:
            lit = st <= t < en
            pulse = 1 + (0.05 * abs(math.sin(t * 6)) if lit else 0)
            paste(c, base.phone_pill(num, lit), 280 + i * 520, 775, ease_out_back(q) * pulse)


def scene_responsible(c, t, s, e):
    lt = t - s
    paste(c, base.warning_sign(), CX, 330, ease_out_back(prog(lt, 0.1, 0.5)) * (1 + 0.03 * math.sin(t * 4)))
    title_in(c, t, s + 0.4, text_img("लॉटरी में जोखिम है", "xbold", 76, fill=WHITE, stroke=5, stroke_fill=MAROON, shadow=5),
             CX, 540, "up")
    title_in(c, t, 89.5, grad_text("ज़िम्मेदारी से खेलें", "xbold", 92, stroke=7, stroke_fill=MAROON), CX, 670, "pop")


def scene_outro(c, t, s, e):
    paste(c, toran(), CX, 115, alpha=prog(t, s, 0.4))
    firework_show(c, t, s - 0.6, [(0.7, 240, 330), (1.5, 840, 280), (2.4, 540, 200), (3.6, 300, 260), (4.4, 800, 320)],
                  seed=5)
    title_in(c, t, s + 0.1, grad_text("HAPPY DIWALI", "anton", 140, top=(255, 245, 170), bottom=(255, 120, 20), stroke=7,
                                      stroke_fill=MAROON), CX, 330, "pop")
    title_in(c, t, s + 0.4, pill("दिवाली की ढेरों शुभकामनाएँ!", "xbold", 48, fill=(200, 20, 70, 255), color=WHITE),
             CX, 470, "up")
    ls = 93.72
    like_pressed = 94.45 <= t < 94.65
    share_pressed = 95.45 <= t < 95.65
    title_in(c, t, ls, base.action_button("LIKE", (40, 110, 240), like_pressed), 290, 640, "left")
    title_in(c, t, ls + 0.15, base.action_button("SHARE", (30, 170, 80), share_pressed), 790, 640, "right")
    if t > ls + 0.2:
        if t < 94.45:
            k = ease_in_out(prog(t, ls + 0.2, 0.5))
            x, y = lerp(700, 300, k), lerp(900, 660, k)
        elif t < 95.45:
            k = ease_in_out(prog(t, 94.7, 0.7))
            x, y = lerp(300, 800, k), 660
        else:
            x, y = 800, 660
        paste(c, base.cursor_sprite(), x + 30, y + 46, 0.85 if (like_pressed or share_pressed) else 1.0)
    if t > 94.45:
        for i in range(6):
            k = prog(t, 94.45 + i * 0.08, 1.2)
            if 0 < k < 1:
                paste(c, base.heart_sprite((255, 70, 110)), 290 + math.sin(i * 2) * 120, 600 - k * 380, 0.6, alpha=1 - k)
    title_in(c, t, s + 0.8, pill("DRAW: 16-11-2026 • 6 PM • ₹12 CRORE", "anton", 46, fill=(200, 30, 60, 255),
                                 color=WHITE), CX, 800, "up")


SCENE_FUNCS = {
    "intro": scene_intro, "ticket": scene_ticket, "history": scene_history, "jackpot": scene_jackpot,
    "sold": scene_sold, "draw_date": scene_draw_date, "mrp": scene_mrp, "rashi": scene_rashi, "total": scene_total,
    "prizes": scene_prizes, "consolation": scene_consolation, "live": scene_live, "contact": scene_contact,
    "responsible": scene_responsible, "outro": scene_outro,
}
