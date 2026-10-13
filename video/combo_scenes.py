"""Scenes for the 3-ticket COMBO offer video (₹1199, free delivery).

Reuses the Diwali video's festive elements (fireworks, toran, rangoli, ticker, pop-up card)
and the generic widgets from scenes.py.
"""
import math
import os
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

import diwali_scenes as D
import scenes as base
from combo_timeline import CONTACT_POPUPS
from gfx import (DEEP_RED, GOLD, GOLD_LIGHT, ROOT, WHITE, ease_in_out, ease_out_back, ease_out_cubic,
                 ease_out_elastic, font, glow_sprite, grad_text, gradient_box, lerp, paste, prog, rounded_box,
                 supersampled, text_img)
from timeline import W

CX = W // 2
MAROON = D.MAROON
title_in, pill, sparkles, gold_ribbon = base.title_in, base.pill, base.sparkles, D.gold_ribbon

ALL_PHONES = ("89688 69862", "70598 77770", "70598 77771", "75088 77772", "70808 02080")
TICKER = (f"  ★ SUMIT LOTTERY AGENCY  •  One Way Traffic Road, Mansa  •  COMBO ₹1199 + FREE DELIVERY  •  "
          f"☎ / WhatsApp  {'  •  '.join(ALL_PHONES)}  ")

# key: (poster crop or None for the real Diwali ticket, name lines, prize, draw, price, colours)
TICKETS = {
    "ticket1": dict(crop=(450, 428, 808, 660), label="TICKET 1", name=("NAGALAND STATE DEAR", "PUJA BUMPER 2026"),
                    prize="₹3 CRORE", draw="24-10-2026 • 6 PM", price="₹500", prize_t=13.6, draw_t=16.6, price_t=19.4,
                    cols=((150, 40, 200), (70, 10, 110))),
    "ticket2": dict(crop=(30, 398, 440, 652), label="TICKET 2", name=("PUNJAB STATE DEAR 200", "MONTHLY LOTTERY"),
                    prize="₹1.50 CRORE", draw="07-11-2026 • 6 PM", price="₹200", prize_t=25.1, draw_t=28.3,
                    price_t=31.2, cols=((220, 40, 50), (130, 10, 30))),
    "ticket3": dict(crop=None, label="TICKET 3", name=("PUNJAB STATE DEAR", "DIWALI BUMPER 2026"), prize="₹12 CRORE",
                    draw="16-11-2026 • 6 PM", price="₹500", prize_t=36.1, draw_t=39.8, price_t=42.8,
                    cols=((30, 60, 160), (10, 25, 80))),
}


# ================================================================== assets
@lru_cache(maxsize=None)
def poster():
    return Image.open(os.path.join(ROOT, "assets", "combo", "poster.png")).convert("RGBA")


def framed(img, width, radius=18, border=8):
    h = int(img.height * width / img.width)
    img = img.resize((width, h), Image.LANCZOS)
    fr = Image.new("RGBA", (width + border * 2, h + border * 2), GOLD + (255,))
    fr.paste(img, (border, border))
    mask = Image.new("L", fr.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, fr.width - 1, fr.height - 1), radius, fill=255)
    out = Image.new("RGBA", (fr.width + 50, fr.height + 50), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 170), (25, 35), mask)
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    out.paste(fr, (25, 25), mask)
    return out


@lru_cache(maxsize=None)
def ticket_img(key, width=740):
    crop = TICKETS[key]["crop"]
    src = poster().crop(crop) if crop else D.ticket_full().crop((0, 0, 1292, 800))
    return framed(src, width)


@lru_cache(maxsize=None)
def crown():
    def draw(d, s, img):
        pts = [(10, 150), (30, 40), (80, 100), (130, 10), (180, 100), (230, 40), (250, 150)]
        d.polygon([(x * s, y * s) for x, y in pts], fill=(255, 200, 30), outline=(190, 120, 0))
        d.rectangle((10 * s, 140 * s, 250 * s, 175 * s), fill=(230, 160, 10))
        for x, col in ((60, (230, 30, 60)), (130, (40, 170, 230)), (200, (230, 30, 60))):
            d.ellipse(((x - 12) * s, (146) * s, (x + 12) * s, 170 * s), fill=col)
        for x, y in ((30, 40), (130, 10), (230, 40)):
            d.ellipse(((x - 12) * s, (y - 12) * s, (x + 12) * s, (y + 12) * s), fill=(255, 240, 160))
    return supersampled(260, 185, draw)


@lru_cache(maxsize=None)
def van():
    def draw(d, s, img):
        S = lambda *v: [x * s for x in v]  # noqa: E731
        d.rounded_rectangle(S(10, 30, 330, 200), 18 * s, fill=(255, 255, 255))
        d.rounded_rectangle(S(320, 80, 450, 200), 22 * s, fill=(230, 40, 50))
        d.polygon(S(340, 95, 420, 95, 440, 140, 340, 140), fill=(180, 220, 255))
        d.rectangle(S(10, 150, 450, 175), fill=(200, 30, 40))
        d.text((170 * s, 90 * s), "FREE", font=font("anton", 48 * s), fill=(200, 30, 40), anchor="mm")
        d.text((170 * s, 135 * s), "DELIVERY", font=font("anton", 32 * s), fill=(30, 60, 160), anchor="mm")
        for x in (90, 370):
            d.ellipse(S(x - 34, 166, x + 34, 234), fill=(30, 30, 35))
            d.ellipse(S(x - 15, 185, x + 15, 215), fill=(200, 200, 210))
    return supersampled(460, 240, draw)


# ================================================================== header / overlay
@lru_cache(maxsize=None)
def header_img():
    w, h = 1000, 120
    img = gradient_box(w, h, 26, (200, 25, 45), (110, 5, 30), outline=GOLD + (255,), width=4, shadow=10, horizontal=True)
    off = 20
    img.alpha_composite(text_img("SUMIT LOTTERY AGENCY • MANSA", "anton", 46, fill=GOLD_LIGHT), (off + 26, off + 8))
    img.alpha_composite(text_img("3 TICKETS COMBO • FREE DELIVERY", "semi", 28, fill=(255, 230, 190)), (off + 30, off + 70))
    chip = rounded_box(220, 84, 20, GOLD + (255,))
    d = ImageDraw.Draw(chip)
    d.text((110, 24), "ONLY", font=font("anton", 28), fill=MAROON, anchor="mm")
    d.text((110, 58), "₹1199", font=font("xbold", 40), fill=(200, 20, 40), anchor="mm")
    img.alpha_composite(chip, (off + w - 236, off + 18))
    return img


def overlay(c, t):
    for st in CONTACT_POPUPS:
        lt = t - st
        if 0 <= lt < 4.2:
            p_in = ease_out_back(prog(lt, 0, 0.45))
            p_out = ease_in_out(prog(lt, 3.7, 0.5))
            paste(c, D.popup_card(), lerp(-420, 345, p_in) - p_out * 800, 1515 + math.sin(t * 3) * 4)
    D.draw_ticker(c, t, TICKER, 1.0, 84.0)


# ================================================================== scenes
def scene_intro(c, t, s, e):
    D.firework_show(c, t, 0.1, [(0, 230, 360), (1.6, 860, 300), (3.2, 540, 230)], seed=2)
    paste(c, D.toran(), CX, 115, alpha=prog(t, 0, 0.4))
    paste(c, grad_text("धमाकेदार ऑफ़र!", "xbold", 120, stroke=8, stroke_fill=MAROON), CX, 330,
          ease_out_elastic(prog(t, 0.15, 1.0)))
    title_in(c, t, 1.5, pill("SUMIT LOTTERY AGENCY, MANSA", "anton", 50, fill=(255, 250, 235, 255), color=MAROON),
             CX, 470, "up")
    title_in(c, t, 4.1, gold_ribbon("तीन ज़बरदस्त टिकटें", 640, 100, size=58, fname="xbold"), CX, 590, "pop")
    cp = prog(t, 5.35, 0.6)
    if cp > 0:
        paste(c, glow_sprite(420, (255, 210, 90), 0.6), CX, 760, 1.2)
        paste(c, crown(), CX, 655, ease_out_back(cp) * 0.8)
        paste(c, grad_text("COMBO", "anton", 230, stroke=10, stroke_fill=MAROON), CX, 780, ease_out_elastic(cp))
    sparkles(c, t, CX, 600, (460, 280), 14, seed=7)


def scene_hook(c, t, s, e):
    paste(c, D.rangoli(), CX, 700, 1.3, rot=t * 12, alpha=0.4)
    title_in(c, t, s + 0.05, gold_ribbon("एक ही कॉम्बो में", 600, 100, size=60, fname="xbold"), CX, 300, "pop")
    for i, (key, rot, x) in enumerate((("ticket1", -10, 250), ("ticket3", 0, 540), ("ticket2", 10, 830))):
        p = prog(t, 6.1 + i * 0.25, 0.45)
        if p > 0:
            paste(c, ticket_img(key, 420), lerp(CX, x, ease_out_cubic(p)), 640 + abs(i - 1) * 40,
                  ease_out_back(p), rot=rot * p)
    for i, (txt, x) in enumerate((("₹3 Cr", 250), ("₹12 Cr", 540), ("₹1.5 Cr", 830))):
        title_in(c, t, 6.6 + i * 0.2, pill(txt, "anton", 54, fill=GOLD + (255,), color=MAROON), x, 860, "pop")
    title_in(c, t, 7.7, grad_text("3 करोड़पति बनने के मौके!", "xbold", 82, stroke=6, stroke_fill=MAROON), CX, 1030, "up")


def scene_ticket(key):
    T = TICKETS[key]

    def draw(c, t, s, e):
        lt = t - s
        title_in(c, t, s + 0.05, ribbon_for(key), CX, 268, "pop")
        p = ease_out_cubic(prog(lt, 0.1, 0.6))
        paste(c, glow_sprite(480, (255, 210, 100), 0.35), CX, 590, alpha=p)
        paste(c, ticket_img(key), lerp(-W, CX, p) if key != "ticket2" else lerp(2 * W, CX, p),
              590 + 8 * math.sin(lt * 2), lerp(0.8, 1.0, p) * (1 + 0.03 * prog(lt, 0.7, 8)), rot=lerp(20, 0, p))
        title_in(c, t, s + 0.6, text_img(T["name"][0], "anton", 64, fill=WHITE, stroke=4, stroke_fill=MAROON, shadow=4),
                 CX, 880, "up")
        title_in(c, t, s + 0.8, grad_text(T["name"][1], "anton", 74, stroke=5, stroke_fill=MAROON), CX, 955, "up")
        pp = prog(t, T["prize_t"], 0.7)
        if pp > 0:
            paste(c, text_img("1st PRIZE", "anton", 50, fill=GOLD_LIGHT, stroke=3, stroke_fill=MAROON), CX, 1040,
                  alpha=min(1, pp * 3))
            paste(c, grad_text(T["prize"], "anton", 130, stroke=8, stroke_fill=MAROON), CX, 1130, ease_out_elastic(pp))
            base.coin_rain(c, t, T["prize_t"], count=14, seed=int(key[-1]) * 7, dur=2.2)
        dp = prog(t, T["draw_t"], 0.4)
        if dp > 0:
            paste(c, info_chip("DRAW", T["draw"]), 330, 1285, ease_out_back(dp))
        rp = prog(t, T["price_t"], 0.4)
        if rp > 0:
            paste(c, info_chip("TICKET", T["price"]), 820, 1285, ease_out_back(rp))
    return draw


@lru_cache(maxsize=None)
def ribbon_for(key):
    T = TICKETS[key]
    return base.ribbon(T["label"], 440, 96, T["cols"][0], T["cols"][1], 58, "anton")


@lru_cache(maxsize=None)
def info_chip(label, value):
    lt = text_img(label, "anton", 30, fill=MAROON)
    vt = text_img(value, "anton", 48 if len(value) > 6 else 62, fill=DEEP_RED)
    w = max(lt.width, vt.width) + 50
    h = lt.height + vt.height + 14
    img = rounded_box(w, h, 22, (255, 245, 220, 255), outline=GOLD + (255,), width=5, shadow=8)
    off = 16
    img.alpha_composite(lt, (off + (w - lt.width) // 2, off + 6))
    img.alpha_composite(vt, (off + (w - vt.width) // 2, off + lt.height + 2))
    return img


def guaranteed_stamp():
    st = text_img(" GUARANTEED ", "anton", 52, fill=WHITE)
    box = gradient_box(st.width + 12, st.height + 6, 14, (40, 180, 90), (10, 110, 50), outline=GOLD + (255,), width=5)
    box.alpha_composite(st, ((box.width - st.width) // 2, (box.height - st.height) // 2))
    return box


def scene_guarantee(c, t, s, e):
    title_in(c, t, s + 0.1, gold_ribbon("सबसे खास बात!", 560, 100, size=60, fname="xbold"), CX, 290, "pop")
    for i, (key, prize, y) in enumerate((("ticket1", "₹3 CRORE", 470), ("ticket2", "₹1.50 CRORE", 680),
                                         ("ticket3", "₹12 CRORE", 890))):
        p = prog(t, s + 0.3 + i * 0.2, 0.4)
        if p > 0:
            paste(c, ticket_img(key, 380), lerp(-400, 270, ease_out_cubic(p)), y)
            paste(c, grad_text(prize, "anton", 76, stroke=5, stroke_fill=MAROON), lerp(W + 400, 760, ease_out_cubic(p)),
                  y - 30)
            sp = prog(t, 46.9 + i * 0.25, 0.22)
            if sp > 0:
                paste(c, guaranteed_stamp(), 760, y + 50, lerp(2.4, 0.9, ease_out_cubic(sp)), rot=-6, alpha=min(1, sp * 2))
    msg = gradient_box(980, 200, 30, (40, 180, 90), (10, 110, 50), outline=GOLD + (255,), width=6, shadow=12)
    d = ImageDraw.Draw(msg)
    d.text((514, 92), "पहला इनाम सिर्फ़ बिके हुए", font=font("xbold", 58), fill=WHITE, anchor="mm")
    d.text((514, 162), "टिकटों में से ही निकलेगा!", font=font("xbold", 58), fill=GOLD_LIGHT, anchor="mm")
    title_in(c, t, 48.2, msg, CX, 1150, "pop")


def scene_price(c, t, s, e):
    title_in(c, t, s + 0.05, gold_ribbon("COMBO PRICE", 560, 100), CX, 290, "pop")
    parts = [("₹200", 52.3), ("+  ₹500", 52.7), ("+  ₹500", 53.1)]
    xs = (210, 520, 850)
    for (txt, st), x in zip(parts, xs):
        title_in(c, t, st, text_img(txt, "anton", 90, fill=WHITE, stroke=4, stroke_fill=MAROON, shadow=4), x, 450, "pop")
    if t >= 53.7:
        old = text_img("= ₹1200", "anton", 120, fill=(255, 235, 200), stroke=4, stroke_fill=MAROON, shadow=4)
        paste(c, old, CX, 600, ease_out_back(prog(t, 53.7, 0.4)))
        k = prog(t, 54.85, 0.35)
        if k > 0:
            d = ImageDraw.Draw(c)
            x0, x1 = CX - old.width / 2 + 10, CX + old.width / 2 - 10
            d.line((x0, 640, lerp(x0, x1, k), 560), fill=(255, 40, 60), width=14)
    if t >= 55.2 and t < 56.4:  # build-up while "sirf..." is said
        paste(c, glow_sprite(300, (255, 230, 150), 0.5), CX, 960, 1 + prog(t, 55.2, 1.2))
    if t >= 56.4:
        paste(c, glow_sprite(560, (255, 210, 90), 0.75), CX, 960, 1.2 + 0.05 * math.sin(t * 6))
        paste(c, text_img("ONLY", "anton", 90, fill=WHITE, stroke=4, stroke_fill=MAROON), CX, 800,
              ease_out_back(prog(t, 56.4, 0.4)))
        paste(c, grad_text("₹1199", "anton", 270, stroke=12, stroke_fill=MAROON), CX, 970,
              ease_out_elastic(prog(t, 56.4, 0.9)))
        base.confetti(c, t, 56.4, count=110, burst_y=1000)
        D.firework(c, t, 56.0, 220, 500, D.FW_COLS[0], seed=9)
        D.firework(c, t, 56.3, 860, 460, D.FW_COLS[2], seed=8)
    vp = prog(t, 58.9, 0.9)
    if vp > 0:
        x = lerp(-300, CX, ease_out_cubic(vp))
        bounce = abs(math.sin(t * 12)) * 4 if vp < 1 else 0
        paste(c, van(), x, 1255 - bounce)
        for i in range(3):  # speed lines
            ImageDraw.Draw(c).line((x - 330 - i * 30, 1215 + i * 30, x - 260 - i * 30, 1215 + i * 30),
                                   fill=(255, 255, 255, int(200 * (1 - vp))), width=6)


def scene_contact(c, t, s, e):
    title_in(c, t, s + 0.05, gold_ribbon("अभी ऑर्डर करें!", 600, 104, size=60, fname="xbold"), CX, 290, "pop")
    p = prog(t, 61.5, 0.5)
    if p > 0:
        paste(c, base.agency_card(), CX, 530, ease_out_back(p) * (1 + 0.012 * math.sin(t * 3)))
    for i, (num, st, en) in enumerate(((ALL_PHONES[0], 66.7, 70.6), (ALL_PHONES[1], 71.3, 75.9))):
        q = prog(t, st, 0.45)
        if q > 0:
            lit = st <= t < en
            paste(c, base.phone_pill(num, lit), 280 + i * 520, 800,
                  ease_out_back(q) * (1 + (0.05 * abs(math.sin(t * 6)) if lit else 0)))
    title_in(c, t, 65.6, pill("CALL / WhatsApp", "anton", 44, fill=(30, 170, 80, 255), color=WHITE, padx=30, pady=10),
             CX, 705, "pop")


def scene_responsible(c, t, s, e):
    lt = t - s
    paste(c, base.warning_sign(), CX, 330, ease_out_back(prog(lt, 0.1, 0.5)) * (1 + 0.03 * math.sin(t * 4)))
    title_in(c, t, s + 0.4, text_img("लॉटरी में जोखिम है", "xbold", 76, fill=WHITE, stroke=5, stroke_fill=MAROON, shadow=5),
             CX, 540, "up")
    title_in(c, t, 78.8, grad_text("ज़िम्मेदारी से खेलें", "xbold", 92, stroke=7, stroke_fill=MAROON), CX, 670, "pop")
    bp = prog(t, 80.2, 0.4)
    if bp > 0:
        def draw(d, s_, img):
            d.ellipse((0, 0, 150 * s_, 150 * s_), fill=WHITE, outline=(220, 30, 40), width=12 * s_)
            d.text((75 * s_, 78 * s_), "18+", font=font("anton", 64 * s_), fill=(220, 30, 40), anchor="mm")
        paste(c, supersampled(150, 150, draw), 860, 330, ease_out_back(bp))


SCENE_FUNCS = {
    "intro": scene_intro, "hook": scene_hook, "ticket1": scene_ticket("ticket1"), "ticket2": scene_ticket("ticket2"),
    "ticket3": scene_ticket("ticket3"), "guarantee": scene_guarantee, "price": scene_price, "contact": scene_contact,
    "responsible": scene_responsible,
}
