#!/usr/bin/env python3
"""Generate assets/img/og-default.png and assets/img/apple-touch-icon.png.

    pip install Pillow && python3 scripts/make-social-images.py

Optional one-off tool — the site itself has no build dependencies, and the two
PNGs it writes are committed. Re-run it only if the branding changes, or replace
its output with hand-designed artwork.

  og-default.png     1200x630  the card social networks show when a link to the
                               site is shared. Uses the real logo unmodified.
  apple-touch-icon.png 180x180 iOS home-screen icon, matching favicon.svg.
"""

import pathlib

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
FONTS = ROOT / "scripts" / "fonts"

# Brand tokens — same values as the CSS custom properties in assets/css/site.css.
FOREST = (16, 76, 47)
DEEP = (8, 40, 26)
GREEN = (13, 132, 61)
GLOW = (76, 215, 135)
STONE = (242, 245, 242)
MUTED = (74, 90, 81)
PALE = (207, 229, 217)
WHITE = (255, 255, 255)

SS = 3  # supersample factor, downscaled at the end for clean edges


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def og_card():
    W, H = 1200, 630
    im = Image.new("RGB", (W * SS, H * SS), WHITE)
    d = ImageDraw.Draw(im)

    # Faint diagonal rules, echoing the .gridfx texture on the site's hero.
    for x in range(-H, W + H, 34):
        d.line([(x * SS, 0), ((x + H) * SS, H * SS)], fill=(237, 243, 238), width=1 * SS)

    # Forest band across the foot of the card.
    band = 104
    d.rectangle([0, (H - band) * SS, W * SS, H * SS], fill=FOREST)
    d.rectangle([0, (H - band) * SS, W * SS, (H - band + 6) * SS], fill=GLOW)

    # The real logo, scaled to width and composited on the white field.
    logo = Image.open(IMG / "logo.png").convert("RGBA")
    lw = 430 * SS
    lh = round(lw * logo.height / logo.width)
    logo = logo.resize((lw, lh), Image.LANCZOS)
    im.paste(logo, (72 * SS, 66 * SS), logo)

    headline = font("Archivo-800.ttf", 62 * SS)
    sub = font("Figtree-600.ttf", 30 * SS)
    small = font("Figtree-600.ttf", 25 * SS)
    mark = font("Archivo-800.ttf", 27 * SS)

    d.text((72 * SS, 252 * SS), "Approval-Ready", font=headline, fill=FOREST)
    d.text((72 * SS, 324 * SS), "Borrowing", font=headline, fill=GREEN)

    d.text((72 * SS, 424 * SS),
           "We work for builders to get their loans approved.",
           font=sub, fill=MUTED)

    d.text((72 * SS, (H - band + 40) * SS), "generedge.com", font=mark, fill=WHITE)

    right = "Lender matching  ·  Underwriting  ·  Closing"
    rw = d.textlength(right, font=small)
    d.text((W * SS - 72 * SS - rw, (H - band + 43) * SS), right, font=small, fill=PALE)

    im = im.resize((W, H), Image.LANCZOS)
    out = IMG / "og-default.png"
    im.save(out, optimize=True)
    print(f"wrote {out.relative_to(ROOT)} ({W}x{H}, {out.stat().st_size/1024:.0f} KB)")


def touch_icon():
    # Same marks as assets/img/favicon.svg, on its 64-unit grid. iOS applies its
    # own corner mask, so this is drawn full-bleed and square.
    S = 180
    k = S * SS / 64.0
    im = Image.new("RGB", (S * SS, S * SS), DEEP)
    d = ImageDraw.Draw(im)
    # The forward chevron of the logo mark, stroked with round caps and joins.
    pts = [(23 * k, 17 * k), (38 * k, 32 * k), (23 * k, 47 * k)]
    w = round(9 * k)
    d.line(pts, fill=GLOW, width=w, joint="curve")
    for x, y in pts:
        d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=GLOW)
    im = im.resize((S, S), Image.LANCZOS)
    out = IMG / "apple-touch-icon.png"
    im.save(out, optimize=True)
    print(f"wrote {out.relative_to(ROOT)} ({S}x{S}, {out.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    og_card()
    touch_icon()
