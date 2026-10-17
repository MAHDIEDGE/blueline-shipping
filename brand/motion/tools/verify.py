#!/usr/bin/env python3
"""Contrôles des exports de brand/motion.

    python3 brand/motion/tools/verify.py

Pour chaque rendu (images PNG sans perte de .frames/, MP4, GIF) :
1. Dernière image (versions « logo seul ») : identique au pixel près aux tracés de logo-horizontal.svg (version claire,
   sur Écume) ou de logo-horizontal-reverse.svg (version sombre, sur Marine nuit), et contre-vérification avec le SVG
   affiché en <img>.
   Fin conteneur : les 480 premières images identiques à la version sombre, le logo sur la paroi aux proportions exactes
   du SVG, la zone d'exclusion libre.
   Fins port et navire : jusqu'à 9,8 s identiques à la fin conteneur ; au plan final, logo ≥ 12 % de la largeur
   d'image, zone d'exclusion libre, étoiles fixes hors de la zone et hors de tout objet, ciel exact (bandes de
   1 niveau, sans tramage), lune, orange réservé à la ligne et au feu, feux de 4 px, navire ≈ 85 % de la largeur.
0. Fins « logo seul » et « conteneur » strictement inchangées : empreintes des pixels de chaque image comparées à
   tools/baseline.json.
2. Fond : constant (version claire) ou calculé en OKLCH sans retour en arrière et stable avant la fin de sa courbe
   (version sombre) ; ligne orange inchangée.
3. Contraste WCAG des éléments sur le fond, image par image.
4. Specs MP4 et GIF (≤ 5 Mo, première image = image finale), fond du GIF sans marches ni tramage ; ciel des GIF
   port et navire sans bandes, étoiles sans scintillement.
5. Fluidité : pas de saut isolé hors bascule volontaire, pas d'image figée au milieu d'un mouvement, tenue finale.
"""

import glob
import hashlib
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

MOTION = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND = os.path.dirname(MOTION)
FRAMES = os.path.join(MOTION, ".frames")
FPS = 60
NAVY, WHITE, ORANGE, DAY, MARINE = "#0B2F6E", "#FFFFFF", "#FF6A33", "#F3F5F9", "#0A1A3A"

JOBS = {
    "light-16x9": dict(mp4="reveal-light-16x9.mp4", W=1920, H=1080, theme="light", curve=None),
    "light-1x1": dict(mp4="reveal-light-1x1.mp4", W=1080, H=1080, theme="light", curve=None),
    "dark-16x9": dict(mp4="reveal-dark-16x9.mp4", W=1920, H=1080, theme="dark", curve=(0.0, 5.4)),
    "dark-1x1": dict(mp4="reveal-dark-1x1.mp4", W=1080, H=1080, theme="dark", curve=(0.0, 5.4)),
    "container-16x9": dict(mp4="reveal-container-16x9.mp4", W=1920, H=1080, theme="dark", curve=(0.0, 5.4),
                           container=True, same_as="dark-16x9"),
    # fins port et navire : identiques à la fin conteneur jusqu'à 9,8 s (en 1:1, à la version sombre jusqu'à 8,0 s,
    # puis l'une à l'autre jusqu'à 9,8 s)
    "port-16x9": dict(mp4="reveal-port-16x9.mp4", W=1920, H=1080, theme="dark", curve=(0.0, 5.4), container=True,
                      scene="port", same_as="container-16x9", upto=9.8),
    "port-1x1": dict(mp4="reveal-port-1x1.mp4", W=1080, H=1080, theme="dark", curve=(0.0, 5.4), container=True,
                     scene="port", same_as="dark-1x1"),
    "ship-16x9": dict(mp4="reveal-ship-16x9.mp4", W=1920, H=1080, theme="dark", curve=(0.0, 5.4), container=True,
                      scene="ship", same_as="container-16x9", upto=9.8),
    "ship-1x1": dict(mp4="reveal-ship-1x1.mp4", W=1080, H=1080, theme="dark", curve=(0.0, 5.4), container=True,
                     scene="ship", same_as="dark-1x1", twin="port-1x1", upto_twin=9.8),
}
GIFS = {"reveal-dark.gif": "dark-16x9", "reveal-container.gif": "container-16x9",
        "reveal-port.gif": "port-16x9", "reveal-ship.gif": "ship-16x9"}
BASELINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "baseline.json")
ECUME = DAY
GIF = dict(width=800, fps=30, hold=45, fade=15)
FAIL, NOTES = [], []


# --------------------------------------------------------------------------
def img(path):
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.int16)


def check(ok, msg):
    print(("  OK     " if ok else "  ÉCHEC  ") + msg)
    if not ok:
        FAIL.append(msg)


def note(msg):
    print("  LIMITE " + msg)
    NOTES.append(msg)


def info(msg):
    print("  INFO   " + msg)


def hexrgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], dtype=np.int16)


def lum(h):
    def lin(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(float(v)) for v in hexrgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    x, y = sorted([lum(a), lum(b)], reverse=True)
    return (x + 0.05) / (y + 0.05)


def ink(a, bg):
    return np.abs(a - bg).max(axis=2).astype(np.float64)


def dilate(m):
    out = m.copy()
    for oy in (-1, 0, 1):
        for ox in (-1, 0, 1):
            out |= np.roll(np.roll(m, oy, 0), ox, 1)
    return out


def erode(m):
    return ~dilate(~m)


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-show_entries",
                          "stream=width,height,r_frame_rate,nb_read_frames,codec_name,pix_fmt,color_space"
                          ":format=duration,size,nb_streams", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    s, f = j["streams"][0], j["format"]
    num, den = (int(v) for v in s["r_frame_rate"].split("/"))
    return {"w": s["width"], "h": s["height"], "fps": num / den, "frames": int(s["nb_read_frames"]),
            "codec": s["codec_name"], "pix": s.get("pix_fmt"), "space": s.get("color_space"),
            "dur": float(f["duration"]), "size": int(f["size"]), "streams": int(f["nb_streams"])}


def decode(path, select, out):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", path, "-vf", f"select={select}", "-vsync", "0", out],
                   check=True)


def psnr(a, b):
    mse = np.mean((a.astype(np.float64) - b) ** 2)
    return float("inf") if mse == 0 else 10 * np.log10(255 ** 2 / mse)


# --------------------------------------------------------------------------
def final_logo(d, last, W, H):
    ref = img(os.path.join(d, "reference.png"))
    diff = np.abs(last - ref).max(axis=2)
    check(diff.max() == 0, f"dernière image = tracés du SVG du logo sur le fond final (même position, même échelle) : "
                           f"{int((diff > 0).sum())} pixels d'écart")
    alt = img(os.path.join(d, "reference-img.png"))
    bg0 = ref[0, 0]
    ia, ib = ink(last, bg0), ink(alt, bg0)
    yy, xx = np.mgrid[0:H, 0:W]
    dx = (ia * xx).sum() / ia.sum() - (ib * xx).sum() / ib.sum()
    dy = (ia * yy).sum() / ia.sum() - (ib * yy).sum() / ib.sum()
    d2 = np.abs(last - alt).max(axis=2) > 0
    band = dilate(dilate(dilate(ib > 0) & ~erode(ib > 0)))
    outside = int((d2 & ~band).sum())
    check(abs(dx) < 0.25 and abs(dy) < 0.25 and outside == 0,
          f"vs le SVG affiché en <img> (rééchantillonné) : centre décalé de ({dx:+.3f}, {dy:+.3f}) px, "
          f"{int(d2.sum())} pixels de contour lissés autrement, {outside} à plus de 2 px d'un contour")
    ys, xs = np.nonzero(ib > 0)
    cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
    check(abs(cx - W / 2) <= 1 and abs(cy - H / 2) <= 1, f"logo centré : centre ({cx:.1f}, {cy:.1f})")


def pixel_hash(path):
    return hashlib.sha256(np.asarray(Image.open(path).convert("RGB")).tobytes()).hexdigest()


def same_start(frames, ref_dir, n, label):
    """Les n premières images sont identiques, pixel pour pixel, à celles d'un autre rendu (toutes comparées)."""
    diff = [i for i in range(n) if pixel_hash(frames[i]) != pixel_hash(os.path.join(ref_dir, f"f{i:04d}.png"))]
    check(not diff, f"les {n} premières images (jusqu'à {(n - 1) / FPS:.2f} s) = {label}, comparées une à une : "
                    f"{len(diff)} différente(s){' (' + str(diff[:5]) + ')' if diff else ''}")


def final_container(d, last, W, H, frames, same_dir, cfg):
    # 1. le début est exactement la version sombre « logo seul » (fin conteneur), ou la fin conteneur (port, navire)
    n_logo = len(glob.glob(os.path.join(same_dir, "f[0-9][0-9][0-9][0-9].png")))
    if cfg.get("upto"):
        same_start(frames, same_dir, int(round(cfg["upto"] * FPS)) + 1, f"rendu {cfg['same_as']}")
        n_logo = 480
    else:
        same_start(frames, same_dir, n_logo, "version sombre « logo seul »")
    if cfg.get("twin"):
        same_start(frames, os.path.join(FRAMES, cfg["twin"]), int(round(cfg["upto_twin"] * FPS)) + 1,
                   f"rendu {cfg['twin']}")
    # 2. le logo sur la paroi : mêmes proportions que logo-horizontal.svg
    C = json.load(open(os.path.join(d, "container.json")))
    bx0, by0, bx1, by1 = C["box"]
    if cfg.get("scene"):
        cam = json.load(open(os.path.join(d, "scene.json")))["camera"]
        s, tx, ty = cam["s"], cam["tx"], cam["ty"]
    else:
        fr = C["framing"]
        s = fr["width"] * W / (bx1 - bx0)
        tx, ty = W / 2 - (bx0 + bx1) / 2 * s, fr["center_y"] * H - (by0 + by1) / 2 * s
    lx0, ly0, lx1, ly1 = C["logo"]
    X0, Y0, X1, Y1 = tx + lx0 * s, ty + ly0 * s, tx + lx1 * s, ty + ly1 * s
    pad = 3
    crop = last[int(Y0) - pad:int(np.ceil(Y1)) + pad, int(X0) - pad:int(np.ceil(X1)) + pad]
    m = (np.abs(crop - hexrgb(WHITE)).max(axis=2) < 60) | (np.abs(crop - hexrgb(ORANGE)).max(axis=2) < 60)
    ys, xs = np.nonzero(m)
    w_px, h_px = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
    ratio, expect = w_px / h_px, (lx1 - lx0) / (ly1 - ly0)
    check(abs(w_px - (X1 - X0)) <= 2 and abs(h_px - (Y1 - Y0)) <= 2,
          f"logo sur la paroi : {w_px} × {h_px} px pour {X1 - X0:.1f} × {Y1 - Y0:.1f} attendus ; proportions "
          f"{ratio:.3f} (logo-horizontal-reverse.svg : {expect:.3f})")
    if cfg.get("scene"):
        check(w_px >= 0.12 * W, f"logo lisible au plan final : {w_px} px = {w_px / W * 100:.1f} % de la largeur "
                                f"d'image (≥ 12 %)")
    wx0, wy0, wx1, wy1 = C["wall"]
    info(f"rapport largeur du logo / longueur de la paroi : mesuré {w_px / ((wx1 - wx0) * s):.3f}, géométrie "
         f"{(lx1 - lx0) / (wx1 - wx0):.3f} ; hauteur du logo / hauteur de paroi {(ly1 - ly0) / (wy1 - wy0):.3f}")
    for k_, label in (("wall", "paroi"), ("corrugation", "tôle ondulée")):
        info(f"{label} {C['colors'][k_]}")
    cw = contrast(WHITE, C["colors"]["wall"])
    co = contrast(ORANGE, C["colors"]["wall"])
    check(cw >= 7, f"texte blanc et anneau sur la paroi Marine nuit : {cw:.2f}:1 (≥ 7:1)")
    print(f"  INFO   ligne orange sur la paroi : {co:.2f}:1 (élément graphique ; seuil WCAG non-texte 3:1)")
    cc = contrast(C["colors"]["corrugation"], C["colors"]["wall"])
    check(1.1 <= cc <= 1.6, f"tôle ondulée visible mais discrète : contraste {cc:.2f}:1 avec la paroi")
    check(C["colors"]["sky"] == MARINE and C["colors"]["wall"] == MARINE,
          f"ciel et paroi en Marine nuit {MARINE} (transition invisible depuis le fond final)")
    # 3. zone d'exclusion : 1 x (= rayon de l'anneau) autour du logo. L'absence de tout élément dans la zone est
    #    garantie géométriquement par build_container.py (intersection exacte) ; ici, on vérifie à l'image que la
    #    bande entre le logo et la limite de la zone ne montre que la paroi et sa tôle ondulée.
    ex0, ey0, ex1, ey1 = C["exclusion"]
    zx0, zy0, zx1, zy1 = (int(tx + ex0 * s) + 1, int(ty + ey0 * s) + 1, int(tx + ex1 * s) - 1, int(ty + ey1 * s) - 1)
    ring = np.ones((zy1 - zy0, zx1 - zx0), dtype=bool)
    ring[int(Y0) - zy0 - 1:int(np.ceil(Y1)) - zy0 + 1, int(X0) - zx0 - 1:int(np.ceil(X1)) - zx0 + 1] = False
    E = last[zy0:zy1, zx0:zx1].astype(np.float64)
    # chaque pixel de la bande doit être un mélange paroi / tôle ondulée (lissage des lignes compris) : rien d'autre
    a, b = hexrgb(C["colors"]["wall"]).astype(np.float64), hexrgb(C["colors"]["corrugation"]).astype(np.float64)
    u = np.clip(((E - a) @ (b - a)) / ((b - a) @ (b - a)), 0, 1)
    resid = np.abs(E - (a + u[..., None] * (b - a))).max(axis=2)
    stray = ring & (resid > 3)
    check(not stray.any(), f"zone d'exclusion ({ex1 - ex0:.0f} × {ey1 - ey0:.0f} u, 1 x autour du logo) : la bande "
                           f"autour du logo ne montre que la paroi et la tôle ({int(stray.sum())} pixel étranger)")
    return n_logo, (s, tx, ty), (X0, Y0, X1, Y1), (tx + ex0 * s, ty + ey0 * s, tx + ex1 * s, ty + ey1 * s)


def final_scene(d, last, W, H, cam, logo_box, zone):
    S = json.load(open(os.path.join(d, "scene.json")))
    s, tx, ty = cam
    C = json.load(open(os.path.join(d, "container.json")))
    bx0, by0, bx1, by1 = C["box"]
    box = (tx + bx0 * s, ty + by0 * s, tx + bx1 * s, ty + by1 * s)
    # Étoiles : nombre, taille, opacité, place
    st = S["stars"]
    check(40 <= len(st) <= 70 and all(1 <= x[2] <= 2.5 and 0.25 <= x[3] <= 0.7 for x in st),
          f"{len(st)} étoiles (40 à 70), diamètres {min(x[2] for x in st):.1f} à {max(x[2] for x in st):.1f} px, "
          f"opacités {min(x[3] for x in st):.2f} à {max(x[3] for x in st):.2f}")
    t_end = S["timeline"]["pull"][1]
    check(all(S["timeline"]["pull"][0] < x[4] and x[5] <= t_end for x in st),
          f"les étoiles apparaissent en fondu pendant le second recul ({min(x[4] for x in st):.2f} – "
          f"{max(x[5] for x in st):.2f} s)")

    def inside(x, y, r, b, m=0.0):
        return b[0] - m - r <= x <= b[2] + m + r and b[1] - m - r <= y <= b[3] + m + r
    bad = [x for x in st if inside(x[0], x[1], x[2] / 2, zone) or inside(x[0], x[1], x[2] / 2, box)]
    check(not bad, f"aucune étoile dans la zone d'exclusion du logo ni derrière le conteneur et son texte : {bad or 'aucune'}")
    # Ciel : bandes exactes (1 niveau par marche, sans tramage), du haut à l'horizon
    sky = S["sky"]
    exp = np.zeros((H, 3), dtype=np.int16)
    for y0, y1, c in sky:
        exp[y0:y1] = hexrgb(c)
    yh = int(sky[-1][0]) - 2
    match = (np.abs(last[:yh] - exp[:yh, None, :]).max(axis=2) == 0)
    best = int(match.sum(axis=0).max())
    steps = [int(np.abs(hexrgb(a[2]) - hexrgb(b[2])).max()) for a, b in zip(sky, sky[1:])]
    check(best == yh and max(steps) <= 1,
          f"ciel en {len(sky)} bandes {sky[0][2]} → {sky[-1][2]} : marche maximale {max(steps)} niveau, colonne "
          f"témoin identique au calcul sur {best}/{yh} lignes (aucun tramage)")
    check(sky[-1][2] == MARINE and sky[0][2] == S["tones"]["sky_top"],
          f"deux tons : {sky[0][2]} en haut, Marine nuit {MARINE} à l'horizon, interpolés en OKLCH")
    bgsky = exp[:, None, :]
    # Lune : croissant blanc Écume à 85 %, en haut à droite, diamètre ≈ 7 % de la hauteur
    mx0, my0, md = S["moon"]["box"]
    win = last[int(my0) - 4:int(my0 + md) + 5, int(mx0) - 4:int(mx0 + md) + 5]
    mm = win.min(axis=2) > 120
    ys, xs = np.nonzero(mm)
    dpx = ys.max() - ys.min() + 1
    peak = win[mm].max(axis=0)
    yref = int(my0 + md / 2)
    want = 0.85 * hexrgb(ECUME) + 0.15 * exp[yref]
    check(abs(dpx - 0.07 * H) <= 3 and mx0 > 0.6 * W and my0 < 0.25 * H and np.abs(peak - want).max() <= 3,
          f"lune : croissant de {dpx} px de haut ({dpx / H * 100:.1f} % de la hauteur), en haut à droite "
          f"({mx0 + md / 2:.0f}, {my0 + md / 2:.0f}), teinte {tuple(int(v) for v in peak)} pour Écume à 85 % "
          f"{tuple(int(round(v)) for v in want)}")
    # Feux : 4 px ; l'orange n'apparaît que sur la ligne du logo et sur le feu orange
    lights = [(lt["x"] * s + tx, lt["y"] * s + ty, lt["color"]) for lt in S["lights"]]
    n_or = sum(1 for lt in lights if lt[2].upper() == ORANGE)
    sizes = []
    for x, y, c in lights:
        xi, yi = int(round(x)), int(round(y))
        w = last[yi - 6:yi + 7, xi - 6:xi + 7]
        m = np.abs(w - exp[yi - 6:yi + 7, None, :]).max(axis=2) > 40
        ys, xs = np.nonzero(m)
        sizes.append((xs.max() - xs.min() + 1, ys.max() - ys.min() + 1))
    check(n_or == 1 and all(3 <= a <= 5 and 3 <= b <= 5 for a, b in sizes),
          f"feux de 4 px : {sizes} ; un seul feu orange")
    R, G, B = last[..., 0], last[..., 1], last[..., 2]
    orange = (R - np.maximum(G, B)) > 30
    lx0, ly0, lx1, ly1 = logo_box
    keep = np.zeros_like(orange)
    keep[int(ly0) - 2:int(np.ceil(ly1)) + 3, int(lx0) - 2:int(np.ceil(lx1)) + 3] = True
    for x, y, c in lights:
        if c.upper() == ORANGE:
            keep[int(y) - 4:int(y) + 6, int(x) - 4:int(x) + 6] = True
    stray = int((orange & ~keep).sum())
    check(stray == 0, f"orange réservé à la ligne du logo et au feu de signalisation : {stray} pixel orange ailleurs")
    if S.get("ship"):
        sw = (S["ship"][1] - S["ship"][0]) * s / W
        check(0.83 <= sw <= 0.87, f"navire : {sw * 100:.1f} % de la largeur d'image (≈ 85 %)")
    # Étoiles visibles au plan final, sur le ciel seul (aucun trait ni objet autour)
    hidden, crowded = [], []
    for x, y, dd, o, *_ in st:
        xi, yi = int(round(x)), int(round(y))
        w = last[yi - 4:yi + 5, xi - 4:xi + 5]
        e = exp[yi - 4:yi + 5, None, :]
        lift = (w - e).max()
        if lift < 8:
            hidden.append((x, y))
        ring_ = np.ones(w.shape[:2], dtype=bool)
        ring_[2:7, 2:7] = False
        if np.abs(w - e).max(axis=2)[ring_].max() > 2:
            crowded.append((x, y))
    check(not hidden and not crowded, f"chaque étoile est visible et seule sur le ciel au plan final "
                                      f"(masquées : {hidden or 'aucune'} ; touchant un objet : {crowded or 'aucune'})")
    return S


def job(name, cfg):
    W, H = cfg["W"], cfg["H"]
    d = os.path.join(FRAMES, name)
    print(f"\n{name}  ({W}×{H}, {cfg['theme']}{', fin conteneur' if cfg.get('container') else ''})")
    lay = json.load(open(os.path.join(d, "layout.json")))
    col = json.load(open(os.path.join(d, "colors.json")))
    n = lay["total"]
    frames = [os.path.join(d, f"f{i:04d}.png") for i in range(n)]
    last = img(frames[-1])

    # 1. Image finale
    S = None
    if cfg.get("container"):
        n_bg, cam, logo_box, zone = final_container(d, last, W, H, frames, os.path.join(FRAMES, cfg["same_as"]), cfg)
        if cfg.get("scene"):
            S = final_scene(d, last, W, H, cam, logo_box, zone)
    else:
        final_logo(d, last, W, H)
        n_bg = n
    # étoiles : une fois apparues, plus aucun changement (ni scintillement ni occultation) jusqu'à la fin
    star_patches = []
    if S:
        for x, y, dd, o, t0, t1, *_ in S["stars"]:
            xi, yi = int(round(x)), int(round(y))
            star_patches.append((int(np.ceil(t1 * FPS)), yi, xi, last[yi - 3:yi + 4, xi - 3:xi + 4].copy()))
    star_dev = 0
    hashes = []

    # Une seule lecture de chaque image : fond, ligne orange, énergie de mouvement du contenu
    hy = round(lay["Hc"])
    bg_px, orange, e = [], set(), []
    prev, pbg = None, None
    for i, f in enumerate(frames):
        cur = img(f)
        hashes.append(hashlib.sha256(cur.astype(np.uint8).tobytes()).hexdigest())
        for i0, yi, xi, ref in star_patches:
            if i >= i0:
                star_dev = max(star_dev, int(np.abs(cur[yi - 3:yi + 4, xi - 3:xi + 4] - ref).max()))
        bg_px.append(cur[2, 2].copy())
        if int(1.35 * FPS) <= i < int(3.05 * FPS):
            orange.add(tuple(cur[hy, 8].tolist()))
        cbg = hexrgb(col["frames"][i]["bg"]) if col["frames"][i]["bg"] else cur[2, 2]
        if prev is not None:
            mask = (np.abs(cur - cbg).max(axis=2) > 0) | (np.abs(prev - pbg).max(axis=2) > 0)
            e.append(float((np.abs(cur - prev).max(axis=2) * mask).mean()))
        prev, pbg = cur, cbg
    e = np.array(e)
    if S:
        check(star_dev == 0, f"étoiles fixes : une fois apparues, aucune ne change d'un niveau jusqu'à la fin "
                             f"(écart max {star_dev}/255)")
    base = json.load(open(BASELINE)) if os.path.exists(BASELINE) else {}
    if name in base:
        if UPDATE:
            base[name] = {"frames": n, "last": hashes[-1], "all": hashlib.sha256("".join(hashes).encode()).hexdigest()}
            json.dump(base, open(BASELINE, "w"), indent=1, ensure_ascii=False)
            info(f"empreintes de {name} mises à jour dans {os.path.basename(BASELINE)}")
        else:
            b = base[name]
            same_all = b["frames"] == n and b["all"] == hashlib.sha256("".join(hashes).encode()).hexdigest()
            check(same_all and b["last"] == hashes[-1],
                  f"strictement inchangé : les {n} images, dont la dernière, ont les mêmes pixels qu'avant "
                  f"l'ajout des fins port et navire ({os.path.basename(BASELINE)})")

    # 2. Fond (jusqu'à la fin du logo seul) et ligne orange
    bgs = [c["bg"] for c in col["frames"][:n_bg]]
    worst = max(int(np.abs(bg_px[i] - hexrgb(b)).max()) for i, b in enumerate(bgs))
    check(worst == 0, f"fond rendu = fond calculé en OKLCH sur {n_bg} images (écart max {worst}/255)")
    Ls = [lum(b) for b in bgs]
    rises = [(i, (Ls[i] - Ls[i - 1]) / Ls[i - 1]) for i in range(1, n_bg) if Ls[i] > Ls[i - 1]]
    # l'arrondi 8 bits du chemin OKLCH peut remonter un canal d'un niveau : invisible sous ~1 % de luminance
    check(all(r < 0.01 for _, r in rises),
          f"le fond ne s'éclaircit jamais de façon perceptible : "
          f"{', '.join(f'image {i} +{r * 100:.2f} %' for i, r in rises) or 'aucune remontée'} (seuil 1 %)")
    if cfg["curve"] is None:
        check(set(bgs) == {DAY}, f"fond Écume {DAY} constant sur les {n_bg} images : {sorted(set(bgs))}")
    else:
        first_final = next(i for i in range(n_bg) if bgs[i] == bgs[-1])
        a, b = cfg["curve"]
        check(bgs[-1] == MARINE and all(x == bgs[-1] for x in bgs[first_final:]) and first_final / FPS <= b + 1e-9,
              f"fond final {bgs[-1]} atteint à {first_final / FPS:.3f} s (courbe {a}–{b} s) puis stable")
        steps = [int(np.abs(hexrgb(bgs[i]) - hexrgb(bgs[i - 1])).max()) for i in range(1, n_bg)]
        info(f"fond {bgs[0]} → {bgs[-1]} ; pas maximal {max(steps)}/255 par image ; à 2,0 s : "
             f"{(Ls[0] - Ls[120]) / (Ls[0] - Ls[-1]) * 100:.0f} % de la variation de luminance")
    acc = {c["accent"] for c in col["frames"]}
    check(len(acc) == 1 and orange == {tuple(hexrgb(next(iter(acc))).tolist())},
          f"ligne orange {next(iter(acc))} inchangée (calcul et image, de 1,35 à 3,05 s) : {orange}")

    # 3. Contraste élément / fond
    fgs_set = {c["fg"] for c in col["frames"]}
    expect_fg = NAVY if cfg["theme"] == "light" else WHITE
    check(fgs_set == {expect_fg}, f"coque, anneau et texte toujours en {expect_fg} (aucune bascule) : {sorted(fgs_set)}")
    cr = [contrast(c["fg"], c["bg"]) for c in col["frames"][:n_bg]]
    need = 4.5 if cfg["theme"] == "light" else 7.0
    check(min(cr) >= need, f"contraste coque / anneau / texte sur le fond, sur toutes les images : mini {min(cr):.2f}:1 "
                           f"(≥ {need}:1)")
    oc = [contrast(c["accent"], c["bg"]) for c in col["frames"][:n_bg]]
    info(f"ligne orange sur le fond : {min(oc):.2f}:1 à {max(oc):.2f}:1 (élément graphique, seuil WCAG non-texte 3:1)")

    # 4. MP4
    p = probe(os.path.join(MOTION, cfg["mp4"]))
    check((p["w"], p["h"]) == (W, H) and abs(p["fps"] - FPS) < 1e-9 and p["frames"] == n and p["streams"] == 1,
          f"{cfg['mp4']} : {p['w']}×{p['h']}, {p['fps']:g} i/s, {p['frames']} images, {p['dur']:.3f} s, {p['codec']} "
          f"{p['pix']} {p['space']}, sans son, {p['size'] / 1e6:.2f} Mo")
    out = os.path.join(d, "mp4-last.png")
    decode(os.path.join(MOTION, cfg["mp4"]), f"eq(n\\,{n - 1})", out)
    q = psnr(img(out), last)
    check(q > 40, f"dernière image du MP4 vs la même image sans perte : PSNR {q:.1f} dB (H.264 4:2:0)")

    # 5. Fluidité (énergie du contenu : l'assombrissement d'un niveau du fond n'est pas une saccade)
    spikes = [i + 1 for i in range(1, len(e) - 1) if e[i] > 0.05 and e[i] > 4 * max(e[i - 1], e[i + 1], 1e-3)]
    # image figée entre deux images en mouvement visible (sous 0,05, le mouvement est sous-pixel : en fin de
    # ralenti, Chrome peut ne pas redessiner un déplacement de quelques centièmes de pixel)
    holes = [i + 1 for i in range(1, len(e) - 1) if e[i] == 0 and e[i - 1] > 0.05 and e[i + 1] > 0.05]
    check(not spikes, f"pas de saut isolé (saccade) : {spikes or 'aucun'}")
    check(not holes, f"pas d'image figée au milieu d'un mouvement : {holes or 'aucune'}")
    tail = int(np.argmax(e[::-1] > 0))
    check(tail >= 59, f"image finale figée sur les {tail + 1} dernières images ({(tail + 1) / FPS:.2f} s)")
    return frames


def gif(name, src, src_frames):
    print(f"\n{name}  (source : {src})")
    g = os.path.join(MOTION, name)
    p = probe(g)
    check(p["w"] == GIF["width"] and abs(p["fps"] - GIF["fps"]) < 1e-9 and p["size"] <= 5 * 1024 * 1024,
          f"{p['w']}×{p['h']}, {p['fps']:g} i/s, {p['frames']} images, {p['dur']:.2f} s, {p['size'] / 1e6:.2f} Mo "
          f"(max 5 Mo)")
    with tempfile.TemporaryDirectory() as t:
        decode(g, "1", os.path.join(t, "g%04d.png"))
        gf = sorted(glob.glob(os.path.join(t, "g*.png")))
        start = GIF["hold"] + GIF["fade"]
        flat, errs = [], []
        for k in range(len(gf) - start):
            src_img = img(src_frames[2 * k])
            if np.ptp(src_img[:60].reshape(-1, 3), axis=0).max() == 0:       # source : bandeau supérieur uni
                gimg = img(gf[start + k])
                flat.append(int(np.ptp(gimg[:24].reshape(-1, 3), axis=0).max()))
                errs.append(int(np.abs(gimg[0, 0] - src_img[0, 0]).max()))
        check(max(flat) == 0, f"aucun tramage dans le fond ({len(flat)} images à fond uni) : écart max {max(flat)}/255")
        check(max(errs) <= 2, f"fond du GIF = fond de la vidéo à chaque image (pas de marches) : écart max {max(errs)}/255")
        first = img(gf[0])
        ref = Image.open(src_frames[-1]).convert("RGB").resize(first.shape[1::-1], Image.LANCZOS)
        q = psnr(first, np.asarray(ref, dtype=np.int16))
        check(q > 30, f"première image = image finale (Outlook n'affiche qu'elle) : PSNR {q:.1f} dB")
        sj = os.path.join(FRAMES, src, "scene.json")
        if os.path.exists(sj):
            S = json.load(open(sj))
            W0, H0 = JOBS[src]["W"], JOBS[src]["H"]
            k = first.shape[1] / W0
            # ciel : référence = la même réduction ffmpeg, sans palette, du ciel seul et de l'image finale ; sur les
            # pixels de ciel pur, le GIF ne s'en écarte pas de plus d'un niveau (aucune bande ajoutée)
            sky = np.zeros((H0, W0, 3), dtype=np.uint8)
            for y0, y1, c in S["sky"]:
                sky[y0:y1] = hexrgb(c)
            Image.fromarray(sky).save(os.path.join(t, "sky.png"))
            exp, small = (scale_like_gif(os.path.join(t, "sky.png"), t), scale_like_gif(src_frames[-1], t))
            pure = np.abs(small - exp).max(axis=2) == 0
            pure[int((S["sky"][-1][0] - 4) * k):] = False
            pairs = pure[:-1] & pure[1:]
            err = int(np.abs(first - exp).max(axis=2)[pure].max())
            dif = first[1:] - first[:-1]
            step = int(np.abs(dif).max(axis=2)[pairs].max())
            back = int((-dif).max(axis=2)[pairs].max())
            check(err <= 1 and step <= 2 and back <= 1,
                  f"ciel sans bandes ({int(pure.sum())} pixels de ciel pur) : écart max {err}/255 à la même réduction "
                  f"sans palette, marche max {step}, retour max {back}")
            # étoiles : une fois apparues, plus aucune variation d'une image à l'autre (pas de scintillement)
            dev = 0
            start = GIF["hold"] + GIF["fade"]
            frames_g = {}
            for x, y, dd, o, t0, t1, *_ in S["stars"]:
                xi, yi = int(round(x * k)), int(round(y * k))
                i0 = start + int(np.ceil(t1 * FPS / 2))
                ref_p = first[yi - 2:yi + 3, xi - 2:xi + 3]
                for gi in list(range(0, GIF["hold"])) + list(range(i0, len(gf))):
                    if gi not in frames_g:
                        frames_g[gi] = img(gf[gi])
                    dev = max(dev, int(np.abs(frames_g[gi][yi - 2:yi + 3, xi - 2:xi + 3] - ref_p).max()))
            check(dev == 0, f"étoiles sans scintillement : écart max {dev}/255 sur chaque étoile, de son apparition à "
                            f"la fin et pendant la tenue initiale")


def scale_like_gif(png, tmp):
    out = os.path.join(tmp, "scaled-" + os.path.basename(png))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", png, "-vf", f"scale={GIF['width']}:-1:flags=lanczos", out],
                   check=True)
    return img(out)


def mockup():
    for name, src_job in (("container-dark", "container-16x9"), ("port-night", "port-16x9"), ("ship-night", "ship-16x9")):
        print(f"\nmockups/{name}")
        svg = os.path.join(BRAND, "mockups", f"{name}.svg")
        png = os.path.join(BRAND, "mockups", f"{name}.png")
        src = open(svg, encoding="utf-8").read().lower()
        if name == "container-dark":
            check(not any(k in src for k in ("<image", "<text", "filter", "gradient", "<style")),
                  f"SVG vectoriel pur ({len(src) / 1024:.0f} Ko) : aucun texte vivant, image, filtre, dégradé ni style")
        else:
            check(not any(k in src for k in ("<image", "<text", "filter", "<style")) and src.count("<lineargradient") == 1,
                  f"SVG vectoriel pur ({len(src) / 1024:.0f} Ko) : aucun texte vivant, image, filtre ni style ; un seul "
                  f"dégradé, celui du ciel (continu, pour l'impression)")
        w, h = Image.open(png).size
        check((w, h) == (2000, 1125), f"PNG {w} × {h} px")
        last = sorted(glob.glob(os.path.join(FRAMES, src_job, "f[0-9][0-9][0-9][0-9].png")))
        if last:
            a = np.asarray(Image.open(png).convert("RGB").resize((1920, 1080), Image.LANCZOS), dtype=np.int16)
            q = psnr(a, img(last[-1]))
            check(q > 40, f"même plan que la dernière image de {src_job} : PSNR {q:.1f} dB (> 40 dB)")
        sj = os.path.join(FRAMES, src_job, "scene.json")
        if name != "container-dark" and os.path.exists(sj):
            mockup_scene(png, json.load(open(sj)))


def mockup_scene(png, S):
    """Contrôles ciblés de l'image fixe (le PSNR global ne voit pas une étoile ou un feu manquant)."""
    M = np.asarray(Image.open(png).convert("RGB"), dtype=np.int16)
    f = M.shape[1] / JOBS["port-16x9"]["W"]
    missing = []
    for x, y, dd, o, *_ in S["stars"]:
        xi, yi = int(round(x * f)), int(round(y * f))
        around = M[yi - 7:yi + 8, xi - 7:xi + 8].reshape(-1, 3)
        bg = np.median(around, axis=0)
        if (M[yi - 2:yi + 3, xi - 2:xi + 3] - bg).max() < 8:
            missing.append((x, y))
    mx0, my0, md = (v * f for v in S["moon"]["box"])
    win = M[int(my0) - 4:int(my0 + md) + 5, int(mx0) - 4:int(mx0 + md) + 5]
    ys, xs = np.nonzero(win.min(axis=2) > 120)
    dpx = (ys.max() - ys.min() + 1) if len(ys) else 0
    s, tx, ty = S["camera"]["s"], S["camera"]["tx"], S["camera"]["ty"]
    lights = []
    for lt in S["lights"]:
        xi, yi = int(round((lt["x"] * s + tx) * f)), int(round((lt["y"] * s + ty) * f))
        w = M[yi - 4:yi + 5, xi - 4:xi + 5]
        ok = ((w[..., 0] - np.maximum(w[..., 1], w[..., 2])) > 30).any() if lt["color"].upper() == ORANGE \
            else (w.min(axis=2) > 120).any()
        lights.append(ok)
    top, hor = M[2:12, 40:400].reshape(-1, 3).mean(axis=0), hexrgb(S["sky"][0][2])
    check(not missing and abs(dpx - 0.07 * M.shape[0]) <= 3 and all(lights) and np.abs(top - hor).max() <= 2,
          f"contenu : {len(S['stars']) - len(missing)}/{len(S['stars'])} étoiles visibles à leur place, lune de {dpx} px "
          f"(7 % de {M.shape[0]} = {0.07 * M.shape[0]:.0f}), feux présents {lights}, haut du ciel "
          f"{tuple(int(round(v)) for v in top)} pour {S['sky'][0][2]}")


UPDATE = "--update-baseline" in sys.argv


def main():
    only = set(a for a in sys.argv[1:] if not a.startswith("--"))   # ex. : verify.py port-16x9 reveal-port.gif mockup
    frames = {}
    for name, cfg in JOBS.items():
        if not only or name in only:
            frames[name] = job(name, cfg)
    for g, src in GIFS.items():
        if not only or g in only:
            frames.setdefault(src, [os.path.join(FRAMES, src, f"f{i:04d}.png")
                                    for i in range(len(glob.glob(os.path.join(FRAMES, src, "f[0-9][0-9][0-9][0-9].png"))))])
            gif(g, src, frames[src])
    if not only or "mockup" in only:
        mockup()
    print("\n" + ("Tous les contrôles passent." if not FAIL else f"{len(FAIL)} contrôle(s) en échec.")
          + (f" {len(NOTES)} limite(s) documentée(s)." if NOTES else ""))
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
