#!/usr/bin/env python3
"""Génère les 5 concepts de logo Blue Line Shipping dans brand/logos/.

    ./fetch_fonts.sh            # une fois : polices Google Fonts (OFL)
    python3 build_logos.py      # régénère SVG + README de chaque concept

Chaque concept produit :
    logo-horizontal.svg, logo-vertical.svg, icon.svg,
    logo-mono-black.svg, logo-mono-white.svg,
    logo-horizontal-reverse.svg, logo-vertical-reverse.svg (fonds sombres),
    README.md
"""

import os

from blsvg import (DIFF, HERE, INTER, Font, all_bounds, bounds, flatten, move,
                   op, rect, rrect, svg, union, xform)
from concepts import CONCEPTS

ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "logos")

WHITE = "#FFFFFF"
BLACK = "#000000"
ICON = 512.0           # côté de l'icône
ICON_R = 104.0         # rayon des coins de la tuile
PAINT_ORDER = ["p", "t", "s", "a"]


# --------------------------------------------------------------------------
# Mises en page
# --------------------------------------------------------------------------

def normalize(layers, height):
    """Met un jeu de couches à la hauteur voulue, coin haut-gauche en (0, 0)."""
    b = all_bounds(layers.values())
    s = height / (b[3] - b[1])
    return {k: xform(v, s, 0, 0, s, -b[0] * s, -b[1] * s) for k, v in layers.items()}


def place(layers, dx, dy, s=1.0):
    return {k: move(v, dx, dy, s) for k, v in layers.items()}


def merge(*groups):
    out = {}
    for g in groups:
        for k, v in g.items():
            out[k] = union(out[k], v) if k in out else v
    return out


def size_of(layers):
    b = all_bounds(layers.values())
    return b[2] - b[0], b[3] - b[1]


def horizontal(c):
    S = 100.0
    if getattr(c, "logotype", False):
        wm = c.wordmark(S)
        return normalize(wm, size_of(wm)[1])
    sh = S * c.h_sym
    sym = normalize(c.symbol(), sh)
    sw, _ = size_of(sym)
    wm = c.wordmark(S)
    ww, wh = size_of(wm)
    wm = normalize(wm, wh)
    top = max(sh, wh)
    dy = (top - wh) if c.h_align == "bottom" else (top - wh) / 2
    return merge(place(sym, 0, (top - sh) / 2),
                 place(wm, sw + c.h_gap * S, dy + c.h_offset * S))


def vertical(c):
    S = 100.0
    sym = normalize(c.symbol(vertical=True), S)
    sw, _ = size_of(sym)
    wm = c.wordmark(S * c.v_scale, align="center")
    ww, wh = size_of(wm)
    wm = normalize(wm, wh)
    width = max(sw, ww)
    return merge(place(sym, (width - sw) / 2 + c.v_shift * S, 0),
                 place(wm, (width - ww) / 2, S + c.v_gap * S))


def icon(c):
    """Tuile carrée bleu profond, symbole en blanc + accent, rognée à la tuile."""
    tile = rrect(0, 0, ICON, ICON, ICON_R)
    sym = c.icon_symbol(ICON)
    clipped = {k: op(v, tile, INTER) for k, v in sym.items()}
    return tile, clipped


# --------------------------------------------------------------------------
# Rendu
# --------------------------------------------------------------------------

def paint(layers, colors):
    seq = [(colors[k], layers[k]) for k in PAINT_ORDER if k in layers]
    return flatten(seq)


def mono(layers, color):
    return [(color, union(*layers.values()))]


def write(path, content):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def box(layers):
    return all_bounds(layers.values())


def build(c):
    d = os.path.join(OUT, c.dir)
    os.makedirs(d, exist_ok=True)
    pal = c.palette
    title = "Blue Line Shipping"
    light = {"p": pal["primary"], "t": pal["primary"], "s": pal["primary"], "a": pal["accent"]}
    dark = {"p": WHITE, "t": WHITE, "s": WHITE, "a": pal["accent_dark"]}

    h = horizontal(c)
    v = vertical(c)
    write(os.path.join(d, "logo-horizontal.svg"), svg(paint(h, light), box(h), title))
    write(os.path.join(d, "logo-vertical.svg"), svg(paint(v, light), box(v), title))
    write(os.path.join(d, "logo-horizontal-reverse.svg"), svg(paint(h, dark), box(h), title))
    write(os.path.join(d, "logo-vertical-reverse.svg"), svg(paint(v, dark), box(v), title))
    write(os.path.join(d, "logo-mono-black.svg"), svg(mono(h, BLACK), box(h), title))
    write(os.path.join(d, "logo-mono-white.svg"), svg(mono(h, WHITE), box(h), title))

    tile, sym = icon(c)
    layers = [(pal["primary"], tile)] + [(dark[k], sym[k]) for k in PAINT_ORDER if k in sym]
    write(os.path.join(d, "icon.svg"), svg(layers, (0, 0, ICON, ICON), title))

    hw, hh = size_of(h)
    vw, vh = size_of(v)
    meta = {"h_ratio": hw / hh, "v_ratio": vw / vh, "h_w": hw, "v_w": vw,
            "h_ship": c.ship_cap(), "v_ship": c.ship_cap(vertical=True)}
    write(os.path.join(d, "README.md"), c.readme(meta))
    return meta


def main():
    for c in CONCEPTS:
        meta = build(c)
        print(f"{c.dir}: ok  (horizontal {meta['h_ratio']:.2f}:1, vertical {meta['v_ratio']:.2f}:1)")


if __name__ == "__main__":
    main()
