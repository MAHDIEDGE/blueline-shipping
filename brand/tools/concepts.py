"""Définition des 5 concepts : symbole, mot-symbole, palette, typographie, texte du README."""

import math

from blsvg import Font, bounds, move, rect, union, xform
from symbols import c01_horizon, c02_container, c04_bridge, c05_loadline


# --------------------------------------------------------------------------
# Outils
# --------------------------------------------------------------------------

def _lum(hex_):
    rgb = [int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    la, lb = sorted([_lum(a), _lum(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


def ratio(a, b):
    """Contraste WCAG formaté à la française : « 4,5:1 »."""
    return f"{contrast(a, b):.1f}".replace(".", ",") + ":1"


def rgb(hex_):
    return ", ".join(str(int(hex_[i:i + 2], 16)) for i in (1, 3, 5))


def fit_layers(layers, x, y, s):
    return {k: xform(v, s, 0, 0, s, x, y) for k, v in layers.items()}


# --------------------------------------------------------------------------
# Base commune
# --------------------------------------------------------------------------

class Concept:
    num = "00"
    slug = ""
    name = ""
    tagline = ""
    font_main = font_sec = ""
    family = ""
    weights = ""
    cap1, cap2, lead = 0.36, 0.16, 0.15   # en fraction de la hauteur du symbole
    track1, track2 = 0.0, 0.30            # approche, en fraction de corps
    h_sym = 1.0                            # hauteur du symbole dans l'horizontal
    h_gap, h_offset, h_align = 0.32, 0.0, "center"
    v_gap, v_scale, v_shift = 0.30, 0.95, 0.0
    palette = {}
    names = {}
    intention = []
    accent_why = ""
    type_why = ""
    clear = ""
    dont = []

    def ship_cap(self, vertical=False):
        """Hauteur de capitale de SHIPPING dans les fichiers (unités SVG)."""
        return self.cap2 * 100 * (self.v_scale if vertical else 1.0)

    @property
    def dir(self):
        return f"concept-{self.num}"

    # -- mot-symbole standard : BLUE LINE sur SHIPPING, justifiés --------
    def wordmark(self, S, align="left"):
        f1, f2 = Font(self.font_main), Font(self.font_sec)
        c1, c2 = self.cap1 * S, self.cap2 * S
        p1, _ = f1.text("BLUE LINE", c1, self.track1)
        b1 = bounds(p1)
        p1 = move(p1, -b1[0], c1)
        w1 = b1[2] - b1[0]
        p2, _ = f2.text("SHIPPING", c2, self.track2)
        b2 = bounds(p2)
        x2 = -b2[0] + ((w1 - (b2[2] - b2[0])) / 2 if align == "center" else 0)
        p2 = move(p2, x2, c1 + self.lead * S + c2)
        return {"t": p1, "s": p2}

    # -- README ------------------------------------------------------------
    def readme(self, meta):
        p = self.palette
        night, white = p["night"], "#FFFFFF"
        rows = [
            ("Dominante", self.names["primary"], p["primary"], f"{ratio(p['primary'], white)} sur blanc"),
            ("Accent", self.names["accent"], p["accent"], f"{ratio(p['accent'], white)} sur blanc · {ratio(p['accent'], p['primary'])} sur la dominante"),
            ("Accent sur fond sombre", self.names["accent_dark"], p["accent_dark"], f"{ratio(p['accent_dark'], night)} sur {self.names['night']}"),
            ("Fond sombre", self.names["night"], night, f"{ratio(white, night)} avec le blanc"),
            ("Fond clair", self.names["paper"], p["paper"], "papier, écrans, documents"),
        ]
        if "night2" in p:
            rows.insert(4, ("Fond sombre secondaire", self.names["night2"], p["night2"],
                            f"{ratio(white, p['night2'])} avec le blanc · {ratio(p['accent_dark'], p['night2'])} avec l'accent"))
        table = "\n".join(f"| {r} | {n} | `{h}` | {rgb(h)} | {c} |" for r, n, h, c in rows)
        # règle : la capitale de SHIPPING ne descend pas sous 5 px à l'écran, 1,5 mm imprimée
        hmin_px = int(math.ceil(meta["h_w"] * 5 / meta["h_ship"] / 10.0) * 10)
        vmin_px = int(math.ceil(meta["v_w"] * 5 / meta["v_ship"] / 10.0) * 10)
        hmin_mm = int(math.ceil(meta["h_w"] * 1.5 / meta["h_ship"] / 5.0) * 5)
        vmin_mm = int(math.ceil(meta["v_w"] * 1.5 / meta["v_ship"] / 5.0) * 5)
        intention = "\n".join(f"{i}. {t}" for i, t in enumerate(self.intention, 1))
        dont = "\n".join(f"- {d}" for d in self.dont)
        note = f"\n{self.palette_note}\n" if getattr(self, "palette_note", "") else ""
        return f"""# Concept {self.num} — {self.name}

> {self.tagline}

<p>
  <img src="logo-horizontal.svg" alt="Blue Line Shipping, logo horizontal" height="72">
  &nbsp;&nbsp;
  <img src="icon.svg" alt="Icône" height="72">
</p>

## Intention

{intention}

## Fichiers

| Fichier | Usage |
|---|---|
| `logo-horizontal.svg` | Version principale : en-têtes, documents, signatures |
| `logo-vertical.svg` | Formats carrés ou hauts : flancs de camion, kakémonos, réseaux sociaux |
| `icon.svg` | Symbole seul sur tuile carrée : favicon, avatar, application |
| `logo-mono-black.svg` | Une couleur : tampons, fax, gravure, sérigraphie, documents douaniers |
| `logo-mono-white.svg` | Une couleur en réserve : sur photo, sur le bleu, sur la tôle d'un conteneur |
| `logo-horizontal-reverse.svg`, `logo-vertical-reverse.svg` | Couleur sur fond sombre (blanc + accent éclairci) |

Tous les fichiers sont des aplats vectoriels purs : aucun texte vivant, aucun filtre, aucune image, aucune
dépendance externe. Les superpositions de couleur sont résolues, donc un fichier passe tel quel en découpe vinyle
ou en sérigraphie.

## Palette

| Rôle | Nom | Hex | RVB | Contraste |
|---|---|---|---|---|
{table}

**Pourquoi cet accent ?** {self.accent_why}
{note}
Le logo n'utilise que deux couleurs, en aplat : il s'imprime en deux tons directs, et en un seul avec les versions
mono.

## Typographie

**{self.family}** ({self.weights}), via Google Fonts, sous licence SIL Open Font License 1.1 (usage commercial
libre, y compris dans l'ERP et sur le web).

{self.type_why}

Dans les fichiers SVG, le texte est déjà converti en tracés : la police n'est nécessaire que pour composer
d'autres textes (site, documents, ERP).

## Zone d'exclusion

{self.clear} Aucun texte, aucun bord de support ni aucun autre logo ne doit entrer dans cette zone.
Pour l'icône, la tuile elle-même fait office de zone de protection : laisser au moins 1/8 de sa largeur autour.

## Taille minimale

| Version | Écran | Impression |
|---|---|---|
| Horizontale | {hmin_px} px de large | {hmin_mm} mm de large |
| Verticale | {vmin_px} px de large | {vmin_mm} mm de large |
| Icône | 16 px (favicon), testée nette à 24 px | 6 mm |

Ces minimums garantissent une capitale de SHIPPING d'au moins 5 px à l'écran et 1,5 mm à l'impression. En dessous,
utiliser l'icône seule.

Pas de taille maximale : les tracés vectoriels restent nets sur un conteneur de 40 pieds (12 m) ou une remorque.

## À éviter

{dont}
- Déformer, incliner, ajouter une ombre, un contour, un dégradé ou un effet.
- Recomposer le nom dans une autre police ou changer la position du symbole.
"""


# --------------------------------------------------------------------------
# 01 · Horizon
# --------------------------------------------------------------------------

class C01(Concept):
    num = "01"
    name = "Horizon"
    tagline = "Monogramme B + L : une seule hampe, et le pied du L qui file en ligne d'horizon."
    font_main, font_sec = "Manrope-800", "Manrope-500"
    family, weights = "Manrope", "ExtraBold 800 pour BLUE LINE, Medium 500 pour SHIPPING"
    h_gap, h_align = 0.30, "bottom"
    palette = {"primary": "#0A2A6B", "accent": "#139FDB", "accent_dark": "#33C2F5",
               "night": "#061638", "paper": "#F3F6FB"}
    names = {"primary": "Bleu Nuit", "accent": "Cyan Horizon", "accent_dark": "Cyan Horizon clair",
             "night": "Nuit", "paper": "Brume"}
    intention = [
        "Le B et le L partagent une seule hampe : la colonne vertébrale de l'entreprise, lisible comme un monogramme « BL ».",
        "Le pied du L dépasse les panses du B et devient la ligne d'horizon, la route vers laquelle tout avance.",
        "La coupe en pochoir entre hampe et panses reprend le marquage des conteneurs : un signe industriel, fait pour être peint.",
    ]
    accent_why = ("Le cyan est la lumière de l'horizon marin. De la même famille que le bleu, il garde une identité "
                  "sobre et sérieuse, mais il est assez lumineux pour ressortir sur fond sombre, sur la tôle d'un "
                  "conteneur ou sur un écran. Il ne sert qu'à la ligne : c'est elle qu'on retient.")
    type_why = ("Manrope est une grotesque géométrique aux formes ouvertes et aux terminaisons nettes. En ExtraBold, "
                "elle a la densité du monogramme ; en Medium espacé, SHIPPING reste lisible en petit. Ses chiffres "
                "sont clairs pour les références de dossiers et de conteneurs.")
    clear = "Unité **x = la moitié de la hauteur du symbole** (environ la hauteur de la panse haute du B). Laisser 1 x de chaque côté du logo."
    dont = ["Raccourcir la ligne d'horizon au ras du B : c'est elle qui porte le nom « Line ».",
            "Refermer la coupe pochoir entre la hampe et les panses."]

    def symbol(self, vertical=False):
        return c01_horizon()

    def icon_symbol(self, size):
        s = size * 0.44 / 100
        x0, y0 = size * 0.25, (size - 100 * s) / 2 + size * 0.01
        sym = c01_horizon(t=18, gap=8, reach=(size - x0) / s + 20)
        return fit_layers(sym, x0, y0, s)


# --------------------------------------------------------------------------
# 02 · Ondulation
# --------------------------------------------------------------------------

class C02(Concept):
    num = "02"
    name = "Ondulation"
    tagline = "Un conteneur réduit à un bloc et à ses lignes de tôle ondulée, posé sur la route."
    font_main, font_sec = "SpaceGrotesk-700", "SpaceGrotesk-500"
    family, weights = "Space Grotesk", "Bold 700 pour BLUE LINE, Medium 500 pour SHIPPING"
    h_gap = 0.26
    palette = {"primary": "#0B2A5C", "accent": "#F2A007", "accent_dark": "#FFB627",
               "night": "#081A3A", "paper": "#F5F3EE"}
    names = {"primary": "Bleu Marine", "accent": "Jaune Conteneur", "accent_dark": "Jaune Conteneur clair",
             "night": "Nuit Portuaire", "paper": "Quai"}
    intention = [
        "Le conteneur est l'unité de base du métier : ici, un bloc et sept fentes, la tôle ondulée dessinée en lignes négatives.",
        "Il est posé sur une ligne jaune qui le dépasse vers l'avant : la route maritime, le transit, la livraison.",
        "Le sens est immédiat pour un importateur ou un transitaire, même à 24 px, sans tomber dans l'illustration.",
    ]
    accent_why = ("Le jaune ambré est la couleur de la signalisation portuaire, des portiques et de nombreux "
                  "conteneurs. Opposé au bleu marine sur le cercle chromatique, il donne le contraste maximal entre "
                  "les deux teintes et reste visible de loin sur un camion. Sur fond blanc, il ne porte jamais de texte, "
                  "seulement la ligne.")
    type_why = ("Space Grotesk est une grotesque au caractère technique, héritée d'une monospace. Elle évoque la "
                "logistique et l'ingénierie sans froideur, et ses chiffres sont très lisibles. C'est un atout pour "
                "l'ERP : numéros de BL, de conteneurs (ISO 6346), de DAU.")
    clear = "Unité **x = la hauteur du conteneur divisée par deux**. Laisser 1 x de chaque côté du logo."
    dont = ["Ajouter des fentes ou du détail au conteneur : sept lignes suffisent, et cinq dans l'icône.",
            "Détacher la route du conteneur ou la placer au-dessus."]

    def symbol(self, vertical=False):
        return c02_container()

    def icon_symbol(self, size):
        sym = c02_container(W=140, H=66, n=5, slit=9, inset=13, gap=10, rail=13, ext=400)
        s = size * 0.60 / 140
        h = (66 + 10 + 13) * s
        return fit_layers(sym, (size - 140 * s) / 2, (size - h) / 2, s)


# --------------------------------------------------------------------------
# 03 · La Ligne (logotype)
# --------------------------------------------------------------------------

class C03(Concept):
    num = "03"
    name = "La Ligne"
    tagline = "Logotype pur : le L de LINE descend sous la ligne de base et souligne le mot."
    font_main, font_sec = "Outfit-600", "Outfit-400"
    family, weights = "Outfit", "SemiBold 600 pour BLUE LINE, Regular 400 pour SHIPPING"
    logotype = True
    v_gap, v_scale = 0.30, 0.62
    palette = {"primary": "#0A1F4F", "accent": "#2563EB", "accent_dark": "#5B8CFF",
               "night": "#050E26", "paper": "#F4F6FA"}
    names = {"primary": "Bleu Encre", "accent": "Bleu Électrique", "accent_dark": "Bleu Électrique clair",
             "night": "Nuit", "paper": "Papier"}
    intention = [
        "Pas de symbole ajouté : la marque, c'est le nom. Le L de LINE descend sous la ligne de base et file sous « INE ».",
        "La lettre devient la ligne, et la ligne souligne la promesse. SHIPPING vient se ranger à sa hauteur, sous BLUE.",
        "Le monogramme BL de l'icône reprend le même L : un seul geste typographique, reconnaissable partout.",
    ]
    accent_why = ("C'est « Blue Line » au sens propre : le nom en bleu encre, la ligne en bleu électrique. On obtient "
                  "une identité presque monochrome, très B2B, où l'accent ne crie pas : il signale. Le bleu électrique "
                  "est la couleur de l'écran et du signal, cohérente avec un ERP et des outils numériques.")
    type_why = ("Outfit est une géométrique pure, aux capitales rondes et régulières, très lisibles à distance. "
                "Sa chasse moyenne garde le logotype compact malgré ses neuf lettres. Le L est redessiné à partir "
                "des épaisseurs de la police (fût et barre) pour rester dans la famille.")
    clear = "Unité **x = la hauteur des capitales de BLUE LINE**. Laisser 0,5 x au-dessus, à gauche et à droite, et 0,5 x sous la ligne."
    dont = ["Remettre un L standard ou détacher la ligne du L.",
            "Prolonger la ligne au-delà du E final ou la colorer autrement que le L."]

    L_DROP = 0.25   # écart sous la ligne de base, en fraction de capitale
    SHIP = 0.27     # capitale de SHIPPING, en fraction de capitale
    SCALE = 0.62    # échelle du logotype par rapport à la hauteur du symbole

    def ship_cap(self, vertical=False):
        return self.SHIP * 100 * self.SCALE * (self.v_scale if vertical else 1.0)

    def _metrics(self, C):
        f = Font(self.font_main)
        ib = bounds(f.glyph("I", C)[0])
        return ib[2] - ib[0], 0.172 * C   # fût, barre (mesurés sur Outfit 600)

    def _custom_L(self, x, C, x_end):
        stem, foot = self._metrics(C)
        d = self.L_DROP * C
        return union(rect(x, -C, stem, C + d + foot), rect(x, d, x_end - x, foot))

    def wordmark(self, S, align="left"):
        """Le logotype complet (utilisé seul en horizontal, sous le monogramme en vertical)."""
        C = 100.0
        f, f2 = Font(self.font_main), Font(self.font_sec)
        gl, _ = f.glyphs("BLUE LINE", C)
        parts = {cl: p for cl, p in gl}
        blue = union(*[parts[i] for i in range(4)])
        ine = union(*[parts[i] for i in (6, 7, 8)])
        Lx = bounds(parts[5])[0]
        x_end = bounds(parts[8])[2]
        L = self._custom_L(Lx, C, x_end)
        stem, foot = self._metrics(C)
        bb = bounds(blue)
        cap2 = self.SHIP * C
        tr = f2.fit("SHIPPING", cap2, bb[2] - bb[0])
        sp, _ = f2.text("SHIPPING", cap2, tr)
        sb = bounds(sp)
        y = self.L_DROP * C + foot / 2 + cap2 / 2
        sp = move(sp, bb[0] - sb[0], y)
        k = S / 100.0 * self.SCALE
        return {k_: xform(v, k, 0, 0, k, 0, 0) for k_, v in {"t": union(blue, ine), "a": L, "s": sp}.items()}

    def monogram(self, C, foot_len):
        f = Font(self.font_main)
        gl, _ = f.glyphs("BL", C)
        parts = {cl: p for cl, p in gl}
        Lx = bounds(parts[1])[0]
        return {"p": parts[0], "a": self._custom_L(Lx, C, Lx + foot_len)}

    def symbol(self, vertical=False):
        return self.monogram(100.0, 150.0)

    def icon_symbol(self, size):
        C = 100.0
        s = size * 0.40 / C
        m = self.monogram(C, (size / s) * 1.2)
        b = bounds(m["p"])
        stem, foot = self._metrics(C)
        total_h = C * (1 + self.L_DROP) + foot
        x0 = size * 0.20 - b[0] * s
        y0 = (size - total_h * s) / 2 + C * s
        return fit_layers(m, x0, y0, s)


# --------------------------------------------------------------------------
# 04 · Pont
# --------------------------------------------------------------------------

class C04(Concept):
    num = "04"
    name = "Pont"
    tagline = "Deux ports, un arc : la trajectoire qui relie la Chine à l'Algérie."
    font_main, font_sec = "Sora-600", "Sora-400"
    family, weights = "Sora", "SemiBold 600 pour BLUE LINE, Regular 400 pour SHIPPING"
    h_sym = 0.62
    h_gap = 0.24
    v_gap, v_scale = 0.32, 1.0
    palette = {"primary": "#0B2C66", "accent": "#E4412B", "accent_dark": "#FF5C45",
               "night": "#08193A", "paper": "#F6F3EE"}
    names = {"primary": "Bleu Profond", "accent": "Vermillon", "accent_dark": "Vermillon clair",
             "night": "Nuit", "paper": "Sable"}
    intention = [
        "Deux ports reliés par un arc tendu : l'anneau est le départ (Chine, à l'est), le point plein l'arrivée (Algérie, à l'ouest).",
        "L'arc se lit d'est en ouest comme sur une carte, et de droite à gauche comme en arabe : il parle aux deux rives.",
        "C'est un signe abstrait et calme qui dit « nous relions », sans pictogramme ni cliché maritime.",
    ]
    accent_why = ("Le rouge est la seule couleur commune aux drapeaux chinois et algérien. Posé sur le point d'arrivée, "
                  "le vermillon devient le pont entre les deux pays et marque la destination : l'Algérie, le client. "
                  "Il reste un point de couleur, jamais une surface, pour garder le sérieux du bleu.")
    type_why = ("Sora est une géométrique contemporaine, large et ouverte, avec des courbes qui répondent à l'arc "
                "du symbole. Son SemiBold reste dense sans être massif ; le Regular espacé assure SHIPPING en "
                "petite taille.")
    clear = "Unité **x = la hauteur de l'arc** (de la base des points au sommet). Laisser 1 x de chaque côté du logo."
    dont = ["Inverser le sens (le point plein vermillon est toujours l'arrivée, à gauche).",
            "Remplir l'anneau de départ ou ajouter d'autres points ou étapes sur l'arc."]

    def symbol(self, vertical=False):
        return c04_bridge()

    def icon_symbol(self, size):
        sym = c04_bridge(R=64, span=150, t=15, dot=15, gap=7, ring_in=7)
        b = bounds(union(*sym.values()))
        s = size * 0.70 / (b[2] - b[0])
        w, h = (b[2] - b[0]) * s, (b[3] - b[1]) * s
        return fit_layers(sym, (size - w) / 2 - b[0] * s, (size - h) / 2 - b[1] * s, s)


# --------------------------------------------------------------------------
# 05 · Ligne de charge
# --------------------------------------------------------------------------

class C05(Concept):
    num = "05"
    name = "Ligne de charge"
    tagline = "Le disque de Plimsoll, la marque de sécurité de chaque navire marchand, traversé par la ligne."
    font_main, font_sec = "ReadexPro-600", "ReadexPro-400"
    family, weights = "Readex Pro", "SemiBold 600 pour BLUE LINE, Regular 400 pour SHIPPING"
    h_gap = 0.26
    palette = {"primary": "#0B2F6E", "accent": "#FF5A1F", "accent_dark": "#FF6A33",
               "night": "#071A3E", "night2": "#0A1A3A", "paper": "#F3F5F9"}
    names = {"primary": "Bleu Coque", "accent": "Orange International", "accent_dark": "Orange International clair",
             "night": "Nuit", "night2": "Marine nuit", "paper": "Écume"}
    palette_note = ("**Marine nuit** (`#0A1A3A`) est le fond sombre secondaire. C'est le bleu nuit profond dans lequel se "
                    "fige la version sombre de l'animation, et la teinte de la tôle des conteneurs. Le Bleu Coque reste la "
                    "couleur des lettres et de l'anneau en version claire.\n\n"
                    "**Sur un conteneur** (voir `brand/mockups/container-dark.svg`) :\n\n"
                    "- la tôle, les portes, les montants et les rails sont en Marine nuit `#0A1A3A` ;\n"
                    "- la tôle ondulée, les arêtes et les barres de verrouillage sont en `#1F2C45`, soit Marine nuit plus "
                    "7 points de luminance OKLCH avec la chroma × 0,75 (contraste 1,23:1 : visible mais discret) ;\n"
                    "- le logo horizontal est en blanc et en orange `#FF6A33`, centré sur le flanc.\n\n"
                    "La largeur du logo représente 42,5 % de la longueur de la paroi, soit 5,18 m sur un 40'. C'est le "
                    "maximum compatible avec la zone d'exclusion, 1 x au-dessus et au-dessous du logo, entre les rails.")
    intention = [
        "Le disque de Plimsoll est peint sur la coque de chaque navire marchand : c'est la ligne de charge à ne jamais dépasser.",
        "Ici, l'anneau est coupé par la ligne, qui en sort vers l'avant. Le signe dit sécurité, conformité, précision : le cœur du transit et du dédouanement.",
        "C'est un signe de métier, que reconnaissent les professionnels du maritime, et sans aucun cliché (ni ancre, ni vague).",
    ]
    accent_why = ("L'orange international est la couleur de sécurité de la marine : canots, engins de sauvetage, "
                  "marquages. Il porte la ligne de charge, donc le message de sécurité. Complémentaire du bleu "
                  "coque, il offre le contraste le plus fort de la palette et reste lisible en grand format "
                  "comme en favicon.")
    type_why = ("Readex Pro est une géométrique issue de Lexend, une famille conçue pour la lisibilité. Elle couvre "
                "**le latin et l'arabe dans la même famille**. Factures, documents douaniers, signalétique et "
                "interfaces de l'ERP peuvent donc être bilingues français-arabe avec une seule voix "
                "typographique.")
    clear = "Unité **x = le rayon de l'anneau**. Laisser 1 x de chaque côté du logo."
    dont = ["Prolonger la ligne des deux côtés de l'anneau : on retomberait sur une cocarde de transport urbain.",
            "Refermer l'anneau derrière la ligne ou épaissir la ligne au-delà du trait de l'anneau."]

    def symbol(self, vertical=False):
        return c05_loadline()

    def icon_symbol(self, size):
        R = size * 0.235
        s = R / 44.0
        sym = c05_loadline(right=(size / s) / 44 + 1)
        return fit_layers(sym, size * 0.40, size * 0.5, s)


CONCEPTS = [C01(), C02(), C03(), C04(), C05()]
