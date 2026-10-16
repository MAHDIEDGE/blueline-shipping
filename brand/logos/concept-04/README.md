# Concept 04 — Pont

> Deux ports, un arc : la trajectoire qui relie la Chine à l'Algérie.

<p>
  <img src="logo-horizontal.svg" alt="Blue Line Shipping, logo horizontal" height="72">
  &nbsp;&nbsp;
  <img src="icon.svg" alt="Icône" height="72">
</p>

## Intention

1. Deux ports reliés par un arc tendu : l'anneau est le départ (Chine, à l'est), le point plein l'arrivée (Algérie, à l'ouest).
2. L'arc se lit d'est en ouest comme sur une carte, et de droite à gauche comme en arabe : il parle aux deux rives.
3. C'est un signe abstrait et calme qui dit « nous relions », sans pictogramme ni cliché maritime.

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
| Dominante | Bleu Profond | `#0B2C66` | 11, 44, 102 | 13,4:1 sur blanc |
| Accent | Vermillon | `#E4412B` | 228, 65, 43 | 4,1:1 sur blanc · 3,2:1 sur la dominante |
| Accent sur fond sombre | Vermillon clair | `#FF5C45` | 255, 92, 69 | 5,7:1 sur Nuit |
| Fond sombre | Nuit | `#08193A` | 8, 25, 58 | 17,3:1 avec le blanc |
| Fond clair | Sable | `#F6F3EE` | 246, 243, 238 | papier, écrans, documents |

**Pourquoi cet accent ?** Le rouge est la seule couleur commune aux drapeaux chinois et algérien. Posé sur le point d'arrivée, le vermillon devient le pont entre les deux pays et marque la destination : l'Algérie, le client. Il reste un point de couleur, jamais une surface, pour garder le sérieux du bleu.

Le logo n'utilise que deux couleurs, en aplat : il s'imprime en deux tons directs, et en un seul avec les versions
mono.

## Typographie

**Sora** (SemiBold 600 pour BLUE LINE, Regular 400 pour SHIPPING), via Google Fonts, sous licence SIL Open Font License 1.1 (usage commercial
libre, y compris dans l'ERP et sur le web).

Sora est une géométrique contemporaine, large et ouverte, avec des courbes qui répondent à l'arc du symbole. Son SemiBold reste dense sans être massif ; le Regular espacé assure SHIPPING en petite taille.

Dans les fichiers SVG, le texte est déjà converti en tracés : la police n'est nécessaire que pour composer
d'autres textes (site, documents, ERP).

## Zone d'exclusion

Unité **x = la hauteur de l'arc** (de la base des points au sommet). Laisser 1 x de chaque côté du logo. Aucun texte, aucun bord de support ni aucun autre logo ne doit entrer dans cette zone.
Pour l'icône, la tuile elle-même fait office de zone de protection : laisser au moins 1/8 de sa largeur autour.

## Taille minimale

| Version | Écran | Impression |
|---|---|---|
| Horizontale | 150 px de large | 45 mm de large |
| Verticale | 100 px de large | 30 mm de large |
| Icône | 16 px (favicon), testée nette à 24 px | 6 mm |

Ces minimums garantissent une capitale de SHIPPING d'au moins 5 px à l'écran et 1,5 mm à l'impression. En dessous,
utiliser l'icône seule.

Pas de taille maximale : les tracés vectoriels restent nets sur un conteneur de 40 pieds (12 m) ou une remorque.

## À éviter

- Inverser le sens (le point plein vermillon est toujours l'arrivée, à gauche).
- Remplir l'anneau de départ ou ajouter d'autres points ou étapes sur l'arc.
- Déformer, incliner, ajouter une ombre, un contour, un dégradé ou un effet.
- Recomposer le nom dans une autre police ou changer la position du symbole.
