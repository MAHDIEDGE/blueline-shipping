#!/usr/bin/env python3
"""Fins alternatives « port » et « navire » de la version sombre : la caméra continue de reculer après la fin conteneur
et révèle une scène de nuit autour de notre conteneur.

Même style que le conteneur : dessin plat et vectoriel, aplats de Marine nuit et traits fins, sans texture, sans 3D.
La géométrie est en unités du logo (le logo horizontal occupe [0, 448.41] × [0, 100], y vers le bas), dans le même
repère que le conteneur de build_container.py, que ce script réutilise tel quel.

Le script :
  - injecte les deux scènes dans brand/motion/reveal.html (bloc SCENES) : éléments du décor (repère du monde),
    ciel en bandes, étoiles et lune (repère de l'image, un jeu par format), feux, cadrages finaux, minutage ;
  - écrit les images fixes brand/mockups/port-night.svg et ship-night.svg (2000 × 1125, plan final 16:9) ;
  - vérifie que le logo reste lisible (≥ 12 % de la largeur d'image), que le navire occupe ≈ 85 % de la largeur,
    et qu'aucune étoile ne tombe dans la zone d'exclusion du logo, derrière le texte ou derrière un objet.

    python3 brand/motion/tools/build_scenes.py     (après build_container.py)
"""

import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_container as BC  # noqa: E402  (ajoute aussi brand/tools au chemin)
from blsvg import P, UNION, bounds, circle, op, rect, to_d, union  # noqa: E402
import pathops  # noqa: E402

REVEAL = BC.REVEAL
MOCKUPS = os.path.join(BC.BRAND, "mockups")
LOGO_SVG = BC.LOGO_SVG

# --------------------------------------------------------------------------
# Couleurs : Marine nuit et ses déclinaisons en luminance OKLCH (teinte conservée). L'orange international est
# réservé à la ligne du logo et aux feux de signalisation ; le blanc Écume à la lune.
# --------------------------------------------------------------------------
MARINE, EDGE, WHITE = BC.MARINE, BC.LINE, BC.WHITE
ECUME = "#F3F5F9"
ORANGE = "#FF6A33"     # orange international de la version sombre (= ligne de logo-horizontal-reverse.svg)
TONES = {
    "sky_top": BC.lighten(MARINE, -0.040),   # haut du ciel, à peine plus sombre que l'horizon (Marine nuit)
    "sea": BC.lighten(MARINE, -0.030),       # mer : Marine nuit un ton plus sombre
    "quay": BC.lighten(MARINE, -0.012),      # face du quai, dans l'ombre
    "near": BC.lighten(MARINE, 0.030, 0.85),  # conteneurs anonymes proches : à peine plus clairs, ils restent
    "far": BC.lighten(MARINE, 0.015, 0.90),   # derrière notre conteneur ; les lointains se fondent dans la nuit
}
SW = 1.3        # épaisseur des traits du décor, en pixels d'image (constante pendant le recul)
SW_BOLD = 1.5   # silhouettes sur le ciel (portique, coque, château) : un peu plus marquées
SW_REFLECT = 1.5

# --------------------------------------------------------------------------
# Minutage (secondes). 0 – 8,0 s : exactement la version sombre (logo figé) ; puis un seul recul, continu.
# --------------------------------------------------------------------------
TIMELINE = {
    "pull": [8.00, 12.00],          # recul continu : exponentiel, une seule courbe inOut, du logo au plan large
    "end": 13.20,                   # tenue 1,2 s
    "fades": {                      # apparition des éléments du décor (fondu), tous terminés avant 12,0 s
        "ground": [9.80, 10.90],    # quai, mer, reflets
        "hull": [9.85, 10.95],      # coque et château du navire
        "accent": [9.85, 11.30],    # contour de notre conteneur, au trait du décor
        "back": [9.90, 11.00],      # piles et rangées de conteneurs anonymes
        "far": [10.05, 11.20],      # portiques
        "mark": [10.60, 11.50],     # marque de Plimsoll sur la coque
        "sky": [9.80, 11.60],       # le haut du ciel s'assombrit
        "moon": [11.35, 11.95],     # après le passage des portiques devant sa place (11,28 s au plus tard)
        "lights": [11.20, 11.80],
    },
    "stars": {"start": 11.00, "spread": 0.35, "dur": 0.55},   # chaque étoile : début dans [11,0 ; 11,35], 0,55 s
}

FORMATS = {"16x9": (1920, 1080), "1x1": (1080, 1080)}


def _logo_share():
    """Part de la largeur occupée par le logo figé, lue dans FORMATS de reveal.html (une seule source)."""
    html = open(REVEAL, encoding="utf-8").read()
    out = {f: float(m) for f, m in re.findall(r"'(16x9|1x1)':\s*\{[^}]*logo:\s*([0-9.]+)", html)}
    assert set(out) == set(FORMATS), "FORMATS introuvable dans reveal.html"
    return out


LOGO_SHARE = _logo_share()
MOCKUP = (2000, 1125)          # plan final 16:9 mis à l'échelle
STAR_SEED = {"port": 0x5EA, "ship": 0xB0A7}
N_STARS = 56

M = BC.H_WALL / 2.591          # unités du logo par mètre (paroi d'un 40' : 2,591 m)
BOX = (BC.X0, BC.Y0, BC.X2, BC.Y1)
PC = ((BC.X0 + BC.X2) / 2, (BC.Y0 + BC.Y1) / 2)   # centre du conteneur : point d'ancrage de la caméra
BIG = 40000.0


# --------------------------------------------------------------------------
# Outils
# --------------------------------------------------------------------------
def bezier(x1, y1, x2, y2):
    """Même courbe que bezier() dans reveal.html."""
    cx, bx = 3 * x1, 3 * (x2 - x1) - 3 * x1
    ax = 1 - cx - bx
    cy, by = 3 * y1, 3 * (y2 - y1) - 3 * y1
    ay = 1 - cy - by

    def f(x):
        if x <= 0:
            return 0.0
        if x >= 1:
            return 1.0
        lo, hi, t = 0.0, 1.0, x
        for _ in range(60):
            v = ((ax * t + bx) * t + cx) * t
            if abs(v - x) < 1e-9:
                break
            if v < x:
                lo = t
            else:
                hi = t
            t = (lo + hi) / 2
        return ((ay * t + by) * t + cy) * t
    return f


IN_OUT = bezier(0.65, 0, 0.35, 1)


def seg(t, ab):
    a, b = ab
    return min(1.0, max(0.0, (t - a) / (b - a)))


def mulberry32(seed):
    """Générateur pseudo-aléatoire à graine fixe : mêmes étoiles à chaque export."""
    state = [seed & 0xFFFFFFFF]

    def nxt():
        state[0] = (state[0] + 0x6D2B79F5) & 0xFFFFFFFF
        z = state[0]
        z = ((z ^ (z >> 15)) * (z | 1)) & 0xFFFFFFFF
        z ^= (z + (((z ^ (z >> 7)) * (z | 61)) & 0xFFFFFFFF)) & 0xFFFFFFFF
        return ((z ^ (z >> 14)) & 0xFFFFFFFF) / 4294967296
    return nxt


def oklch(hex_):
    L, A, B = BC.oklab(hex_)
    return L, math.hypot(A, B), math.degrees(math.atan2(B, A)) % 360


def from_oklch(L, C, h):
    A, B = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    l, m, s = ((L + 0.3963377774 * A + 0.2158037573 * B) ** 3, (L - 0.1055613458 * A - 0.0638541728 * B) ** 3,
               (L - 0.0894841775 * A - 1.2914855480 * B) ** 3)
    rgb = (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
           -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
           -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)
    return tuple(int(math.floor(BC._enc(v) + 0.5)) for v in rgb)


def mix_oklch(a, b, u):
    L0, C0, h0 = oklch(a)
    L1, C1, h1 = oklch(b)
    dh = ((h1 - h0 + 540) % 360) - 180
    return from_oklch(L0 + (L1 - L0) * u, C0 + (C1 - C0) * u, h0 + dh * u)


def hexc(rgb):
    return "#" + "".join(f"{v:02X}" for v in rgb)


def line(*pts):
    p = P()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    return p


def frame(x0, y0, x1, y1):
    """Contour fermé d'un rectangle (tracé médian, pour un trait)."""
    p = line((x0, y0), (x1, y0), (x1, y1), (x0, y1))
    p.close()
    return p


def stroke_outline(path, width):
    """Trait → aplat (pour les mockups et les tests d'occultation)."""
    q = P()
    path.draw(q.getPen())
    q.stroke(width, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 4)
    q.convertConicsToQuads()
    return pathops.simplify(q, fix_winding=True, keep_starting_points=False)


class Scene:
    """Liste ordonnée d'éléments du monde. z = 'back' (sous notre conteneur) ou 'front' (par-dessus)."""

    def __init__(self, name):
        self.name, self.els, self.lights = name, [], []

    def fill(self, path, color, fade, z="back", op_=1.0, stroke=None, sw=SW):
        self.els.append(dict(path=path, fill=color, stroke=stroke, sw=sw if stroke else 0, fade=fade, z=z, op=op_))

    def stroke(self, path, color, fade, z="back", op_=1.0, sw=SW):
        self.els.append(dict(path=path, fill="none", stroke=color, sw=sw, fade=fade, z=z, op=op_))

    def light(self, x, y, color):
        self.lights.append(dict(x=round(x, 2), y=round(y, 2), color=color))


def accent(sc):
    """Contour de notre conteneur au trait du décor : il apparaît pendant le second recul, quand les arêtes
    d'origine (épaisseur proportionnelle) deviennent plus fines qu'un pixel."""
    X0, X1, X2, Y0, Y1 = BC.X0, BC.X1, BC.X2, BC.Y0, BC.Y1
    e = BC.EDGE / 2
    p = frame(X0 + e, Y0 + e, X2 - e, Y1 - e)
    for y in (Y0 + BC.RAIL_T - e, Y1 - BC.RAIL_B + e):
        p.addPath(line((X0, y), (X2, y)))
    for x in (X0 + BC.POST - e, X1 - BC.POST / 2 + e, X1 + BC.POST / 2 - e, X2 - BC.POST + e,
              X1 + BC.W_DOOR / 2):
        p.addPath(line((x, Y0), (x, Y1)))
    sc.stroke(p, EDGE, "accent", z="front")
    sc.accent = p


def anon_container(x, y_base, w, h, tone, fade, sc):
    """Conteneur anonyme vu de côté : aplat, contour et montants d'angle, sans logo ni texte."""
    p = frame(x, y_base - h, x + w, y_base)
    post = 0.028 * w
    for xx in (x + post, x + w - post):
        p.addPath(line((xx, y_base - h), (xx, y_base)))
    sc.fill(frame(x, y_base - h, x + w, y_base), tone, fade, stroke=None)
    sc.stroke(p, EDGE, fade)


def reflections(sc, y_sea, spans):
    """Reflets immobiles sur la mer : traits blancs à 15 %."""
    p = P()
    for x0, x1, dy in spans:
        p.addPath(line((x0, y_sea + dy), (x1, y_sea + dy)))
    sc.stroke(p, WHITE, "ground", op_=0.15, sw=SW_REFLECT)


# --------------------------------------------------------------------------
# Scène « port » : notre conteneur posé sur le quai, au premier plan
# --------------------------------------------------------------------------
W40, H40 = BC.W_SIDE, BC.H_WALL          # flanc d'un 40' (sans la face des portes), en unités du logo
Y_GROUND = BC.Y1                          # dessus du quai = base de notre conteneur
QUAY_H = 1.6 * M                          # hauteur de la face du quai au-dessus de l'eau


def port():
    sc = Scene("port")
    yg = Y_GROUND
    # Portique (grue de quai) : silhouette au trait, à droite, entière dans les deux formats
    crane(sc, 1240.0, yg, 250.0)
    # Piles de conteneurs anonymes, à gauche et derrière le nôtre : plus elles sont loin, plus elles sont petites
    # et basses (profondeur sans perspective)
    piles = [  # (gauche, échelle, colonnes, niveaux, ton)
        (-1080.0, 0.46, 1, 2, "far"),
        (-700.0, 0.62, 1, 2, "far"),
        (150.0, 0.80, 1, 2, "near"),
    ]
    for x0, f, cols, tiers, tone in piles:
        w, h = W40 * f, H40 * f
        gap = 6.0 * f
        for c in range(cols):
            for t in range(tiers):
                anon_container(x0 + c * (w + gap), yg - t * (h + gap), w, h, TONES[tone], "back", sc)
    # Quai : face verticale entre le dessus du quai et la mer, défenses, arête
    sc.fill(rect(-BIG, yg, 2 * BIG, QUAY_H), TONES["quay"], "ground")
    fend = P()
    for i in range(-6, 8):
        x = 282.0 + i * 9.0 * M
        fend.addPath(frame(x - 0.22 * M, yg + 0.25 * M, x + 0.22 * M, yg + 1.25 * M))
    sc.stroke(fend, EDGE, "ground")
    sc.stroke(line((-BIG, yg), (BIG, yg)), EDGE, "ground")
    # Mer
    y_sea = yg + QUAY_H
    sc.fill(rect(-BIG, y_sea, 2 * BIG, BIG), TONES["sea"], "ground")
    reflections(sc, y_sea, [(-560, -250, 0.55 * M), (1480, 1690, 0.9 * M), (330, 560, 1.7 * M),
                            (1560, 1960, 2.6 * M), (-1000, -820, 3.4 * M)])
    accent(sc)
    sc.horizon = yg
    return sc


def crane(sc, x, yg, u):
    """Portique à conteneurs de profil : deux jambes, flèche horizontale, chevalet et haubans. Unité u = écart
    des jambes. Un feu orange en haut du premier portique."""
    def pt(a, b):
        return (x + a * u, yg - b * u)
    p = P()
    for a in (0.0, 1.0):
        p.addPath(line(pt(a, 0), pt(a, 2.40)))             # jambes
    p.addPath(line(pt(0, 0.35), pt(1, 0.35)))               # traverse basse
    p.addPath(line(pt(0, 2.00), pt(1, 2.00)))               # poutre de portique
    p.addPath(line(pt(0, 0.35), pt(1, 2.00)))               # contreventement
    p.addPath(line(pt(1, 0.35), pt(0, 2.00)))
    p.addPath(line(pt(-2.30, 2.40), pt(1.95, 2.40)))        # flèche (vers l'eau) et contre-flèche
    p.addPath(line(pt(-2.30, 2.26), pt(1.95, 2.26)))
    for a in (-1.90, -1.35, -0.80, -0.30, 1.40):
        p.addPath(line(pt(a, 2.26), pt(a + 0.25, 2.40)))  # treillis de la flèche
    p.addPath(line(pt(0, 2.40), pt(0.42, 3.25), pt(1, 2.40)))   # chevalet
    p.addPath(line(pt(0.42, 3.25), pt(-2.30, 2.40)))        # haubans
    p.addPath(line(pt(0.42, 3.25), pt(-1.10, 2.40)))
    p.addPath(line(pt(0.42, 3.25), pt(1.95, 2.40)))
    p.addPath(frame(*pt(0.12, 2.40), *pt(0.80, 2.62)))      # salle des machines
    sc.stroke(p, EDGE, "far", sw=SW_BOLD)
    if not sc.lights:
        sc.light(*pt(0.42, 3.25 + 0.06), ORANGE)


# --------------------------------------------------------------------------
# Scène « navire » : notre conteneur sur le pont d'un porte-conteneurs, en mer
# --------------------------------------------------------------------------
HULL = {   # le cargo du début de l'animation (unités de coque : longueur 1000, y = 0 à la ligne de charge)
    "outline": [(4, 48), (0, -122), (858, -122), (872, -150), (1000, -150), (958, -20)],
    "bow": [(946, 10), (930, 34), (900, 52)],
    "house": (40, -292, 150, -122),
    "wing": ((24, -262), (166, -262)),
    "cargo": (176, -226, 832, -122),
    "bays": [258, 340, 422, 504, 586, 668, 750],
    "mark": (480, 18.0),
}
SHIP_WIDTH = 0.85      # longueur du navire / largeur d'image au plan final
SHIP_LOGO = 0.13       # largeur du logo / largeur d'image au plan final (≥ 0,12)
G = SHIP_WIDTH * BC.LOGO_W / (1000 * SHIP_LOGO)   # unités du logo par unité de coque


def ship_geometry():
    L40 = (BC.X2 - BC.X0) / G                 # notre conteneur (flanc + portes), en unités de coque
    L20 = 6.058 * M / G                       # un 20' anonyme
    gap = 4.0
    cx0, _, cx1, _ = HULL["cargo"]
    left = cx0 + (cx1 - cx0 - (L20 + gap + L40)) / 2
    hx0 = left + L20 + gap                    # bord gauche de notre conteneur sur le pont
    return L40, L20, gap, left, hx0


def ship():
    sc = Scene("ship")
    L40, L20, gap, left, hx0 = ship_geometry()
    Hc = BC.H_WALL / G

    def w(hx, hy):                            # coque → monde : le pont (y = -122) porte notre conteneur
        return (BC.X0 + (hx - hx0) * G, BC.Y1 + (hy + 122) * G)

    def poly(pts, close=False):
        p = line(*[w(*q) for q in pts])
        if close:
            p.close()
        return p

    # Coque : aplat Marine nuit, contour au trait
    hull = P()
    o, b = HULL["outline"], HULL["bow"]
    hull.moveTo(*w(*o[0]))
    for q in o[1:]:
        hull.lineTo(*w(*q))
    hull.cubicTo(*w(*b[0]), *w(*b[1]), *w(*b[2]))
    hull.close()
    sc.fill(hull, MARINE, "hull", stroke=EDGE, sw=SW_BOLD)
    # Château, aileron de passerelle, mât et hampe de proue
    x0, y0, x1, y1 = HULL["house"]
    sc.fill(poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], True), MARINE, "hull", stroke=EDGE, sw=SW_BOLD)
    det = poly(HULL["wing"])
    for wx in range(45, 136, 18):                                     # vitres de la passerelle, centrées
        det.addPath(poly([(wx, -284), (wx + 10, -284), (wx + 10, -274), (wx, -274)], True))
    det.addPath(poly([(95, -292), (95, -338)]))
    det.addPath(poly([(990, -150), (990, -176)]))
    sc.stroke(det, EDGE, "hull")
    # Rangées arrière (la pile du début, avec ses travées) puis rangée avant : conteneurs anonymes, deux tons
    cx0, cy0, cx1, cy1 = HULL["cargo"]
    sc.fill(poly([(cx0, cy0), (cx1, cy0), (cx1, cy1), (cx0, cy1)], True), TONES["far"], "back", stroke=EDGE)
    bays = P()
    for x in HULL["bays"]:
        bays.addPath(poly([(x, cy0), (x, cy1)]))
    sc.stroke(bays, EDGE, "back")
    ax, ay = w(left, -122)
    anon_container(ax, ay, L20 * G, Hc * G, TONES["near"], "back", sc)
    # Mer : la ligne de charge affleure l'eau
    _, y_wl = w(0, 0)
    sc.fill(rect(-BIG, y_wl, 2 * BIG, BIG), TONES["sea"], "ground")
    mx, mr = HULL["mark"]
    sx, sy = w(mx, 0)
    reflections(sc, y_wl, [(sx - 760, sx - 430, 0.45 * M), (sx + 1500, sx + 1820, 0.9 * M),
                           (sx - 1750, sx - 1500, 1.6 * M), (sx + 450, sx + 760, 2.3 * M)])
    # Marque de Plimsoll (blanc fin) : la barre sur l'eau, la moitié immergée vue à travers la surface
    R = mr * G
    up, dn = P(), P()
    up.moveTo(sx + R, sy)
    BC_arc(up, sx, sy, R, 0, -180)
    dn.moveTo(sx + R, sy)
    BC_arc(dn, sx, sy, R, 0, 180)
    up.addPath(line((sx - 1.45 * R, sy), (sx + 1.45 * R, sy)))
    sc.stroke(up, WHITE, "mark", sw=1.6)
    sc.stroke(dn, WHITE, "mark", op_=0.30, sw=1.6)
    accent(sc)
    sc.light(*w(95, -338 - 1.5), ORANGE)      # feu de mât
    sc.light(*w(990, -176 - 1.5), WHITE)      # feu de proue
    sc.horizon = y_wl
    sc.ship_x = (w(0, 0)[0], w(1000, 0)[0])
    return sc


def BC_arc(p, cx, cy, r, a0, a1):
    """Arc de cercle en cubiques (angles en degrés, sens trigonométrique de l'écran)."""
    n = max(1, int(math.ceil(abs(a1 - a0) / 90)))
    da = (a1 - a0) / n
    for i in range(n):
        t0, t1 = math.radians(a0 + i * da), math.radians(a0 + (i + 1) * da)
        kk = 4 / 3 * math.tan((t1 - t0) / 4)
        p0 = (cx + r * math.cos(t0), cy + r * math.sin(t0))
        p3 = (cx + r * math.cos(t1), cy + r * math.sin(t1))
        p1 = (p0[0] - kk * r * math.sin(t0), p0[1] + kk * r * math.cos(t0))
        p2 = (p3[0] + kk * r * math.sin(t1), p3[1] - kk * r * math.cos(t1))
        p.cubicTo(*p1, *p2, *p3)


# --------------------------------------------------------------------------
# Cadrages finaux, ciel, lune, étoiles (par format)
# --------------------------------------------------------------------------
LAYOUT = {   # largeur du logo / largeur d'image ; position de notre conteneur ou du navire ; horizon ; lune
    "port": {"16x9": dict(logo=0.14, ax=0.45, horizon=0.66, moon=(0.88, 0.14)),
             "1x1": dict(logo=0.15, ax=0.50, horizon=0.68, moon=(0.82, 0.14))},
    "ship": {"16x9": dict(logo=SHIP_LOGO, horizon=0.70, moon=(0.88, 0.14)),
             "1x1": dict(logo=SHIP_LOGO, horizon=0.69, moon=(0.82, 0.14))},
}


def final_camera(sc, fmt, W, H):
    L = LAYOUT[sc.name][fmt]
    s2 = L["logo"] * W / BC.LOGO_W
    if sc.name == "ship":
        mid = (sc.ship_x[0] + sc.ship_x[1]) / 2
        qx = W / 2 + (PC[0] - mid) * s2
    else:
        qx = L["ax"] * W
    qy = L["horizon"] * H + (PC[1] - sc.horizon) * s2
    return s2, (qx, qy)


def logo_framing(W, H):
    """Cadrage du logo figé (layout() dans reveal.html) : échelle k et coin (X0, Y0), au pixel entier."""
    fmt = next(f for f, wh in FORMATS.items() if wh == (W, H))
    k = LOGO_SHARE[fmt] * W / BC.LOGO_W
    return k, math.floor((W - k * BC.LOGO_W) / 2 + 0.5), math.floor((H - k * BC.LOGO_H) / 2 + 0.5)


def camera(t, W, H, s2, q2):
    """Même caméra que sceneCamera() dans reveal.html : du logo figé (8,0 s) au plan large (12,0 s), en une seule
    courbe ; l'échelle décroît de façon exponentielle, le centre de notre conteneur glisse en ligne droite."""
    k, X0, Y0 = logo_framing(W, H)
    q0 = (X0 + PC[0] * k, Y0 + PC[1] * k)
    e = IN_OUT(seg(t, TIMELINE["pull"]))
    s = k * (s2 / k) ** e
    qx, qy = q0[0] + (q2[0] - q0[0]) * e, q0[1] + (q2[1] - q0[1]) * e
    return s, qx - PC[0] * s, qy - PC[1] * s


def sky_bands(H, y_h):
    """Ciel : du haut (sky_top) à l'horizon (Marine nuit), interpolé en OKLCH puis quantifié en bandes de
    1 niveau sur 8 bits, aux limites de pixels entiers : ni tramage (qui ruinerait le GIF) ni marche visible."""
    N = 8192
    cols = [mix_oklch(TONES["sky_top"], MARINE, i / N) for i in range(N + 1)]
    runs = []
    for i, c in enumerate(cols):
        if runs and runs[-1][2] == c:
            runs[-1][1] = i
        else:
            runs.append([i, i, c])
    bands, y = [], 0
    for k_, (i0, i1, c) in enumerate(runs):
        y1 = H if k_ == len(runs) - 1 else round(y_h * (i1 + 0.5) / N)
        if y1 > y:
            bands.append([y, y1, hexc(c)])
            y = y1
    steps = [max(abs(int(a[2][j:j + 2], 16) - int(b[2][j:j + 2], 16)) for j in (1, 3, 5))
             for a, b in zip(bands, bands[1:])]
    assert max(steps) <= 1, "ciel : une marche dépasse 1 niveau"
    assert bands[-1][2] == MARINE
    return bands


def moon_path(cx, cy, d):
    """Croissant fin : disque moins un disque décalé vers le haut à gauche."""
    r = d / 2
    return op(circle(cx, cy, r), circle(cx - 0.20 * r, cy - 0.08 * r, 0.95 * r), pathops.PathOp.DIFFERENCE)


def occluder(sc, s_min):
    """Tout ce qui peut cacher une étoile, en unités du monde (traits épaissis pour la plus petite échelle)."""
    parts = []
    for el in sc.els:
        if el["fill"] != "none":
            parts.append(el["path"])
        if el["stroke"]:
            parts.append(stroke_outline(el["path"], (el["sw"] + 2.0) / s_min))
    parts.append(rect(BOX[0], BOX[1], BOX[2] - BOX[0], BOX[3] - BOX[1]))
    return union(*parts)


def frame_times(t0):
    """Instants des images (i / 60) de t0 à la fin du second recul : ceux que render.js exporte."""
    i, end = math.ceil(t0 * 60 - 1e-9), round(TIMELINE["pull"][1] * 60)
    return [k / 60 for k in range(i, end + 1)]


def light_hit(sc, t, x, y, r, W, H, s2, q2):
    """Un feu (4 px à l'écran, visible à partir de son fondu) touche-t-il le disque (x, y, r) à l'instant t ?"""
    if t < TIMELINE["fades"]["lights"][0]:
        return False
    s, tx, ty = camera(t, W, H, s2, q2)
    return any(math.hypot(lt["x"] * s + tx - x, lt["y"] * s + ty - y) < 2 + r for lt in sc.lights)


def stars(sc, fmt, W, H, s2, q2, occ, moon):
    rnd = mulberry32(STAR_SEED[sc.name] + (0 if fmt == "16x9" else 101))
    TS = TIMELINE["stars"]
    y_h = q2[1] + (sc.horizon - PC[1]) * s2
    ex0, ey0, ex1, ey1 = BC.EXCLUSION
    mcx, mcy, mr = moon
    out, tries = [], 0
    while len(out) < N_STARS:
        tries += 1
        assert tries < 200000, "impossible de placer les étoiles"
        x = 10 + rnd() * (W - 20)
        y = 10 + (rnd() ** 1.35) * (y_h - 60)          # plus denses vers le haut du ciel
        d = 1.0 + 1.5 * rnd()
        o = 0.25 + 0.45 * rnd()
        t0 = TS["start"] + TS["spread"] * rnd()
        if math.hypot(x - mcx, y - mcy) < mr + 22:
            continue
        if any(math.hypot(x - a, y - b) < 34 for a, b, *_ in out):
            continue
        # au plan final, à distance des silhouettes (28 px) et de notre conteneur (60 px) : les étoiles restent dans
        # le ciel, sans s'accumuler contre la scène ni près du logo
        s, tx, ty = camera(TIMELINE["pull"][1], W, H, s2, q2)
        X, Y = (x - tx) / s, (y - ty) / s
        bx = (60 + d / 2) / s
        if BOX[0] - bx <= X <= BOX[2] + bx and BOX[1] - bx <= Y <= BOX[3] + bx:
            continue
        m = (28 + d / 2) / s
        if any(occ.contains((X + m * math.cos(a), Y + m * math.sin(a))) for a in [k * math.pi / 8 for k in range(16)]):
            continue
        # jamais dans la zone d'exclusion du logo, ni derrière un objet ou un feu, de son apparition à la fin
        ok = True
        for t in frame_times(t0):
            s, tx, ty = camera(t, W, H, s2, q2)
            m = (d / 2 + 4) / s
            X, Y = (x - tx) / s, (y - ty) / s
            if ex0 - m <= X <= ex1 + m and ey0 - m <= Y <= ey1 + m:
                ok = False
            for ddx, ddy in ((0, 0), (m, 0), (-m, 0), (0, m), (0, -m), (.7 * m, .7 * m), (-.7 * m, .7 * m),
                             (.7 * m, -.7 * m), (-.7 * m, -.7 * m)):
                if ok and occ.contains((X + ddx, Y + ddy)):
                    ok = False
            if ok and light_hit(sc, t, x, y, d / 2 + 4, W, H, s2, q2):
                ok = False
            if not ok:
                break
        if ok:
            out.append([round(x, 2), round(y, 2), round(d, 2), round(o, 2), round(t0, 3),
                        round(t0 + TS["dur"], 3), star_pixels(round(x, 2), round(y, 2), round(d, 2))])
    return out


def star_pixels(x, y, d, n=16):
    """Disque de diamètre d centré en (x, y), réduit à la couverture exacte de chaque pixel (échantillonnage
    16 × 16). L'étoile est dessinée en carrés de 1 px alignés sur la grille : aucun lissage laissé au navigateur,
    donc des pixels identiques à chaque image (Chrome lisse les très petites formes un peu différemment selon ce
    qu'il redessine autour)."""
    r = d / 2
    px = []
    for py in range(int(math.floor(y - r)), int(math.ceil(y + r))):
        for qx in range(int(math.floor(x - r)), int(math.ceil(x + r))):
            hit = sum(1 for i in range(n) for j in range(n)
                      if (qx + (i + 0.5) / n - x) ** 2 + (py + (j + 0.5) / n - y) ** 2 <= r * r)
            if hit:
                px.append([qx, py, round(hit / (n * n), 3)])
    return px


def moon_clear(sc, W, H, s2, q2, occ, moon):
    mcx, mcy, mr = moon
    for t in frame_times(TIMELINE["fades"]["moon"][0]):
        assert not light_hit(sc, t, mcx, mcy, mr + 6, W, H, s2, q2), f"{sc.name} : un feu passe devant la lune à {t:.2f} s"
        s, tx, ty = camera(t, W, H, s2, q2)
        for a in range(0, 360, 15):
            X = (mcx + (mr + 6) * math.cos(math.radians(a)) - tx) / s
            Y = (mcy + (mr + 6) * math.sin(math.radians(a)) - ty) / s
            if occ.contains((X, Y)):
                if os.environ.get("BLS_DRAFT"):
                    print(f"  ! {sc.name} : un objet passe devant la lune à {t:.2f} s")
                    return
                raise AssertionError(f"{sc.name} : un objet passe devant la lune à {t:.2f} s")


def formats(sc):
    out = {}
    for fmt, (W, H) in FORMATS.items():
        s2, q2 = final_camera(sc, fmt, W, H)
        L = LAYOUT[sc.name][fmt]
        y_h = q2[1] + (sc.horizon - PC[1]) * s2
        d = 0.07 * H
        moon = (L["moon"][0] * W, L["moon"][1] * H, d / 2)
        occ = occluder(sc, s2)
        moon_clear(sc, W, H, s2, q2, occ, moon)
        # le contour de notre conteneur, à son épaisseur maximale dans le monde (plan final), reste hors de la zone
        # d'exclusion du logo (intersection exacte des tracés, comme build_container.py)
        ex0, ey0, ex1, ey1 = BC.EXCLUSION
        acc = stroke_outline(sc.accent, SW / s2)
        assert BC.is_empty(op(acc, rect(ex0, ey0, ex1 - ex0, ey1 - ey0), pathops.PathOp.INTERSECTION)), \
            f"{sc.name} {fmt} : le contour du conteneur entre dans la zone d'exclusion du logo"
        out[fmt] = {
            "s2": round(s2, 6), "q2": [round(q2[0], 3), round(q2[1], 3)],
            "horizon": round(y_h, 2),
            "sky": sky_bands(H, round(y_h)),
            "moon": {"d": to_d(moon_path(*moon[:2], d)), "fill": ECUME, "op": 0.85,
                     "box": [round(moon[0] - d / 2, 2), round(moon[1] - d / 2, 2), round(d, 2)]},
            "stars": stars(sc, fmt, W, H, s2, q2, occ, moon),
        }
        logo_px = BC.LOGO_W * s2
        assert logo_px >= 0.12 * W, f"{sc.name} {fmt} : logo {logo_px:.0f} px < 12 % de {W}"
    return out


def data(sc):
    return {
        "elements": [{"d": to_d(el["path"]), "fill": el["fill"], "stroke": el["stroke"] or "none", "sw": el["sw"],
                      "fade": el["fade"], "z": el["z"], "op": el["op"]} for el in sc.els],
        "lights": sc.lights,
        "horizon": round(sc.horizon, 3),
        "formats": formats(sc),
        **({"ship": [round(v, 2) for v in sc.ship_x]} if sc.name == "ship" else {}),
    }


# --------------------------------------------------------------------------
# Image fixe : plan final 16:9, mis à l'échelle 2000 × 1125
# --------------------------------------------------------------------------
def mockup(sc, d16):
    W, H = MOCKUP
    f = W / FORMATS["16x9"][0]
    s = d16["s2"] * f
    qx, qy = d16["q2"][0] * f, d16["q2"][1] * f
    tx, ty = qx - PC[0] * s, qy - PC[1] * s
    y_h = d16["horizon"] * f
    # Ciel : un dégradé SVG continu (meilleur à l'impression que des bandes), arrêts calculés en OKLCH
    stops = "".join(f'<stop offset="{i / 12:.4f}" stop-color="{hexc(mix_oklch(TONES["sky_top"], MARINE, i / 12))}"/>'
                    for i in range(13))
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
           f'aria-label="{"Conteneur Blue Line Shipping sur le quai, de nuit" if sc.name == "port" else "Conteneur Blue Line Shipping sur le pont d’un porte-conteneurs, de nuit"}">',
           f"<title>Blue Line Shipping — {'port' if sc.name == 'port' else 'navire'}, de nuit</title>",
           f'<defs><linearGradient id="sky" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="{y_h:.2f}">'
           f"{stops}</linearGradient></defs>",
           f'<rect width="{W}" height="{H}" fill="{MARINE}"/>',
           f'<rect width="{W}" height="{y_h:.2f}" fill="url(#sky)"/>']
    for x, y, dd, o, *_ in d16["stars"]:
        out.append(f'<circle cx="{x * f:.2f}" cy="{y * f:.2f}" r="{dd * f / 2:.2f}" fill="{WHITE}" fill-opacity="{o}"/>')
    mcx = d16["moon"]["box"][0] + d16["moon"]["box"][2] / 2
    mcy = d16["moon"]["box"][1] + d16["moon"]["box"][2] / 2
    out.append(f'<path fill="{ECUME}" opacity="0.85" d="{to_d(moon_path(mcx * f, mcy * f, d16["moon"]["box"][2] * f))}"/>')

    def world(els):
        g = []
        for el in els:
            if el["fill"] != "none":
                g.append(f'<path fill="{el["fill"]}"{op_attr(el)} d="{to_d(el["path"])}"/>')
            if el["stroke"]:
                g.append(f'<path fill="{el["stroke"]}"{op_attr(el)} d="{to_d(stroke_outline(el["path"], el["sw"] * f / s))}"/>')
        return "".join(g)

    tf = f'translate({tx:.3f} {ty:.3f}) scale({s:.6f})'
    logo_paths = "".join(re.findall(r"<path [^>]*/>", open(LOGO_SVG, encoding="utf-8").read()))
    cont = "".join(f'<path fill="{c}" d="{to_d(p)}"/>' for _, c, p in BC.build())
    out.append(f'<g transform="{tf}">{world([e for e in sc.els if e["z"] == "back"])}{cont}'
               f'{world([e for e in sc.els if e["z"] == "front"])}{logo_paths}</g>')
    for lt in sc.lights:
        out.append(f'<circle cx="{lt["x"] * s + tx:.2f}" cy="{lt["y"] * s + ty:.2f}" r="{2 * f:.2f}" fill="{lt["color"]}"/>')
    out.append("</svg>\n")
    path = os.path.join(MOCKUPS, f"{sc.name}-night.svg")
    os.makedirs(MOCKUPS, exist_ok=True)
    open(path, "w", encoding="utf-8").write("".join(out))
    return path


def op_attr(el):
    return f' opacity="{el["op"]}"' if el["op"] != 1 else ""


def main():
    scenes = {"port": port(), "ship": ship()}
    payload = {"timeline": TIMELINE, "tones": TONES, "colors": {"edge": EDGE, "moon": ECUME, "orange": ORANGE},
               **{name: data(sc) for name, sc in scenes.items()}}
    html = open(REVEAL, encoding="utf-8").read()
    block = "/*SCENES:BEGIN*/ const SCENES = " + json.dumps(payload, separators=(",", ":"), ensure_ascii=False) + "; /*SCENES:END*/"
    html, n = re.subn(r"/\*SCENES:BEGIN\*/.*?/\*SCENES:END\*/", lambda m: block, html, flags=re.S)
    assert n == 1, "marqueurs SCENES introuvables dans reveal.html"
    open(REVEAL, "w", encoding="utf-8").write(html)
    for name, sc in scenes.items():
        path = mockup(sc, payload[name]["formats"]["16x9"])
        msg = []
        for fmt, d in payload[name]["formats"].items():
            W = FORMATS[fmt][0]
            msg.append(f"{fmt} : logo {BC.LOGO_W * d['s2']:.0f} px ({BC.LOGO_W * d['s2'] / W * 100:.1f} %), "
                       f"{len(d['stars'])} étoiles, ciel en {len(d['sky'])} bandes")
            if name == "ship":
                sx0, sx1 = payload[name]["ship"]
                msg[-1] += f", navire {(sx1 - sx0) * d['s2'] / W * 100:.1f} % de la largeur"
        print(f"{name} : " + " ; ".join(msg) + f" → {os.path.relpath(path, BC.BRAND)}")
    print("tons : " + ", ".join(f"{k} {v}" for k, v in TONES.items()))


if __name__ == "__main__":
    main()
