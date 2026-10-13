"""Drawing helpers: fonts, cached text sprites, easing, safe compositing, shapes."""
import math
import os
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "assets", "fonts")
FONTS = {
    "anton": "Anton-Regular.ttf",
    "xbold": "Poppins-ExtraBold.ttf",
    "bold": "Poppins-Bold.ttf",
    "semi": "Poppins-SemiBold.ttf",
    "hind": "Hind-Bold.ttf",
}

GOLD = (255, 205, 40)
GOLD_LIGHT = (255, 236, 140)
RED = (226, 35, 45)
DEEP_RED = (150, 10, 25)
WHITE = (255, 255, 255)
NAVY = (12, 22, 80)
GREEN = (30, 185, 90)
PINK = (236, 40, 140)
ORANGE = (255, 140, 20)


# ------------------------------------------------------------------ easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, start, dur):
    return clamp((t - start) / dur) if dur > 0 else float(t >= start)


def ease_out_cubic(x):
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    return 3 * x * x - 2 * x * x * x


def ease_out_back(x, s=1.7):
    x -= 1
    return x * x * ((s + 1) * x + s) + 1


def ease_out_elastic(x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    return 2 ** (-10 * x) * math.sin((x * 10 - 0.75) * (2 * math.pi) / 3) + 1


def lerp(a, b, x):
    return a + (b - a) * x


def indian_format(n):
    s = str(int(n))
    if len(s) <= 3:
        return s
    head, tail = s[:-3], s[-3:]
    parts = []
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    if head:
        parts.insert(0, head)
    return ",".join(parts) + "," + tail


# ------------------------------------------------------------------ fonts/text
@lru_cache(maxsize=None)
def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, FONTS[name]), size)


@lru_cache(maxsize=4096)
def text_img(text, fname, size, fill=WHITE, stroke=0, stroke_fill=(0, 0, 0), shadow=0, shadow_alpha=150):
    f = font(fname, size)
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t, r, b = dummy.textbbox((0, 0), text, font=f, stroke_width=stroke)
    pad = stroke + shadow * 2 + 6
    w, h = r - l + pad * 2, b - t + pad * 2
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((pad - l + shadow, pad - t + shadow), text, font=f, fill=(0, 0, 0, shadow_alpha),
                                stroke_width=stroke, stroke_fill=(0, 0, 0, shadow_alpha))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(shadow * 0.6)))
    ImageDraw.Draw(img).text((pad - l, pad - t), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return img


@lru_cache(maxsize=512)
def grad_text(text, fname, size, top=GOLD_LIGHT, bottom=ORANGE, stroke=0, stroke_fill=DEEP_RED, shadow=6):
    """Text filled with a vertical gradient, with outline and soft shadow."""
    base = text_img(text, fname, size, fill=WHITE, stroke=0)
    w, h = base.size
    pad = stroke + shadow * 2 + 6
    out = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    mask = base.getchannel("A")
    if stroke:
        outline = mask.filter(ImageFilter.MaxFilter(stroke * 2 + 1))
        if shadow:
            sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
            sh.paste((0, 0, 0, 170), (pad + shadow, pad + shadow), outline)
            out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(shadow * 0.7)))
        out.paste(stroke_fill + (255,), (pad, pad), outline)
    grad = np.zeros((h, w, 4), np.uint8)
    for c in range(3):
        grad[..., c] = np.linspace(top[c], bottom[c], h)[:, None]
    grad[..., 3] = 255
    g = Image.fromarray(grad, "RGBA")
    layer = Image.new("RGBA", out.size, (0, 0, 0, 0))
    layer.paste(g, (pad, pad), mask)
    out.alpha_composite(layer)
    return out


def wrap_words(words, fname, size, max_w):
    f = font(fname, size)
    lines, cur = [], []
    for w in words:
        trial = " ".join(cur + [w])
        if cur and f.getlength(trial) > max_w:
            lines.append(cur)
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------ compositing
def with_alpha(img, alpha):
    if alpha >= 0.999:
        return img
    img = img.copy()
    a = np.asarray(img.getchannel("A"), dtype=np.float32) * clamp(alpha)
    img.putalpha(Image.fromarray(a.astype(np.uint8)))
    return img


def transform(img, scale=1.0, rot=0.0, sx=1.0, sy=1.0):
    if scale != 1.0 or sx != 1.0 or sy != 1.0:
        w, h = img.size
        nw, nh = max(1, int(w * scale * sx)), max(1, int(h * scale * sy))
        img = img.resize((nw, nh), Image.BICUBIC)
    if rot:
        img = img.rotate(rot, resample=Image.BICUBIC, expand=True)
    return img


def paste(canvas, img, cx, cy, scale=1.0, rot=0.0, alpha=1.0, sx=1.0, sy=1.0, anchor="center"):
    if alpha <= 0.003 or scale <= 0.003:
        return
    img = transform(img, scale, rot, sx, sy)
    img = with_alpha(img, alpha)
    w, h = img.size
    if anchor == "center":
        x, y = int(round(cx - w / 2)), int(round(cy - h / 2))
    else:  # top-left
        x, y = int(cx), int(cy)
    cw, ch = canvas.size
    if x >= cw or y >= ch or x + w <= 0 or y + h <= 0:
        return
    l, t = max(0, -x), max(0, -y)
    r, b = min(w, cw - x), min(h, ch - y)
    if l or t or r < w or b < h:
        img = img.crop((l, t, r, b))
    canvas.alpha_composite(img, (x + l, y + t))


def rounded_box(w, h, r, fill, outline=None, width=0, shadow=0):
    pad = shadow * 2
    img = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((pad, pad + shadow // 2, pad + w, pad + h + shadow // 2), r, fill=(0, 0, 0, 140))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(shadow * 0.6)))
    ImageDraw.Draw(img).rounded_rectangle((pad, pad, pad + w - 1, pad + h - 1), r, fill=fill, outline=outline, width=width)
    return img


def gradient_box(w, h, r, c1, c2, outline=None, width=0, shadow=0, horizontal=False):
    g = np.zeros((h, w, 4), np.uint8)
    lin = np.linspace(0, 1, w if horizontal else h)
    for c in range(3):
        v = (c1[c] + (c2[c] - c1[c]) * lin).astype(np.uint8)
        g[..., c] = v[None, :] if horizontal else v[:, None]
    g[..., 3] = 255
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255)
    pad = shadow * 2
    img = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sh.paste((0, 0, 0, 150), (pad, pad + shadow // 2), mask)
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(shadow * 0.6)))
    img.paste(Image.fromarray(g, "RGBA"), (pad, pad), mask)
    if outline:
        ImageDraw.Draw(img).rounded_rectangle((pad, pad, pad + w - 1, pad + h - 1), r, outline=outline, width=width)
    return img


@lru_cache(maxsize=64)
def glow_sprite(radius, color, strength=1.0):
    s = radius * 2
    y, x = np.mgrid[0:s, 0:s]
    d = np.sqrt((x - radius + 0.5) ** 2 + (y - radius + 0.5) ** 2) / radius
    a = np.clip(1 - d, 0, 1) ** 2 * 255 * strength
    img = np.zeros((s, s, 4), np.uint8)
    img[..., 0], img[..., 1], img[..., 2] = color
    img[..., 3] = np.clip(a, 0, 255).astype(np.uint8)
    return Image.fromarray(img, "RGBA")


def supersampled(w, h, draw_fn, ss=2):
    """Draw at ss x resolution then downsample for anti-aliased vector shapes."""
    big = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(big), ss, big)
    return big.resize((w, h), Image.LANCZOS)
