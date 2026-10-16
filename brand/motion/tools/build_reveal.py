#!/usr/bin/env python3
"""Injecte dans reveal.html la géométrie exacte du logo horizontal du concept 05.

Les tracés sont lus directement dans brand/logos/concept-05/logo-horizontal*.svg
(aucun redessin) puis découpés :
  - l'anneau en deux demi-anneaux (haut / bas),
  - la ligne,
  - BLUE LINE et SHIPPING lettre par lettre (contours regroupés par inclusion),
et les chemins complets sont conservés tels quels pour l'image finale.

    python3 brand/motion/tools/build_reveal.py
"""

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
MOTION = os.path.dirname(HERE)
BRAND = os.path.dirname(MOTION)
LOGOS = os.path.join(BRAND, "logos", "concept-05")
REVEAL = os.path.join(MOTION, "reveal.html")

NUM = re.compile(r"-?(?:\d+\.?\d*|\.\d+)")
TOK = re.compile(r"[MmLlHhVvCcQqZz]|-?(?:\d+\.?\d*|\.\d+)")
ARITY = {"m": 2, "l": 2, "h": 1, "v": 1, "c": 6, "q": 4, "z": 0}


def read_svg(name):
    src = open(os.path.join(LOGOS, name), encoding="utf-8").read()
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', src).group(1).split()]
    paths = re.findall(r'<path fill="([^"]+)" d="([^"]+)"', src)
    return vb, paths


def r2(v):
    v = round(v + 0.0, 2)
    return 0.0 if v == 0 else v


def fmt(v):
    s = f"{r2(v):.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def subpaths(d):
    """Découpe un attribut d en sous-chemins absolus [(segments, bbox)]."""
    toks = TOK.findall(d)
    i, cmd = 0, None
    x = y = sx = sy = 0.0
    out, cur, pts = [], [], []

    def close_sub():
        if cur:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            out.append((list(cur), (min(xs), min(ys), max(xs), max(ys))))
        cur.clear()
        pts.clear()

    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd in "zZ":
                cur.append(("Z",))
                x, y = sx, sy
                close_sub()
                continue
        rel = cmd.islower()
        c = cmd.lower()
        n = ARITY[c]
        vals = [float(v) for v in toks[i:i + n]]
        i += n
        if c == "m":
            if cur:
                close_sub()
            x, y = (x + vals[0], y + vals[1]) if rel else (vals[0], vals[1])
            sx, sy = x, y
            cur.append(("M", x, y))
            pts.append((x, y))
            cmd = "l" if rel else "L"  # coordonnées suivantes implicites
        elif c == "l":
            x, y = (x + vals[0], y + vals[1]) if rel else (vals[0], vals[1])
            cur.append(("L", x, y))
            pts.append((x, y))
        elif c == "h":
            x = x + vals[0] if rel else vals[0]
            cur.append(("L", x, y))
            pts.append((x, y))
        elif c == "v":
            y = y + vals[0] if rel else vals[0]
            cur.append(("L", x, y))
            pts.append((x, y))
        elif c == "c":
            p = [(x + vals[k], y + vals[k + 1]) if rel else (vals[k], vals[k + 1]) for k in (0, 2, 4)]
            cur.append(("C", *p[0], *p[1], *p[2]))
            pts.extend(p)
            x, y = p[2]
        elif c == "q":
            p = [(x + vals[k], y + vals[k + 1]) if rel else (vals[k], vals[k + 1]) for k in (0, 2)]
            cur.append(("Q", *p[0], *p[1]))
            pts.extend(p)
            x, y = p[1]
    close_sub()
    return out


def to_d(segs):
    parts = []
    for s in segs:
        parts.append(s[0] + " ".join(fmt(v) for v in s[1:]))
    return "".join(parts)


def contains(a, b):
    return a[0] <= b[0] and a[1] <= b[1] and a[2] >= b[2] and a[3] >= b[3]


def glyphs(d):
    """Regroupe les contours d'un texte en lettres (les contre-formes vont dans leur lettre)."""
    subs = subpaths(d)
    order = sorted(range(len(subs)), key=lambda k: -(subs[k][1][2] - subs[k][1][0]) * (subs[k][1][3] - subs[k][1][1]))
    groups = []
    for k in order:
        segs, bb = subs[k]
        host = next((g for g in groups if contains(g["bbox"], bb)), None)
        if host:
            host["segs"] += segs
        else:
            groups.append({"segs": list(segs), "bbox": bb})
    groups.sort(key=lambda g: g["bbox"][0])
    return [{"d": to_d(g["segs"]), "bbox": [r2(v) for v in g["bbox"]]} for g in groups]


def line_metrics(gl):
    """Ligne de base = bas des lettres à fond plat ; capitale = haut des lettres à sommet plat."""
    bottoms = sorted(g["bbox"][3] for g in gl)
    tops = sorted(g["bbox"][1] for g in gl)
    base = bottoms[len(bottoms) // 2]
    top = tops[len(tops) // 2]
    return {"base": r2(base), "cap": r2(base - top), "max_bottom": r2(bottoms[-1])}


def main():
    vb, light = read_svg("logo-horizontal.svg")
    vb2, dark = read_svg("logo-horizontal-reverse.svg")
    assert vb == vb2 and len(light) == 4 and len(dark) == 4
    assert [d for _, d in light] == [d for _, d in dark], "les deux versions doivent partager les tracés"
    d_ring, d_title, d_tag, d_line = (d for _, d in light)

    ring = subpaths(d_ring)
    assert len(ring) == 2, "l'anneau doit compter deux demi-anneaux"
    ring.sort(key=lambda s: s[1][1])
    (up, ubb), (lo, lbb) = ring
    # La coupe passe sous l'équateur : le rayon se lit au sommet, pas à la largeur.
    cx, cy = (ubb[0] + ubb[2]) / 2, (ubb[3] + lbb[1]) / 2
    R = cy - ubb[1]
    assert abs((lbb[3] - cy) - R) < 0.02, "anneau non symétrique"
    ycut = cy - ubb[3]

    line = subpaths(d_line)
    assert len(line) == 1
    lbx = line[0][1]

    # Fond « bleu » = la couleur dominante du concept (Bleu Coque), lue dans la version claire
    t = 13.0 / 44.0  # épaisseur de l'anneau / rayon (symbols.c05_loadline)
    title, tag = glyphs(d_title), glyphs(d_tag)
    assert len(title) == 8 and len(tag) == 8, (len(title), len(tag))

    geo = {
        "source": "brand/logos/concept-05/logo-horizontal.svg + logo-horizontal-reverse.svg",
        "vb": [r2(vb[2]), r2(vb[3])],
        "colors": {
            "dark": {"bg": light[0][0], "fg": dark[0][0], "accent": dark[3][0]},
            "light": {"bg": "#FFFFFF", "fg": light[0][0], "accent": light[3][0]},
        },
        "ring": {"cx": r2(cx), "cy": r2(cy), "R": r2(R), "r": r2(R * (1 - t)), "ycut": r2(ycut),
                 "upper": to_d(up), "lower": to_d(lo)},
        "line": {"x0": r2(lbx[0]), "x1": r2(lbx[2]), "y0": r2(lbx[1]), "y1": r2(lbx[3])},
        "title": {"glyphs": title, **line_metrics(title)},
        "tagline": {"glyphs": tag, **line_metrics(tag)},
        "full": {"ring": d_ring, "title": d_title, "tagline": d_tag, "line": d_line},
    }

    html = open(REVEAL, encoding="utf-8").read()
    block = "/*GEOMETRY:BEGIN*/ const GEO = " + json.dumps(geo, ensure_ascii=False, separators=(",", ":")) + "; /*GEOMETRY:END*/"
    html, n = re.subn(r"/\*GEOMETRY:BEGIN\*/.*?/\*GEOMETRY:END\*/", lambda m: block, html, flags=re.S)
    assert n == 1, "marqueurs GEOMETRY introuvables dans reveal.html"
    open(REVEAL, "w", encoding="utf-8").write(html)
    print(f"reveal.html : géométrie injectée (viewBox {vb[2]} × {vb[3]}, anneau R={R:.2f} cx={cx:.2f} cy={cy:.2f}, "
          f"coupe ±{ycut:.2f}, ligne {lbx[0]:.2f}→{lbx[2]:.2f}, {len(title)}+{len(tag)} lettres)")


if __name__ == "__main__":
    main()
