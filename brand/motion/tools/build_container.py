#!/usr/bin/env python3
"""Fin alternative « conteneur » : un conteneur 40' Marine nuit dont le flanc porte le logo.

Le dessin est plat et vectoriel, en unités du logo : le logo horizontal occupe [0, 448.41] × [0, 100], et le
conteneur est construit autour de lui, le plus serré possible :
  - la hauteur de la paroi est la plus petite qui loge, entre les rails, le logo et sa zone d'exclusion
    (1 x = un rayon d'anneau au-dessus et au-dessous) ;
  - la longueur suit les proportions exactes d'un 40' (12,192 × 2,591 m).
Le logo occupe ainsi la plus grande part possible du flanc sans enfreindre la règle de marque.

Le script :
  - injecte la géométrie dans brand/motion/reveal.html (bloc CONTAINER) ;
  - écrit l'image fixe brand/mockups/container-dark.svg (2000 × 1125) ;
  - vérifie, par intersection exacte des tracés, que rien (montant, rail, texte, porte) n'entre dans la zone
    d'exclusion du logo.

    python3 brand/motion/tools/build_container.py     (après build_reveal.py)

Les textes sont composés en Readex Pro et convertis en tracés (polices : brand/tools/fetch_fonts.sh).
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOTION = os.path.dirname(HERE)
BRAND = os.path.dirname(MOTION)
sys.path.insert(0, os.path.join(BRAND, "tools"))
from blsvg import DIFF, INTER, Font, bounds, is_empty, move, op, rect, to_d, union  # noqa: E402

REVEAL = os.path.join(MOTION, "reveal.html")
LOGO_SVG = os.path.join(BRAND, "logos", "concept-05", "logo-horizontal-reverse.svg")
MOCKUP = os.path.join(BRAND, "mockups", "container-dark.svg")

# --------------------------------------------------------------------------
# Couleurs : tout le conteneur est en Marine nuit ; seules ses lignes sont un peu plus claires.
# Les éclaircissements se font en OKLCH (luminance +ΔL, teinte conservée, chroma un peu réduite pour rester
# un bleu acier et ne jamais tirer vers le Bleu Coque, réservé aux lettres de la version claire).
# --------------------------------------------------------------------------
MARINE = "#0A1A3A"   # Marine nuit : tôle, portes, montants, rails, et ciel (= fond final de la version sombre)
WHITE = "#FFFFFF"
LINE_DL = 0.07       # tôle ondulée et arêtes : +7 points de luminance OKLCH (demande : +6 à +8, pas plus)
CHROMA = 0.75        # chroma conservée sur les lignes (désaturation légère)


def _lin(v):
    v /= 255
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def _enc(v):
    v = min(1, max(0, v))
    return 255 * (12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055)


def oklab(hex_):
    r, g, b = (_lin(int(hex_[i:i + 2], 16)) for i in (1, 3, 5))
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def lighten(hex_, dL, chroma=1.0):
    """Éclaircit de dL en luminance OKLCH, teinte conservée, chroma multipliée par `chroma`."""
    L, A, B = oklab(hex_)
    L, A, B = L + dL, A * chroma, B * chroma
    l, m, s = ((L + 0.3963377774 * A + 0.2158037573 * B) ** 3, (L - 0.1055613458 * A - 0.0638541728 * B) ** 3,
               (L - 0.0894841775 * A - 1.2914855480 * B) ** 3)
    rgb = (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
           -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
           -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)
    return "#" + "".join(f"{round(_enc(v)):02X}" for v in rgb)


LINE = lighten(MARINE, LINE_DL, CHROMA)
COLORS = {
    "sky": MARINE, "wall": MARINE, "door": MARINE,
    "corrugation": LINE,   # tôle ondulée
    "edge": LINE,          # arêtes des rails, montants, pièces de coin, portes, silhouette
    "steel": LINE,         # barres de verrouillage, gâches, poignées
    "text": WHITE,
}

# --------------------------------------------------------------------------
# Géométrie (unités du logo ; y vers le bas)
# --------------------------------------------------------------------------
LOGO_W, LOGO_H = 448.41, 100.0
R = 50.0                                   # rayon de l'anneau = unité x de la zone d'exclusion
LOGO_CX, LOGO_CY = LOGO_W / 2, LOGO_H / 2
EXCLUSION = (-R, -R, LOGO_W + R, LOGO_H + R)

RAIL_T_F, RAIL_B_F = 20 / 640, 26 / 640    # rails haut et bas, en fraction de la hauteur de paroi
SAFE = 4.0                                 # marge entre la zone d'exclusion et les rails
H_WALL = round((EXCLUSION[3] - EXCLUSION[1] + 2 * SAFE) / (1 - RAIL_T_F - RAIL_B_F), 1)
W_SIDE = round(H_WALL * 12.192 / 2.591, 1)  # flanc d'un 40'
k = H_WALL / 640                           # échelle des détails (dessinés pour une paroi de 640 u)
RAIL_T, RAIL_B, POST = 20 * k, 26 * k, 30 * k
W_DOOR = 330 * k                           # face des portes, montrée à plat à droite
EDGE = 2.6 * k                             # épaisseur des arêtes
X0 = LOGO_CX - W_SIDE / 2                  # le logo est centré sur le flanc, horizontalement et verticalement
X1 = X0 + W_SIDE
X2 = X1 + W_DOOR
Y0 = LOGO_CY - H_WALL / 2
Y1 = Y0 + H_WALL
FRAMING = {"width": 0.92, "center_y": 0.50}   # cadrage final : conteneur sur 92 % de la largeur, centré


def text_path(font, txt, cap, x, base, anchor="left", tracking=0.0):
    p, _ = Font(font).text(txt, cap, tracking)
    b = bounds(p)
    dx = x - b[0] if anchor == "left" else x - b[2]
    return move(p, dx, base)


def outline(x, y, w, h, t):
    """Contour (cadre) d'un rectangle, d'épaisseur t vers l'intérieur."""
    return op(rect(x, y, w, h), rect(x + t, y + t, w - 2 * t, h - 2 * t), DIFF)


def build():
    layers = []   # (rôle, couleur, tracé) dans l'ordre de peinture

    # Flanc et face des portes : aplats Marine nuit (= le fond, d'où une transition invisible)
    layers.append(("wall", COLORS["wall"], rect(X0, Y0, W_SIDE, H_WALL)))
    layers.append(("door", COLORS["door"], rect(X1, Y0, W_DOOR, H_WALL)))

    # Tôle ondulée : fines lignes verticales sur le flanc, entre montants et rails
    pitch = 64.0 * k
    n = int((W_SIDE - 2 * POST) // pitch)
    off = X0 + POST + ((W_SIDE - 2 * POST) - (n - 1) * pitch) / 2
    corr = union(*[rect(off + i * pitch - 1.5 * k, Y0 + RAIL_T, 3.0 * k, H_WALL - RAIL_T - RAIL_B) for i in range(n)])
    layers.append(("corrugation", COLORS["corrugation"], corr))

    # Arêtes : silhouette, rails, montants d'angle, pièces de coin percées, séparation des vantaux
    edges = [
        outline(X0, Y0, X2 - X0, H_WALL, EDGE),
        rect(X0, Y0 + RAIL_T - EDGE, X2 - X0, EDGE),
        rect(X0, Y1 - RAIL_B, X2 - X0, EDGE),
        rect(X0 + POST - EDGE, Y0, EDGE, H_WALL),
        rect(X1 - POST / 2, Y0, EDGE, H_WALL), rect(X1 + POST / 2 - EDGE, Y0, EDGE, H_WALL),
        rect(X2 - POST, Y0, EDGE, H_WALL),
        rect(X1 + W_DOOR / 2 - EDGE / 2, Y0 + RAIL_T, EDGE, H_WALL - RAIL_T - RAIL_B),
    ]
    for cx in (X0, X1 - 22 * k, X2 - 44 * k):
        for cy in (Y0, Y1 - 34 * k):
            edges.append(outline(cx, cy, 44 * k, 34 * k, EDGE))
            edges.append(outline(cx + 12 * k, cy + 11 * k, 20 * k, 12 * k, EDGE * 0.8))
    layers.append(("edge", COLORS["edge"], union(*edges)))

    # Portes : 4 barres de verrouillage, gâches haut et bas, poignées
    parts = []
    for f in (0.15, 0.35, 0.65, 0.85):
        x = X1 + W_DOOR * f
        parts.append(rect(x - 4 * k, Y0 + RAIL_T + 10 * k, 8 * k, H_WALL - RAIL_T - RAIL_B - 20 * k))
        parts += [rect(x - 9 * k, Y0 + RAIL_T + 4 * k, 18 * k, 26 * k),
                  rect(x - 9 * k, Y1 - RAIL_B - 30 * k, 18 * k, 26 * k)]
        hy = LOGO_CY + 0.11 * H_WALL                       # poignées un peu sous la mi-hauteur
        parts += [rect(x, hy, 30 * k, 8 * k), rect(x + 24 * k, hy - 10 * k, 8 * k, 26 * k)]
    layers.append(("steel", COLORS["steel"], union(*parts)))

    # Marquages : numéro de conteneur (ISO 6346, chiffre de contrôle encadré) en haut à droite, raison sociale en bas
    code_cap = 34.0 * k
    code_x = X1 - POST - 70 * k
    code_base = Y0 + RAIL_T + 40 * k + code_cap
    owner = text_path("ReadexPro-600", "BLSU 001234", code_cap, code_x - 64 * k, code_base, "right", 0.04)
    check = text_path("ReadexPro-600", "6", code_cap, code_x - 8 * k, code_base, "right")
    cb = bounds(check)
    box = op(rect(cb[0] - 12 * k, cb[1] - 10 * k, cb[2] - cb[0] + 24 * k, cb[3] - cb[1] + 20 * k),
             rect(cb[0] - 8 * k, cb[1] - 6 * k, cb[2] - cb[0] + 16 * k, cb[3] - cb[1] + 12 * k), DIFF)
    size_type = text_path("ReadexPro-600", "42G1", 26.0 * k, code_x - 8 * k, code_base + (22 + 26 + 10) * k,
                          "right", 0.04)
    company = text_path("ReadexPro-500", "BLUE LINE SHIPPING SARL · ALGÉRIE", 18.0 * k, X0 + POST + 40 * k,
                        Y1 - RAIL_B - 30 * k, "left", 0.08)
    layers.append(("text", COLORS["text"], union(owner, check, box, size_type, company)))

    # Zone d'exclusion : seuls le flanc et sa tôle peuvent la toucher (intersection exacte des tracés)
    ex0, ey0, ex1, ey1 = EXCLUSION
    zone = rect(ex0, ey0, ex1 - ex0, ey1 - ey0)
    for role, _, path in layers:
        if role in ("wall", "corrugation"):
            continue
        assert is_empty(op(path, zone, INTER)), f"« {role} » entre dans la zone d'exclusion du logo"
    assert ey0 >= Y0 + RAIL_T and ey1 <= Y1 - RAIL_B, "la zone d'exclusion touche un rail"
    return layers


def main():
    layers = build()
    logo_src = open(LOGO_SVG, encoding="utf-8").read()
    logo_paths = re.findall(r"<path [^>]*/>", logo_src)
    data = {
        "colors": COLORS,
        "box": [round(v, 2) for v in (X0, Y0, X2, Y1)],
        "wall": [round(v, 2) for v in (X0, Y0, X1, Y1)],
        "exclusion": [round(v, 2) for v in EXCLUSION],
        "logo": [0, 0, LOGO_W, LOGO_H],
        "framing": FRAMING,
        "layers": [{"role": r, "fill": c, "d": to_d(p)} for r, c, p in layers],
    }

    html = open(REVEAL, encoding="utf-8").read()
    block = "/*CONTAINER:BEGIN*/ const CONTAINER = " + json.dumps(data, separators=(",", ":")) + "; /*CONTAINER:END*/"
    html, n = re.subn(r"/\*CONTAINER:BEGIN\*/.*?/\*CONTAINER:END\*/", lambda m: block, html, flags=re.S)
    assert n == 1, "marqueurs CONTAINER introuvables dans reveal.html"
    open(REVEAL, "w", encoding="utf-8").write(html)

    # Image fixe 2000 × 1125 : même cadrage que la dernière image de reveal-container-16x9.mp4
    W, H = 2000, 1125
    s = FRAMING["width"] * W / (X2 - X0)
    tx = W / 2 - (X0 + X2) / 2 * s
    ty = FRAMING["center_y"] * H - (Y0 + Y1) / 2 * s
    body = "".join(f'<path fill="{c}" d="{to_d(p)}"/>' for _, c, p in layers)
    os.makedirs(os.path.dirname(MOCKUP), exist_ok=True)
    open(MOCKUP, "w", encoding="utf-8").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
        f'aria-label="Conteneur 40 pieds Blue Line Shipping, logo sur le flanc">'
        f"<title>Conteneur 40 pieds Blue Line Shipping</title>"
        f'<rect width="{W}" height="{H}" fill="{COLORS["sky"]}"/>'
        f'<g transform="translate({tx:.3f} {ty:.3f}) scale({s:.6f})">{body}{"".join(logo_paths)}</g></svg>\n')
    print(f"conteneur : paroi {W_SIDE} × {H_WALL} u (40'), portes {W_DOOR:.1f} u ; logo = {LOGO_W / W_SIDE * 100:.1f} % "
          f"de la longueur de paroi ({LOGO_W / W_SIDE * 12.192:.2f} m), {LOGO_H / H_WALL * 100:.1f} % de sa hauteur ; "
          f"lignes {LINE} ; zone d'exclusion libre ; {os.path.relpath(MOCKUP, BRAND)}")


if __name__ == "__main__":
    main()
