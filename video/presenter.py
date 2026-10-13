"""Animated 2D presenter (anchor) whose mouth, eyes and brows follow the voiceover."""
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

PW, PH = 600, 700
SKIN = (205, 150, 108)
SKIN_SHADE = (178, 122, 84)
HAIR = (30, 22, 20)
SUIT = (24, 40, 92)
SUIT_DARK = (14, 26, 64)
SHIRT = (245, 247, 252)
TIE = (176, 22, 40)
MOUTH_LEVELS = 8


@lru_cache(maxsize=None)
def presenter_img(mouth=0, blink=False, brow=0):
    """mouth: 0..MOUTH_LEVELS-1, blink: eyes closed, brow: 0/1 raised."""
    ss = 2
    img = Image.new("RGBA", (PW * ss, PH * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def S(*v):
        return [x * ss for x in v]

    # --- body / suit
    d.ellipse(S(30, 455, 570, 1000), fill=SUIT)
    d.polygon(S(232, 470, 368, 470, 300, 640), fill=SHIRT)
    # lapels
    d.polygon(S(232, 470, 205, 500, 262, 640, 300, 640), fill=SUIT_DARK)
    d.polygon(S(368, 470, 395, 500, 338, 640, 300, 640), fill=SUIT_DARK)
    d.polygon(S(240, 470, 222, 505, 275, 625, 300, 640), fill=SUIT)
    d.polygon(S(360, 470, 378, 505, 325, 625, 300, 640), fill=SUIT)
    # collar + tie
    d.polygon(S(258, 462, 300, 500, 276, 520), fill=SHIRT)
    d.polygon(S(342, 462, 300, 500, 324, 520), fill=SHIRT)
    d.polygon(S(288, 494, 312, 494, 318, 512, 306, 520, 294, 520, 282, 512), fill=TIE)
    d.polygon(S(294, 518, 306, 518, 318, 610, 300, 632, 282, 610), fill=TIE)
    d.line(S(296, 540, 312, 556), fill=(210, 60, 70), width=3 * ss)
    d.line(S(292, 570, 314, 592), fill=(210, 60, 70), width=3 * ss)
    # pocket square + lapel mic
    d.polygon(S(410, 560, 460, 560, 452, 575, 440, 548, 428, 575, 418, 552), fill=(255, 205, 40))
    d.rectangle(S(408, 572, 462, 578), fill=SUIT_DARK)
    d.ellipse(S(244, 528, 258, 542), fill=(15, 15, 15))

    # --- neck
    d.rounded_rectangle(S(258, 380, 342, 488), radius=20 * ss, fill=SKIN)
    d.polygon(S(258, 430, 342, 430, 342, 455, 300, 470, 258, 455), fill=SKIN_SHADE)

    # --- ears
    d.ellipse(S(178, 262, 222, 338), fill=SKIN)
    d.ellipse(S(378, 262, 422, 338), fill=SKIN)
    d.ellipse(S(190, 280, 210, 322), fill=SKIN_SHADE)
    d.ellipse(S(390, 280, 410, 322), fill=SKIN_SHADE)

    # --- hair back + beard base
    d.ellipse(S(184, 112, 416, 330), fill=HAIR)
    d.ellipse(S(196, 250, 404, 452), fill=HAIR)  # trimmed beard
    # face
    d.ellipse(S(198, 150, 402, 428), fill=SKIN)
    d.ellipse(S(214, 300, 386, 448), fill=HAIR)  # jaw beard
    d.ellipse(S(222, 170, 378, 398), fill=SKIN)  # cheeks
    # hair top / quiff
    d.chord(S(192, 108, 408, 268), 180, 360, fill=HAIR)
    d.ellipse(S(250, 96, 380, 172), fill=HAIR)
    d.polygon(S(198, 200, 214, 150, 232, 205), fill=HAIR)
    d.polygon(S(402, 200, 386, 150, 368, 205), fill=HAIR)

    # --- eyebrows
    by = 236 - (7 if brow else 0)
    d.rounded_rectangle(S(232, by, 284, by + 12), radius=6 * ss, fill=HAIR)
    d.rounded_rectangle(S(316, by, 368, by + 12), radius=6 * ss, fill=HAIR)

    # --- eyes
    for ex in (258, 342):
        if blink:
            d.arc(S(ex - 22, 258, ex + 22, 286), 20, 160, fill=(60, 35, 25), width=4 * ss)
        else:
            d.ellipse(S(ex - 22, 258, ex + 22, 288), fill=(252, 252, 250))
            d.ellipse(S(ex - 11, 261, ex + 11, 285), fill=(70, 42, 25))
            d.ellipse(S(ex - 6, 266, ex + 6, 280), fill=(15, 10, 8))
            d.ellipse(S(ex + 1, 264, ex + 7, 270), fill=(255, 255, 255))
            d.arc(S(ex - 23, 256, ex + 23, 290), 200, 340, fill=(40, 25, 18), width=3 * ss)

    # --- nose
    d.line(S(300, 280, 296, 330), fill=SKIN_SHADE, width=4 * ss)
    d.arc(S(282, 320, 318, 346), 10, 170, fill=SKIN_SHADE, width=4 * ss)

    # --- moustache + mouth
    m = mouth / (MOUTH_LEVELS - 1)
    mw = 30 + 8 * m
    mh = 3 + 30 * m
    my = 372
    if m < 0.08:
        d.arc(S(300 - mw, my - 14, 300 + mw, my + 8), 20, 160, fill=(110, 40, 40), width=5 * ss)
    else:
        d.ellipse(S(300 - mw, my - 6, 300 + mw, my - 6 + mh + 8), fill=(95, 25, 30))
        d.chord(S(300 - mw + 6, my - 6, 300 + mw - 6, my + 10), 180, 360, fill=(250, 250, 250))  # teeth
        if m > 0.4:
            d.ellipse(S(300 - mw * 0.55, my + mh * 0.45, 300 + mw * 0.55, my + mh + 2), fill=(200, 80, 90))  # tongue
    d.chord(S(254, 344, 346, 376), 180, 360, fill=HAIR)  # moustache

    img = img.resize((PW, PH), Image.LANCZOS)
    return img


@lru_cache(maxsize=None)
def presenter_shadow():
    base = presenter_img(0, False, 0)
    a = base.getchannel("A").filter(ImageFilter.GaussianBlur(14))
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: int(v * 0.55)))
    return sh


def presenter_state(frame, env):
    """Returns (mouth_level, blink, brow) for a frame from the voice envelope."""
    import numpy as np

    lo, hi = max(0, frame - 1), min(len(env), frame + 2)
    v = float(np.mean(env[lo:hi])) if hi > lo else 0.0
    mouth = int(round(min(1.0, max(0.0, (v - 0.08) / 0.75)) * (MOUTH_LEVELS - 1)))
    blink = (frame % 97) in (0, 1, 2) or (frame % 151) in (0, 1)
    brow = 1 if v > 0.95 else 0
    return mouth, blink, brow
