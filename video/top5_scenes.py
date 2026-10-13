"""Scenes for the "TOP 5 baatein" Diwali Bumper 2026 video.

Same host-led style as the first two videos, but a new graphics set: night skyline with rising sky
lanterns, light streaks, laser ticket scanner, TOP-5 flip cards, slot-machine jackpot, sold-tickets
draw drum, podium with falling gift boxes, rashi prize wheel, neon price sign, flip clock, live TV,
neon shop front for the agency, and a light-flash + ring transition.
"""
import math
import random
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

import diwali_scenes as D
import scenes as base
from gfx import (DEEP_RED, GOLD, GOLD_LIGHT, GREEN, WHITE, ease_in_out, ease_out_back, ease_out_cubic,
                 ease_out_elastic, font, glow_sprite, grad_text, gradient_box, indian_format, lerp, paste, prog,
                 rounded_box, supersampled, text_img)
from timeline import H, W
from top5_timeline import CONTACT_POPUPS, SCENES

CX = W // 2
NAVY = (10, 20, 60)
CYAN = (90, 220, 255)
MAGENTA = (255, 60, 170)
title_in, pill, sparkles = base.title_in, base.pill, base.sparkles

PHONES = ("89688 69862", "70598 77770")
TICKER = ("  ★ SUMIT LOTTERY AGENCY  •  One Way Traffic Road, Mansa  •  ☎ 89688 69862  •  ☎ 70598 77770  •  "
          "DIWALI BUMPER 2026 – 1st PRIZE ₹12 CRORE – DRAW 16 NOV  ")


# ================================================================== backdrop pieces
@lru_cache(maxsize=None)
def skyline():
    w, h = W, 700
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rnd = random.Random(12)
    x = 0
    while x < w:
        bw = rnd.randint(70, 150)
        bh = rnd.randint(220, 620)
        d.rectangle((x, h - bh, x + bw, h), fill=(12, 14, 40, 255))
        if rnd.random() < 0.3:  # domes / spires
            d.pieslice((x + 10, h - bh - 40, x + bw - 10, h - bh + 40), 180, 360, fill=(12, 14, 40, 255))
        for wy in range(h - bh + 20, h - 20, 34):
            for wx in range(x + 12, x + bw - 18, 26):
                if rnd.random() < 0.45:
                    d.rectangle((wx, wy, wx + 12, wy + 16), fill=(255, 210, 110, rnd.randint(140, 255)))
        x += bw + rnd.randint(2, 10)
    # string lights along the rooftops
    return img


def light_streaks(c, t, alpha=1.0):
    """Diagonal moving light streaks (motion-graphics background)."""
    layer = Image.new("RGBA", c.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rnd = random.Random(31)
    for i in range(7):
        sp = rnd.uniform(250, 520)
        off = rnd.uniform(0, 2400)
        x = (off + t * sp) % 2600 - 700
        y = rnd.uniform(200, 1600)
        ln = rnd.uniform(160, 360)
        col = (CYAN if i % 2 else (255, 200, 90)) + (int(70 * alpha),)
        for k in range(3):
            d.line((x - ln + k * 4, y + ln * 0.35, x + k * 4, y), fill=col, width=6 - k * 2)
    c.alpha_composite(layer)


@lru_cache(maxsize=None)
def lantern_sprite(hue):
    cols = [((255, 150, 40), (255, 220, 120)), ((255, 90, 60), (255, 190, 120)), ((255, 190, 60), (255, 240, 170))]
    c1, c2 = cols[hue % 3]

    def draw(d, s, img):
        d.polygon([(20 * s, 10 * s), (80 * s, 10 * s), (92 * s, 120 * s), (8 * s, 120 * s)], fill=c1)
        d.polygon([(34 * s, 20 * s), (66 * s, 20 * s), (74 * s, 110 * s), (26 * s, 110 * s)], fill=c2)
        d.ellipse((38 * s, 96 * s, 62 * s, 120 * s), fill=(255, 250, 220))
    spr = supersampled(100, 130, draw)
    out = Image.new("RGBA", (220, 250), (0, 0, 0, 0))
    out.alpha_composite(glow_sprite(110, (255, 170, 70), 0.55).resize((220, 220)), (0, 20))
    out.alpha_composite(spr, (60, 60))
    return out


def lanterns(c, t, n=14, seed=5, alpha=1.0):
    rnd = random.Random(seed)
    for i in range(n):
        x0 = rnd.uniform(40, W - 40)
        sp = rnd.uniform(50, 110)
        ph = rnd.uniform(0, 30)
        sc = rnd.uniform(0.35, 0.8)
        y = H + 150 - ((t + ph) * sp) % (H + 400)
        x = x0 + math.sin((t + ph) * 0.8) * 30
        paste(c, lantern_sprite(i), x, y, sc * (0.9 + 0.1 * math.sin(t * 6 + i)), alpha=alpha * min(1, y / 400))


def backdrop(c, t, lantern_alpha=0.7):
    light_streaks(c, t, 0.8)
    lanterns(c, t, 10, 5, lantern_alpha)


# ================================================================== header / overlay / transition
@lru_cache(maxsize=None)
def header_img():
    w, h = 1000, 120
    img = gradient_box(w, h, 26, (20, 40, 110), (8, 14, 50), outline=CYAN + (255,), width=4, shadow=10, horizontal=True)
    off = 20
    img.alpha_composite(text_img("DIWALI BUMPER 2026", "anton", 50, fill=GOLD_LIGHT), (off + 26, off + 6))
    img.alpha_composite(text_img("TOP 5 बातें • GOVT. OF PUNJAB", "semi", 28, fill=(200, 230, 255)), (off + 30, off + 70))
    chip = rounded_box(220, 84, 20, GOLD + (255,))
    d = ImageDraw.Draw(chip)
    d.text((110, 26), "1st PRIZE", font=font("anton", 28), fill=NAVY, anchor="mm")
    d.text((110, 60), "₹12 CRORE", font=font("anton", 36), fill=DEEP_RED, anchor="mm")
    img.alpha_composite(chip, (off + w - 236, off + 18))
    return img


def overlay(c, t):
    for st in CONTACT_POPUPS:
        lt = t - st
        if 0 <= lt < 4.2:
            p_in = ease_out_back(prog(lt, 0, 0.45))
            p_out = ease_in_out(prog(lt, 3.7, 0.5))
            paste(c, D.popup_card(), lerp(-420, 345, p_in) - p_out * 800, 1515 + math.sin(t * 3) * 4)
    D.draw_ticker(c, t, TICKER, 0.8, 74.0)


def draw_transition(c, t):
    """Light flash with an expanding golden ring at each scene change."""
    for _, s in SCENES[1:]:
        k = (t - s + 0.08) / 0.4
        if 0 < k < 1:
            a = math.sin(math.pi * k)
            c.alpha_composite(Image.new("RGBA", c.size, (255, 250, 230, int(150 * a))))
            r = int(lerp(60, 1300, ease_out_cubic(k)))
            ring = Image.new("RGBA", c.size, (0, 0, 0, 0))
            ImageDraw.Draw(ring).ellipse((CX - r, H / 2 - r, CX + r, H / 2 + r), outline=GOLD + (int(255 * (1 - k)),),
                                         width=int(40 * (1 - k)) + 2)
            c.alpha_composite(ring)


# ================================================================== widgets
@lru_cache(maxsize=None)
def number_card(n):
    w, h = 300, 300
    img = gradient_box(w, h, 40, (255, 215, 80), (230, 140, 20), outline=WHITE + (255,), width=8, shadow=14)
    d = ImageDraw.Draw(img)
    off = 28
    d.text((off + w / 2, off + 70), "NUMBER", font=font("anton", 46), fill=NAVY, anchor="mm")
    d.text((off + w / 2, off + 185), str(n), font=font("anton", 200), fill=DEEP_RED, anchor="mm")
    return img


def flip_in(c, t, start, img, x, y, scale=1.0):
    """3D-ish card flip: horizontal squash from edge-on to full, with a little overshoot."""
    p = prog(t, start, 0.55)
    if p <= 0:
        return
    sx = max(0.02, ease_out_back(p, 2.2))
    paste(c, img, x, y, scale, sx=sx)


def number_badge(c, t, s, n):
    flip_in(c, t, s + 0.1, number_card(n), 190, 330, 0.75)


@lru_cache(maxsize=None)
def headline(text, size=72, col1=(255, 250, 220), col2=(255, 190, 60)):
    return grad_text(text, "xbold", size, top=col1, bottom=col2, stroke=6, stroke_fill=NAVY)


def neon(text, size, col, t, start):
    """Neon sign text that flickers on."""
    if t < start:
        return None
    k = t - start
    on = 1.0 if k > 0.6 else (1.0 if (int(k * 22) % 3) else 0.25)
    base_t = text_img(text, "anton", size, fill=(255, 255, 255))
    glow_t = text_img(text, "anton", size, fill=col).filter(ImageFilter.GaussianBlur(14))
    out = Image.new("RGBA", (glow_t.width + 40, glow_t.height + 40), (0, 0, 0, 0))
    for _ in range(2):
        out.alpha_composite(glow_t, (20, 20))
    out.alpha_composite(base_t, (20 + (glow_t.width - base_t.width) // 2, 20 + (glow_t.height - base_t.height) // 2))
    if on < 1:
        out.putalpha(out.getchannel("A").point(lambda v: int(v * on)))
    return out


# ================================================================== scenes
def scene_intro(c, t, s, e):
    backdrop(c, t, 1.0)
    paste(c, skyline(), 0, H - 700 - 220, anchor="tl")
    words = [("दिवाली पर", 0.07, 250), ("करोड़पति", 0.75, 360), ("बनने का सपना?", 1.3, 470)]
    for txt, st, y in words:
        p = prog(t, st, 0.3)
        if p > 0:  # stomp-in: big to normal with shake
            sc = lerp(2.2, 1.0, ease_out_cubic(p))
            paste(c, headline(txt, 86 if txt == "करोड़पति" else 64), CX, y, sc, alpha=min(1, p * 2))
    gp = prog(t, 2.3, 0.35)
    if gp > 0:  # glitch-in: RGB split that settles
        img = text_img("ये वीडियो आपके लिए है!", "xbold", 56, fill=WHITE, stroke=4, stroke_fill=NAVY)
        off = int((1 - gp) * 26)
        if off:
            paste(c, text_img("ये वीडियो आपके लिए है!", "xbold", 56, fill=(255, 40, 80)), CX - off, 600, alpha=0.6)
            paste(c, text_img("ये वीडियो आपके लिए है!", "xbold", 56, fill=(40, 220, 255)), CX + off, 600, alpha=0.6)
        paste(c, img, CX, 600)


def scene_title(c, t, s, e):
    backdrop(c, t)
    lt = t - s
    # laser scanner over the ticket
    tk = D.ticket_front(820)
    p = ease_out_cubic(prog(lt, 0, 0.4))
    ty = 560
    paste(c, tk, CX, ty, lerp(0.85, 1.0, p), alpha=p)
    scan = prog(t, 5.0, 1.2)
    if 0 < scan < 1:
        top = ty - tk.height / 2 + 20
        y = top + (tk.height - 40) * ease_in_out(scan)
        tint = Image.new("RGBA", c.size, (0, 0, 0, 0))
        ImageDraw.Draw(tint).rectangle((CX - 420, top, CX + 420, y), fill=CYAN + (45,))
        c.alpha_composite(tint)
        paste(c, glow_sprite(120, CYAN, 0.9), CX, y, sx=7.0, sy=0.35)
        ImageDraw.Draw(c).line((CX - 430, y, CX + 430, y), fill=(220, 250, 255, 255), width=5)
    if t > 6.2:
        title_in(c, t, 6.2, pill("✔ VERIFIED • GOVT. OF PUNJAB", "anton", 40, fill=(20, 150, 70, 255), color=WHITE,
                                 padx=30, pady=10), CX, 880, "pop")
    # TOP 5 reveal
    if t > 7.5:
        paste(c, headline("TOP 5", 170, (255, 255, 230), (255, 170, 30)), CX, 1040, ease_out_elastic(prog(t, 7.5, 0.8)))
        title_in(c, t, 7.9, text_img("बड़ी बातें", "xbold", 64, fill=WHITE, stroke=4, stroke_fill=NAVY), CX, 1170, "up")
        for i in range(5):
            p = prog(t, 8.0 + i * 0.2, 0.3)
            if p > 0:
                x = CX + (i - 2) * 170
                bub = gradient_box(130, 130, 65, (255, 215, 80), (230, 140, 20), outline=WHITE + (255,), width=5)
                ImageDraw.Draw(bub).text((65, 68), str(i + 1), font=font("anton", 80), fill=NAVY, anchor="mm")
                paste(c, bub, x, 1300 + math.sin(t * 5 + i) * 6, ease_out_back(p))


REEL_SYMBOLS = ["7", "★", "₹", "◆", "12", "CR", "♛", "₹", "12", "CR"]


@lru_cache(maxsize=None)
def reel_strip():
    cell = 150
    img = Image.new("RGBA", (190, cell * len(REEL_SYMBOLS)), (255, 252, 240, 255))
    d = ImageDraw.Draw(img)
    for i, sym in enumerate(REEL_SYMBOLS):
        f = font("sym", 96) if sym in ("★", "◆", "♛") else font("anton", 100 if len(sym) < 3 else 80)
        col = DEEP_RED if sym in ("12", "7") else (NAVY if sym == "CR" else (200, 140, 0))
        d.text((95, i * cell + cell / 2), sym, font=f, fill=col, anchor="mm")
        d.line((0, (i + 1) * cell - 1, 190, (i + 1) * cell - 1), fill=(220, 210, 190), width=2)
    return img


def slot_machine(c, t, x, y, start, stops, targets):
    cell = 150
    strip = reel_strip()
    n = len(REEL_SYMBOLS)
    frame = gradient_box(720, 360, 40, (230, 40, 60), (140, 10, 30), outline=GOLD + (255,), width=10, shadow=16)
    paste(c, frame, x, y)
    for i in range(3):
        rx = x + (i - 1) * 215
        win = Image.new("RGBA", (190, 240), (0, 0, 0, 0))
        if t < start:
            pos = targets[i] * cell
        elif t < stops[i]:
            pos = ((t - start) * 2200 + i * 300) % (n * cell)
        else:
            k = min(1.0, (t - stops[i]) / 0.25)
            pos = targets[i] * cell - math.sin(k * math.pi) * 30 * (1 - k)
        top = pos - (240 - cell) / 2
        for rep in (-1, 0, 1):
            win.alpha_composite(strip, (0, int(-top + rep * n * cell)))
        mask = Image.new("L", win.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, 189, 239), 20, fill=255)
        out = Image.new("RGBA", win.size, (0, 0, 0, 0))
        out.paste(win, (0, 0), mask)
        if start <= t < stops[i]:
            out = out.filter(ImageFilter.GaussianBlur(3))
        paste(c, out, rx, y)
    ImageDraw.Draw(c).line((x - 330, y, x + 330, y), fill=(255, 255, 255, 90), width=4)


def scene_n1(c, t, s, e):
    backdrop(c, t)
    number_badge(c, t, s, 1)
    title_in(c, t, s + 0.2, headline("1st PRIZE", 90), 650, 330, "right")
    # vault glow behind slot machine
    paste(c, glow_sprite(500, (255, 200, 80), 0.55), CX, 760, 1 + 0.04 * math.sin(t * 5))
    slot_machine(c, t, CX, 760, 12.3, (13.4, 13.7, 14.0), (2, 4, 5))
    if t >= 14.0:
        paste(c, headline("₹12 CRORE", 130, (255, 255, 230), (255, 170, 30)), CX, 1010,
              ease_out_elastic(prog(t, 14.0, 0.8)))
        base.coin_rain(c, t, 14.0, count=26, seed=8, dur=2.5)
    sp = prog(t, 14.85, 0.25)
    if sp > 0:
        paste(c, base.official_stamp(), 860, 1180, lerp(2.4, 0.85, ease_out_cubic(sp)), rot=-10, alpha=min(1, sp * 2))
        title_in(c, t, 15.1, pill("पंजाब सरकार की ऑफिशियल लॉटरी", "xbold", 44, fill=(20, 150, 70, 255), color=WHITE),
                 430, 1200, "left")


@lru_cache(maxsize=None)
def shield():
    def draw(d, s, img):
        pts = [(160, 10), (300, 60), (290, 200), (160, 330), (30, 200), (20, 60)]
        d.polygon([(x * s, y * s) for x, y in pts], fill=(30, 170, 90))
        pts2 = [(160, 36), (276, 78), (268, 192), (160, 300), (52, 192), (44, 78)]
        d.polygon([(x * s, y * s) for x, y in pts2], fill=(40, 200, 110))
        d.line([(100 * s, 170 * s), (145 * s, 220 * s), (225 * s, 120 * s)], fill=WHITE, width=30 * s, joint="curve")
    return supersampled(320, 340, draw)


@lru_cache(maxsize=None)
def mini_ticket(state):
    """state: 0 neutral, 1 sold (green tick), 2 unsold (grey)."""
    w, h = 130, 70
    c1, c2 = ((255, 215, 80), (220, 150, 20)) if state != 2 else ((150, 150, 160), (100, 100, 110))
    img = gradient_box(w, h, 10, c1, c2, outline=WHITE + (255,), width=3)
    d = ImageDraw.Draw(img)
    d.text((w / 2, h / 2), "₹12 Cr", font=font("anton", 30), fill=NAVY if state != 2 else (70, 70, 80), anchor="mm")
    if state == 1:
        d.ellipse((w - 34, -2, w + 2, 34), fill=GREEN)
        d.text((w - 16, 16), "✔", font=font("sym", 24), fill=WHITE, anchor="mm")
    return img


def scene_n2(c, t, s, e):
    backdrop(c, t)
    number_badge(c, t, s, 2)
    title_in(c, t, s + 0.2, headline("GUARANTEED", 84, (220, 255, 230), (60, 220, 120)), 650, 330, "right")
    if t >= 19.7:
        paste(c, glow_sprite(260, (80, 255, 150), 0.5), CX, 640)
        paste(c, shield(), CX, 640, ease_out_elastic(prog(t, 19.7, 0.8)) * 0.85)
    # sold tickets go into the draw drum, unsold fade out
    if t >= 20.7:
        rnd = random.Random(4)
        drum_x, drum_y = CX, 1180
        paste(c, glow_sprite(170, (255, 220, 120), 0.5), drum_x, drum_y)
        d = ImageDraw.Draw(c)
        d.ellipse((drum_x - 130, drum_y - 130, drum_x + 130, drum_y + 130), fill=(30, 40, 90), outline=GOLD, width=8)
        d.text((drum_x, drum_y - 20), "DRAW", font=font("anton", 54), fill=GOLD_LIGHT, anchor="mm")
        d.text((drum_x, drum_y + 34), "SOLD ONLY", font=font("anton", 34), fill=WHITE, anchor="mm")
        for i in range(10):
            sold = rnd.random() < 0.6
            gx, gy = 140 + (i % 5) * 200, 900 + (i // 5) * 90
            k = prog(t, 21.5 + i * 0.06, 0.5)
            if not sold:
                paste(c, mini_ticket(2 if k > 0 else 0), gx, gy + k * 40, alpha=1 - 0.75 * k)
            else:
                m = ease_in_out(prog(t, 22.2 + i * 0.05, 0.6))
                paste(c, mini_ticket(1 if k > 0 else 0), lerp(gx, drum_x, m), lerp(gy, drum_y, m), 1 - 0.7 * m,
                      alpha=1 - m * 0.9)
        title_in(c, t, 22.9, pill("सिर्फ़ बिके हुए टिकटों में से!", "xbold", 48, fill=(20, 150, 70, 255), color=WHITE),
                 CX, 1370, "pop")


@lru_cache(maxsize=None)
def gift_box(i):
    cols = [((230, 40, 90), GOLD), ((40, 140, 230), (255, 255, 255)), ((40, 180, 100), GOLD), ((180, 60, 220), GOLD)]
    body, rib = cols[i % 4]

    def draw(d, s, img):
        d.rectangle((10 * s, 40 * s, 110 * s, 120 * s), fill=body)
        d.rectangle((4 * s, 26 * s, 116 * s, 48 * s), fill=tuple(int(v * 0.85) for v in body))
        d.rectangle((52 * s, 26 * s, 68 * s, 120 * s), fill=rib)
        d.ellipse((30 * s, 4 * s, 60 * s, 32 * s), outline=rib, width=8 * s)
        d.ellipse((60 * s, 4 * s, 90 * s, 32 * s), outline=rib, width=8 * s)
    return supersampled(120, 124, draw)


def gift_rain(c, t, t0, count=16, seed=2, dur=3.0):
    lt = t - t0
    if lt < 0 or lt > dur + 2:
        return
    rnd = random.Random(seed)
    for i in range(count):
        delay = rnd.uniform(0, dur * 0.6)
        k = lt - delay
        if k < 0:
            continue
        x = rnd.uniform(60, W - 60)
        y = -100 + rnd.uniform(500, 800) * k + 200 * k * k
        if y < H:
            paste(c, gift_box(i), x, y, rnd.uniform(0.5, 0.9), rot=math.sin(k * 3 + i) * 20)


@lru_cache(maxsize=None)
def podium_block(label, amount, sub, h, c1, c2):
    w = 300
    img = gradient_box(w, h, 16, c1, c2, outline=WHITE + (255,), width=5, shadow=10)
    d = ImageDraw.Draw(img)
    off = 20
    d.text((off + w / 2, off + 50), label, font=font("anton", 64), fill=WHITE, anchor="mm")
    d.text((off + w / 2, off + 120), amount, font=font("anton", 46), fill=GOLD_LIGHT, anchor="mm")
    d.text((off + w / 2, off + 172), sub, font=font("bold", 30), fill=WHITE, anchor="mm")
    return img


@lru_cache(maxsize=None)
def trophy(col):
    def draw(d, s, img):
        d.pieslice((20 * s, 0, 140 * s, 120 * s), 0, 180, fill=col)
        d.rectangle((20 * s, 0, 140 * s, 60 * s), fill=col)
        d.arc((0, 10 * s, 40 * s, 70 * s), 90, 270, fill=col, width=8 * s)
        d.arc((120 * s, 10 * s, 160 * s, 70 * s), 270, 90, fill=col, width=8 * s)
        d.rectangle((70 * s, 115 * s, 90 * s, 150 * s), fill=col)
        d.rectangle((40 * s, 150 * s, 120 * s, 170 * s), fill=col)
    return supersampled(160, 172, draw)


def scene_n3(c, t, s, e):
    backdrop(c, t)
    number_badge(c, t, s, 3)
    title_in(c, t, s + 0.2, headline("इनामों की बरसात!", 74), 650, 330, "right")
    gift_rain(c, t, 24.7, count=16, seed=3, dur=3.0)
    base.coin_rain(c, t, 24.7, count=16, seed=6, dur=2.6)
    base_y = 1330
    blocks = [(26.6, 230, "2nd", "₹1 CRORE", "3 विजेता", 330, ((210, 215, 230), (120, 130, 160)), (225, 230, 240)),
              (24.2, 540, "1st", "₹12 CRORE", "1 विजेता", 430, ((255, 215, 80), (220, 140, 20)), GOLD),
              (29.1, 850, "3rd", "₹50 LAKH", "3 विजेता", 280, ((235, 150, 90), (160, 80, 30)), (235, 160, 100))]
    for st, x, lab, amt, sub, h, cols, tcol in blocks:
        p = prog(t, st, 0.5)
        if p > 0:
            blk = podium_block(lab, amt, sub, h, *cols)
            y = base_y - h / 2 + (1 - ease_out_back(p)) * h
            paste(c, blk, x, y)
            paste(c, trophy(tcol), x, base_y - h - 80 + (1 - ease_out_back(p)) * h, 0.8 * ease_out_back(p))
    cp = prog(t, 31.4, 1.5)
    if cp > 0:
        val = 190842 if cp >= 1 else int(190842 * ease_out_cubic(cp))
        paste(c, headline(indian_format(val) + "+ इनाम", 96, (255, 255, 230), (255, 170, 30)), CX, 560,
              ease_out_back(min(1, cp * 3)))
        if t > 33.0:
            base.confetti(c, t, 33.0, count=90, burst_y=600)


@lru_cache(maxsize=None)
def prize_wheel():
    r = 380
    cols = [(230, 40, 90), (255, 170, 30), (40, 140, 230), (40, 180, 100), (180, 60, 220), (255, 90, 60)]

    def draw(d, s, img):
        c0 = r * s
        for i in range(12):
            d.pieslice((0, 0, 2 * r * s, 2 * r * s), i * 30 - 90 - 15, i * 30 - 90 + 15, fill=cols[i % 6],
                       outline=(255, 255, 255), width=4 * s)
        for i in range(12):
            a = math.radians(i * 30 - 90)
            d.text((c0 + math.cos(a) * 280 * s, c0 + math.sin(a) * 280 * s), chr(0x2648 + i), font=font("sym", 64 * s),
                   fill=WHITE, anchor="mm")
            d.text((c0 + math.cos(a) * 180 * s, c0 + math.sin(a) * 180 * s), D.RASHIS[i][0], font=font("xbold", 30 * s),
                   fill=WHITE, anchor="mm")
        d.ellipse((c0 - 90 * s, c0 - 90 * s, c0 + 90 * s, c0 + 90 * s), fill=NAVY, outline=GOLD, width=10 * s)
        d.text((c0, c0), "12", font=font("anton", 100 * s), fill=GOLD_LIGHT, anchor="mm")
        d.ellipse((4 * s, 4 * s, (2 * r - 4) * s, (2 * r - 4) * s), outline=GOLD, width=14 * s)
    return supersampled(2 * r, 2 * r, draw)


def wheel_angle(t):
    """Spins fast, eases to land on मेष (index 0) at 38.0, then turns slowly to मीन by 38.6."""
    if t < 36.1:
        return (t - 34.6) * 40
    if t < 38.0:
        k = ease_out_cubic((t - 36.1) / 1.9)
        return lerp(60, 720, k)
    if t < 38.6:
        return 720 - 30 * ease_in_out((t - 38.0) / 0.6)
    return 690 + (t - 38.6) * 8


def scene_n4(c, t, s, e):
    backdrop(c, t)
    number_badge(c, t, s, 4)
    title_in(c, t, s + 0.2, headline("12 राशियाँ", 90), 650, 330, "right")
    p = ease_out_back(prog(t, s + 0.3, 0.6))
    paste(c, glow_sprite(420, (255, 200, 100), 0.4), CX, 860)
    paste(c, prize_wheel(), CX, 860, 0.95 * p, rot=wheel_angle(t))
    d = ImageDraw.Draw(c)  # pointer
    d.polygon([(CX - 36, 470), (CX + 36, 470), (CX, 540)], fill=WHITE, outline=GOLD)
    if t > 40.6:
        title_in(c, t, 40.6, pill("हर राशि में 3 लाख टिकट", "xbold", 50, fill=(255, 250, 235, 255), color=NAVY), CX, 1310,
                 "pop")


@lru_cache(maxsize=None)
def flap(text, w=170, h=200):
    img = rounded_box(w, h, 18, (25, 25, 32, 255), shadow=8)
    d = ImageDraw.Draw(img)
    off = 16
    d.text((off + w / 2, off + h / 2), text, font=font("anton", 150 if len(text) < 3 else 90), fill=WHITE, anchor="mm")
    d.line((off, off + h / 2, off + w, off + h / 2), fill=(0, 0, 0), width=4)
    return img


def flip_clock(c, t, x, y, old, new, at, w=170):
    if t < at:
        paste(c, flap(old, w), x, y)
        return
    k = min(1.0, (t - at) / 0.25)
    paste(c, flap(new if k > 0.5 else old, w), x, y, sy=max(0.05, abs(1 - 2 * k)))


def scene_n5(c, t, s, e):
    backdrop(c, t)
    number_badge(c, t, s, 5)
    title_in(c, t, s + 0.2, headline("कीमत • ड्रॉ • लाइव", 64), 650, 330, "right")
    sign = neon("₹500", 210, MAGENTA, t, 44.4)
    if sign is not None:
        d = ImageDraw.Draw(c)
        d.rounded_rectangle((CX - 300, 470, CX + 300, 760), 30, outline=(255, 120, 200, 200), width=6)
        paste(c, sign, CX, 600)
        paste(c, text_img("TICKET MRP", "anton", 40, fill=(255, 200, 230)), CX, 495)
    if t >= 46.0:
        title_in(c, t, 46.0, text_img("DRAW", "anton", 54, fill=CYAN), CX, 810, "up")
        flip_clock(c, t, CX - 200, 925, "00", "16", 46.7)
        flip_clock(c, t, CX + 60, 925, "JAN", "NOV", 46.85, 300)
        flip_clock(c, t, CX - 200, 1130, "00", "6", 47.7)
        flip_clock(c, t, CX + 60, 1130, "AM", "PM", 47.85, 300)
    if t >= 49.3:
        tv = rounded_box(660, 170, 24, (15, 15, 25, 255), outline=(120, 120, 140, 255), width=6, shadow=10)
        dd = ImageDraw.Draw(tv)
        dd.ellipse((40, 36, 70, 66), fill=(230, 30, 40) if int(t * 3) % 2 else (120, 20, 30))
        dd.text((86, 51), "LIVE DRAW", font=font("anton", 44), fill=WHITE, anchor="lm")
        dd.text((350, 122), "punjablotteries.com/livedraw", font=font("bold", 34), fill=CYAN, anchor="mm")
        paste(c, tv, CX - 110, 1300, ease_out_back(prog(t, 49.3, 0.4)) * 0.88)


@lru_cache(maxsize=None)
def shop_front():
    w, h = 960, 560
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 120, w, h), fill=(60, 40, 70))  # wall
    for y in range(140, h, 40):  # bricks
        for x in range((y // 40 % 2) * 40, w, 80):
            d.rectangle((x + 2, y + 2, x + 76, y + 36), outline=(80, 55, 90), width=2)
    d.rectangle((120, 250, w - 120, h), fill=(150, 150, 165))  # shutter
    for y in range(260, h, 22):
        d.line((120, y, w - 120, y), fill=(110, 110, 125), width=4)
    d.rounded_rectangle((60, 20, w - 60, 200), 24, fill=(20, 10, 40), outline=GOLD, width=6)  # signboard
    return img


def scene_contact(c, t, s, e):
    backdrop(c, t, 0.5)
    p = ease_out_cubic(prog(t, 52.7, 0.6))
    shop_y = 470 + (1 - p) * -700
    paste(c, shop_front(), CX, shop_y, alpha=p)
    sign = neon("SUMIT LOTTERY AGENCY", 84, (255, 190, 60), t, 53.0)
    if sign is not None:
        paste(c, sign, CX, shop_y - 175)
    d = ImageDraw.Draw(c)
    for i in range(24):  # string lights along the sign
        x = CX - 470 + i * 41
        y = shop_y - 290 + abs(math.sin(i * 0.5)) * 18
        on = (int(t * 4) + i) % 3 != 0
        col = [(255, 80, 80), (255, 210, 60), (80, 220, 120), (90, 180, 255)][i % 4]
        d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=col + (255 if on else 90,))
    if t > 54.0:
        title_in(c, t, 54.0, pill("One Way Traffic Road, Mansa", "bold", 44, fill=(255, 250, 235, 255), color=NAVY),
                 CX, shop_y + 40, "pop")
    for i, x in enumerate((180, 900)):
        D.diya(c, t, x, shop_y + 250, 0.8, seed=i)
    for i, (num, st, en) in enumerate(((PHONES[0], 58.6, 62.4), (PHONES[1], 62.9, 67.4))):
        q = prog(t, st, 0.45)
        if q > 0:
            lit = st <= t < en
            paste(c, base.phone_pill(num, lit), 280 + i * 520, 820,
                  ease_out_back(q) * 0.95 * (1 + (0.05 * abs(math.sin(t * 6)) if lit else 0)))


def scene_outro(c, t, s, e):
    lanterns(c, t, 18, 9, 1.0)
    paste(c, skyline(), 0, H - 700 - 220, anchor="tl", alpha=0.8)
    D.firework_show(c, t, s - 0.5, [(0.7, 220, 330), (1.6, 860, 290), (2.5, 540, 220), (3.5, 300, 420)], seed=6)
    title_in(c, t, s + 0.2, text_img("लॉटरी में जोखिम है,", "xbold", 60, fill=WHITE, stroke=4, stroke_fill=NAVY), CX,
             300, "up")
    title_in(c, t, 69.8, headline("ज़िम्मेदारी से खेलें", 80), CX, 410, "pop")
    if t > 71.7:
        paste(c, grad_text("HAPPY DIWALI", "anton", 140, top=(255, 245, 170), bottom=(255, 120, 20), stroke=7,
                           stroke_fill=NAVY), CX, 590, ease_out_elastic(prog(t, 71.7, 0.9)))
    sparkles(c, t, CX, 450, (460, 200), 14, seed=13)


SCENE_FUNCS = {
    "intro": scene_intro, "title": scene_title, "n1": scene_n1, "n2": scene_n2, "n3": scene_n3, "n4": scene_n4,
    "n5": scene_n5, "contact": scene_contact, "outro": scene_outro,
}
