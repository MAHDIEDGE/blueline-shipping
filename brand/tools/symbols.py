"""Géométrie des symboles des 5 concepts.

Chaque fonction retourne des tracés dans un repère y vers le bas.
Rôles de couleur : p = bleu profond, a = accent.
"""

import math

from blsvg import (DIFF, INTER, Font, arc_to, circle, op, rect, ring, rrect,
                   stroke, union)


# --------------------------------------------------------------------------
# 01 · Horizon — le B et le L partagent la même hampe ; le pied du L file
#                 au-delà des panses et devient la ligne d'horizon.
# --------------------------------------------------------------------------

def c01_horizon(t=17.0, gap=6.0, waist=44.0, reach=134.0, right=80.0):
    H = 100.0
    yw1, yw2 = waist - t / 2, waist + t / 2  # barre médiane du B
    R1 = yw2 / 2                             # panse haute
    R2 = (H - yw1) / 2                       # panse basse, plus ample
    cx = right - R2                          # centre commun aux deux panses

    def d_shape(y0, R, inset=0.0):
        r = R - inset
        return union(rect(inset, y0 + inset, cx - inset, 2 * r), circle(cx, y0 + R, r))

    b = op(union(d_shape(0, R1), d_shape(yw1, R2)),
           union(d_shape(0, R1, t), d_shape(yw1, R2, t)), DIFF)
    # coupe « pochoir » (le marquage des conteneurs) entre la hampe et les panses
    bowls = op(b, rect(-1, -1, t + gap + 1, H + 2), DIFF)
    bowls = op(bowls, rect(-1, H - t, reach + 2, t + 1), DIFF)
    spine = union(rect(0, 0, t, H), rect(0, H - t, right, t))
    horizon = rect(right, H - t, reach - right, t)
    return {"p": union(spine, bowls), "a": horizon}


# --------------------------------------------------------------------------
# 02 · Ondulation — un conteneur dont la tôle ondulée est faite de lignes,
#                    posé sur la route qui file vers l'avant.
# --------------------------------------------------------------------------

def c02_container(W=140.0, H=62.0, n=7, slit=5.0, inset=10.0, radius=3.5,
                  gap=8.0, rail=11.0, ext=44.0):
    block = rrect(0, 0, W, H, radius)
    pitch = (W - 2 * inset) / n
    slits = union(*[rect(inset + pitch * (i + 0.5) - slit / 2, inset, slit, H - 2 * inset)
                    for i in range(n)])
    body = op(block, slits, DIFF)
    route = rect(0, H + gap, W + ext, rail)
    return {"p": body, "a": route}


# --------------------------------------------------------------------------
# 04 · Pont — un arc tendu entre deux ports : anneau = départ (Chine, à l'est),
#              point plein = arrivée (Algérie, à l'ouest).
# --------------------------------------------------------------------------

def c04_bridge(R=86.0, span=118.0, t=11.0, dot=10.5, gap=5.0, ring_in=5.0):
    a0, a1 = 270 - span / 2, 270 + span / 2
    da = math.degrees((dot + gap) / R)

    def build(p):
        p.moveTo(R * math.cos(math.radians(a0 + da)), R * math.sin(math.radians(a0 + da)))
        arc_to(p, 0, 0, R, a0 + da, a1 - da)

    arc = stroke(build, t, cap="round")
    west = (R * math.cos(math.radians(a0)), R * math.sin(math.radians(a0)))
    east = (R * math.cos(math.radians(a1)), R * math.sin(math.radians(a1)))
    return {"p": union(arc, ring(*east, dot, ring_in)), "a": circle(*west, dot)}


# --------------------------------------------------------------------------
# 05 · Ligne de charge — le disque de Plimsoll, marque de sécurité peinte sur
#                         chaque navire marchand ; la ligne sort vers l'avant.
# --------------------------------------------------------------------------

def c05_loadline(R=44.0, t=13.0, bar=8.0, gap=5.0, right=1.9):
    y_cut = bar / 2 + gap
    halves = op(ring(0, 0, R, R - t), rect(-R - 1, -y_cut, 2 * R + 2, 2 * y_cut), DIFF)
    line = rect(-R, -bar / 2, R * (1 + right), bar)
    return {"p": halves, "a": line}
