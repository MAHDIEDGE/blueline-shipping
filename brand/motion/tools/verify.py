#!/usr/bin/env python3
"""Contrôles des exports de brand/motion.

    python3 brand/motion/tools/verify.py

Pour chaque rendu (images PNG sans perte de .frames/, MP4, GIF) :
1. Dernière image (versions « logo seul ») : identique au pixel près aux tracés de logo-horizontal.svg (version claire,
   sur Écume) ou de logo-horizontal-reverse.svg (version sombre, sur Marine nuit), et contre-vérification avec le SVG
   affiché en <img>.
   Fin conteneur : les 480 premières images identiques à la version sombre, le logo sur la paroi aux proportions exactes
   du SVG, la zone d'exclusion libre.
2. Fond : constant (version claire) ou calculé en OKLCH sans retour en arrière et stable avant la fin de sa courbe
   (version sombre) ; ligne orange inchangée.
3. Contraste WCAG des éléments sur le fond, image par image.
4. Specs MP4 et GIF (≤ 5 Mo, première image = image finale), fond du GIF sans marches ni tramage.
5. Fluidité : pas de saut isolé hors bascule volontaire, pas d'image figée au milieu d'un mouvement, tenue finale.
"""

import glob
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
}
GIFS = {"reveal-dark.gif": "dark-16x9", "reveal-container.gif": "container-16x9"}
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


def final_container(d, last, W, H, frames, same_dir):
    # 1. le début est exactement la version sombre « logo seul »
    n_logo = len(glob.glob(os.path.join(same_dir, "f[0-9][0-9][0-9][0-9].png")))
    idx = sorted(set(range(0, n_logo, 7)) | {n_logo - 1})
    worst = max(int(np.abs(img(frames[i]) - img(os.path.join(same_dir, f"f{i:04d}.png"))).max()) for i in idx)
    check(worst == 0, f"les {n_logo} premières images = version sombre « logo seul » ({len(idx)} images comparées, "
                      f"dont la dernière) : écart max {worst}/255")
    # 2. le logo sur la paroi : mêmes proportions que logo-horizontal.svg
    C = json.load(open(os.path.join(d, "container.json")))
    bx0, by0, bx1, by1 = C["box"]
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
    E = last[zy0:zy1, zx0:zx1]
    near = np.zeros(E.shape[:2], dtype=bool)
    for c in (C["colors"]["wall"], C["colors"]["corrugation"]):
        near |= np.abs(E - hexrgb(c)).max(axis=2) <= 2
    near |= ~ring
    stray = ring & ~near & ~dilate(near & ring)   # lissage paroi / tôle toléré
    check(not stray.any(), f"zone d'exclusion ({ex1 - ex0:.0f} × {ey1 - ey0:.0f} u, 1 x autour du logo) : la bande "
                           f"autour du logo ne montre que la paroi et la tôle ({int(stray.sum())} pixel étranger)")
    return n_logo


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
    if cfg.get("container"):
        n_bg = final_container(d, last, W, H, frames, os.path.join(FRAMES, cfg["same_as"]))
    else:
        final_logo(d, last, W, H)
        n_bg = n

    # Une seule lecture de chaque image : fond, ligne orange, énergie de mouvement du contenu
    hy = round(lay["Hc"])
    bg_px, orange, e = [], set(), []
    prev, pbg = None, None
    for i, f in enumerate(frames):
        cur = img(f)
        bg_px.append(cur[2, 2].copy())
        if int(1.35 * FPS) <= i < int(3.05 * FPS):
            orange.add(tuple(cur[hy, 8].tolist()))
        cbg = hexrgb(col["frames"][i]["bg"]) if col["frames"][i]["bg"] else cur[2, 2]
        if prev is not None:
            mask = (np.abs(cur - cbg).max(axis=2) > 0) | (np.abs(prev - pbg).max(axis=2) > 0)
            e.append(float((np.abs(cur - prev).max(axis=2) * mask).mean()))
        prev, pbg = cur, cbg
    e = np.array(e)

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


def mockup():
    print("\nmockups/container-dark")
    svg = os.path.join(BRAND, "mockups", "container-dark.svg")
    png = os.path.join(BRAND, "mockups", "container-dark.png")
    src = open(svg, encoding="utf-8").read()
    check(not any(k in src.lower() for k in ("<image", "<text", "filter", "gradient", "<style")),
          f"SVG vectoriel pur ({len(src) / 1024:.0f} Ko) : aucun texte vivant, image, filtre, dégradé ni style")
    w, h = Image.open(png).size
    check(w == 2000, f"PNG {w} × {h} px")


def main():
    only = set(sys.argv[1:])          # ex. : verify.py container-16x9 reveal-container.gif mockup
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
