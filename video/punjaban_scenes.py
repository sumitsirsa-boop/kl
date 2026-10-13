"""Scenes for the Diwali Bumper video presented by a Punjabi girl holding the ticket.

Different style from the other videos: the host is large and holds the real ticket; "zoom lenses"
pop out of the ticket in her hands, Instagram-story style sticker texts, phulkari borders, and
full-screen B-roll cutaways (jackpot, prize ladder, rashi wheel) with the host in a corner circle.
"""
import math
import os
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

import diwali_scenes as D
import presenter_girl as G
import scenes as base
from gfx import (DEEP_RED, GOLD, GOLD_LIGHT, ROOT, WHITE, clamp, ease_in_out, ease_out_back, ease_out_cubic,
                 ease_out_elastic, font, glow_sprite, grad_text, gradient_box, indian_format, lerp, paste, prog,
                 rounded_box, supersampled, text_img)
from presenter import presenter_state
from punjaban_timeline import BROLL_SCENES, scene_at
from timeline import W

CX = W // 2
MAGENTA = (190, 20, 100)
PLUM = (90, 10, 55)
TICKET_PATH = os.path.join(ROOT, "assets", "punjaban", "ticket_source.jpg")
FRONT = (0, 0, 1320, 815)
TICKER = ("  ★ SUMIT LOTTERY AGENCY  •  One Way Traffic Road, Mansa  •  ☎ 89688 69862  •  ☎ 70598 77770  •  "
          "DIWALI BUMPER 2026 – 1st PRIZE ₹12 CRORE  ")

# regions of the ticket photo used by the zoom lenses
REG = dict(title=(350, 45, 990, 140), jack=(430, 225, 900, 665), second=(105, 325, 360, 565),
           third=(955, 325, 1215, 565), date=(1030, 240, 1240, 300), mrp=(925, 255, 1020, 310),
           logo=(155, 60, 300, 200), sold=(440, 715, 870, 750))

# host placement: body sprite centre and scale (screen = centre + (body - size/2) * scale)
HOST_S = 1.25
HOST_C = (CX, 1690 - G.GH * HOST_S / 2)
TICKET_W = 470


@lru_cache(maxsize=None)
def ticket_src():
    return Image.open(TICKET_PATH).convert("RGBA")


@lru_cache(maxsize=None)
def region(name, w=None):
    img = ticket_src().crop(REG[name])
    if w:
        img = img.resize((w, int(img.height * w / img.width)), Image.LANCZOS)
    return img


# ================================================================== host
RAISES = ((3.25, 6.7, 1.12, -60), (37.5, 42.5, 1.06, -25))  # (start, end, scale, dy) "show the ticket" moments


def raise_amount(t):
    for a, b, sc, dy in RAISES:
        if a - 0.4 <= t <= b + 0.4:
            k = ease_in_out(clamp((t - a + 0.4) / 0.4)) * ease_in_out(clamp((b + 0.4 - t) / 0.4))
            return 1 + (sc - 1) * k, dy * k
    return 1.0, 0.0


def host_geom(t):
    """Screen transform of the hold group: (cx, cy, scale)."""
    bob = math.sin(t * 2.1) * 6
    sc, dy = raise_amount(t)
    return HOST_C[0], HOST_C[1] + bob + dy, HOST_S * sc


def ticket_point(t, u, v):
    """Screen position of pixel (u, v) of the ticket photo while the host holds it."""
    cx, cy, s = host_geom(t)
    tx, ty, tw, th = G.ticket_box(TICKET_W, (FRONT[2], FRONT[3]))
    bx = tx + u / FRONT[2] * tw
    by = ty + v / FRONT[3] * th
    return cx + (bx - G.GW / 2) * s, cy + (by - G.GH / 2) * s


def draw_host(c, t, frame, env):
    name, s, e = scene_at(t)
    mouth, blink, brow = presenter_state(frame, env)
    if name in BROLL_SCENES:
        draw_pip(c, t, mouth, blink, brow, s, e)
        return
    k_in = ease_out_cubic(prog(t, 0.0, 0.7))
    sway = math.sin(t * 1.3) * 1.2
    cx, cy, s_hold = host_geom(t)
    y_off = (1 - k_in) * 700
    body = G.body_img(mouth, blink, brow)
    paste(c, glow_sprite(420, (255, 220, 150), 0.35), CX, HOST_C[1] - 180 + y_off)
    paste(c, body, HOST_C[0], HOST_C[1] + math.sin(t * 2.1) * 4 + y_off, HOST_S, rot=sway)
    paste(c, G.hold_img(TICKET_PATH, FRONT, TICKET_W), cx, cy + y_off, s_hold)


@lru_cache(maxsize=None)
def pip_frame():
    s = 330
    return gradient_box(s, s, s // 2, (255, 230, 200), (255, 180, 120))


def draw_pip(c, t, mouth, blink, brow, s, e):
    k = ease_out_back(prog(t, s, 0.4)) * (1 - prog(t, e - 0.25, 0.25))
    if k <= 0:
        return
    size = 330
    frame_img = pip_frame().copy()
    face = G.body_img(mouth, blink, brow).crop((140, 110, 580, 700)).resize((330, 442), Image.BICUBIC)
    frame_img.alpha_composite(face, (0, 10))
    mask = Image.new("L", frame_img.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    out = Image.new("RGBA", frame_img.size, (0, 0, 0, 0))
    out.paste(frame_img, (0, 0), mask)
    ring = Image.new("RGBA", (size + 30, size + 30), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse((5, 5, size + 24, size + 24), outline=GOLD + (255,), width=10)
    x, y = W - 200, 1490
    paste(c, out, x, y, k)
    paste(c, ring, x, y, k)
    paste(c, sticker("PUNJABAN UPDATE", 30, MAGENTA, WHITE, rot=0), x, y + 175, k)


# ================================================================== style pieces
@lru_cache(maxsize=None)
def phulkari_border(w=W, h=64):
    def draw(d, s, img):
        d.rectangle((0, 0, w * s, h * s), fill=MAGENTA)
        n = 18
        step = w / n
        for i in range(n):
            cx = (i + 0.5) * step
            col = (255, 200, 40) if i % 2 else (255, 120, 30)
            d.polygon([(cx * s, 6 * s), ((cx + step / 2 - 4) * s, h / 2 * s), (cx * s, (h - 6) * s),
                       ((cx - step / 2 + 4) * s, h / 2 * s)], fill=col)
            d.polygon([(cx * s, 20 * s), ((cx + 10) * s, h / 2 * s), (cx * s, (h - 20) * s),
                       ((cx - 10) * s, h / 2 * s)], fill=(230, 30, 90))
        d.rectangle((0, (h - 5) * s, w * s, h * s), fill=GOLD)
    return supersampled(w, h, draw)


@lru_cache(maxsize=None)
def sticker(text, size=60, bg=WHITE, fg=MAGENTA, rot=-3, fname="xbold", pad=26):
    t = text_img(text, fname, size, fill=fg)
    img = rounded_box(t.width + pad * 2, t.height + pad, 26, bg + (255,), shadow=10)
    img.alpha_composite(t, ((img.width - t.width) // 2, (img.height - t.height) // 2))
    return img.rotate(rot, expand=True, resample=Image.BICUBIC) if rot else img


def sticker_in(c, t, start, img, x, y, end=None):
    """Story-style sticker: pops with a bounce, wiggles gently, pops out at `end`."""
    p = prog(t, start, 0.4)
    if p <= 0:
        return
    out = prog(t, end, 0.25) if end else 0
    if out >= 1:
        return
    paste(c, img, x, y, ease_out_back(p) * (1 - out) * (1 + 0.015 * math.sin(t * 4 + x)),
          rot=math.sin(t * 2.5 + y) * 1.5)


@lru_cache(maxsize=None)
def lens_img(name, r):
    src = region(name)
    scale = max(2 * r / src.width, 2 * r / src.height)
    img = src.resize((int(src.width * scale), int(src.height * scale)), Image.LANCZOS)
    img = img.crop(((img.width - 2 * r) // 2, (img.height - 2 * r) // 2, (img.width + 2 * r) // 2,
                    (img.height + 2 * r) // 2))
    mask = Image.new("L", (2 * r, 2 * r), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=255)
    out = Image.new("RGBA", (2 * r + 40, 2 * r + 40), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((20, 30, 2 * r + 20, 2 * r + 30), fill=(0, 0, 0, 150))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    out.paste(img, (20, 20), mask)
    ImageDraw.Draw(out).ellipse((14, 14, 2 * r + 26, 2 * r + 26), outline=GOLD + (255,), width=12)
    ImageDraw.Draw(out).arc((34, 34, 2 * r + 6, 2 * r + 6), 200, 250, fill=(255, 255, 255, 180), width=8)
    return out


@lru_cache(maxsize=None)
def wide_lens(name, w):
    """Rounded-rectangle zoom panel for wide regions (title, date strip)."""
    img = region(name, w)
    fr = rounded_box(img.width + 24, img.height + 24, 22, GOLD + (255,), shadow=10)
    fr.alpha_composite(img, (fr.width // 2 - img.width // 2, fr.height // 2 - img.height // 2 - 5))
    return fr


def lens(c, t, start, end, img, x, y, src_center):
    """Zoom lens popping out of the ticket in the host's hands, with a guide line to the spot."""
    p = prog(t, start, 0.45)
    if p <= 0 or t > end + 0.3:
        return
    out = prog(t, end, 0.3)
    k = ease_out_back(p) * (1 - out)
    sx, sy = ticket_point(t, *src_center)
    d = ImageDraw.Draw(c)
    ex, ey = lerp(sx, x, ease_out_cubic(p)), lerp(sy, y, ease_out_cubic(p))
    d.line((sx, sy, ex, ey), fill=(255, 240, 180, int(230 * (1 - out))), width=6)
    d.ellipse((sx - 14, sy - 14, sx + 14, sy + 14), outline=(255, 240, 180, int(255 * (1 - out))), width=6)
    paste(c, img, lerp(sx, x, ease_out_cubic(p)), lerp(sy, y, ease_out_cubic(p)), k)


def overlay(c, t):
    paste(c, phulkari_border(), 0, 0, anchor="tl")
    D.draw_ticker(c, t, TICKER, 0.8, 62.4)


# ================================================================== host scenes
def scene_hello(c, t, s, e):
    D.firework_show(c, t, 0.1, [(0, 220, 360), (1.2, 860, 320)], seed=4)
    sticker_in(c, t, 0.15, sticker("सत श्री अकाल जी!", 76, WHITE, MAGENTA, -4), CX, 250)
    sticker_in(c, t, 1.2, sticker("की हाल ए?", 58, (255, 200, 40), PLUM, 5), 760, 400)
    base.sparkles(c, t, CX, 330, (420, 140), 10, seed=2)


def scene_show(c, t, s, e):
    sticker_in(c, t, 2.65, sticker("देखो!", 90, (255, 200, 40), PLUM, -6), 300, 260)
    p = prog(t, 3.0, 0.4)
    if p > 0:  # bouncing arrow pointing at the ticket
        ax, ay = 300, 400 + math.sin(t * 8) * 14
        d = ImageDraw.Draw(c)
        d.polygon([(ax - 26, ay), (ax + 26, ay), (ax + 26, ay + 70), (ax + 52, ay + 70), (ax, ay + 130),
                   (ax - 52, ay + 70), (ax - 26, ay + 70)], fill=WHITE + (int(255 * p),))
    sticker_in(c, t, 5.5, sticker("इस दिवाली का सबसे वड्डा टिकट!", 50, MAGENTA, WHITE, 3), 640, 330)
    if t > 3.3:
        base.sparkles(c, t, CX, 1300, (380, 120), 12, seed=6)


def scene_name(c, t, s, e):
    lens(c, t, 6.9, 10.2, wide_lens("title", 820), CX, 300, (670, 92))
    sticker_in(c, t, 10.4, sticker("पंजाब सरकार की ऑफिशियल लॉटरी", 48, (20, 150, 70), WHITE, -2),
               660, 300)
    lens(c, t, 10.45, 12.7, lens_img("logo", 90), 130, 330, (228, 130))


def scene_sold(c, t, s, e):
    sticker_in(c, t, 16.6, sticker("1st PRIZE", 64, (255, 200, 40), PLUM, -4, "anton"), CX, 230)
    msg = gradient_box(940, 200, 30, (40, 180, 90), (10, 110, 50), outline=GOLD + (255,), width=6, shadow=12)
    d = ImageDraw.Draw(msg)
    d.text((494, 92), "सिर्फ़ बिके हुए टिकटों में से", font=font("xbold", 58), fill=WHITE, anchor="mm")
    d.text((494, 162), "ही निकलेगा!", font=font("xbold", 62), fill=GOLD_LIGHT, anchor="mm")
    sticker_in(c, t, 17.0, msg, CX, 420)
    lens(c, t, 18.2, 20.0, wide_lens("sold", 760), CX, 590, (655, 732))
    if t > 19.4:
        paste(c, base.check_badge(int(prog(t, 19.4, 0.35) * 20)), 960, 380, ease_out_back(prog(t, 19.4, 0.3)))


def scene_total(c, t, s, e):
    sticker_in(c, t, 29.2, sticker("कुल मिलाकर", 54, WHITE, MAGENTA, -3), 330, 230)
    cp = prog(t, 29.4, 1.6)
    if cp > 0:
        val = 190842 if cp >= 1 else int(190842 * ease_out_cubic(cp))
        num = grad_text(indian_format(val), "anton", 170, stroke=8, stroke_fill=PLUM)
        paste(c, num, CX, 400, ease_out_back(min(1, cp * 3)))
        sticker_in(c, t, 31.0, sticker("इनाम!", 64, (255, 200, 40), PLUM, 4), 850, 540)
        if t > 31.0:
            base.confetti(c, t, 31.0, count=70, burst_y=500)


def scene_date(c, t, s, e):
    lens(c, t, 37.55, 40.4, wide_lens("date", 640), CX, 300, (1135, 270))
    sticker_in(c, t, 38.4, sticker("16 NOV • 6 PM", 56, (255, 200, 40), PLUM, -4, "anton"), 300, 470, end=40.4)
    lens(c, t, 40.55, 42.45, lens_img("mrp", 105), 300, 330, (972, 282))
    sticker_in(c, t, 41.4, sticker("सिर्फ़ ₹500", 70, MAGENTA, WHITE, 4), 700, 380)


def scene_contact(c, t, s, e):
    sticker_in(c, t, 42.6, sticker("तो फिर देर किस गल दी?", 56, (255, 200, 40), PLUM, -3), CX, 240, end=43.9)
    p = prog(t, 43.95, 0.5)
    if p > 0:
        paste(c, base.agency_card(), CX, 300, ease_out_back(p) * 0.92)
    for i, (num, st, en) in enumerate((("89688 69862", 48.6, 52.0), ("70598 77770", 52.6, 56.7))):
        q = prog(t, st, 0.45)
        if q > 0:
            lit = st <= t < en
            paste(c, base.phone_pill(num, lit), 280 + i * 520, 520,
                  ease_out_back(q) * 0.95 * (1 + (0.05 * abs(math.sin(t * 6)) if lit else 0)))


def scene_bye(c, t, s, e):
    D.firework_show(c, t, s - 0.5, [(0.8, 220, 330), (1.6, 860, 300), (2.5, 540, 240), (3.3, 280, 420)], seed=7)
    sticker_in(c, t, 56.8, sticker("ज़िम्मेदारी नाल खेलो", 56, WHITE, MAGENTA, -3), CX, 230)
    sticker_in(c, t, 58.1, grad_text("HAPPY DIWALI", "anton", 120, top=(255, 245, 170), bottom=(255, 120, 20),
                                     stroke=7, stroke_fill=PLUM), CX, 390)
    sticker_in(c, t, 60.05, sticker("बल्ले बल्ले!", 80, (255, 200, 40), PLUM, 6), 760, 540)
    for i, x in enumerate((140, 940)):
        D.diya(c, t, x, 1300, 1.0, seed=i)


# ================================================================== B-roll cutaways
def broll_bg(c, t, s, col=(30, 6, 40)):
    a = prog(t, s, 0.25)
    c.alpha_composite(Image.new("RGBA", c.size, col + (int(150 * a),)))


def scene_jackpot(c, t, s, e):
    broll_bg(c, t, s)
    paste(c, D.rangoli(), CX, 760, 1.5, rot=t * 25, alpha=0.5)
    paste(c, glow_sprite(560, (255, 210, 90), 0.7), CX, 760, 1.2 + 0.05 * math.sin(t * 6))
    D.firework_show(c, t, s - 0.4, [(0.5, 200, 380), (1.2, 880, 330), (1.9, 540, 250), (2.6, 300, 1100)], seed=3)
    base.coin_rain(c, t, s + 0.3, count=36, seed=5, dur=3.2)
    p = prog(t, s + 0.05, 0.8)
    paste(c, region("jack", 640), CX, 760, ease_out_elastic(p) * (1 + 0.02 * math.sin(t * 3)), rot=(1 - p) * -40)
    sticker_in(c, t, s + 0.2, sticker("1st PRIZE", 70, (255, 200, 40), PLUM, -4, "anton"), CX, 250)
    if t > 13.9:
        paste(c, grad_text("₹12 CRORE", "anton", 170, stroke=9, stroke_fill=PLUM), CX, 1180,
              ease_out_elastic(prog(t, 13.95, 0.8)))
    gp = prog(t, 15.5, 0.25)
    if gp > 0:
        st = text_img(" GUARANTEED ", "anton", 96, fill=WHITE)
        box = gradient_box(st.width + 20, st.height + 10, 20, (40, 180, 90), (10, 110, 50), outline=GOLD + (255,),
                           width=8, shadow=10)
        box.alpha_composite(st, ((box.width - st.width) // 2, (box.height - st.height) // 2))
        paste(c, box, CX, 1330, lerp(2.4, 1.0, ease_out_cubic(gp)), rot=-5, alpha=min(1, gp * 2))
    flash = clamp(1 - (t - s) / 0.3)
    if flash > 0:
        c.alpha_composite(Image.new("RGBA", c.size, (255, 255, 255, int(255 * flash))))


@lru_cache(maxsize=None)
def ladder_card(img_name, title, amount, count, c1, c2):
    w, h = 960, 300
    card = gradient_box(w, h, 32, c1, c2, outline=GOLD + (255,), width=6, shadow=12, horizontal=True)
    off = 24
    x0 = off + 40
    if img_name:
        m = region(img_name, 230)
        mask = Image.new("L", m.size, 0)
        ImageDraw.Draw(mask).ellipse((0, 0, m.width - 1, m.height - 1), fill=255)
        card.paste(m, (off + 24, off + (h - m.height) // 2), mask)
        x0 = off + 290
    card.alpha_composite(text_img(title, "anton", 62, fill=WHITE, shadow=3), (x0, off + 30))
    card.alpha_composite(text_img(amount, "xbold", 80, fill=GOLD_LIGHT, stroke=4, stroke_fill=DEEP_RED, shadow=4),
                         (x0 - 4, off + 105))
    card.alpha_composite(text_img(count, "anton", 46, fill=WHITE), (x0, off + 215))
    return card


def scene_prizes(c, t, s, e):
    broll_bg(c, t, s)
    sticker_in(c, t, s + 0.1, sticker("और भी बड़े इनाम!", 64, (255, 200, 40), PLUM, -3), CX, 240)
    cards = [(20.2, "second", "2nd PRIZE", "₹1 CRORE each", "3 WINNERS", (60, 70, 140), (25, 30, 80)),
             (23.0, "third", "3rd PRIZE", "₹50 LAKH each", "3 WINNERS", (170, 90, 40), (100, 45, 20)),
             (26.3, None, "CONSOLATION", "₹10 LAKH each", "11 WINNERS", (200, 40, 120), (110, 10, 70))]
    for i, (st, img, title, amt, cnt, c1, c2) in enumerate(cards):
        p = prog(t, st, 0.45)
        if p > 0:
            card = ladder_card(img, title, amt, cnt, c1, c2)
            paste(c, card, lerp(-W if i % 2 == 0 else 2 * W, CX, ease_out_cubic(p)), 470 + i * 330)
    if t > 26.9:
        for i in range(11):
            p = prog(t, 26.9 + i * 0.09, 0.25)
            paste(c, base.winner_icon(), 470 + (i % 6) * 80 + (i // 6) * 40, 1080 + (i // 6) * 70, ease_out_back(p) * 0.8)


@lru_cache(maxsize=None)
def rashi_chip(i, lit):
    hi, en = D.RASHIS[i]
    col = (255, 200, 40) if lit else (255, 255, 255)
    img = rounded_box(150, 150, 75, col + (255,), outline=GOLD + (255,), width=5, shadow=6)
    d = ImageDraw.Draw(img)
    d.text((87, 70), chr(0x2648 + i), font=font("sym", 56), fill=MAGENTA, anchor="mm")
    d.text((87, 122), hi, font=font("xbold", 28), fill=PLUM, anchor="mm")
    return img


def scene_rashi(c, t, s, e):
    broll_bg(c, t, s)
    sticker_in(c, t, s + 0.1, sticker("12 राशियों में टिकट", 64, (255, 200, 40), PLUM, -3), CX, 240)
    wp = ease_out_back(prog(t, s + 0.2, 0.6))
    paste(c, D.zodiac_wheel(), CX, 800, wp * 0.85, rot=-t * 18)
    for i in range(12):  # chips orbiting the wheel
        a = -math.pi / 2 + i * math.pi / 6 + t * 0.25
        x, y = CX + math.cos(a) * 400, 800 + math.sin(a) * 400
        lit = (i == 0 and 36.3 <= t < 37.0) or (i == 11 and t >= 37.0)
        p = prog(t, s + 0.4 + i * 0.07, 0.3)
        paste(c, rashi_chip(i, lit), x, y, ease_out_back(p) * (1.25 if lit else 0.85))
    sticker_in(c, t, 34.6, sticker("अपनी राशि चुनो!", 60, MAGENTA, WHITE, 3), CX, 1300)


SCENE_FUNCS = {
    "hello": scene_hello, "show": scene_show, "name": scene_name, "jackpot": scene_jackpot, "sold": scene_sold,
    "prizes": scene_prizes, "total": scene_total, "rashi": scene_rashi, "date": scene_date,
    "contact": scene_contact, "bye": scene_bye,
}
