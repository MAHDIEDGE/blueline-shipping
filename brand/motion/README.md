# Motion : révélation du logo (concept 05, Ligne de charge)

<img src="reveal-dark.gif" alt="Animation : la marque de ligne de charge d'un cargo devient le logo Blue Line Shipping" width="480">

En 8 secondes, l'animation raconte l'histoire du symbole. Sur la coque d'un cargo, la marque de Plimsoll indique la
ligne de charge que le navire ne doit jamais dépasser. Elle devient le logo Blue Line Shipping. La ligne orange ne
change jamais : c'est le fil conducteur, le soleil à l'horizon.

Il existe deux versions et trois fins alternatives, toutes en version sombre :

| Version | Fond | Coque, anneau, texte | Ligne | Dernière image |
|---|---|---|---|---|
| **Claire** (par défaut) | Écume `#F3F5F9`, constant | Bleu Coque `#0B2F6E` | `#FF5A1F` | `logo-horizontal.svg` sur Écume, au pixel près |
| **Sombre** (`?theme=dark`) | Bleu Coque `#0B2F6E` → Marine nuit `#0A1A3A` | Blanc | `#FF6A33` | `logo-horizontal-reverse.svg` sur Marine nuit, au pixel près |
| **Fin conteneur** (`?theme=dark&ending=container`) | version sombre, puis la caméra recule | Blanc | `#FF6A33` | le logo peint sur le flanc d'un conteneur 40' Marine nuit |
| **Fin port** (`?theme=dark&ending=port`) | version sombre, puis un seul recul continu (8,0 – 12,0 s) | Blanc | `#FF6A33` | ce conteneur posé sur le quai, de nuit : piles de conteneurs, portique, mer, étoiles, lune |
| **Fin navire** (`?theme=dark&ending=ship`) | version sombre, puis un seul recul continu (8,0 – 12,0 s) | Blanc | `#FF6A33` | ce conteneur sur le pont d'un porte-conteneurs, en mer, de nuit |

Les couleurs du logo sont exactement celles des deux SVG livrés : la version claire reprend
`logo-horizontal.svg`, la version sombre `logo-horizontal-reverse.svg`.

## Fichiers

| Fichier | Contenu |
|---|---|
| [`reveal.html`](reveal.html) | L'animation, autonome (HTML + SVG + JS, aucune dépendance). Elle joue en boucle et propose lecture/pause, curseur, fond clair/sombre, fin (logo seul, conteneur, port, navire) et format 16:9/1:1. |
| `reveal-light-16x9.mp4` · `reveal-light-1x1.mp4` | Claire, 1920 × 1080 et 1080 × 1080, 60 i/s, 8,0 s (260 Ko · 225 Ko) |
| `reveal-dark-16x9.mp4` · `reveal-dark-1x1.mp4` | Sombre, 1920 × 1080 et 1080 × 1080, 60 i/s, 8,0 s (370 Ko · 290 Ko) |
| `reveal-dark.gif` | Sombre, 800 × 450, 30 i/s, 10,0 s en boucle (0,92 Mo) |
| `reveal-container-16x9.mp4` | Fin conteneur, 1920 × 1080, 60 i/s, 10,8 s (0,96 Mo) |
| `reveal-container.gif` | Fin conteneur, 800 × 450, 30 i/s, 12,8 s en boucle (2,37 Mo) |
| `reveal-port-16x9.mp4` · `reveal-port-1x1.mp4` | Fin port, 1920 × 1080 et 1080 × 1080, 60 i/s, 13,2 s (1,67 Mo · 1,13 Mo) |
| `reveal-port.gif` | Fin port, 800 × 450, 30 i/s, 15,2 s en boucle (3,56 Mo) |
| `reveal-ship-16x9.mp4` · `reveal-ship-1x1.mp4` | Fin navire, 1920 × 1080 et 1080 × 1080, 60 i/s, 13,2 s (1,59 Mo · 1,04 Mo) |
| `reveal-ship.gif` | Fin navire, 800 × 450, 30 i/s, 15,2 s en boucle (3,33 Mo) |
| [`../mockups/container-dark.svg`](../mockups/container-dark.svg) · `.png` | Image fixe du conteneur pour plaquettes et site : SVG vectoriel et PNG 2000 × 1125 |
| [`../mockups/port-night.svg`](../mockups/port-night.svg) · `.png` | Plan final de la fin port : SVG vectoriel et PNG 2000 × 1125 |
| [`../mockups/ship-night.svg`](../mockups/ship-night.svg) · `.png` | Plan final de la fin navire : SVG vectoriel et PNG 2000 × 1125 |
| `tools/build_reveal.py` | Relit les tracés de `concept-05/` et les injecte dans `reveal.html` (bloc `GEO`) |
| `tools/build_container.py` | Dessine le conteneur (textes en tracés), vérifie la zone d'exclusion, injecte le bloc `CONTAINER` et écrit le mockup |
| `tools/build_scenes.py` | Dessine les scènes port et navire (décor, ciel, étoiles, lune, feux, cadrages), vérifie lisibilité et place des étoiles, injecte le bloc `SCENES` et écrit les deux images fixes |
| `tools/render.js` | Export image par image (Playwright), puis encodage ffmpeg |
| `tools/verify.py` | Contrôles : dernière image vs SVG, fond, contraste, conteneur, scènes, specs, GIF, fluidité |
| `tools/baseline.json` | Empreintes des images des fins logo seul et conteneur : `verify.py` prouve qu'elles n'ont pas changé d'un pixel |

Toutes les versions sont muettes : aucune piste son n'est livrée.

## Palette

| Couleur | Hex | Rôle dans l'animation |
|---|---|---|
| Écume | `#F3F5F9` | Fond de la version claire, constant |
| Bleu Coque | `#0B2F6E` | Coque, anneau et lettres de la version claire ; fond de départ de la version sombre |
| Orange International | `#FF5A1F` · `#FF6A33` | La ligne, inchangée du début à la fin : `#FF5A1F` en version claire, `#FF6A33` en version sombre |
| Blanc | `#FFFFFF` | Coque, anneau et lettres de la version sombre ; marquages du conteneur |
| **Marine nuit** | `#0A1A3A` | **Fond sombre secondaire** : fond final de la version sombre, ciel, tôle, portes et montants du conteneur. Il figure dans la charte : [`concept-05/README.md`](../logos/concept-05/README.md). |
| Lignes du conteneur | `#1F2C45` | Marine nuit + 7 points de luminance OKLCH, chroma × 0,75 : tôle ondulée, arêtes, barres de verrouillage ; tous les traits des scènes port et navire |

Les scènes port et navire déclinent Marine nuit en luminance OKLCH, teinte conservée :

| Ton | Hex | Écart à Marine nuit | Rôle |
|---|---|---|---|
| Haut du ciel | `#03102F` | −0,040 | haut de l'image ; le ciel descend en dégradé jusqu'à Marine nuit à l'horizon |
| Mer | `#051332` | −0,030 | la mer, un ton plus sombre |
| Quai | `#081737` | −0,012 | face du quai, dans l'ombre |
| Conteneurs proches | `#14223E` | +0,030, chroma × 0,85 | pile derrière notre conteneur (port), 20' du premier rang (navire) |
| Conteneurs lointains | `#0F1E3B` | +0,015, chroma × 0,90 | piles du fond (port), rangées arrière (navire) |

L'orange `#FF6A33` n'y sert qu'à la ligne du logo et aux feux de signalisation. La lune est en Écume `#F3F5F9` à 85 %.

## Storyboard chronométré

Temps en secondes. Le récit est le même dans les deux versions ; seules les couleurs diffèrent.

| Temps | Plan | Ce qu'on voit | Ce que ça dit | Courbe |
|---|---|---|---|---|
| 0,00 – 0,30 | Mer | Un plan vide. | | |
| 0,30 – 1,30 | Mer | Une fine ligne d'horizon orange s'ouvre depuis le centre jusqu'aux bords. | Le « Blue » et la « Line ». | `inOut` |
| 1,50 – 2,15 | Cargo | La coque se dessine en traits, de la poupe à la proue (1,50 – 2,05). Puis viennent le château (1,65 – 2,10) et la pile de conteneurs (1,70 – 2,15). La mer cache ce qui passe sous l'horizon. | Un porte-conteneurs, le métier. | `inOut` |
| 2,15 – 2,59 | Cargo | Le cargo est complet. Sur la coque, la marque de Plimsoll (un petit cercle traversé d'une barre) s'allume puis clignote deux fois, à une période d'environ 0,2 s. | La ligne de charge. | `fade` |
| 2,60 – 2,82 | Cargo | Le cargo se charge : la coque s'enfonce et s'arrête net, exactement quand la ligne de charge touche l'eau. | Chargé à la limite exacte. | `settle` |
| 2,82 – 3,32 | Cargo | Micro-pulse orange, déclenché sur l'image d'arrivée : un cercle tenu 0,12 s s'élargit (de 1,3 à 2,6 fois le rayon) puis s'éteint. | Charge sûre. | `inOut` · `fade` |
| 3,00 – 4,30 | Transition | La caméra plonge sur la marque (zoom × 6,5 en 16:9, × 6,9 en 1:1) pendant que la coque s'estompe (3,00 – 3,80). L'horizon se resserre sur l'anneau (3,10 – 4,20). | Le cercle devient l'anneau du logo. | `inOut` |
| 3,30 – 4,30 | Anneau | La moitié immergée de l'anneau se révèle (3,30 – 3,90), déjà séparée de la ligne. La ligne coupe réellement l'anneau en deux demi-anneaux : à aucun moment l'anneau n'apparaît fermé sous la ligne. | En haut, la partie émergée ; en bas, la charge. Rien derrière. | `inOut` |
| 4,50 – 5,50 | Ligne | La ligne s'étire vers la droite uniquement ; à gauche, elle reste à ras de l'anneau. | Le sens de la marche, la livraison. | `inOut` |
| 5,50 – 6,42 | Nom | BLUE LINE apparaît lettre par lettre (décalage de 0,065 s) : chaque lettre monte de sous sa ligne de base en 0,55 s. | Le nom émerge de la ligne. | `out` |
| 6,15 – 6,97 | Nom | SHIPPING suit de la même façon (décalage de 0,045 s, 0,50 s par lettre). | | `out` |
| 7,00 – 8,00 | Logo | Le logo complet est figé pendant 1 s, identique au SVG. | | |

### Le fond, selon la version

- **Claire** : Écume constant de 0 à 8 s. Il n'y a ni assombrissement ni bascule de couleur.
- **Sombre** : le fond passe du Bleu Coque à Marine nuit sur 0 – 5,40 s, avec la courbe `night`, interpolée en
  OKLCH (pas en RVB, ce qui évite les gris ternes au milieu). La progression est lente au début : 13 % de la
  variation de luminance à 2,0 s. Elle est la plus marquée pendant le zoom (pic de vitesse vers 3,5 s, 64 % du
  changement entre 3 et 5 s). Le fond atteint Marine nuit à 4,97 s, avant l'arrivée du texte à 5,5 s, puis reste
  fixe.

### Fin conteneur (version sombre)

| Temps | Ce qu'on voit | Courbe |
|---|---|---|
| 0,00 – 8,00 | Exactement la version sombre : les 480 premières images sont identiques au pixel près. | |
| 8,00 – 9,80 | La caméra recule depuis le cadrage du logo figé jusqu'au conteneur entier (× 1,3, exponentiel). La tôle et le ciel ont la couleur du fond final (Marine nuit) : rien ne bouge à 8,0 s. Puis les lignes du conteneur apparaissent autour du logo (8,05 – 9,10) — arêtes, rails, montants, portes, marquages — et la tôle ondulée se dessine (8,20 – 9,30). On comprend que le fond était la tôle. | `inOut` · `fade` |
| 9,80 – 10,80 | Le conteneur complet est figé 1 s. | |

Le conteneur est un 40' (12,192 × 2,591 m) en dessin plat, sans 3D, sans texture ni ombre :
- la tôle, les portes, les montants et les rails sont en Marine nuit ;
- leurs arêtes, la tôle ondulée et les quatre barres de verrouillage des portes (à droite, avec gâches et poignées)
  sont en `#1F2C45` ;
- en haut à droite, le numéro fictif `BLSU 001234 6` au format ISO 6346, avec le chiffre de contrôle calculé et
  encadré et le code de type `42G1`, en Readex Pro blanc ;
- en bas à gauche, `BLUE LINE SHIPPING SARL · ALGÉRIE`.

**Le logo sur la paroi.** Il est centré horizontalement et verticalement sur le flanc (portes exclues). Sa largeur
représente **42,5 % de la longueur de la paroi**, soit 5,18 m sur un 40', et sa hauteur 44,6 % de la hauteur de paroi.
Il occupe 676 × 150 px dans la dernière image, et le conteneur 92 % de sa largeur. La zone d'exclusion (1 x = un
rayon d'anneau tout autour) ne contient que la paroi et sa tôle. `build_container.py` le vérifie par intersection
exacte des tracés, et `verify.py` le contrôle à l'image.

### Fins port et navire (version sombre)

| Temps | Ce qu'on voit | Courbe |
|---|---|---|
| 0,00 – 8,00 | Exactement la version sombre : les 480 premières images sont identiques au pixel près. | |
| 8,00 – 12,00 | Un seul recul, continu, sans arrêt, du logo figé au plan large. L'échelle est divisée par 3,3 à 5,7 selon la scène et le format ; le recul est le plus rapide à 10,0 s (à 9,8 s, 88 % de cette vitesse). Comme dans la fin conteneur, la tôle a la couleur du fond : rien ne bouge à 8,0 s, puis les lignes du conteneur apparaissent (8,05 – 9,10) et la tôle ondulée se dessine (8,20 – 9,30). Notre conteneur rapetisse et glisse en ligne droite jusqu'à sa place. Autour de lui, la scène apparaît en fondu : quai, mer et reflets (9,80 – 10,90) ; coque et château (9,85 – 10,95) ; contour du conteneur au trait du décor (9,85 – 11,30) ; piles de conteneurs (9,90 – 11,00) ; portique (10,05 – 11,20) ; haut du ciel qui s'assombrit (9,80 – 11,60) ; marque de Plimsoll (10,60 – 11,50) ; étoiles une à une (11,00 – 11,90, 0,55 s chacune) ; feux (11,20 – 11,80) ; lune (11,35 – 11,95). | `inOut` · `fade` |
| 12,00 – 13,20 | Plan large figé 1,2 s. | |

Le ciel, les étoiles et la lune sont fixes à l'écran, comme un décor à l'infini : pendant le recul, seul le premier plan
rapetisse. Les étoiles et la lune n'apparaissent qu'une fois que plus aucun objet ne passera devant elles (10,82 s au
plus tard pour le portique, devant la place de la lune) ; aucune n'est jamais cachée, puis découverte, ce qui ferait
scintiller.

#### Éléments de la scène « port » (`?ending=port`)

| Élément | Couleur |
|---|---|
| Notre conteneur, sur le quai, au premier plan, un peu à gauche du centre (45 % de la largeur en 16:9, centré en 1:1) | tel quel (Marine nuit, lignes `#1F2C45`, logo blanc et `#FF6A33`) |
| Son contour, redessiné au trait du décor pendant le recul | `#1F2C45`, 1,3 px |
| 3 piles de conteneurs anonymes (sans logo ni texte), deux niveaux chacune : plus elles sont loin, plus elles sont petites et basses (échelles 0,80, 0,62 et 0,46) | proche `#14223E`, lointaines `#0F1E3B`, arêtes `#1F2C45` |
| Un portique à conteneurs, à droite, au trait fin, qui dépasse dans le ciel, entier dans les deux formats | `#1F2C45`, 1,5 px |
| Un feu de signalisation, au sommet du portique | orange `#FF6A33`, point de 4 px |
| Le quai : face verticale, défenses, arête | `#081737`, traits `#1F2C45` |
| La mer, tout en bas, avec 5 reflets immobiles | `#051332`, reflets blancs à 15 %, 1,5 px |
| Ciel, étoiles, lune | voir ci-dessous |

#### Éléments de la scène « navire » (`?ending=ship`)

| Élément | Couleur |
|---|---|
| Le cargo du début de l'animation (coque, château, aileron de passerelle, pile), rempli en aplat, vu de côté, sur 85 % de la largeur | aplat Marine nuit `#0A1A3A`, contours `#1F2C45` à 1,5 px |
| Vitres de passerelle, mât, hampe de proue | `#1F2C45` |
| Rangées arrière : la pile du début avec ses travées | `#0F1E3B`, arêtes `#1F2C45` |
| Rangée avant : un 20' anonyme et notre conteneur, au premier rang, seul à porter le logo | `#14223E` ; notre conteneur tel quel |
| La marque de Plimsoll sur la coque, sous notre conteneur : le cercle traversé par la barre, la barre au ras de l'eau (chargé « juste ») ; la moitié immergée se devine sous la surface | blanc, 1,6 px ; moitié immergée à 30 % |
| La mer, avec 4 reflets immobiles, sans vagues | `#051332`, reflets blancs à 15 % |
| Feu de mât, en haut du château | orange `#FF6A33`, 4 px |
| Feu de proue | blanc, 4 px |

#### Ciel de nuit (les deux scènes)

| Élément | Couleur |
|---|---|
| Ciel : deux tons interpolés en OKLCH, du haut de l'image à l'horizon | `#03102F` (Marine nuit −0,040 de luminance) → Marine nuit `#0A1A3A` |
| 56 étoiles, de 1 à 2,5 px, opacité 0,25 à 0,7, placées par un générateur à graine fixe (mulberry32, graines `0x5EA` pour le port et `0xB0A7` pour le navire, + 101 en 1:1), dans le haut du ciel : à 28 px au moins des silhouettes et à 60 px au moins de notre conteneur | blanc |
| Lune : croissant fin, en haut à droite, diamètre 7 % de la hauteur d'image (76 px), sans halo, sans visage, sans rayons | Écume `#F3F5F9` à 85 % |

## Décisions prises (à valider)

1. **Logo à 42,5 % de la paroi au lieu des 55 % demandés.** Sur un flanc de 40', un logo à 55 % de la longueur ferait
   58 % de la hauteur de paroi. Avec sa zone d'exclusion (1 x au-dessus et 1 x au-dessous, soit deux fois la hauteur
   du logo), il occuperait 115 % de la hauteur et déborderait sur les rails. J'ai gardé la règle du README et pris le
   plus grand logo qu'elle autorise : la zone d'exclusion tient entre les deux rails, à 4 unités près.

   Pour atteindre 55 %, il faudrait réduire la zone d'exclusion verticale à 0,25 x. Le réglage tient en une ligne
   dans `build_container.py` (`H_WALL`).
2. **« +6 à +8 % de luminance OKLCH »** est compris comme +0,06 à +0,08 sur l'échelle L d'OKLCH (0 à 1). La valeur
   retenue est +0,07, avec la chroma réduite à 75 % pour que les lignes restent un bleu acier et ne tirent pas vers le
   Bleu Coque. Le contraste avec la tôle est de 1,23:1 : visible, mais discret.
3. **Ciel du conteneur en Marine nuit, sans quai.** Le conteneur se lit donc par ses lignes, et la transition depuis
   le logo figé est invisible.
4. **Orange de la version claire.** `#FF5A1F` sur Écume ne fait que 2,86:1. C'est la couleur exacte de
   `logo-horizontal.svg`, et les logos sont exemptés des seuils WCAG. La coque, l'anneau et le texte sont à 11,69:1.
   De même, en version sombre et sur le conteneur, le blanc est à 17,19:1 sur Marine nuit, mais la ligne `#FF6A33`
   n'y atteint que 6,03:1 : au-dessus du seuil AA (4,5:1), sous 7:1. C'est accepté : le seuil de 7:1 s'applique
   au texte, pas à la ligne (voir le point 18). La couleur du logo n'est pas modifiée.

Fins port et navire :

5. **Ciel en bandes de 1 niveau, pas en dégradé SVG.** Chrome trame les dégradés SVG (bruit de ±1 niveau). Avec la
   palette d'un GIF, ce bruit aurait donné des plaques et des bandes. Le ciel est donc calculé en OKLCH, puis découpé
   en 29 bandes horizontales, chacune exactement un niveau 8 bits plus claire que la précédente : c'est le dégradé
   le plus fin possible sans tramage. Les images fixes (SVG) gardent un vrai dégradé, meilleur à l'impression.
6. **Ciel, étoiles et lune fixes à l'écran, décor dans le monde.** Pendant le recul, le ciel ne bouge pas, comme un
   décor à l'infini ; seul le premier plan rapetisse.
7. **Étoiles et lune tardives.** Pour qu'aucune étoile ne passe derrière le portique en mouvement (elle
   s'éteindrait puis se rallumerait : un scintillement), une étoile n'est placée que si aucun objet ne la couvre
   entre son apparition et la fin du recul. Le portique balaie le haut à droite jusqu'à 10,82 s. Les étoiles
   apparaissent entre 11,0 et 11,9 s, et la lune entre 11,35 et 11,95 s : toujours pendant le recul, dans sa
   dernière partie, quand la scène est presque en place.
8. **Étoiles dessinées en pixels entiers.** Chrome lisse les très petits disques un peu différemment d'une image à
   l'autre quand la scène bouge (jusqu'à 4 niveaux d'écart). Chaque étoile est donc précalculée : couverture exacte
   du disque sur chaque pixel, puis carrés de 1 px alignés sur la grille. Une fois apparue, une étoile ne change
   plus d'un seul niveau.
9. **GIF port et navire : palette commune à partir de 11,0 s.** Avec une palette par image, une étoile fixe
   changeait de quelques niveaux tant que la scène bougeait. Les images de la tenue initiale et celles qui suivent
   l'apparition des étoiles partagent donc une palette de 256 couleurs ; les autres gardent une palette par image.
10. **Traits du décor à épaisseur constante à l'écran** : 1,3 px ; 1,5 px pour le portique, la coque et le château.
    Pendant le recul, les arêtes de notre conteneur, proportionnelles à l'échelle, tombent sous le pixel. Son contour
    est donc redessiné au trait du décor, en fondu (9,85 – 11,30 s), pour qu'il reste le plus net de l'image.
11. **Décor en retrait.** Les conteneurs anonymes ne sont que légèrement plus clairs que Marine nuit (+0,030 et
    +0,015) et les piles ne font que deux niveaux. Notre conteneur, au premier plan, reste ainsi l'objet le plus net.
    Un seul portique : deux portiques de profil croisaient leurs structures, et le second sortait du cadre en 1:1.
12. **Taille du logo au plan final.** Port : 14 % de la largeur en 16:9, 15 % en 1:1. Navire : 13 %. Avec un navire à
    85 % de la largeur, un logo d'au moins 12 % impose un conteneur d'environ 38 % de la longueur du navire : c'est
    un petit porte-conteneurs stylisé, avec un seul niveau de conteneurs au premier rang.
13. **Navire.** La pile du cargo d'ouverture, avec ses travées, devient les rangées arrière. Le premier rang reçoit un
    20' anonyme et notre conteneur. La moitié immergée de la marque de Plimsoll se devine sous la surface (blanc à
    30 %), comme la moitié basse de l'anneau du logo.
14. **Port en 1:1.** Notre conteneur est centré, comme demandé ; en 16:9, il est un peu à gauche du centre (45 % de
    la largeur). L'horizon est placé à 66 % de la hauteur en 16:9 et à 68 % en 1:1, pour laisser plus de ciel.
15. **Feux.** L'orange des feux est `#FF6A33`, celui de la ligne en version sombre. Les feux gardent 4 px à l'écran
    pendant tout le recul.
16. **Bouton « Fin : … ».** Il affiche la fin en cours (logo seul, conteneur, port, navire) ; un clic passe à la
    suivante.
17. **Recul continu de 8,0 à 12,0 s (validé).** Pour le port et le navire, une seule courbe `inOut` mène du logo
    figé au plan large : la caméra ne s'arrête plus à 9,8 s, où elle recule à 88 % de sa vitesse maximale (atteinte
    à 10,0 s). Les images jusqu'à 8,0 s restent identiques à la version sombre. La fin conteneur garde son propre
    recul, arrêté à 9,8 s : elle est inchangée.
18. **Ligne orange à 6,03:1 sur la paroi (validé).** C'est la couleur du logo, `#FF6A33`, et elle ne change pas. Le
    seuil de 7:1 s'applique au texte : le nom, les marquages et l'anneau, en blanc, sont à 17,19:1. Il ne s'applique
    pas à la ligne, élément graphique.
19. **Fin de boucle.** Dans les fins port et navire, la scène s'efface d'un bloc (une seule opacité), pour que le décor
    ne transparaisse pas à travers notre conteneur pendant le fondu.
20. **Aperçu dans le navigateur.** Si la fenêtre n'a pas les proportions du format, le ciel et la mer débordent dans
    les bandes latérales au lieu d'un aplat Marine nuit (sans effet sur les exports, faits au format exact).

## Direction artistique

- **Palette du concept 05 uniquement**, sans particule, 3D ni flou, et sans dégradé spatial, sauf le ciel de nuit des
  fins port et navire (deux tons voisins). Seuls des aplats bougent ; les apparitions sont des fondus d'opacité, et le
  fond de la version sombre change de couleur dans le temps, jamais dans l'espace.
- **Courbes sans rebond.** Ce sont des cubic-bezier qui ne dépassent jamais leur valeur d'arrivée :
  - `inOut` = `(0.65, 0, 0.35, 1)` pour les transitions ;
  - `settle` = `(0.40, 0, 0.70, 0.85)` pour l'enfoncement : départ souple, arrivée encore en mouvement, d'où un arrêt
    net ;
  - `out` = `(0.22, 1, 0.36, 1)` pour les lettres ;
  - `fade` = `(0.37, 0, 0.63, 1)` pour les fondus ;
  - `night` = `(0.80, 0, 0.50, 1)` pour le fond de la version sombre.

  Les mouvements de caméra (plongée et reculs) sont exponentiels : la vitesse perçue reste constante. Au second
  recul, le centre de notre conteneur glisse en ligne droite, à l'écran, jusqu'à sa place dans le plan large.
- **Le texte**, ce sont les tracés Readex Pro du SVG final, découpés lettre par lettre ; les marquages du conteneur
  sont composés en Readex Pro puis convertis en tracés. Aucune police n'est chargée.
- **Mise en page.** Le logo occupe 46 % de la largeur en 16:9 et 74 % en 1:1, centré, positionné au pixel entier. Le
  conteneur final occupe 92 % de la largeur, centré.
- **Scènes de nuit.** Aplats de Marine nuit déclinés en luminance et traits fins, sans texture, sans 3D ni
  perspective : la profondeur vient de la taille (les piles lointaines sont plus petites et plus basses) et du ton
  (plus proche du ciel au loin). Le seul dégradé est celui du ciel, sur deux tons voisins.

## Contraste

| | Coque, anneau, texte sur le fond | Ligne orange sur le fond |
|---|---|---|
| Claire | 11,69:1 (Bleu Coque sur Écume) | 2,86:1 (couleur du logo, voir les décisions) |
| Sombre | 12,76:1 à 17,19:1 (blanc sur Bleu Coque, puis Marine nuit) | 4,47:1 à 6,03:1 |
| Conteneur | 17,19:1 (blanc sur Marine nuit) | 6,03:1 |
| Port, navire (logo sur la paroi) | 17,19:1 (blanc sur Marine nuit) | 6,03:1 |
| Tôle ondulée sur la paroi | 1,23:1 : discrète, comme demandé | |
| Traits du décor | 1,23:1 sur Marine nuit, 1,34:1 sur le haut du ciel, 1,19:1 et 1,13:1 sur les conteneurs lointains et proches : discrets | |

**Seuil de 7:1 : il s'applique au texte, pas à la ligne.** Le nom, les marquages et l'anneau, en blanc, sont à
17,19:1 sur Marine nuit. La ligne orange `#FF6A33` est un élément graphique de la couleur exacte du logo : ses 6,03:1
sont acceptés et la couleur ne change pas (au-dessus du seuil AA de 4,5:1 et du seuil non-texte de 3:1).

## Comment c'est construit

`reveal.html` ne contient pas d'animation CSS. Une fonction `renderAt(t)` calcule l'état exact de l'image à l'instant
`t` :

- **à la lecture**, `requestAnimationFrame` l'appelle avec l'horloge du navigateur ;
- **à l'export**, `render.js` appelle `renderAt(i / 60)` pour chaque image, ce qui exclut toute image sautée ou
  dupliquée ;
- **à partir de 7,00 s**, l'image n'affiche plus que les quatre `<path>` du SVG du logo, recopiés sans modification
  par `build_reveal.py`. Les lettres animées sont ces mêmes tracés, découpés par contour. Pour les fins conteneur,
  port et navire, ces tracés reçoivent la transformation de la caméra, identique à celle du logo seul à 8,0 s ;
- **après 8,00 s**, la fin conteneur suit `containerCamera()` (recul arrêté à 9,8 s) ; les fins port et navire
  suivent `sceneCamera()`, qui part exactement du cadrage du logo figé et mène au plan large en une seule courbe. Le
  décor (repère du monde) suit la caméra ; le ciel, les étoiles et la lune restent fixes ; les feux gardent 4 px.

Options d'URL :

| Option | Effet |
|---|---|
| `?theme=dark` | Version sombre |
| `?ending=container` | Fin conteneur (avec `theme=dark`) |
| `?ending=port` · `?ending=ship` | Fins port et navire (avec `theme=dark`) |
| `?format=1x1` | Format carré |
| `?t=4.2` | Image fixe à l'instant 4,2 s |
| `?export=1` | Sans contrôles, expose `window.BLS` |

Si l'utilisateur a demandé à réduire les animations dans son système, la page montre directement l'image finale.

## Régénérer

Prérequis :
- Node.js avec Playwright (Chromium) ;
- ffmpeg (avec libx264) ;
- Python 3 avec numpy et Pillow, plus fonttools, uharfbuzz et skia-pathops pour `build_container.py` et
  `build_scenes.py` ;
- les polices, via `../tools/fetch_fonts.sh`.

```sh
python3 brand/motion/tools/build_reveal.py      # 1. relit concept-05/*.svg et met à jour reveal.html
python3 brand/motion/tools/build_container.py   # 2. conteneur : géométrie, zone d'exclusion, mockups/container-dark.svg
python3 brand/motion/tools/build_scenes.py      # 3. port et navire : décor, ciel, étoiles, mockups/*-night.svg
node brand/motion/tools/render.js               # 4. 9 rendus (5 736 images, ≈ 8 min), 9 MP4, 4 GIF, 3 PNG fixes
python3 brand/motion/tools/verify.py            # 5. contrôles (≈ 25 min ; code de sortie ≠ 0 en cas d'échec)
```

On peut ne refaire que certains rendus, par exemple `render.js port-16x9 mockup`, et ne contrôler qu'une partie :
`verify.py port-16x9 reveal-port.gif mockup`. Après une modification voulue des fins logo seul ou conteneur,
`verify.py --update-baseline` remplace leurs empreintes dans `tools/baseline.json`. Les images intermédiaires vont
dans `brand/motion/.frames/`, ignoré par git.

### Commandes ffmpeg utilisées

MP4 (H.264, profil High, 4:2:0, BT.709, une commande par rendu) :

```sh
ffmpeg -y -framerate 60 -i .frames/dark-16x9/f%04d.png \
  -c:v libx264 -preset slow -crf 12 -tune animation -profile:v high \
  -vf "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p" \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv \
  -r 60 -movflags +faststart -an reveal-dark-16x9.mp4
```

- `-crf 12` donne une qualité quasi transparente.
- La matrice BT.709 est explicite : sans elle, ffmpeg convertirait en BT.601 et les bleus dériveraient à la lecture.
- `+faststart` permet de lancer la lecture avant la fin du téléchargement.

GIF, avec une palette par image, sans tramage ni transparence entre images :

```sh
ffmpeg -y -framerate 30 -i .frames/gif-dark-16x9/g%04d.png \
  -vf "scale=800:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=64:stats_mode=single[p];[b][p]paletteuse=new=1:dither=none" \
  -gifflags -transdiff -loop 0 reveal-dark.gif
```

Le fond de la version sombre change de couleur à chaque image. Avec une palette commune, il avancerait par marches
visibles ; avec une palette par image (`stats_mode=single`, `new=1`), chaque image garde la teinte exacte du fond.
Deux options sont alors incompatibles et ont été retirées :
- `diff_mode=rectangle` réutiliserait les indices de l'image précédente ;
- la transparence entre images (`transdiff`) mélangerait deux palettes.

GIF port et navire : la tenue initiale et les images qui suivent l'apparition des étoiles (à partir de 11,0 s)
partagent une palette de 256 couleurs, calculée sur ces images-là ; le reste garde une palette par image
(`render.js`, `encodeGif`). Pour reveal-ship.gif (images de la séquence : 45 de tenue, puis 15 de retour, puis
l'animation ; la palette commune reprend à l'image 390) :

```sh
ffmpeg -y -framerate 30 -i .frames/gif-ship-16x9/g%04d.png \
  -vf "select='lt(n\,45)+gte(n\,390)',scale=800:-1:flags=lanczos,palettegen=max_colors=256:stats_mode=full" \
  .frames/gif-ship-16x9/palette.png
ffmpeg -y -framerate 30 -i .frames/gif-ship-16x9/g%04d.png -i .frames/gif-ship-16x9/palette.png -filter_complex \
  "[0:v]scale=800:-1:flags=lanczos,split=3[s1][s2][s3];[1:v]split[p1][p2];\
   [s1]trim=end_frame=45,setpts=PTS-STARTPTS[a0];[a0][p1]paletteuse=dither=none[A];\
   [s2]trim=start_frame=45:end_frame=390,setpts=PTS-STARTPTS,split[b1][b2];\
   [b1]palettegen=max_colors=64:stats_mode=single[pb];[b2][pb]paletteuse=new=1:dither=none[B];\
   [s3]trim=start_frame=390,setpts=PTS-STARTPTS[c0];[c0][p2]paletteuse=dither=none[C];\
   [A][B][C]concat=n=3:v=1:a=0" \
  -gifflags -transdiff -loop 0 reveal-ship.gif
```

Chaque GIF commence sur son image finale (logo, conteneur ou scène) tenue 1,5 s. Viennent ensuite 0,5 s de retour au fond de
départ (Marine nuit → Bleu Coque), puis l'animation à 30 i/s (une image sur deux), qui finit sur la même image : la
boucle est sans couture. Ce choix tient à un défaut d'Outlook pour Windows, qui n'affiche que la première image d'un
GIF : la signature y montre le logo, pas un fond vide.

## Contrôles (`verify.py`)

| Contrôle | light-16x9 · light-1x1 | dark-16x9 · dark-1x1 | container-16x9 |
|---|---|---|---|
| Dernière image comparée aux tracés relus dans le SVG livré, sur le fond final | **0 pixel d'écart** (`logo-horizontal.svg` sur Écume) | **0 pixel d'écart** (`logo-horizontal-reverse.svg` sur Marine nuit) | |
| Dernière image comparée au SVG en `<img>` (rééchantillonné) | centre décalé de 0,05 px (16:9) et 0,16 px (1:1), écarts uniquement sur les contours | idem | |
| Début identique à la version sombre | | | 480 images, 0 écart |
| Logo sur la paroi | | | 676 × 150 px pour 677 × 151 attendus ; rapport logo / paroi 0,425 |
| Zone d'exclusion du logo | | | libre (géométrie et image) |
| Fond | Écume constant | calcul OKLCH exact, Marine nuit dès 4,97 s puis fixe | idem, ciel et tôle Marine nuit |
| Ligne orange inchangée | `#FF5A1F` | `#FF6A33` | `#FF6A33` |
| Couleur des éléments | Bleu Coque, aucune bascule | blanc, aucune bascule | blanc |
| Saccades, image figée en plein mouvement | aucune | aucune | aucune |
| Image finale figée | 1,00 s | 1,00 s | 1,00 s |
| Dernière image du MP4 (H.264 4:2:0) | PSNR 43,7 dB | 44,1 dB | 43,3 dB |
| **Strictement inchangé** depuis l'ajout des fins port et navire : pixels de chaque image (`baseline.json`) | 480 images, identiques | 480 images, identiques | 648 images, identiques |

Les 7 fichiers MP4 et GIF de ces versions, réencodés, sont aussi identiques à l'octet près.

| Contrôle | port-16x9 · port-1x1 | ship-16x9 · ship-1x1 |
|---|---|---|
| Début identique (toutes les images comparées une à une) | 480 images (jusqu'à 8,0 s) = version sombre | idem |
| Recul continu de 8,0 à 12,0 s (caméra de chaque image) | vitesse jamais nulle, un seul pic (10,0 s), aucun creux ; à 9,8 s, 88 % du pic | idem |
| Largeur du logo au plan final (≥ 12 %) | 269 px = 14,0 % ; 162 px = 15,0 % | 249 px = 13,0 % ; 139 px = 12,9 % |
| Contraste du texte sur la paroi (≥ 7:1, seuil du texte) | blanc 17,19:1 ; ligne orange 6,03:1, acceptée | idem |
| Zone d'exclusion du logo | seuls la paroi et sa tôle (0 pixel étranger) | idem |
| Étoiles | 56, de 1,0 à 2,5 px, opacité 0,25 à 0,70 ; aucune dans la zone d'exclusion ni derrière le conteneur ; chacune visible et seule sur le ciel | idem |
| Étoiles fixes après leur apparition | 0 niveau d'écart jusqu'à la fin | idem |
| Ciel | 29 bandes de 1 niveau, de `#03102F` à Marine nuit ; colonne témoin identique au calcul, sans tramage | idem |
| Lune | 75 px de haut (6,9 % de la hauteur), en haut à droite, teinte = Écume à 85 % (± 1) | idem |
| Feux | 4 à 5 px (lissage) ; un seul feu orange | 4 à 5 px ; un seul feu orange (mât), un blanc (proue) |
| Orange ailleurs que sur la ligne et le feu | 0 pixel | 0 pixel |
| Largeur du navire | | 85,0 % |
| Saccades, image figée en plein mouvement | aucune | aucune |
| Image finale figée | 1,20 s | 1,20 s |
| Dernière image du MP4 | PSNR 43,7 et 43,9 dB | 43,9 et 43,7 dB |

GIF : 800 px de large, 30 i/s, fond identique à la vidéo à chaque image, sans tramage, et première image = image
finale. Poids : 0,92 Mo (`reveal-dark.gif`), 2,37 Mo (`reveal-container.gif`), 3,56 Mo (`reveal-port.gif`) et
3,33 Mo (`reveal-ship.gif`), pour une limite de 5 Mo. Pour le port et le navire :
- le ciel s'écarte d'au plus 1 niveau de la même réduction sans palette, donc sans bande ;
- les étoiles ne varient pas d'un seul niveau entre leur apparition et la fin, ni pendant la tenue initiale.

Images fixes : SVG vectoriels sans texte vivant, image ni filtre (les deux scènes de nuit ont un seul dégradé, celui
du ciel), PNG 2000 × 1125, même plan que la dernière image de la vidéo 16:9 (PSNR 43,8, 47,1 et 46,8 dB). Pour le
port et le navire, contrôle ciblé en plus : les 56 étoiles visibles à leur place, la lune, les feux, le haut du ciel.

**Reproductibilité.** Chrome rend chaque image de façon déterministe, à une exception près, observée une fois : un
rendu lancé sous très forte charge machine a produit 2 images de `light-16x9` (3,25 s) différentes, la dernière restant
identique. Relancé normalement, le rendu est revenu identique au pixel près, et les MP4 identiques à l'octet près. Si
le contrôle « strictement inchangé » échoue sur quelques images isolées, refaire ce rendu avant de chercher une cause
dans le code.

Le MP4 ne peut pas être identique au pixel près : le H.264 en 4:2:0 sous-échantillonne la couleur. Le PSNR mesure
cet écart, invisible à l'œil au-delà de 40 dB. Dans la version sombre, la courbe OKLCH arrondie sur 8 bits fait une
fois remonter le rouge d'un niveau (+0,26 % de luminance, à 2,43 s), ce qui reste imperceptible ; le contrôle tolère
1 %. En fin de recul de la caméra, le mouvement passe sous le centième de pixel et Chrome peut ne pas redessiner une
image (9,78 s) : le contrôle d'image figée ne porte que sur les mouvements visibles.

## لوحة القصة (بالعربية) — للتواصل الداخلي

<div dir="rtl" lang="ar">

**الفكرة:** تحكي هذه الحركة قصة شعارنا في ثماني ثوانٍ. على هيكل كل سفينة تجارية تُرسم علامة خط الحمولة (علامة
بليمسول)، وهي الحدّ الذي لا يجوز أن تُحمَّل السفينة بعده. تتحوّل هذه العلامة إلى شعار «بلو لاين للشحن». أمّا الخط
البرتقالي فلا يتغيّر أبدًا: إنه الخيط الناظم، والشمس عند الأفق.

| التوقيت | ما نراه | المعنى |
|---|---|---|
| من 0,0 إلى 1,5 ثانية | خلفية خالية، يظهر في وسطها خط أفق برتقالي رفيع يمتدّ من المركز نحو الطرفين. | «الأزرق» و«الخط»: اسم الشركة نفسه. |
| من 1,5 إلى 3,0 ثانية | تُرسم سفينة حاويات بخطوط بسيطة فوق خط الأفق. على هيكلها دائرة صغيرة يقطعها خط، تضيء ثم تومض مرتين: إنها علامة بليمسول. تغوص السفينة قليلًا وتتوقّف بحزم في اللحظة التي تلامس فيها العلامةُ سطحَ الماء، فتصدر نبضة برتقالية خفيفة. | الحمولة آمنة ومطابقة للقواعد. |
| من 3,0 إلى 4,5 ثانية | تقترب الكاميرا من العلامة وتتلاشى السفينة. تكبر الدائرة لتصبح حلقة الشعار، ويظهر نصفها الذي كان تحت الماء منفصلًا عن الخط، فيقطع الخطُّ الحلقةَ فعلًا إلى نصفين. | النصف العلوي هو الجزء الظاهر فوق الماء، والنصف السفلي هو الحمولة. لا شيء مخفيّ خلف الخط. |
| من 4,5 إلى 5,5 ثانية | يمتدّ الخط نحو اليمين فقط، كمسار ينطلق، ويبقى طرفه الأيسر ملاصقًا للحلقة. | اتجاه السير والتسليم. |
| من 5,5 إلى 7,0 ثانية | تظهر عبارة BLUE LINE حرفًا بعد حرف، ثم كلمة SHIPPING، بخط Readex Pro، وكأنّ كل حرف يصعد من تحت السطر. | الاسم يولد من الخط. |
| من 7,0 إلى 8,0 ثانية | الشعار النهائي ثابت لمدة ثانية، مطابق تمامًا لملف الشعار الرسمي. | وعدنا: الموثوقية. |

**النسختان:**

- **النسخة الفاتحة:** الخلفية بلون فاتح جدًا (Écume) ثابت من البداية إلى النهاية. السفينة والحلقة والنص باللون
  الأزرق الداكن (Bleu Coque)، والخط برتقالي.
- **النسخة الداكنة:** تبدأ الخلفية بالأزرق الداكن (Bleu Coque) وتُظلِم ببطء، ثم بوضوح أكبر أثناء الاقتراب من الحلقة،
  حتى تبلغ الأزرق الليلي العميق (Marine nuit) قبل ظهور النص. تبقى العناصر كلها بيضاء.

**النهاية البديلة، الحاوية (للنسخة الداكنة):**

- بعد ثبات الشعار، تبتعد الكاميرا بين الثانية 8,0 والثانية 9,8. لون الحاوية هو الأزرق الليلي نفسه، فتظهر خطوطها
  تدريجيًا حول الشعار، ونفهم أن الخلفية كانت جدار الحاوية.
- الحاوية بطول 40 قدمًا، والشعار في وسط جدارها الجانبي، بعرض يقارب 42 % من طول الجدار. هذا أقصى حجم يسمح باحترام
  المسافة الفارغة المطلوبة حول الشعار.
- على الجدار رقم حاوية افتراضي في الأعلى إلى اليمين (BLSU 001234 6)، وعبارة «BLUE LINE SHIPPING SARL · ALGÉRIE»
  في الأسفل، والأبواب على اليمين بقضبان إقفالها.
- تبقى الحاوية كاملة ثابتة لمدة ثانية.

**النهايتان البديلتان «الميناء» و«السفينة» (للنسخة الداكنة):**

| التوقيت | ما نراه |
|---|---|
| من 0,0 إلى 8,0 ثانية | مطابقتان تمامًا للنسخة الداكنة، صورةً بصورة. |
| من 8,0 إلى 12,0 ثانية | تبتعد الكاميرا في حركة واحدة متصلة، من دون أي توقف. تظهر أولًا خطوط الحاوية حول الشعار، ثم تصغر حاويتنا وتنزلق إلى مكانها، ويظهر المشهد حولها تدريجيًا: الرصيف أو السفينة، ثم أكوام الحاويات والرافعة، ثم تزداد السماء قتامة نحو الأعلى. بعدها تظهر النجوم واحدة تلو الأخرى، ثم القمر والأضواء. |
| من 12,0 إلى 13,2 ثانية | يبقى المشهد العام ثابتًا لمدة 1,2 ثانية. |

- **الميناء:** حاويتنا موضوعة على الرصيف في المقدمة، إلى يسار الوسط قليلًا (وفي الوسط تمامًا في الصيغة المربعة).
  خلفها ثلاث أكوام من الحاويات بلا شعار ولا كتابة، من طبقتين، تصغر كلما ابتعدت، بدرجتين من الأزرق الليلي أفتح قليلًا. على
  اليمين رافعة حاويات مرسومة بخط رفيع ترتفع في السماء، وفي أعلاها ضوء إشارة برتقالي صغير. في الأسفل
  الرصيف، ثم البحر مع خمسة خطوط انعكاس بيضاء خافتة وثابتة.
- **السفينة:** حاويتنا محمّلة على سطح سفينة حاويات في عرض البحر ليلًا. السفينة هي نفسها التي تظهر في بداية الحركة،
  لكنها مملوءة بالأزرق الليلي ومحاطة بخطوط رفيعة، وتشغل 85 % من عرض الصورة. حاويتنا في الصف الأمامي، الأقرب إلى
  الكاميرا، وهي الوحيدة التي تحمل الشعار. على الهيكل، تحت حاويتنا، تظهر علامة بليمسول (دائرة يقطعها خط، بالأبيض)،
  وخطها عند سطح الماء تمامًا: السفينة محمّلة «بالقدر الصحيح». ضوء برتقالي في أعلى الصاري وضوء أبيض في المقدمة،
  والبحر أغمق بدرجة، مع أربعة خطوط انعكاس خافتة، بلا أمواج.
- **السماء:** أزرق ليلي يزداد قتامة قليلًا نحو الأعلى، و56 نجمة صغيرة ثابتة لا تومض، وهلال رفيع بلون أبيض مائل إلى
  الزرقة في الأعلى إلى اليمين. لا تظهر أي نجمة حول الشعار ولا خلف الكتابة.
- يبقى عرض الشعار في اللقطة الأخيرة أكبر من 12 % من عرض الصورة، فيبقى مقروءًا. البرتقالي حكر على خط الشعار وأضواء
  الإشارة.
- تباين النص الأبيض مع جدار الحاوية 17,19:1. أما الخط البرتقالي فتباينه 6,03:1، وهو مقبول: حدّ 7:1 يخص النص لا الخط،
  ولون الخط هو لون الشعار نفسه ولا يتغير.

**الألوان:** الأزرق الداكن، والأزرق الليلي العميق ودرجاته، والبرتقالي الدولي (لون السلامة في الملاحة البحرية)،
والأبيض. لا مؤثرات، ولا تدرّج لونيًا إلا في سماء الليل بلونين متقاربين، والحركة هادئة ودقيقة بلا ارتداد.

**الصيغ المتوفرة:**

- فيديو أفقي 16:9 وآخر مربّع 1:1 لكل نسخة من النسختين، ولكل من نهايتي الميناء والسفينة؛
- فيديو أفقي لنهاية الحاوية؛
- أربع صور GIF متحركة للتوقيع الإلكتروني وتطبيقات المراسلة (النسخة الداكنة، الحاوية، الميناء، السفينة)؛
- ثلاث صور ثابتة للمطويات والموقع الإلكتروني: الحاوية، والميناء ليلًا، والسفينة ليلًا.

كل النسخ بدون صوت.

</div>
