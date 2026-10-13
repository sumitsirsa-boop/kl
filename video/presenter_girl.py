"""Animated Punjabi girl presenter who holds the lottery ticket in both hands.

body_img()  – head, hair with paranda braid, kurta, phulkari dupatta, upper arms (lip-sync states)
hold_img()  – forearms, hands and the ticket between them (moves as one group)
"""
import math
from functools import lru_cache

from PIL import Image, ImageDraw

GW, GH = 720, 1000
SKIN = (226, 170, 128)
SKIN_SHADE = (198, 140, 100)
HAIR = (28, 18, 16)
KURTA = (214, 28, 104)
KURTA_DARK = (160, 14, 74)
DUPATTA = (255, 140, 20)
GOLD = (245, 190, 40)
LIP = (196, 50, 70)
MOUTH_LEVELS = 8
ELBOWS = ((150, 760), (570, 760))  # where upper arms end in body_img coords


def _S(ss, *v):
    return [x * ss for x in v]


def _phulkari_band(d, ss, pts_top, pts_bottom, base=DUPATTA):
    """Dupatta band with small phulkari-style diamond motifs."""
    d.polygon([(x * ss, y * ss) for x, y in pts_top + pts_bottom[::-1]], fill=base)
    n = len(pts_top)
    for i in range(n - 1):
        x0, y0 = pts_top[i]
        x1, y1 = pts_bottom[i]
        for k in range(3):
            u = (k + 0.5) / 3
            cx, cy = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
            r = 9
            col = (255, 230, 60) if (i + k) % 2 else (230, 30, 90)
            d.polygon([(cx * ss, (cy - r) * ss), ((cx + r) * ss, cy * ss), (cx * ss, (cy + r) * ss),
                       ((cx - r) * ss, cy * ss)], fill=col)


@lru_cache(maxsize=None)
def body_img(mouth=0, blink=False, brow=0):
    ss = 2
    img = Image.new("RGBA", (GW * ss, GH * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    S = lambda *v: _S(ss, *v)  # noqa: E731

    # hair back (long hair falling behind shoulders)
    d.rounded_rectangle(S(225, 170, 495, 640), 120 * ss, fill=HAIR)
    # torso / kurta
    d.ellipse(S(70, 515, 650, 1200), fill=KURTA)
    # upper arms down to the elbows
    for (ex, ey), sx in zip(ELBOWS, (110, 610)):
        d.line(S(sx, 600, ex, ey), fill=KURTA, width=92 * ss)
        d.ellipse(S(ex - 46, ey - 46, ex + 46, ey + 46), fill=KURTA)
    # neck + neckline
    d.rounded_rectangle(S(318, 420, 402, 520), 24 * ss, fill=SKIN)
    d.polygon(S(318, 448, 402, 448, 402, 470, 360, 488, 318, 470), fill=SKIN_SHADE)
    d.chord(S(282, 460, 438, 600), 0, 180, fill=SKIN)
    d.arc(S(282, 460, 438, 600), 0, 180, fill=GOLD, width=10 * ss)
    for k in range(9):  # neckline embroidery dots
        a = math.pi * (k + 0.5) / 9
        x, y = 360 + math.cos(a) * 92, 530 + math.sin(a) * 82
        d.ellipse(S(x - 6, y - 6, x + 6, y + 6), fill=GOLD)
    # phulkari dupatta over both shoulders
    _phulkari_band(d, ss, [(95, 560), (190, 520), (270, 535)], [(110, 660), (200, 610), (285, 600)])
    _phulkari_band(d, ss, [(450, 535), (530, 520), (625, 560)], [(435, 600), (520, 610), (610, 660)])

    # braid with paranda over the left shoulder
    for k in range(9):
        y = 470 + k * 34
        x = 262 - k * 3
        d.ellipse(S(x - 24, y - 20, x + 24, y + 22), fill=HAIR)
        d.arc(S(x - 24, y - 20, x + 24, y + 22), 200, 340, fill=(60, 40, 35), width=3 * ss)
    for j, col in enumerate(((230, 30, 60), (255, 200, 40), (40, 160, 90), (230, 30, 60))):
        x = 232 + j * 12
        d.line(S(x, 770, x - 6 + j * 3, 860), fill=col, width=8 * ss)
        d.ellipse(S(x - 12, 850 + j * 3, x + 6, 874 + j * 3), fill=col)
    d.ellipse(S(222, 752, 268, 784), fill=GOLD)

    # ears + jhumkas
    for ex in (262, 458):
        d.ellipse(S(ex - 20, 300, ex + 20, 360), fill=SKIN)
        d.ellipse(S(ex - 6, 356, ex + 6, 368), fill=GOLD)
        d.pieslice(S(ex - 20, 362, ex + 20, 410), 0, 180, fill=GOLD)
        for k in range(5):
            d.ellipse(S(ex - 18 + k * 8, 384, ex - 14 + k * 8, 392), fill=(220, 40, 60))

    # face
    d.ellipse(S(268, 190, 452, 452), fill=SKIN)
    # hair front: centre parting, framing the face
    d.chord(S(254, 150, 466, 330), 180, 360, fill=HAIR)
    d.polygon(S(262, 240, 300, 178, 340, 196, 300, 270, 272, 330), fill=HAIR)
    d.polygon(S(458, 240, 420, 178, 380, 196, 420, 270, 448, 330), fill=HAIR)
    d.line(S(360, 152, 360, 196), fill=(150, 40, 40), width=3 * ss)  # parting

    # eyebrows
    by = 262 - (6 if brow else 0)
    d.arc(S(298, by, 346, by + 22), 200, 340, fill=HAIR, width=6 * ss)
    d.arc(S(374, by, 422, by + 22), 200, 340, fill=HAIR, width=6 * ss)
    # eyes with kajal
    for ex in (322, 398):
        if blink:
            d.arc(S(ex - 22, 284, ex + 22, 306), 20, 160, fill=(40, 20, 20), width=5 * ss)
        else:
            d.ellipse(S(ex - 22, 280, ex + 22, 306), fill=(252, 250, 248))
            d.ellipse(S(ex - 11, 281, ex + 11, 305), fill=(80, 45, 25))
            d.ellipse(S(ex - 6, 286, ex + 6, 300), fill=(15, 8, 6))
            d.ellipse(S(ex + 1, 284, ex + 7, 290), fill=(255, 255, 255))
            d.arc(S(ex - 24, 277, ex + 24, 309), 190, 350, fill=(20, 10, 10), width=5 * ss)
            d.line(S(ex + 20, 288, ex + 30, 282), fill=(20, 10, 10), width=4 * ss)  # wing
    # nose + nose stud
    d.arc(S(346, 318, 374, 346), 20, 160, fill=SKIN_SHADE, width=4 * ss)
    d.ellipse(S(368, 330, 376, 338), fill=(255, 245, 210))
    # blush
    for cx in (300, 420):
        d.ellipse(S(cx - 22, 340, cx + 22, 362), fill=(236, 150, 130))

    # mouth
    m = mouth / (MOUTH_LEVELS - 1)
    mw = 24 + 6 * m
    mh = 2 + 24 * m
    my = 384
    if m < 0.08:
        d.chord(S(360 - mw, my - 10, 360 + mw, my + 12), 0, 180, fill=LIP)
        d.arc(S(360 - mw, my - 12, 360 + mw, my + 8), 20, 160, fill=(150, 30, 50), width=3 * ss)
    else:
        d.ellipse(S(360 - mw - 3, my - 9, 360 + mw + 3, my + mh + 7), fill=LIP)
        d.ellipse(S(360 - mw, my - 5, 360 + mw, my + mh + 3), fill=(110, 25, 40))
        d.chord(S(360 - mw + 4, my - 5, 360 + mw - 4, my + 9), 180, 360, fill=(255, 255, 255))
        if m > 0.4:
            d.ellipse(S(360 - mw * 0.5, my + mh * 0.45, 360 + mw * 0.5, my + mh + 2), fill=(220, 100, 110))

    return img.resize((GW, GH), Image.LANCZOS)


@lru_cache(maxsize=None)
def hold_img(ticket_path, crop, width=470):
    """Forearms + hands holding the ticket image at `ticket_path` (cropped to `crop`).
    Returned in body coordinates, same size as body_img."""
    ticket = Image.open(ticket_path).convert("RGBA").crop(crop)
    ss = 2
    tw = width
    th = int(ticket.height * tw / ticket.width)
    tk = ticket.resize((tw * ss, th * ss), Image.LANCZOS)
    tx, ty = (GW - tw) // 2, 610  # ticket top-left
    hands = ((tx + 18, ty + th - 28), (tx + tw - 18, ty + th - 28))
    img = Image.new("RGBA", (GW * ss, GH * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    S = lambda *v: _S(ss, *v)  # noqa: E731
    # forearms (kurta sleeves to the wrist) from the elbows up to the hands
    for (ex, ey), (hx, hy) in zip(ELBOWS, hands):
        d.line(S(ex, ey, hx, hy + 30), fill=KURTA_DARK, width=78 * ss)
        d.ellipse(S(ex - 39, ey - 39, ex + 39, ey + 39), fill=KURTA_DARK)
        d.line(S(hx, hy + 30, hx, hy + 20), fill=GOLD, width=70 * ss)  # bangles
    # palms behind the ticket
    for hx, hy in hands:
        d.ellipse(S(hx - 34, hy - 30, hx + 34, hy + 34), fill=SKIN_SHADE)
    # the ticket itself (white card edge + slight shadow)
    d.rounded_rectangle(S(tx - 6, ty - 6, tx + tw + 6, ty + th + 6), 10 * ss, fill=(255, 255, 255))
    img.alpha_composite(tk, (tx * ss, ty * ss))
    # fingers in front: thumbs on the face of the ticket, fingers curled at the bottom edge
    for i, (hx, hy) in enumerate(hands):
        sgn = 1 if i == 0 else -1
        d.rounded_rectangle(S(hx - 14 + sgn * 6, hy - 46, hx + 14 + sgn * 6, hy + 6), 14 * ss, fill=SKIN)
        d.ellipse(S(hx - 10 + sgn * 6, hy - 44, hx + 10 + sgn * 6, hy - 30), fill=(240, 190, 170))  # nail
        for k in range(3):
            fx = hx - sgn * (6 + k * 20)
            d.rounded_rectangle(S(fx - 11, hy + 14, fx + 11, hy + 44), 11 * ss, fill=SKIN)
        for k in range(2):  # gold bangles
            by = hy + 58 + k * 14
            d.rounded_rectangle(S(hx - 40, by - 6, hx + 40, by + 6), 6 * ss, fill=GOLD if k == 0 else (220, 30, 60))
    return img.resize((GW, GH), Image.LANCZOS)


def ticket_box(width=470, ticket_size=(1292, 800)):
    """(x, y, w, h) of the ticket inside hold_img coordinates."""
    th = int(ticket_size[1] * width / ticket_size[0])
    return (GW - width) // 2, 610, width, th
