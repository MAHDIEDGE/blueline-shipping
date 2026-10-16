# Blue Line Shipping — Identité visuelle

Exploration de logo pour Blue Line Shipping SARL, logistique maritime Chine → Algérie (transport conteneurisé,
transit, dédouanement).

**Pour voir les concepts : ouvrir [`index.html`](index.html) dans un navigateur.** La page est autonome (HTML + CSS,
aucune dépendance) et montre chaque variante sur fond clair et sur fond sombre, en petite taille (16, 24 et 48 px) et en
situation : en-tête de site, carte de visite, flanc de conteneur.

## Les cinq concepts

| | Concept | Idée | Accent | Typographie |
|---|---|---|---|---|
| <img src="logos/concept-01/icon.svg" width="40" alt=""> | [01 · Horizon](logos/concept-01/) | Monogramme B + L : une seule hampe, le pied du L file en ligne d'horizon | Cyan Horizon `#139FDB` | Manrope |
| <img src="logos/concept-02/icon.svg" width="40" alt=""> | [02 · Ondulation](logos/concept-02/) | Un conteneur réduit à ses lignes de tôle ondulée, posé sur la route | Jaune Conteneur `#F2A007` | Space Grotesk |
| <img src="logos/concept-03/icon.svg" width="40" alt=""> | [03 · La Ligne](logos/concept-03/) | Logotype pur : le L de LINE descend et souligne le mot | Bleu Électrique `#2563EB` | Outfit |
| <img src="logos/concept-04/icon.svg" width="40" alt=""> | [04 · Pont](logos/concept-04/) | Deux ports reliés par un arc, de la Chine à l'Algérie | Vermillon `#E4412B` | Sora |
| <img src="logos/concept-05/icon.svg" width="40" alt=""> | [05 · Ligne de charge](logos/concept-05/) | Le disque de Plimsoll, marque de sécurité maritime, traversé par la ligne | Orange International `#FF5A1F` | Readex Pro (latin + arabe) |

**Recommandation : concept 05, Ligne de charge.** L'argumentaire et les itérations proposées figurent en bas de
`index.html`.

## Arborescence

```
brand/
├── index.html                 page de présentation (générée)
├── logos/
│   └── concept-0X/
│       ├── logo-horizontal.svg          symbole + nom côte à côte
│       ├── logo-vertical.svg            symbole au-dessus du nom
│       ├── icon.svg                     symbole seul, tuile carrée 512 × 512
│       ├── logo-mono-black.svg          une couleur, noir
│       ├── logo-mono-white.svg          une couleur, blanc
│       ├── logo-horizontal-reverse.svg  couleurs pour fond sombre
│       ├── logo-vertical-reverse.svg    couleurs pour fond sombre
│       └── README.md                    palette, typographie, intention, zones d'exclusion, tailles minimales
└── tools/                     générateur (source de vérité des logos)
    ├── blsvg.py               géométrie, texte → tracés, export SVG
    ├── symbols.py             construction des symboles
    ├── concepts.py            palettes, typographies, mises en page, textes des README
    ├── build_logos.py         génère logos/
    ├── build_index.py         génère index.html
    ├── fetch_fonts.sh         télécharge les polices Google Fonts (OFL)
    └── requirements.txt
```

## Principes des fichiers

- **Vectoriel pur** : uniquement des `<path>` en aplat, sans texte vivant, filtre, image, dégradé ni ressource
  externe. Le texte est converti en tracés à partir des polices Google Fonts, avec la mise en forme et le crénage de
  HarfBuzz.
- **Superpositions résolues** : chaque couleur est découpée de celles qui la recouvrent. Les fichiers passent tels
  quels en découpe vinyle, en sérigraphie ou en pochoir.
- **viewBox ajusté** au dessin, en unités cohérentes. L'icône est un carré de 512 × 512 avec des coins arrondis de
  rayon 104.
- **Deux couleurs maximum** par logo, plus les versions mono.

## Régénérer

```sh
cd brand/tools
pip install -r requirements.txt   # fonttools, uharfbuzz, skia-pathops
./fetch_fonts.sh                  # polices dans tools/.fonts/ (ignoré par git)
python3 build_logos.py            # logos/ + README de chaque concept
python3 build_index.py            # index.html
```

Toute modification de forme, de couleur ou de mise en page se fait dans `tools/`, jamais à la main dans les SVG.

## Licences des polices

Manrope, Space Grotesk, Outfit, Sora et Readex Pro sont distribuées par Google Fonts sous licence
[SIL Open Font License 1.1](https://openfontlicense.org) : usage commercial libre (impression, web, application,
ERP), redistribution autorisée avec la licence.
