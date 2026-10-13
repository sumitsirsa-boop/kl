"""Scene graphics and procedural B-roll for each part of the script."""
import math
import os
import random
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from gfx import (DEEP_RED, GOLD, GOLD_LIGHT, GREEN, NAVY, ORANGE, PINK, RED, ROOT, WHITE, clamp, ease_in_out,
                 ease_out_back, ease_out_cubic, ease_out_elastic, font, glow_sprite, grad_text, gradient_box,
                 indian_format, lerp, paste, prog, rounded_box, supersampled, text_img)
from timeline import H, W

CX = W // 2


# ================================================================== assets
@lru_cache(maxsize=None)
def ticket_full():
    return Image.open(os.path.join(ROOT, "assets", "ticket.jpg")).convert("RGBA")


@lru_cache(maxsize=None)
def ticket_front(width=980):
    img = ticket_full().crop((0, 0, 1014, 642))
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


@lru_cache(maxsize=None)
def shine_band(w, h):
    band = np.zeros((h, 160, 4), np.uint8)
    band[..., :3] = 255
    band[..., 3] = (np.sin(np.linspace(0, np.pi, 160)) ** 2 * 120).astype(np.uint8)[None, :]
    return Image.fromarray(band, "RGBA").rotate(-18, expand=True, resample=Image.BICUBIC)


@lru_cache(maxsize=None)
def coin_sprite(size=96):
    def draw(d, s, img):
        r = size * s
        d.ellipse((0, 0, r - 1, r - 1), fill=(200, 140, 10))
        d.ellipse((4 * s, 4 * s, r - 4 * s, r - 4 * s), fill=(255, 200, 40))
        d.ellipse((12 * s, 12 * s, r - 12 * s, r - 12 * s), outline=(210, 150, 20), width=3 * s)
        f = font("xbold", int(size * 0.55 * s))
        d.text((r / 2, r / 2 + 2 * s), "₹", font=f, fill=(190, 120, 0), anchor="mm")
        d.ellipse((18 * s, 14 * s, 40 * s, 28 * s), fill=(255, 245, 200))
    return supersampled(size, size, draw)


@lru_cache(maxsize=None)
def note_sprite(kind=0):
    w, h = 170, 80
    cols = [((110, 190, 120), (50, 120, 60)), ((240, 150, 200), (170, 60, 120)), ((240, 210, 120), (160, 120, 30))]
    c1, c2 = cols[kind % 3]
    img = gradient_box(w, h, 8, c1, c2, outline=(255, 255, 255, 180), width=3, horizontal=True)
    d = ImageDraw.Draw(img)
    d.ellipse((w // 2 - 26, h // 2 - 26, w // 2 + 26, h // 2 + 26), outline=(255, 255, 255, 200), width=3)
    d.text((w // 2, h // 2), "₹", font=font("xbold", 34), fill=(255, 255, 255), anchor="mm")
    d.text((14, 8), "500" if kind == 0 else "2000" if kind == 1 else "200", font=font("bold", 18), fill=(255, 255, 255))
    return img


# ================================================================== particles
def coin_rain(canvas, t, t0, count=34, seed=1, dur=4.0):
    lt = t - t0
    if lt < 0 or lt > dur + 2:
        return
    rnd = random.Random(seed)
    for i in range(count):
        delay = rnd.uniform(0, dur * 0.6)
        x = rnd.uniform(40, W - 40)
        speed = rnd.uniform(900, 1500)
        spin = rnd.uniform(4, 9)
        size = rnd.uniform(0.6, 1.2)
        k = lt - delay
        if k < 0:
            continue
        y = -100 + speed * k + 300 * k * k
        if y > H + 100:
            continue
        sx = abs(math.cos(spin * k)) * 0.9 + 0.1
        if i % 4 == 3:
            paste(canvas, note_sprite(i % 3), x + 60 * math.sin(k * 3 + i), y * 0.8, size,
                  rot=math.degrees(math.sin(k * 2 + i)) * 0.6, sy=sx)
        else:
            paste(canvas, coin_sprite(), x, y, size, sx=sx)


CONFETTI_COLS = [GOLD, RED, GREEN, PINK, (60, 160, 255), WHITE, ORANGE]


def confetti(canvas, t, t0, count=120, seed=3, dur=3.5, burst_y=700):
    lt = t - t0
    if lt < 0 or lt > dur:
        return
    rnd = random.Random(seed)
    d = ImageDraw.Draw(canvas)
    fade = clamp((dur - lt) / 0.8)
    for i in range(count):
        ang = rnd.uniform(-math.pi, 0)
        sp = rnd.uniform(700, 1600)
        vx, vy = math.cos(ang) * sp, math.sin(ang) * sp
        x = CX + vx * lt * 0.9
        y = burst_y + vy * lt + 900 * lt * lt
        x += math.sin(lt * 6 + i) * 30
        rot = lt * rnd.uniform(4, 12) + i
        s = rnd.uniform(9, 18)
        col = CONFETTI_COLS[i % len(CONFETTI_COLS)]
        pts = []
        for a in (0, 2.2, math.pi, math.pi + 2.2):
            pts.append((x + math.cos(rot + a) * s, y + math.sin(rot + a) * s * abs(math.cos(lt * 8 + i))))
        d.polygon(pts, fill=col + (int(255 * fade),))


def sparkles(canvas, t, cx, cy, spread, count=14, seed=5, color=(255, 240, 160)):
    rnd = random.Random(seed)
    for i in range(count):
        ph = rnd.uniform(0, 6.28)
        sp = rnd.uniform(1.5, 3.5)
        x = cx + rnd.uniform(-spread[0], spread[0])
        y = cy + rnd.uniform(-spread[1], spread[1])
        a = max(0.0, math.sin(t * sp + ph))
        if a > 0.05:
            star = star_sprite(color)
            paste(canvas, star, x, y, 0.3 + 0.7 * a, rot=t * 60 + i * 20, alpha=a)


@lru_cache(maxsize=None)
def star_sprite(color=(255, 240, 160)):
    def draw(d, s, img):
        c = 40 * s
        pts = []
        for k in range(8):
            r = (38 if k % 2 == 0 else 8) * s
            a = k * math.pi / 4
            pts.append((c + math.cos(a) * r, c + math.sin(a) * r))
        d.polygon(pts, fill=color + (255,))
    return supersampled(80, 80, draw)


# ================================================================== shared widgets
@lru_cache(maxsize=None)
def ribbon(text, w=620, h=96, c1=(240, 50, 60), c2=(170, 10, 30), size=58, fname="anton"):
    img = gradient_box(w, h, 18, c1, c2, outline=GOLD + (255,), width=5, shadow=10)
    t = text_img(text, fname, size, fill=WHITE, shadow=3)
    img.alpha_composite(t, ((img.width - t.width) // 2, (img.height - t.height) // 2))
    return img


@lru_cache(maxsize=None)
def pill(text, fname="bold", size=44, fill=(255, 255, 255, 235), color=NAVY, padx=40, pady=18, outline=None):
    t = text_img(text, fname, size, fill=color)
    w, h = t.width + padx * 2, t.height + pady * 2
    img = rounded_box(w, h, h // 2, fill, outline=outline, width=4 if outline else 0, shadow=8)
    img.alpha_composite(t, ((img.width - t.width) // 2, (img.height - t.height) // 2))
    return img


def title_in(canvas, t, start, img, cx, cy, mode="up"):
    p = prog(t, start, 0.45)
    if p <= 0:
        return
    if mode == "up":
        paste(canvas, img, cx, cy + (1 - ease_out_cubic(p)) * 80, alpha=p)
    elif mode == "pop":
        paste(canvas, img, cx, cy, ease_out_back(p), alpha=min(1, p * 3))
    elif mode == "left":
        paste(canvas, img, cx - (1 - ease_out_cubic(p)) * 700, cy, alpha=min(1, p * 2))
    elif mode == "right":
        paste(canvas, img, cx + (1 - ease_out_cubic(p)) * 700, cy, alpha=min(1, p * 2))


def typewriter(text, t, start, cps=22):
    n = int(max(0, t - start) * cps)
    return text[:n]


# ================================================================== scenes
def scene_intro(c, t, s, e):
    p = prog(t, 0.05, 0.5)
    paste(c, glow_sprite(420, (255, 220, 120), 0.6), CX, 470, 1 + 0.05 * math.sin(t * 3), alpha=p)
    title = grad_text("नमस्कार दोस्तों!", "xbold", 120, stroke=8)
    paste(c, title, CX, 400, ease_out_elastic(prog(t, 0.1, 1.0)), rot=0)
    if t > 1.4:
        title_in(c, t, 1.45, pill("आज की खास जानकारी", "xbold", 54, fill=RED + (255,), color=WHITE), CX, 560, "up")
    if t > 2.4:
        title_in(c, t, 2.4, text_img("LOTTERY TICKET • FULL DETAILS", "anton", 64, fill=GOLD, shadow=4), CX, 680, "up")
    sparkles(c, t, CX, 450, (460, 160), 12, seed=11)


def scene_ticket(c, t, s, e):
    lt = t - s
    p = ease_out_cubic(prog(lt, 0, 0.75))
    zoom = 1 + 0.06 * prog(lt, 0.75, 8)
    tk = ticket_front()
    x = lerp(W + 700, CX, p)
    rot = lerp(-25, 0, p)
    # subtle 3D float
    fy = 640 + 10 * math.sin(lt * 2)
    paste(c, tk, x, fy, 0.98 * zoom * lerp(0.7, 1, p), rot=rot)
    # shine sweep
    sp = prog(lt, 0.6, 0.9)
    if 0 < sp < 1:
        band = shine_band(tk.width, tk.height)
        layer = Image.new("RGBA", tk.size, (0, 0, 0, 0))
        paste(layer, band, lerp(-200, tk.width + 200, sp), tk.height / 2)
        mask = tk.getchannel("A")
        layer.putalpha(Image.fromarray(np.minimum(np.asarray(layer.getchannel("A")), np.asarray(mask))))
        paste(c, layer, x, fy, 0.98 * zoom)
    title_in(c, t, s + 0.75, grad_text("PUNJAB STATE DEAR 1000", "anton", 104, stroke=6), CX, 1040, "up")
    title_in(c, t, s + 1.05, text_img("QUARTERLY LOTTERY", "anton", 84, fill=WHITE, stroke=4, stroke_fill=NAVY, shadow=5),
             CX, 1150, "up")
    # official stamp
    st = prog(t, 10.30, 0.25)
    if st > 0:
        paste(c, official_stamp(), 850, 400, lerp(2.6, 1.0, ease_out_cubic(st)), rot=-12, alpha=min(1, st * 2))
        title_in(c, t, 10.5, pill("पंजाब सरकार की ऑफिशियल लॉटरी", "xbold", 46, fill=(20, 150, 70, 255), color=WHITE),
                 CX, 1270, "pop")


@lru_cache(maxsize=None)
def official_stamp():
    def draw(d, s, img):
        r = 150 * s
        col = (20, 150, 70, 255)
        d.ellipse((6 * s, 6 * s, 2 * r - 6 * s, 2 * r - 6 * s), fill=(255, 255, 255, 230), outline=col, width=10 * s)
        d.ellipse((26 * s, 26 * s, 2 * r - 26 * s, 2 * r - 26 * s), outline=col, width=4 * s)
        d.text((r, r - 40 * s), "GOVT. OF", font=font("anton", 40 * s), fill=col, anchor="mm")
        d.text((r, r + 8 * s), "PUNJAB", font=font("anton", 62 * s), fill=col, anchor="mm")
        d.text((r, r + 62 * s), "✔ OFFICIAL", font=font("bold", 30 * s), fill=col, anchor="mm")
    return supersampled(300, 300, draw)


@lru_cache(maxsize=None)
def calendar_card(day, weekday):
    w, h = 600, 640
    img = rounded_box(w, h, 40, (255, 255, 255, 255), shadow=16)
    d = ImageDraw.Draw(img)
    pad = 32
    d.rounded_rectangle((pad, pad, pad + w - 1, pad + 170), 40, fill=RED)
    d.rectangle((pad, pad + 120, pad + w - 1, pad + 170), fill=RED)
    d.text((pad + w / 2, pad + 88), "JANUARY 2027", font=font("anton", 78), fill=WHITE, anchor="mm")
    for rx in (150, 450):
        d.rounded_rectangle((pad + rx - 14, pad - 30, pad + rx + 14, pad + 40), 12, fill=(60, 60, 70))
    d.text((pad + w / 2, pad + 390), day, font=font("anton", 300), fill=NAVY, anchor="mm")
    d.text((pad + w / 2, pad + 580), weekday, font=font("bold", 48), fill=(120, 120, 140), anchor="mm")
    return img


@lru_cache(maxsize=None)
def clock_face(minutes_angle, hours_angle):
    def draw(d, s, img):
        r = 110 * s
        d.ellipse((4 * s, 4 * s, 2 * r - 4 * s, 2 * r - 4 * s), fill=(255, 255, 255), outline=GOLD, width=12 * s)
        for k in range(12):
            a = k * math.pi / 6
            d.line((r + math.sin(a) * 80 * s, r - math.cos(a) * 80 * s, r + math.sin(a) * 92 * s,
                    r - math.cos(a) * 92 * s), fill=NAVY, width=6 * s)
        for ang, ln, wd in ((hours_angle, 52, 12), (minutes_angle, 78, 7)):
            a = math.radians(ang)
            d.line((r, r, r + math.sin(a) * ln * s, r - math.cos(a) * ln * s), fill=RED if wd == 7 else NAVY,
                   width=wd * s)
        d.ellipse((r - 10 * s, r - 10 * s, r + 10 * s, r + 10 * s), fill=NAVY)
    return supersampled(220, 220, draw)


def scene_draw_date(c, t, s, e):
    lt = t - s
    title_in(c, t, s + 0.05, ribbon("5th DRAW", 420, 96), CX, 300, "pop")
    flips = [14.70, 15.05, 15.40]
    days = ["06", "07", "08", "09"]
    idx = sum(1 for f in flips if t >= f)
    sy = 1.0
    for f in flips:
        if f - 0.12 <= t < f:
            sy = (f - t) / 0.12
        elif f <= t < f + 0.12:
            sy = (t - f) / 0.12
    p = ease_out_back(prog(lt, 0, 0.5))
    weekday = "SATURDAY" if idx == 3 else ""
    card = calendar_card(days[idx], weekday)
    paste(c, card, CX, 760, p * 0.95, sy=max(0.05, sy))
    lock = prog(t, 15.8, 0.5)
    if lock > 0:
        paste(c, glow_sprite(380, (255, 220, 80), 0.5), CX, 760, 1 + 0.1 * lock, alpha=(1 - lock) * 1.0)
        sparkles(c, t, CX, 760, (330, 330), 10, seed=21)
    ct = prog(t, 17.0, 0.4)
    if ct > 0:
        turn = ease_in_out(prog(t, 17.0, 1.6))
        mins = (turn * 360 * 2) % 360
        hrs = lerp(150, 210, turn)
        paste(c, clock_face(int(mins), int(hrs)), 170, 1220, ease_out_back(ct))
        title_in(c, t, 17.2, grad_text("7 PM ONWARDS", "anton", 100, stroke=6), 630, 1220, "right")


def bonfire(c, t, cx, cy):
    rnd = random.Random(77)
    d = ImageDraw.Draw(c)
    # logs
    for a in (-25, 25, -8, 8):
        r = math.radians(a)
        d.line((cx - math.cos(r) * 190, cy + 60 + math.sin(r) * 40, cx + math.cos(r) * 190, cy + 60 - math.sin(r) * 40),
               fill=(90, 50, 25), width=38)
    paste(c, glow_sprite(420, (255, 120, 20), 0.8), cx, cy - 60, 1 + 0.06 * math.sin(t * 9))
    paste(c, glow_sprite(180, (255, 230, 120), 1.0), cx, cy - 20, 1 + 0.08 * math.sin(t * 13))
    for i in range(70):
        life = rnd.uniform(0.6, 1.1)
        ph = rnd.uniform(0, life)
        k = ((t + ph) % life) / life
        x = cx + rnd.uniform(-140, 140) * (1 - k) + math.sin(t * 5 + i) * 18
        y = cy + 40 - k * rnd.uniform(380, 520)
        size = int(rnd.uniform(110, 180) * (1 - k * 0.75))
        col = (255, int(lerp(230, 80, k)), int(lerp(120, 0, k)))
        if size > 4:
            paste(c, glow_sprite(max(4, size // 4 * 4), col, 1.0), x, y, alpha=1 - k * 0.7)
    for i in range(30):  # sparks
        life = rnd.uniform(1.2, 2.2)
        ph = rnd.uniform(0, life)
        k = ((t + ph) % life) / life
        x = cx + rnd.uniform(-200, 200) + math.sin(t * 2 + i) * 60 * k
        y = cy - 100 - k * 900
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(255, 220, 120, int(255 * (1 - k))))


@lru_cache(maxsize=None)
def kite_sprite(col1, col2):
    def draw(d, s, img):
        d.polygon([(60 * s, 0), (120 * s, 70 * s), (60 * s, 160 * s), (0, 70 * s)], fill=col1)
        d.polygon([(60 * s, 0), (120 * s, 70 * s), (60 * s, 70 * s)], fill=col2)
        d.polygon([(0, 70 * s), (60 * s, 160 * s), (60 * s, 70 * s)], fill=col2)
        d.line([(60 * s, 160 * s), (50 * s, 190 * s), (70 * s, 220 * s), (55 * s, 250 * s)], fill=(255, 255, 255), width=3 * s)
    return supersampled(120, 250, draw)


def scene_lohri(c, t, s, e):
    lt = t - s
    dark = Image.new("RGBA", (W, H), (5, 5, 30, int(170 * clamp(lt / 0.3))))
    c.alpha_composite(dark)
    for i, (kx, ky, c1, c2) in enumerate([(200, 330, (255, 60, 90), (255, 200, 40)), (880, 260, (40, 200, 120), (255, 255, 255)),
                                          (760, 560, (80, 120, 255), (255, 120, 40))]):
        paste(c, kite_sprite(c1, c2), kx + math.sin(t * 1.3 + i) * 25, ky + math.cos(t * 1.1 + i) * 18, 0.9,
              rot=math.sin(t * 1.7 + i) * 10)
    bonfire(c, t, CX, 1080)
    title_in(c, t, s + 0.1, grad_text("HAPPY LOHRI", "anton", 160, top=(255, 245, 160), bottom=(255, 110, 20), stroke=7),
             CX, 470, "pop")
    title_in(c, t, s + 0.4, pill("लोहड़ी के मौके पर ड्रॉ!", "xbold", 50, fill=(255, 140, 20, 255), color=WHITE), CX, 640, "up")


@lru_cache(maxsize=None)
def price_tag():
    w, h = 640, 330

    def draw(d, s, img):
        pts = [(90 * s, 10 * s), (w * s - 20 * s, 10 * s), (w * s - 20 * s, h * s - 20 * s), (90 * s, h * s - 20 * s),
               (10 * s, h * s / 2 - 5 * s)]
        d.polygon([(x + 6 * s, y + 10 * s) for x, y in pts], fill=(0, 0, 0, 90))
        d.polygon(pts, fill=(255, 200, 30))
        d.polygon([(100 * s, 26 * s), (w * s - 36 * s, 26 * s), (w * s - 36 * s, h * s - 36 * s), (100 * s, h * s - 36 * s),
                   (30 * s, h * s / 2 - 5 * s)], outline=DEEP_RED, width=5 * s)
        d.ellipse((60 * s, h * s / 2 - 25 * s, 100 * s, h * s / 2 + 15 * s), fill=(255, 255, 255), outline=DEEP_RED, width=5 * s)
        d.text((360 * s, 92 * s), "TICKET MRP", font=font("anton", 54 * s), fill=DEEP_RED, anchor="mm")
        d.text((360 * s, 205 * s), "₹1000", font=font("xbold", 150 * s), fill=DEEP_RED, anchor="mm")
    return supersampled(w, h, draw)


def scene_mrp(c, t, s, e):
    lt = t - s
    crop = ticket_crop((560, 110, 1014, 230), 900)
    p = ease_out_cubic(prog(lt, 0, 0.5))
    paste(c, crop, CX, 430, lerp(1.4, 1.0, p), alpha=p)
    sw = prog(t, 22.45, 0.2)
    if sw > 0:
        k = t - 22.45
        ang = 28 * math.exp(-k * 2.2) * math.cos(k * 7)
        drop = ease_out_back(sw)
        d = ImageDraw.Draw(c)
        pivot_y = lerp(400, 640, drop)
        d.line((CX + 220, 520, CX + 220, pivot_y + 20), fill=(255, 255, 255, 200), width=5)
        paste(c, price_tag(), CX, pivot_y + 230, 1.0, rot=ang)
        sparkles(c, t, CX, pivot_y + 230, (330, 180), 10, seed=31)
    title_in(c, t, 23.2, pill("सिर्फ़ ₹1000 में", "xbold", 62, fill=RED + (255,), color=WHITE), CX, 1220, "pop")


@lru_cache(maxsize=None)
def chest_sprite(open_amt=0):
    w, h = 460, 420

    def draw(d, s, img):
        S = lambda *v: [x * s for x in v]  # noqa: E731
        d.rounded_rectangle(S(20, 190, 440, 400), 24 * s, fill=(130, 70, 25), outline=(70, 35, 10), width=8 * s)
        for bx in (110, 330):
            d.rectangle(S(bx - 20, 190, bx + 20, 400), fill=GOLD)
        if open_amt:
            d.polygon(S(20, 190, 440, 190, 400, 40, 60, 40), fill=(150, 85, 30), outline=(70, 35, 10))
            d.ellipse(S(60, 140, 400, 250), fill=(255, 230, 120))
        else:
            d.rounded_rectangle(S(14, 90, 446, 200), 50 * s, fill=(150, 85, 30), outline=(70, 35, 10), width=8 * s)
            for bx in (110, 330):
                d.rectangle(S(bx - 20, 92, bx + 20, 198), fill=GOLD)
        d.rounded_rectangle(S(195, 170, 265, 250), 12 * s, fill=GOLD, outline=(160, 110, 10), width=5 * s)
        d.ellipse(S(220, 195, 240, 215), fill=(70, 35, 10))
    return supersampled(w, h, draw)


def scene_drumroll(c, t, s, e):
    lt = t - s
    dark = Image.new("RGBA", (W, H), (0, 0, 20, int(150 * clamp(lt / 0.3))))
    c.alpha_composite(dark)
    # sweeping spotlights
    for i, ph in enumerate((0, 2.1)):
        x = CX + math.sin(t * 4 + ph) * 300
        paste(c, glow_sprite(360, (255, 240, 180), 0.35), x, 820)
    shake = lt * 9
    jx, jy = math.sin(t * 60) * shake, math.cos(t * 53) * shake
    title_in(c, t, s + 0.05, grad_text("सबसे बड़ी बात...", "xbold", 100, stroke=7), CX, 420, "pop")
    paste(c, chest_sprite(0), CX + jx, 900 + jy, 1.0 + 0.04 * math.sin(t * 30))
    q = text_img("1st PRIZE ?", "anton", 110, fill=WHITE, stroke=5, stroke_fill=DEEP_RED, shadow=5)
    paste(c, q, CX, 1250, 1 + 0.08 * math.sin(t * 20), alpha=prog(lt, 0.4, 0.3))


def scene_jackpot(c, t, s, e):
    lt = t - s
    flash = clamp(1 - lt / 0.35)
    paste(c, glow_sprite(600, (255, 220, 100), 0.7), CX, 760, 1.2 + 0.05 * math.sin(t * 6))
    paste(c, chest_sprite(1), CX, 1170, 0.85)
    coin_rain(c, t, s + 0.2, count=36, seed=4, dur=3.2)
    confetti(c, t, s, count=110, burst_y=1100)
    title_in(c, t, s + 0.05, ribbon("1st PRIZE", 480, 100), CX, 300, "pop")
    cp = prog(t, 27.40, 1.5)
    val = int(5_000_000 * ease_out_cubic(cp)) // 1000 * 1000 if cp < 1 else 5_000_000
    num = text_img("₹ " + indian_format(val), "xbold", 120, fill=GOLD_LIGHT, stroke=6, stroke_fill=DEEP_RED, shadow=6)
    paste(c, num, CX, 480, 1.0 + (0.08 if cp >= 1 and t < 29.1 else 0))
    if t >= 28.95:
        big = grad_text("50 LAKH", "anton", 250, stroke=10)
        paste(c, big, CX, 740, ease_out_elastic(prog(t, 28.95, 0.9)))
    sparkles(c, t, CX, 600, (460, 300), 16, seed=41)
    if flash > 0:
        c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * flash))))


@lru_cache(maxsize=None)
def medal(label, c1, c2):
    def draw(d, s, img):
        d.polygon([(70 * s, 0), (110 * s, 0), (95 * s, 90 * s), (75 * s, 90 * s)], fill=RED)
        d.polygon([(110 * s, 0), (150 * s, 0), (105 * s, 90 * s), (85 * s, 90 * s)], fill=(30, 90, 200))
        d.ellipse((20 * s, 70 * s, 200 * s, 250 * s), fill=c2)
        d.ellipse((34 * s, 84 * s, 186 * s, 236 * s), fill=c1)
        d.text((110 * s, 162 * s), label, font=font("anton", 72 * s), fill=c2, anchor="mm")
    return supersampled(220, 260, draw)


@lru_cache(maxsize=None)
def prize_card(title, amount, sub, c1, c2, w=960, h=250, medal_label=None, mc=None):
    img = gradient_box(w, h, 30, c1, c2, outline=GOLD + (255,), width=6, shadow=12, horizontal=True)
    off = 24
    x0 = off + 40
    if medal_label:
        m = medal(medal_label, *mc)
        m = m.resize((int(m.width * 0.85), int(m.height * 0.85)), Image.LANCZOS)
        img.alpha_composite(m, (off + 24, off + (h - m.height) // 2))
        x0 = off + 240
    tt = text_img(title, "anton", 60, fill=WHITE, shadow=3)
    img.alpha_composite(tt, (x0, off + 22))
    at = text_img(amount, "xbold", 92, fill=GOLD_LIGHT, stroke=4, stroke_fill=DEEP_RED, shadow=4)
    img.alpha_composite(at, (x0 - 6, off + 88))
    if sub:
        st = text_img(sub, "semi", 34, fill=(255, 255, 255))
        img.alpha_composite(st, (off + w - st.width - 30, off + 30))
    return img


@lru_cache(maxsize=None)
def winner_icon():
    def draw(d, s, img):
        d.ellipse((22 * s, 4 * s, 58 * s, 40 * s), fill=GOLD)
        d.pieslice((6 * s, 40 * s, 74 * s, 108 * s), 180, 360, fill=GOLD)
    return supersampled(80, 76, draw)


def scene_prize2_3(c, t, s, e):
    card2 = prize_card("2nd PRIZE", "₹10 LAKH", "1 WINNER", (90, 100, 130), (40, 50, 90), medal_label="2", mc=((225, 230, 240), (130, 140, 160)))
    title_in(c, t, s, card2, CX, 380, "left")
    if t >= 32.55:
        card3 = prize_card("3rd PRIZE", "₹9,000 each", "40 WINNERS", (170, 90, 40), (100, 45, 20), medal_label="3", mc=((235, 160, 100), (140, 80, 30)))
        title_in(c, t, 32.55, card3, CX, 690, "right")
    if t >= 34.2:
        icon = winner_icon()
        for i in range(40):
            r, col = divmod(i, 10)
            x = 120 + col * 93
            y = 900 + r * 92
            p = prog(t, 34.25 + i * 0.045, 0.25)
            if p > 0:
                paste(c, icon, x, y, ease_out_back(p) * 0.95)
        title_in(c, t, 34.3, text_img("× 40", "anton", 70, fill=WHITE, stroke=4, stroke_fill=NAVY), CX, 1290, "pop")
    if t >= 36.2:
        title_in(c, t, 36.2, pill("कुल ₹3.60 लाख", "xbold", 50, fill=GREEN + (255,), color=WHITE), CX, 1290, "pop")


TABLE = [("1st", "1", "50,00,000"), ("Cons.", "3", "5,00,000"), ("2nd", "1", "10,00,000"), ("3rd", "40", "9,000"),
         ("4th", "40", "7,000"), ("5th", "40", "6,000"), ("6th", "40", "5,000"), ("7th", "80", "3,000"),
         ("8th", "2,000", "1,000")]


@lru_cache(maxsize=None)
def table_row(i, rank, num, amt):
    w, h = 940, 88
    c1, c2 = ((255, 215, 60), (255, 170, 20)) if i == 0 else ((255, 255, 255), (225, 232, 255))
    img = gradient_box(w, h, 18, c1, c2, shadow=6, horizontal=True)
    d = ImageDraw.Draw(img)
    off = 12
    d.text((off + 40, off + h / 2), rank, font=font("anton", 48), fill=DEEP_RED, anchor="lm")
    d.text((off + 400, off + h / 2), num, font=font("bold", 42), fill=NAVY, anchor="mm")
    d.text((off + w - 36, off + h / 2), "₹" + amt, font=font("xbold", 46), fill=NAVY, anchor="rm")
    return img


@lru_cache(maxsize=None)
def table_header():
    w, h = 940, 70
    img = rounded_box(w, h, 18, NAVY + (255,), outline=GOLD + (255,), width=3)
    d = ImageDraw.Draw(img)
    d.text((40, h / 2), "RANK", font=font("anton", 40), fill=GOLD, anchor="lm")
    d.text((400, h / 2), "PRIZES", font=font("anton", 40), fill=GOLD, anchor="mm")
    d.text((w - 36, h / 2), "AMOUNT (each)", font=font("anton", 40), fill=GOLD, anchor="rm")
    return img


def scene_consolation(c, t, s, e):
    if t < 41.75:
        title_in(c, t, s, ribbon("CONSOLATION PRIZES", 820, 100), CX, 300, "pop")
        for i, st in enumerate((38.2, 38.6, 39.0)):
            card = gradient_box(300, 380, 30, (255, 90, 160), (150, 20, 90), outline=GOLD + (255,), width=6, shadow=10)
            p = prog(t, st, 0.4)
            if p > 0:
                x = 190 + i * 350
                paste(c, card, x, 700, ease_out_back(p))
                paste(c, text_img("₹5", "anton", 140, fill=GOLD_LIGHT, stroke=5, stroke_fill=DEEP_RED), x, 650, ease_out_back(p))
                paste(c, text_img("LAKH", "anton", 80, fill=WHITE), x, 790, ease_out_back(p))
        title_in(c, t, 39.4, text_img("3 विजेता × ₹5,00,000", "xbold", 64, fill=WHITE, stroke=4, stroke_fill=NAVY, shadow=4),
                 CX, 1020, "up")
    else:
        title_in(c, t, 41.75, ribbon("PRIZE TABLE", 560, 96), CX, 290, "pop")
        title_in(c, t, 41.85, table_header(), CX, 400, "up")
        for i, row in enumerate(TABLE):
            st = 42.0 + i * 0.22
            p = prog(t, st, 0.35)
            if p > 0:
                img = table_row(i, *row)
                paste(c, img, CX + (1 - ease_out_cubic(p)) * (W if i % 2 else -W), 490 + i * 92, alpha=p)
        if t >= 44.1:
            title_in(c, t, 44.1, pill("कुल 2,245 इनाम", "xbold", 56, fill=GREEN + (255,), color=WHITE), 380, 1360, "pop")


SERIES_COLS = [((255, 80, 80), (170, 20, 40)), ((80, 170, 255), (20, 70, 180)), ((90, 220, 120), (20, 130, 60)),
               ((255, 190, 60), (210, 110, 0))]


def scene_series(c, t, s, e):
    title_in(c, t, s, ribbon("4 SERIES", 480, 96), CX, 300, "pop")
    for i, L in enumerate("ABCD"):
        p = prog(t, 46.1 + i * 0.4, 0.4)
        if p > 0:
            x = 150 + i * 260
            tile = gradient_box(220, 220, 36, *SERIES_COLS[i], outline=WHITE + (255,), width=6, shadow=10)
            paste(c, tile, x, 560, ease_out_back(p), rot=(1 - p) * 30)
            paste(c, text_img(L, "anton", 150, fill=WHITE, shadow=4), x, 552, ease_out_back(p))
            paste(c, text_img("0000-9999", "bold", 34, fill=WHITE, shadow=2), x, 720, alpha=p)
    if t >= 48.0:
        title_in(c, t, 48.0, text_img("4 × 10,000 =", "anton", 90, fill=WHITE, stroke=4, stroke_fill=NAVY, shadow=4),
                 CX, 900, "up")
    if t >= 49.3:
        cp = prog(t, 49.3, 0.9)
        val = int(40000 * ease_out_cubic(cp))
        big = grad_text(indian_format(val) if cp < 1 else "40,000", "anton", 220, stroke=9)
        paste(c, big, CX, 1090, 1.0 + (0.1 * (1 - prog(t, 50.2, 0.3)) if t >= 50.2 else 0))
        title_in(c, t, 49.6, text_img("TICKETS", "anton", 90, fill=GOLD, stroke=4, stroke_fill=DEEP_RED), CX, 1270, "up")


def draw_machine(c, t, cx, cy, r):
    d = ImageDraw.Draw(c)
    d.ellipse((cx - r - 12, cy - r - 12, cx + r + 12, cy + r + 12), fill=(30, 30, 50), outline=GOLD, width=8)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(60, 90, 200))
    rnd = random.Random(9)
    cols = [RED, GOLD, GREEN, PINK, (60, 160, 255), ORANGE, WHITE]
    f = font("bold", 24)
    for i in range(16):
        a = t * rnd.uniform(1.5, 3.5) + i
        rr = r * rnd.uniform(0.25, 0.78) + math.sin(t * 7 + i) * 12
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.9 + abs(math.sin(t * 5 + i)) * 20
        col = cols[i % len(cols)]
        d.ellipse((x - 26, y - 26, x + 26, y + 26), fill=col, outline=(20, 20, 30), width=3)
        d.ellipse((x - 15, y - 15, x + 15, y + 15), fill=(255, 255, 255))
        d.text((x, y), str(i % 10), font=f, fill=(20, 20, 30), anchor="mm")
    d.arc((cx - r + 10, cy - r + 10, cx + r - 10, cy + r - 10), 200, 250, fill=(255, 255, 255), width=10)


@lru_cache(maxsize=None)
def phone_frame():
    w, h = 560, 900
    img = rounded_box(w, h, 70, (15, 15, 22, 255), outline=(90, 90, 110, 255), width=6, shadow=18)
    d = ImageDraw.Draw(img)
    off = 36
    d.rounded_rectangle((off + 30, off + 30, off + w - 30, off + h - 30), 48, fill=(10, 20, 60))
    d.rounded_rectangle((off + w / 2 - 70, off + 42, off + w / 2 + 70, off + 70), 14, fill=(0, 0, 0))
    return img


def scene_live(c, t, s, e):
    lt = t - s
    p = ease_out_back(prog(lt, 0, 0.5))
    ph = phone_frame()
    py = 760 + (1 - p) * 900
    paste(c, ph, CX, py)
    # screen content
    draw_machine(c, t, CX, py - 60, 200)
    blink = 0.6 + 0.4 * abs(math.sin(t * 4))
    live = pill("● LIVE", "anton", 52, fill=(230, 20, 40, 255), color=WHITE, padx=30, pady=10)
    paste(c, live, CX - 140, py - 360, 0.9 * (1 + 0.04 * math.sin(t * 8)), alpha=blink if t > 52.0 else 0)
    paste(c, text_img("HD", "anton", 44, fill=WHITE), CX + 170, py - 360, alpha=p)
    paste(c, text_img("LIVE DRAW", "anton", 60, fill=GOLD), CX, py + 230, alpha=p)
    url = typewriter("www.punjablotteries.com/livedraw", t, 53.0, cps=18)
    if url:
        title_in(c, t, 53.0, pill(url, "bold", 44, fill=(255, 255, 255, 245), color=NAVY), CX, 1310, "up")


@lru_cache(maxsize=None)
def tip_card(text, n):
    w, h = 960, 170
    img = rounded_box(w, h, 36, (255, 255, 255, 245), shadow=10)
    off = 20
    d = ImageDraw.Draw(img)
    d.ellipse((off + 24, off + 30, off + 134, off + 140), fill=(230, 235, 250))
    d.text((off + 79, off + 85), str(n), font=font("anton", 64), fill=NAVY, anchor="mm")
    lines = text.split("\n")
    y = off + h / 2 - (len(lines) - 1) * 30
    for ln in lines:
        d.text((off + 170, y), ln, font=font("xbold", 44), fill=NAVY, anchor="lm")
        y += 60
    return img


@lru_cache(maxsize=None)
def check_badge(p_q):
    p = p_q / 20

    def draw(d, s, img):
        d.ellipse((0, 0, 110 * s, 110 * s), fill=GREEN)
        pts = [(28 * s, 58 * s), (48 * s, 78 * s), (84 * s, 36 * s)]
        if p < 0.5:
            k = p / 0.5
            d.line([pts[0], (lerp(pts[0][0], pts[1][0], k), lerp(pts[0][1], pts[1][1], k))], fill=WHITE, width=12 * s)
        else:
            k = (p - 0.5) / 0.5
            d.line([pts[0], pts[1], (lerp(pts[1][0], pts[2][0], k), lerp(pts[1][1], pts[2][1], k))], fill=WHITE,
                   width=12 * s, joint="curve")
    return supersampled(110, 110, draw)


TIPS = [(57.6, "टिकट सिर्फ़ Authorized Seller\nसे ही खरीदें"),
        (60.3, "रिज़ल्ट पंजाब सरकार के\nGazette से चेक करें"),
        (63.2, "जीतने पर 30 दिन के अंदर\nक्लेम करें")]


def scene_tips(c, t, s, e):
    title_in(c, t, s, ribbon("ज़रूरी बातें", 560, 104, size=62, fname="xbold"), CX, 300, "pop")
    for i, (st, txt) in enumerate(TIPS):
        if t >= st - 0.3:
            y = 520 + i * 260
            title_in(c, t, st - 0.3, tip_card(txt, i + 1), CX, y, "right")
            cp = prog(t, st, 0.35)
            if cp > 0:
                paste(c, check_badge(int(cp * 20)), W - 140, y, ease_out_back(min(1, cp * 2)))


@lru_cache(maxsize=None)
def warning_sign():
    def draw(d, s, img):
        d.polygon([(130 * s, 6 * s), (254 * s, 224 * s), (6 * s, 224 * s)], fill=GOLD, outline=DEEP_RED)
        d.polygon([(130 * s, 36 * s), (226 * s, 208 * s), (34 * s, 208 * s)], outline=(40, 30, 10), width=8 * s)
        d.text((130 * s, 140 * s), "!", font=font("anton", 120 * s), fill=(40, 30, 10), anchor="mm")
    return supersampled(260, 230, draw)


def scene_responsible(c, t, s, e):
    lt = t - s
    paste(c, warning_sign(), CX, 330, ease_out_back(prog(lt, 0.1, 0.5)) * (1 + 0.03 * math.sin(t * 4)))
    title_in(c, t, s + 0.3, text_img("लॉटरी में जोखिम है", "xbold", 76, fill=WHITE, stroke=5, stroke_fill=NAVY, shadow=5),
             CX, 540, "up")
    title_in(c, t, 67.4, grad_text("ज़िम्मेदारी से खेलें", "xbold", 92, stroke=7), CX, 670, "pop")


def heart_sprite(color):
    def draw(d, s, img):
        d.ellipse((4 * s, 6 * s, 50 * s, 52 * s), fill=color)
        d.ellipse((42 * s, 6 * s, 88 * s, 52 * s), fill=color)
        d.polygon([(6 * s, 38 * s), (86 * s, 38 * s), (46 * s, 84 * s)], fill=color)
    return supersampled(92, 88, draw)


@lru_cache(maxsize=None)
def action_button(label, col, pressed):
    w, h = 400, 130
    c1 = tuple(int(v * (0.8 if pressed else 1)) for v in col)
    img = gradient_box(w, h, 65, c1, tuple(int(v * 0.7) for v in col), outline=WHITE + (255,), width=5, shadow=10)
    ic = heart_sprite(WHITE) if label == "LIKE" else None
    t = text_img(label, "anton", 70, fill=WHITE)
    off = 20
    if ic:
        img.alpha_composite(ic.resize((70, 67), Image.LANCZOS), (off + 50, off + 32))
        img.alpha_composite(t, (off + 150, off + (h - t.height) // 2))
    else:
        d = ImageDraw.Draw(img)
        cx, cy = off + 85, off + h // 2
        for dx, dy in ((-22, 0), (20, -26), (20, 26)):
            d.ellipse((cx + dx - 14, cy + dy - 14, cx + dx + 14, cy + dy + 14), fill=WHITE)
        d.line((cx - 22, cy, cx + 20, cy - 26), fill=WHITE, width=7)
        d.line((cx - 22, cy, cx + 20, cy + 26), fill=WHITE, width=7)
        img.alpha_composite(t, (off + 140, off + (h - t.height) // 2))
    return img


@lru_cache(maxsize=None)
def cursor_sprite():
    def draw(d, s, img):
        pts = [(0, 0), (0, 70), (18, 54), (30, 82), (42, 76), (30, 50), (54, 50)]
        d.polygon([(x * s + 4 * s, y * s + 4 * s) for x, y in pts], fill=WHITE, outline=(0, 0, 0))
    return supersampled(64, 92, draw)


def scene_outro(c, t, s, e):
    lt = t - s
    title_in(c, t, s, grad_text("LIKE & SHARE", "anton", 150, stroke=8), CX, 300, "pop")
    like_pressed = 71.3 <= t < 71.5
    share_pressed = 72.4 <= t < 72.6
    title_in(c, t, s + 0.3, action_button("LIKE", (40, 110, 240), like_pressed), 290, 520, "left")
    title_in(c, t, s + 0.5, action_button("SHARE", (30, 170, 80), share_pressed), 790, 520, "right")
    # animated cursor
    if t > 70.6:
        if t < 71.3:
            k = ease_in_out(prog(t, 70.6, 0.7))
            x, y = lerp(700, 300, k), lerp(900, 540, k)
        elif t < 72.4:
            k = ease_in_out(prog(t, 71.6, 0.8))
            x, y = lerp(300, 800, k), 540
        else:
            x, y = 800, 540
        press = 0.85 if (like_pressed or share_pressed) else 1.0
        paste(c, cursor_sprite(), x + 30, y + 46, press)
    if t > 71.3:
        for i in range(6):
            k = prog(t, 71.3 + i * 0.08, 1.2)
            if 0 < k < 1:
                paste(c, heart_sprite((255, 70, 110)), 290 + math.sin(i * 2) * 120, 480 - k * 380, 0.6, alpha=1 - k)
    title_in(c, t, 73.0, pill("DRAW: 09-01-2027 • 7 PM", "anton", 56, fill=RED + (255,), color=WHITE), CX, 720, "up")


SCENE_FUNCS = {
    "intro": scene_intro, "ticket": scene_ticket, "draw_date": scene_draw_date, "lohri": scene_lohri,
    "mrp": scene_mrp, "drumroll": scene_drumroll, "jackpot": scene_jackpot, "prize2_3": scene_prize2_3,
    "consolation": scene_consolation, "series": scene_series, "live": scene_live, "tips": scene_tips,
    "responsible": scene_responsible, "outro": scene_outro,
}
