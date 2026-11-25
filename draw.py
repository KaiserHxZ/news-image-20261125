#!/usr/bin/env python3
"""Draw the news-image-20261125 front page (build-time script, Pillow).

Fresh work for this entry only. Three layout variants; run with an
argument of A, B or C to render that variant to variants/variant-X.png.
The winning variant is rendered to entry.png by the revision pass.
All facts are from reports published on 25 November 2026 (see README).
"""
import sys
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (253, 251, 243)
INK = (20, 20, 20)
GREY = (105, 105, 100)
RED = (178, 28, 28)
DARKRED = (140, 20, 20)
BLUE = (26, 58, 107)
NAVY = (18, 28, 52)
GOLD = (176, 124, 18)
TEAL = (18, 110, 105)
LIGHT = (238, 234, 222)
RULE = (60, 60, 60)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def cw(d, text, f):
    return d.textlength(text, font=f)


def centre(d, y, text, f, fill=INK, x0=0, x1=W):
    d.text((x0 + (x1 - x0 - cw(d, text, f)) / 2, y), text, font=f, fill=fill)


def left(d, x, y, text, f, fill=INK):
    d.text((x, y), text, font=f, fill=fill)


def wrap(d, text, f, width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if cw(d, t, f) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def masthead(d, date_size=34):
    d.rectangle([0, 0, W, 118], fill=PAPER)
    centre(d, 22, "THE DAY'S NEWS", font(SERIF, 62), fill=INK)
    d.line([(28, 100), (W - 28, 100)], fill=INK, width=3)
    d.line([(28, 106), (W - 28, 106)], fill=INK, width=1)
    d.rectangle([28, 118, W - 28, 118 + 46], fill=INK)
    centre(d, 127, "WEDNESDAY, 25 NOVEMBER 2026", font(SANSB, date_size),
           fill=(255, 255, 255))
    centre(d, 172, "WORLD EDITION  |  FIVE STORIES THAT SHAPED THE DAY",
           font(SANS, 17), fill=GREY)


def footer(d):
    centre(d, 992, "Sources: Reuters, The Wall Street Journal, PHIVOLCS.  Full list in README.",
           font(SANS, 15), fill=GREY)


def kicker(d, x, y, text, color=RED):
    left(d, x, y, text, font(SANSB, 17), fill=color)


def headline(d, x, y, text, size, width, fill=INK, leading=None):
    f = font(SANSB, size)
    leading = leading or int(size * 1.12)
    lines = wrap(d, text, f, width)
    for i, ln in enumerate(lines):
        left(d, x, y + i * leading, ln, f, fill=fill)
    return y + len(lines) * leading


def fact(d, x, y, text, size, width, fill=(45, 45, 45)):
    f = font(SANS, size)
    leading = int(size * 1.25)
    lines = wrap(d, text, f, width)
    for i, ln in enumerate(lines):
        left(d, x, y + i * leading, ln, f, fill=fill)
    return y + len(lines) * leading


def panel_box(d, x0, y0, x1, y1, fill=(255, 255, 255)):
    d.rectangle([x0, y0, x1, y1], fill=fill, outline=RULE, width=2)


def falling_chart(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(255, 255, 255), outline=RULE, width=2)
    for gy in range(1, 4):
        gy_y = y0 + (y1 - y0) * gy / 4
        d.line([(x0 + 8, gy_y), (x1 - 8, gy_y)], fill=(220, 218, 210), width=1)
    pts = [(x0 + 30, y0 + 28), (x0 + 170, y0 + 44), (x0 + 310, y0 + 58),
           (x0 + 450, y0 + 88), (x0 + 590, y0 + 118),
           (x1 - 40, y1 - 26)]
    d.line(pts, fill=RED, width=7, joint="curve")
    for p in pts:
        d.ellipse([p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6], fill=RED)
    ex, ey = pts[-1]
    d.polygon([(ex + 4, ey - 16), (ex + 26, ey + 2), (ex - 4, ey + 10)],
              fill=RED)
    cap = "AT THE DAY'S LOWS"
    left(d, x1 - 16 - cw(d, cap, font(SANSB, 16)), y0 + 12, cap,
         font(SANSB, 16), fill=GREY)


def rising_bars(d, x0, y0, x1, y1, pairs, color):
    d.rectangle([x0, y0, x1, y1], fill=(255, 255, 255), outline=RULE, width=2)
    base = y1 - 34
    d.line([(x0 + 12, base), (x1 - 12, base)], fill=RULE, width=2)
    bw = 74
    gap = (x1 - x0 - len(pairs) * bw) / (len(pairs) + 1)
    vmax = max(v for _, v in pairs) * 1.25
    for i, (lab, v) in enumerate(pairs):
        bx = x0 + gap + i * (bw + gap)
        bh = (base - y0 - 30) * v / vmax
        d.rectangle([bx, base - bh, bx + bw, base], fill=color)
        centre(d, base + 8, lab, font(SANSB, 16), fill=INK, x0=bx, x1=bx + bw)
        centre(d, base - bh - 26, "%.1f%%" % v, font(SANSB, 19), fill=INK,
               x0=bx, x1=bx + bw)


def big_number(d, x0, y0, x1, y1, value, old, color):
    d.rectangle([x0, y0, x1, y1], fill=(255, 255, 255), outline=RULE, width=2)
    cx = x0 + 34
    cy = (y0 + y1) // 2
    d.polygon([(cx, cy - 20), (cx - 15, cy + 8), (cx + 15, cy + 8)],
              fill=color)
    left(d, x0 + 62, cy - 32, value, font(SANSB, 42), fill=color)
    left(d, x0 + 62, cy + 14, "from %s in September" % old,
         font(SANS, 17), fill=GREY)


def skyline(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=NAVY)
    import random
    rnd = random.Random(7)
    h = y1 - y0
    bx = x0 + 14
    while bx < x1 - 40:
        bw = rnd.randint(46, 78)
        bh = rnd.randint(24, max(28, h - 12))
        by = y1 - 8 - bh
        d.rectangle([bx, by, bx + bw, y1 - 8], fill=(10, 16, 34))
        for wy in range(by + 10, y1 - 16, 20):
            for wx in range(bx + 8, bx + bw - 8, 18):
                if rnd.random() < 0.5:
                    d.rectangle([wx, wy, wx + 8, wy + 9], fill=(255, 214, 120))
        bx += bw + 10
    cx, cy = x0 + (x1 - x0) * 0.68, y0 + max(20, h // 2 - 6)
    for ang in range(0, 360, 30):
        import math
        r1, r2 = 12, 30
        a = math.radians(ang)
        d.line([(cx, cy), (cx + r2 * math.cos(a), cy + r2 * math.sin(a))],
               fill=(255, 150, 40), width=4)
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(255, 170, 50))


def seismo(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(255, 248, 230), outline=RULE, width=2)
    mid = (y0 + y1) / 2 - 8
    amp_max = max(10, (y1 - y0) / 2 - 14)
    pts = []
    x = x0 + 12
    import math
    while x < x1 - 12:
        t = (x - x0) / (x1 - x0)
        amp = 4 + amp_max * math.exp(-((t - 0.45) ** 2) / 0.012)
        pts.append((x, mid + amp * math.sin(x * 0.55)))
        x += 7
    d.line(pts, fill=RED, width=4, joint="curve")
    d.line([(x0 + 12, mid), (x1 - 12, mid)], fill=(190, 185, 170), width=1)
    gy = y1 - 26
    for gx in range(x0 + 24, x1 - 20, 46):
        d.line([(gx, gy), (gx + 22, gy + 14)], fill=(120, 110, 95), width=3)
    d.rectangle([x0 + 8, y0 + 6, x0 + 122, y0 + 46], fill=(255, 248, 230))
    left(d, x0 + 14, y0 + 10, "M 5.1", font(SANSB, 30), fill=DARKRED)


# ---------------- Variant A: classic front page ----------------

def variant_a():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    masthead(d)
    # Lead story
    y = headline(d, 28, 204, "ASIAN MARKETS TUMBLE", 46, 968)
    fact(d, 28, y + 2,
         "AI doubts and fresh tariff threats hit shares across Asia.",
         20, 968)
    falling_chart(d, 28, 292, W - 28, 452)
    stats = [("NIKKEI", "-2.9%"), ("KOSPI", "-5.3%"), ("SOFTBANK", "-13.8%")]
    sw = (W - 56 - 2 * 16) / 3
    for i, (lab, val) in enumerate(stats):
        sx = 28 + i * (sw + 16)
        d.rectangle([sx, 466, sx + sw, 522], fill=(255, 255, 255),
                    outline=RULE, width=2)
        centre(d, 476, lab, font(SANSB, 17), fill=GREY, x0=sx, x1=sx + sw)
        centre(d, 494, val, font(SANSB, 24), fill=RED, x0=sx, x1=sx + sw)
    # Row 2: inflation panels
    y0, y1 = 540, 748
    for (x0, x1, kick, head, val, old, color, ftext) in [
            (28, 500, "JAPAN  |  ECONOMY", "SERVICES PRICES SOAR",
             "4.2%", "3.8%", BLUE,
             "Services prices rose 4.2% in October, the fastest since 1990."),
            (524, 996, "AUSTRALIA  |  ECONOMY", "INFLATION HITS 4.9%",
             "4.9%", "4.3%", TEAL,
             "Headline CPI hit 4.9%; underlying inflation rose to 3.8%.")]:
        panel_box(d, x0, y0, x1, y1)
        kicker(d, x0 + 16, y0 + 12, kick, color=color)
        headline(d, x0 + 16, y0 + 36, head, 27, x1 - x0 - 32)
        big_number(d, x0 + 16, y0 + 74, x1 - 16, y1 - 58, val, old, color)
        fact(d, x0 + 16, y1 - 54, ftext, 17, x1 - x0 - 32)
    # Row 3: war + quake
    y0, y1 = 766, 978
    panel_box(d, 28, y0, 500, y1)
    kicker(d, 44, y0 + 12, "UKRAINE  |  WAR")
    headline(d, 44, y0 + 36, "STRIKES HIT ODESA, KYIV", 27, 440)
    skyline(d, 44, y0 + 74, 484, y1 - 62)
    fact(d, 44, y1 - 54,
         "Two killed in Odesa; a Kyiv apartment block caught fire.", 17, 440)
    panel_box(d, 524, y0, 996, y1)
    kicker(d, 540, y0 + 12, "PHILIPPINES  |  NATURE", color=GOLD)
    headline(d, 540, y0 + 36, "QUAKE SHAKES ANTIQUE", 27, 440)
    seismo(d, 540, y0 + 74, 980, y1 - 62)
    fact(d, 540, y1 - 54,
         "Magnitude 5.1 at 7:29 a.m.; tremors felt across Panay.", 17, 440)
    footer(d)
    return img


# ---------------- Variant B: big picture lead, 2x2 grid ----------------

def variant_b():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    masthead(d)
    d.rectangle([28, 204, W - 28, 560], fill=INK)
    centre(d, 224, "MARKETS TUMBLE ACROSS ASIA", font(SANSB, 40),
           fill=(255, 255, 255))
    centre(d, 272, "AI doubts and tariff threats sink shares from Tokyo to Seoul",
           font(SANS, 20), fill=(220, 220, 220))
    falling_chart(d, 52, 316, W - 52, 496)
    stats = [("NIKKEI -2.9%", "KOSPI -5.3%", "SOFTBANK -13.8%")]
    centre(d, 512, "NIKKEI  -2.9%      KOSPI  -5.3%      SOFTBANK  -13.8%",
           font(SANSB, 24), fill=(255, 120, 120))
    cards = [
        (28, 578, 500, 770, "JAPAN", "SERVICES PRICES AT 36-YEAR HIGH",
         "+4.2% in October, fastest since 1990", BLUE),
        (524, 578, 996, 770, "AUSTRALIA", "INFLATION JUMPS TO 4.9%",
         "Underlying inflation up to 3.8%", TEAL),
        (28, 786, 500, 978, "UKRAINE", "STRIKES HIT ODESA AND KYIV",
         "Two killed in Odesa; Kyiv flats hit", RED),
        (524, 786, 996, 978, "PHILIPPINES", "QUAKE SHAKES ANTIQUE",
         "Magnitude 5.1; tremors across Panay", GOLD),
    ]
    for x0, y0, x1, y1, kick, head, ftext, color in cards:
        panel_box(d, x0, y0, x1, y1)
        d.rectangle([x0, y0, x0 + 10, y1], fill=color)
        kicker(d, x0 + 24, y0 + 14, kick, color=color)
        headline(d, x0 + 24, y0 + 40, head, 28, x1 - x0 - 40)
        fact(d, x0 + 24, y1 - 44, ftext, 18, x1 - x0 - 40)
    footer(d)
    return img


# ---------------- Variant C: five bands ----------------

def variant_c():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    masthead(d)
    bands = [
        ("MARKETS", "ASIAN SHARES TUMBLE", "Nikkei -2.9%, Kospi -5.3%, SoftBank -13.8%", "chart"),
        ("JAPAN", "SERVICES PRICES AT 36-YEAR HIGH", "+4.2% in October; fastest since 1990", "bars1"),
        ("AUSTRALIA", "INFLATION JUMPS TO 4.9%", "Underlying inflation rises to 3.8%", "bars2"),
        ("UKRAINE", "STRIKES HIT ODESA AND KYIV", "Two killed in Odesa; Kyiv flats hit", "sky"),
        ("PHILIPPINES", "QUAKE SHAKES ANTIQUE", "Magnitude 5.1; tremors across Panay", "seis"),
    ]
    y = 204
    bh = 150
    for i, (kick, head, ftext, kind) in enumerate(bands):
        y0 = y + i * (bh + 8)
        y1 = y0 + bh
        fill = (255, 255, 255) if i % 2 == 0 else (246, 243, 233)
        panel_box(d, 28, y0, W - 28, y1, fill=fill)
        ix0, iy0, ix1, iy1 = 44, y0 + 14, 164, y1 - 14
        if kind == "chart":
            falling_chart(d, ix0, iy0, ix1, iy1)
        elif kind == "bars1":
            rising_bars(d, ix0, iy0, ix1, iy1, [("S", 3.8), ("O", 4.2)], BLUE)
        elif kind == "bars2":
            rising_bars(d, ix0, iy0, ix1, iy1, [("S", 4.3), ("O", 4.9)], TEAL)
        elif kind == "sky":
            skyline(d, ix0, iy0, ix1, iy1)
        else:
            seismo(d, ix0, iy0, ix1, iy1)
        tx = 184
        kicker(d, tx, y0 + 18, kick)
        headline(d, tx, y0 + 44, head, 30, W - 28 - tx - 16)
        fact(d, tx, y0 + 96, ftext, 19, W - 28 - tx - 16)
    footer(d)
    return img


if __name__ == "__main__":
    which = sys.argv[1].upper()
    fn = {"A": variant_a, "B": variant_b, "C": variant_c}[which]
    out = sys.argv[2] if len(sys.argv) > 2 else "variants/variant-%s.png" % which
    fn().save(out, optimize=True)
    print("wrote", out)
