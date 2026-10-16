"""Petite boîte à outils vectorielle pour les logos Blue Line Shipping.

Tout est construit en aplats (pas de traits, pas de filtres) avec skia-pathops :
les contours sont fusionnés et les superpositions de couleurs résolues, pour
des SVG propres, découpables en vinyle et sans dépendance externe.
Le texte est converti en tracés à partir des polices Google Fonts (OFL),
mis en forme par HarfBuzz (crénage, ligatures, arabe).
"""

import math
import os

import pathops
import uharfbuzz as hb
from fontTools.pens.basePen import BasePen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.environ.get("BLS_FONT_DIR", os.path.join(HERE, ".fonts"))

K = 0.5522847498307936  # approximation cubique du quart de cercle

UNION = pathops.PathOp.UNION
DIFF = pathops.PathOp.DIFFERENCE
INTER = pathops.PathOp.INTERSECTION


# --------------------------------------------------------------------------
# Géométrie (repère SVG : y vers le bas)
# --------------------------------------------------------------------------

def P():
    return pathops.Path()


def rect(x, y, w, h):
    p = P()
    p.moveTo(x, y)
    p.lineTo(x + w, y)
    p.lineTo(x + w, y + h)
    p.lineTo(x, y + h)
    p.close()
    return p


def rrect(x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    k = r * (1 - K)
    p = P()
    p.moveTo(x + r, y)
    p.lineTo(x + w - r, y)
    p.cubicTo(x + w - k, y, x + w, y + k, x + w, y + r)
    p.lineTo(x + w, y + h - r)
    p.cubicTo(x + w, y + h - k, x + w - k, y + h, x + w - r, y + h)
    p.lineTo(x + r, y + h)
    p.cubicTo(x + k, y + h, x, y + h - k, x, y + h - r)
    p.lineTo(x, y + r)
    p.cubicTo(x, y + k, x + k, y, x + r, y)
    p.close()
    return p


def _arc_segments(p, cx, cy, r, a0, a1):
    """Ajoute à p un arc (angles en degrés, sens horaire écran si a1 > a0)."""
    n = max(1, int(math.ceil(abs(a1 - a0) / 90.0 - 1e-9)))
    step = (a1 - a0) / n
    for i in range(n):
        t0 = math.radians(a0 + i * step)
        t1 = math.radians(a0 + (i + 1) * step)
        h = 4.0 / 3.0 * math.tan((t1 - t0) / 4.0)
        x0, y0 = cx + r * math.cos(t0), cy + r * math.sin(t0)
        x1, y1 = cx + r * math.cos(t1), cy + r * math.sin(t1)
        p.cubicTo(
            x0 - h * r * math.sin(t0), y0 + h * r * math.cos(t0),
            x1 + h * r * math.sin(t1), y1 - h * r * math.cos(t1),
            x1, y1,
        )


def circle(cx, cy, r):
    p = P()
    p.moveTo(cx + r, cy)
    _arc_segments(p, cx, cy, r, 0, 360)
    p.close()
    return p


def ring(cx, cy, r_out, r_in):
    return op(circle(cx, cy, r_out), circle(cx, cy, r_in), DIFF)


def annular_sector(cx, cy, r_out, r_in, a0, a1):
    """Portion d'anneau entre les angles a0 et a1 (degrés, y vers le bas)."""
    p = P()
    p.moveTo(cx + r_out * math.cos(math.radians(a0)), cy + r_out * math.sin(math.radians(a0)))
    _arc_segments(p, cx, cy, r_out, a0, a1)
    p.lineTo(cx + r_in * math.cos(math.radians(a1)), cy + r_in * math.sin(math.radians(a1)))
    _arc_segments(p, cx, cy, r_in, a1, a0)
    p.close()
    return p


def polygon(pts):
    p = P()
    p.moveTo(*pts[0])
    for pt in pts[1:]:
        p.lineTo(*pt)
    p.close()
    return p


def stroke(build, width, cap="butt", join="miter", miter=4.0):
    """Vectorise un tracé ouvert : build(p) dessine le tracé, on l'épaissit."""
    p = P()
    build(p)
    caps = {"butt": pathops.LineCap.BUTT_CAP, "round": pathops.LineCap.ROUND_CAP,
            "square": pathops.LineCap.SQUARE_CAP}
    joins = {"miter": pathops.LineJoin.MITER_JOIN, "round": pathops.LineJoin.ROUND_JOIN,
             "bevel": pathops.LineJoin.BEVEL_JOIN}
    p.stroke(width, caps[cap], joins[join], miter)
    p.convertConicsToQuads()
    return simplify(p)


def arc_to(p, cx, cy, r, a0, a1):
    _arc_segments(p, cx, cy, r, a0, a1)


def op(a, b, kind):
    return pathops.op(a, b, kind, fix_winding=True, keep_starting_points=False)


def union(*paths):
    out = P()
    for q in paths:
        if q is None:
            continue
        out = op(out, q, UNION)
    return out


def simplify(p):
    return pathops.simplify(p, fix_winding=True, keep_starting_points=False)


def xform(path, a=1, b=0, c=0, d=1, e=0, f=0):
    """Applique la matrice affine (a b c d e f) au tracé."""
    out = P()
    path.draw(TransformPen(out.getPen(), (a, b, c, d, e, f)))
    return out


def move(path, dx, dy, s=1.0):
    return xform(path, s, 0, 0, s, dx, dy)


def bounds(path):
    if not path.segments:
        return (0, 0, 0, 0)
    return path.bounds  # (xmin, ymin, xmax, ymax)


# --------------------------------------------------------------------------
# Texte → tracés
# --------------------------------------------------------------------------

class Font:
    _cache = {}

    def __new__(cls, name):
        if name not in cls._cache:
            obj = super().__new__(cls)
            obj._load(name)
            cls._cache[name] = obj
        return cls._cache[name]

    def _load(self, name):
        path = os.path.join(FONT_DIR, name + ".ttf")
        if not os.path.exists(path):
            raise SystemExit(f"Police manquante : {path} — lancer tools/fetch_fonts.sh")
        self.name = name
        self.tt = TTFont(path)
        self.upem = self.tt["head"].unitsPerEm
        self.gs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        self.hb = hb.Font(hb.Face(hb.Blob.from_file_path(path)))
        self.cap = self.tt["OS/2"].sCapHeight

    def glyph(self, char, cap_h):
        """Contour d'un seul caractère, hauteur de capitale = cap_h, base à y=0."""
        s = cap_h / self.cap
        gname = self.tt.getBestCmap()[ord(char)]
        out = P()
        self.gs[gname].draw(TransformPen(out.getPen(glyphSet=self.gs), (s, 0, 0, -s, 0, 0)))
        return simplify(out), self.gs[gname].width * s

    def glyphs(self, txt, cap_h, tracking=0.0, features=None):
        """Mise en forme HarfBuzz ; retourne ([(indice_caractère, tracé)], avance)."""
        s = cap_h / self.cap
        size = s * self.upem
        buf = hb.Buffer()
        buf.add_str(txt)
        buf.guess_segment_properties()
        hb.shape(self.hb, buf, features or {"kern": True, "liga": True})
        out = []
        x = 0.0
        n = len(buf.glyph_infos)
        for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
            g = self.order[info.codepoint]
            gp = P()
            self.gs[g].draw(TransformPen(gp.getPen(glyphSet=self.gs), (s, 0, 0, -s, x + pos.x_offset * s, -pos.y_offset * s)))
            out.append((info.cluster, gp))
            x += pos.x_advance * s
            if i < n - 1:
                x += tracking * size
        return out, x

    def text(self, txt, cap_h, tracking=0.0, features=None):
        """Retourne (tracé, avance) ; base à y=0, départ à x=0.

        cap_h    : hauteur des capitales en unités de sortie
        tracking : approche en fraction de corps (comme letter-spacing en em)
        """
        gl, x = self.glyphs(txt, cap_h, tracking, features)
        return simplify(union(*[g for _, g in gl])), x

    def size(self, cap_h):
        """Corps (em) correspondant à une hauteur de capitale."""
        return cap_h / self.cap * self.upem

    def fit(self, txt, cap_h, width):
        """Approche qui donne au texte une largeur optique exacte."""
        p, _ = self.text(txt, cap_h)
        b = bounds(p)
        n = len(txt)
        return (width - (b[2] - b[0])) / ((n - 1) * self.size(cap_h))


# --------------------------------------------------------------------------
# Export SVG
# --------------------------------------------------------------------------

def _num(v):
    v = round(v, 2)
    if v == int(v):
        return str(int(v))
    s = f"{v:.2f}".rstrip("0")
    return s.replace("0.", ".", 1) if s.startswith("0.") else s.replace("-0.", "-.", 1)


class _DPen(BasePen):
    """Stylo qui écrit un attribut d compact en coordonnées relatives."""

    def __init__(self):
        super().__init__(None)
        self.parts = []
        self.cur = (0.0, 0.0)
        self.start = (0.0, 0.0)

    def _r(self, pt):
        x, y = round(pt[0], 2), round(pt[1], 2)
        return x, y

    def _moveTo(self, pt):
        x, y = self._r(pt)
        cx, cy = self.cur
        self.parts.append("m" + _join(x - cx, y - cy))
        self.cur = self.start = (x, y)

    def _lineTo(self, pt):
        x, y = self._r(pt)
        cx, cy = self.cur
        dx, dy = x - cx, y - cy
        if abs(dy) < 1e-9 and abs(dx) < 1e-9:
            return
        if abs(dy) < 1e-9:
            self.parts.append("h" + _num(dx))
        elif abs(dx) < 1e-9:
            self.parts.append("v" + _num(dy))
        else:
            self.parts.append("l" + _join(dx, dy))
        self.cur = (x, y)

    def _curveToOne(self, p1, p2, p3):
        cx, cy = self.cur
        a, b, c = self._r(p1), self._r(p2), self._r(p3)
        self.parts.append("c" + _join(a[0] - cx, a[1] - cy, b[0] - cx, b[1] - cy, c[0] - cx, c[1] - cy))
        self.cur = c

    def _qCurveToOne(self, p1, p2):
        cx, cy = self.cur
        a, b = self._r(p1), self._r(p2)
        self.parts.append("q" + _join(a[0] - cx, a[1] - cy, b[0] - cx, b[1] - cy))
        self.cur = b

    def _closePath(self):
        self.parts.append("z")
        self.cur = self.start


def _join(*vals):
    """Concatène des nombres sans séparateur superflu (« 1-2.5.5 » est du SVG valide)."""
    out = ""
    for v in vals:
        s = _num(v)
        if out and not s.startswith("-") and not (s.startswith(".") and _ends_with_decimal(out)):
            out += " "
        out += s
    return out


def _ends_with_decimal(s):
    # « .5.5 » est valide en SVG : un deuxième point démarre un nouveau nombre
    tail = ""
    for ch in reversed(s):
        if ch.isdigit() or ch == ".":
            tail = ch + tail
        else:
            break
    return "." in tail


def to_d(path):
    path = P() if path is None else path
    pen = _DPen()
    path.draw(pen)
    return "".join(pen.parts)


def svg(layers, box, title="Blue Line Shipping", pad=0.0):
    """layers : liste de (couleur, tracé) peints dans l'ordre ; box = (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    x0 -= pad
    y0 -= pad
    x1 += pad
    y1 += pad
    w, h = x1 - x0, y1 - y0
    body = []
    for color, path in layers:
        if path is None or not path.segments:
            continue
        p = move(path, -x0, -y0)
        body.append(f'<path fill="{color}" d="{to_d(p)}"/>')
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_num(w)} {_num(h)}" '
        f'width="{_num(w)}" height="{_num(h)}" role="img" aria-label="{title}">'
        f"<title>{title}</title>" + "".join(body) + "</svg>\n"
    )


def flatten(layers):
    """Résout les superpositions : chaque couche est retirée de celles du dessous.

    Le résultat est un jeu d'aplats juxtaposés, sans zones cachées (propre pour
    l'impression, la sérigraphie et la découpe vinyle).
    """
    out = []
    for i, (role, path) in enumerate(layers):
        above = union(*[p for _, p in layers[i + 1:]])
        out.append((role, op(path, above, DIFF) if above.segments else path))
    return out


def all_bounds(paths):
    bs = [bounds(p) for p in paths if p is not None and p.segments]
    return (min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs))
