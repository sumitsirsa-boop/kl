"""Cover / thumbnail images for the Diwali Bumper 2026 video.

Usage: python3 video/cover.py
Writes output/cover_diwali_reel_1080x1920.jpg (Reels/Facebook cover) and
output/cover_diwali_feed_1080x1350.jpg (Instagram grid / Facebook feed, 4:5).
Key content sits inside the centre 4:5 area so the grid crop of the Reel cover still reads.
"""
import math
import os
import sys

sys.argv += ["--project", "diwali"]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import ImageDraw  # noqa: E402

import diwali_scenes as D  # noqa: E402
import render  # noqa: E402
import scenes as base  # noqa: E402
from gfx import (DEEP_RED, GOLD, GOLD_LIGHT, ROOT, WHITE, font, glow_sprite, grad_text, gradient_box, paste,  # noqa: E402
                 rounded_box, text_img)
from presenter import presenter_img  # noqa: E402

W, H = 1080, 1920
OUT = os.path.join(ROOT, "output")


def agency_bar(w=1000):
    h = 190
    img = gradient_box(w, h, 32, (255, 225, 110), (255, 165, 30), outline=WHITE + (255,), width=6, shadow=14)
    d = ImageDraw.Draw(img)
    off = 28
    d.text((off + w / 2, off + 50), "SUMIT LOTTERY AGENCY", font=font("anton", 72), fill=DEEP_RED, anchor="mm")
    d.text((off + w / 2, off + 108), "One Way Traffic Road, Mansa", font=font("bold", 38), fill=D.MAROON, anchor="mm")
    d.text((off + w / 2, off + 160), "☎ 70598 77770  |  89688 69862", font=font("sym", 42), fill=(20, 40, 110),
           anchor="mm")
    return img


REEL = dict(h=1920, title=365, sub=470, ribbon=580, num=800, num_size=330, crore=1030, crore_size=210, stamp=1195,
            history=1335, draw=1450, bar=1810, bar_scale=1.0, extras=True,
            bursts=[(170, 330), (900, 300), (540, 210), (130, 1500), (950, 1520)])
FEED = dict(h=1350, title=215, sub=305, ribbon=395, num=565, num_size=270, crore=750, crore_size=175, stamp=868,
            history=1008, draw=1102, bar=1262, bar_scale=0.9, extras=False,
            bursts=[(150, 330), (930, 300), (120, 900), (960, 880)])


def cover(L):
    c = render.background(1.3, intensity=2.2).crop((0, 0, W, L["h"]))
    render.bokeh(c, 3.0)
    for i, (x, y) in enumerate(L["bursts"]):  # fireworks frozen mid-burst
        D.firework(c, 1.15 + 0.05 * i, 0.0, x, y, D.FW_COLS[i % len(D.FW_COLS)], seed=i, radius=240)
    paste(c, D.toran(), W / 2, 115 if L["extras"] else 60, alpha=1.0 if L["extras"] else 0.0)
    paste(c, D.rangoli(), W / 2, L["num"] + 20, 1.35 * L["num_size"] / 330, rot=10, alpha=0.55)
    paste(c, glow_sprite(560, (255, 210, 90), 0.75), W / 2, L["num"] + 20, L["num_size"] / 330)

    paste(c, grad_text("DIWALI BUMPER 2026", "anton", 120, top=(255, 250, 210), bottom=(255, 170, 40), stroke=7,
                       stroke_fill=D.MAROON), W / 2, L["title"])
    paste(c, text_img("PUNJAB STATE DEAR • GOVT. OF PUNJAB", "anton", 46, fill=WHITE, stroke=3, stroke_fill=D.MAROON),
          W / 2, L["sub"])
    paste(c, D.gold_ribbon("1st PRIZE", 460, 96), W / 2, L["ribbon"])
    paste(c, grad_text("₹12", "anton", L["num_size"], stroke=12, stroke_fill=D.MAROON), W / 2, L["num"])
    paste(c, grad_text("CRORE", "anton", L["crore_size"], stroke=10, stroke_fill=D.MAROON), W / 2, L["crore"])
    stamp = text_img(" GUARANTEED ", "anton", 96, fill=WHITE)
    box = gradient_box(stamp.width + 20, stamp.height + 10, 20, (40, 180, 90), (10, 110, 50), outline=GOLD + (255,),
                       width=8, shadow=10)
    box.alpha_composite(stamp, ((box.width - stamp.width) // 2, (box.height - stamp.height) // 2))
    paste(c, box, W / 2, L["stamp"], rot=-5)
    paste(c, base.pill("पंजाब लॉटरी के इतिहास में पहली बार!", "xbold", 46, fill=(200, 20, 70, 255), color=WHITE),
          W / 2, L["history"])
    paste(c, base.pill("DRAW 16 NOV • 6 PM  |  TICKET ₹500", "anton", 52, fill=(255, 250, 235, 255), color=D.MAROON),
          W / 2, L["draw"])
    base.sparkles(c, 2.0, W / 2, L["num"] + 100, (440, 260), 16, seed=3)
    if L["extras"]:  # small ticket, diyas and host above the agency bar
        paste(c, D.ticket_front(330), 190, 1625, rot=8)
        for i, x in enumerate((420, 540, 660)):
            D.diya(c, 0.4 + i, x, 1640, 0.9, seed=i)
        paste(c, presenter_img(5, False, 1), 900, 1600, 0.42)
    paste(c, agency_bar(), W / 2, L["bar"], L["bar_scale"])
    return c.convert("RGB")


def main():
    os.makedirs(OUT, exist_ok=True)
    for L, name in ((REEL, "cover_diwali_reel_1080x1920.jpg"), (FEED, "cover_diwali_feed_1080x1350.jpg")):
        p = os.path.join(OUT, name)
        cover(L).save(p, quality=92)
        print(p)


if __name__ == "__main__":
    main()
