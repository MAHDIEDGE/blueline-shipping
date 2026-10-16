#!/usr/bin/env python3
"""Génère brand/index.html, la page de présentation des 5 concepts.

Page autonome : HTML + CSS, aucun framework, aucune police ni ressource externe.
Les spécimens typographiques sont insérés en tracés SVG.
"""

import math
import os

from blsvg import HERE, Font, bounds, move, svg, union
from concepts import CONCEPTS, contrast

ROOT = os.path.dirname(HERE)


def esc(s):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # typographie française : espaces insécables autour de « » : ; ! ?
    for a, b in (("« ", "«&nbsp;"), (" »", "&nbsp;»"), (" :", "&nbsp;:"), (" ;", "&nbsp;;"),
                 (" !", "&nbsp;!"), (" ?", "&nbsp;?"), (" → ", "&nbsp;→ ")):
        s = s.replace(a, b)
    return s


def md_inline(s):
    """**gras** → <strong>, le reste échappé."""
    parts = esc(s).split("**")
    return "".join(f"<strong>{p}</strong>" if i % 2 else p for i, p in enumerate(parts))


def iso6346(owner, serial):
    """Chiffre de contrôle ISO 6346 d'un numéro de conteneur (ex. BLSU + 001234)."""
    vals, v = {}, 10
    for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        if v % 11 == 0:
            v += 1
        vals[ch] = v
        v += 1
    code = owner + serial
    total = sum((vals[c] if c.isalpha() else int(c)) * 2 ** i for i, c in enumerate(code))
    return total % 11 % 10


def specimen(c):
    """Spécimen typographique en tracés (police de titrage + police de texte)."""
    f1, f2 = Font(c.font_main), Font(c.font_sec)
    l1, _ = f1.text("Aa Bb Gg Rr 0123456789", 30)
    l2, _ = f2.text("Transit, dédouanement, conteneurs — Shanghai, Alger", 15)
    b1 = bounds(l1)
    paths = [move(l1, -b1[0], 30), move(l2, -bounds(l2)[0], 30 + 22 + 15)]
    y = 30 + 22 + 15
    if c.num == "05":
        l3, _ = f1.text("بلو لاين للشحن", 24)
        b3 = bounds(l3)
        y += 20 + 24
        paths.append(move(l3, -b3[0], y))
    b = (0, 0, max(bounds(p)[2] for p in paths), y + 8)
    return svg([(c.palette["primary"], union(*paths))], b, f"Spécimen {c.family}")


def min_width(c):
    """Largeur minimale du logo horizontal (même règle que le README)."""
    import re
    path = os.path.join(ROOT, "logos", c.dir, "README.md")
    m = re.search(r"\| Horizontale \| (\d+) px", open(path, encoding="utf-8").read())
    return int(m.group(1))


def concept_section(c, i):
    p = c.palette
    d = f"logos/{c.dir}"
    code = f"BLSU 001234 {iso6346('BLSU', '001234')}"
    intent = "".join(f"<li>{md_inline(t)}</li>" for t in c.intention)
    swatches = "".join(
        f'<div class="sw"><span class="chip" style="background:{p[k]}"></span>'
        f'<span class="sw-name">{esc(c.names[k])}</span><code>{p[k]}</code></div>'
        for k in ("primary", "accent", "accent_dark", "night", "paper"))
    mw = min_width(c)
    kraft = "#C9AE86"
    return f"""
<section class="concept" id="{c.dir}" aria-labelledby="t-{c.dir}"
  style="--p:{p['primary']};--a:{p['accent']};--a2:{p['accent_dark']};--night:{p['night']};--paper:{p['paper']}">
  <header class="c-head">
    <span class="c-num">{c.num}</span>
    <div>
      <h2 id="t-{c.dir}">{esc(c.name)}</h2>
      <p class="c-tag">{esc(c.tagline)}</p>
    </div>
  </header>
  <ol class="intent">{intent}</ol>

  <h3>Déclinaisons — fond clair / fond sombre</h3>
  <div class="variants">
    <figure class="pair span2">
      <div class="duo">
        <div class="tile" style="background:#fff"><img class="h" src="{d}/logo-horizontal.svg" alt="Logo horizontal, couleurs, fond clair"></div>
        <div class="tile" style="background:var(--night)"><img class="h" src="{d}/logo-horizontal-reverse.svg" alt="Logo horizontal, couleurs, fond sombre"></div>
      </div>
      <figcaption><code>logo-horizontal.svg</code> · <code>logo-horizontal-reverse.svg</code></figcaption>
    </figure>
    <figure class="pair">
      <div class="duo">
        <div class="tile" style="background:#fff"><img class="v" src="{d}/logo-vertical.svg" alt="Logo vertical, fond clair"></div>
        <div class="tile" style="background:var(--night)"><img class="v" src="{d}/logo-vertical-reverse.svg" alt="Logo vertical, fond sombre"></div>
      </div>
      <figcaption><code>logo-vertical.svg</code> · <code>-reverse</code></figcaption>
    </figure>
    <figure class="pair">
      <div class="duo">
        <div class="tile" style="background:#fff"><img class="i" src="{d}/icon.svg" alt="Icône sur fond clair"></div>
        <div class="tile" style="background:var(--night)"><img class="i" src="{d}/icon.svg" alt="Icône sur fond sombre"></div>
      </div>
      <figcaption><code>icon.svg</code></figcaption>
    </figure>
    <figure class="pair span2 row">
      <div class="duo">
        <div class="tile" style="background:#fff"><img class="m" src="{d}/logo-mono-black.svg" alt="Monochrome noir sur blanc"></div>
        <div class="tile" style="background:{kraft}"><img class="m" src="{d}/logo-mono-black.svg" alt="Monochrome noir sur carton"></div>
      </div>
      <figcaption><code>logo-mono-black.svg</code> — blanc, carton</figcaption>
    </figure>
    <figure class="pair span2 row">
      <div class="duo">
        <div class="tile" style="background:var(--p)"><img class="m" src="{d}/logo-mono-white.svg" alt="Monochrome blanc sur le bleu"></div>
        <div class="tile" style="background:#111"><img class="m" src="{d}/logo-mono-white.svg" alt="Monochrome blanc sur noir"></div>
      </div>
      <figcaption><code>logo-mono-white.svg</code> — bleu, noir</figcaption>
    </figure>
  </div>

  <h3>Petites tailles — rendu réel</h3>
  <div class="sizes">
    <div class="strip" style="background:#fff">
      <img src="{d}/icon.svg" width="16" height="16" alt="16 px"><span>16</span>
      <img src="{d}/icon.svg" width="24" height="24" alt="24 px"><span>24</span>
      <img src="{d}/icon.svg" width="48" height="48" alt="48 px"><span>48</span>
      <img src="{d}/logo-horizontal.svg" style="width:{mw}px" alt="Logo horizontal à la taille minimale"><span>{mw} px (min.)</span>
    </div>
    <div class="strip dark" style="background:var(--night)">
      <img src="{d}/icon.svg" width="16" height="16" alt="16 px"><span>16</span>
      <img src="{d}/icon.svg" width="24" height="24" alt="24 px"><span>24</span>
      <img src="{d}/icon.svg" width="48" height="48" alt="48 px"><span>48</span>
      <img src="{d}/logo-horizontal-reverse.svg" style="width:{mw}px" alt="Logo horizontal à la taille minimale"><span>{mw} px (min.)</span>
    </div>
    <div class="tabs" aria-hidden="true">
      <div class="tab"><img src="{d}/icon.svg" width="16" height="16" alt=""><span>Blue Line Shipping — Suivi</span></div>
      <div class="tab ghost"><span>Nouvel onglet</span></div>
    </div>
  </div>

  <h3>Mises en situation</h3>
  <div class="mockups">
    <figure class="mock web">
      <div class="browser">
        <div class="chrome"><i></i><i></i><i></i><span class="url"></span></div>
        <div class="site-nav">
          <img src="{d}/logo-horizontal.svg" alt="Logo dans l'en-tête du site">
          <span class="links"><span>Services</span><span>Suivi</span><span>Dédouanement</span><span>Contact</span></span>
          <span class="cta">Demander un devis</span>
        </div>
        <div class="site-hero">
          <span class="eyebrow">Chine → Algérie</span>
          <span class="h">Vos importations, de l'usine chinoise à votre dépôt.</span>
          <span class="sub">Transport conteneurisé · Transit · Dédouanement</span>
          <span class="rule"></span>
        </div>
      </div>
      <figcaption>En-tête de site</figcaption>
    </figure>
    <figure class="mock card">
      <div class="cards">
        <div class="bc front">
          <div class="bc-in">
            <img src="{d}/logo-horizontal.svg" alt="Carte de visite, recto">
            <div class="who"><b>Prénom Nom</b><span>Responsable import</span><span>+213 00 00 00 00 · contact@exemple.dz</span></div>
          </div>
          <span class="bc-rule"></span>
        </div>
        <div class="bc back"><img src="{d}/logo-vertical-reverse.svg" alt="Carte de visite, verso"></div>
      </div>
      <figcaption>Carte de visite 85 × 55 mm, recto / verso</figcaption>
    </figure>
    <figure class="mock ctr-wrap">
      <div class="ctr">
        <div class="ctr-side">
          <img src="{d}/logo-horizontal-reverse.svg" alt="Logo sur le flanc d'un conteneur">
          <span class="ctr-code">{code}<br>22G1</span>
          <i class="cc tl"></i><i class="cc tr"></i><i class="cc bl"></i><i class="cc br"></i>
        </div>
      </div>
      <figcaption>Flanc de conteneur 20 pieds (6,06 × 2,59 m)</figcaption>
    </figure>
  </div>

  <div class="specs">
    <div>
      <h3>Palette</h3>
      <div class="swatches">{swatches}</div>
      <p class="note">{md_inline(c.accent_why)}</p>
    </div>
    <div>
      <h3>Typographie — {esc(c.family)}</h3>
      <div class="spec-img">{specimen(c)}</div>
      <p class="note">{esc(c.weights)}. Google Fonts, SIL Open Font License 1.1. {md_inline(c.type_why)}</p>
      <p class="note"><a href="{d}/README.md">README du concept</a> : zones d'exclusion, tailles minimales, usages.</p>
    </div>
  </div>
</section>"""


def overview_card(c):
    d = f"logos/{c.dir}"
    p = c.palette
    return f"""
<a class="ov" href="#{c.dir}" style="--night:{p['night']}">
  <span class="ov-t"><b>{c.num}</b> {esc(c.name)}</span>
  <span class="ov-l"><img src="{d}/logo-horizontal.svg" alt="Concept {c.num}, fond clair"></span>
  <span class="ov-d"><img src="{d}/logo-horizontal-reverse.svg" alt="Concept {c.num}, fond sombre"></span>
  <span class="ov-i">
    <img src="{d}/icon.svg" width="48" height="48" alt="Icône 48 px">
    <img src="{d}/icon.svg" width="24" height="24" alt="Icône 24 px">
    <span class="ov-tag">{esc(c.tagline)}</span>
  </span>
</a>"""


CSS = """
:root{--ink:#0E1726;--muted:#566175;--bg:#F3F4F6;--card:#fff;--line:#E1E4EA;--radius:14px}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
img{display:block;max-width:100%}
a{color:#1D4ED8}
code{font:13px/1.4 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:var(--muted)}
.wrap{max-width:1280px;margin:0 auto;padding:0 24px}
.top{background:#0A1A3A;color:#fff;padding:56px 0 48px}
.top .kicker{font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:#9FB3D9;margin:0 0 12px}
.top h1{font-size:clamp(30px,4.4vw,52px);line-height:1.08;margin:0 0 16px;letter-spacing:-.01em;font-weight:700}
.top p{max-width:760px;color:#C9D4EA;margin:0 0 24px}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chips a{color:#fff;text-decoration:none;border:1px solid rgba(255,255,255,.28);padding:8px 14px;border-radius:999px;font-size:14px}
.chips a:hover{background:rgba(255,255,255,.1)}
h2{font-size:30px;line-height:1.15;margin:0}
h3{font-size:14px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:40px 0 14px;font-weight:600}
.block{padding:56px 0 8px}
.block>h2{margin-bottom:8px}
.block>p{color:var(--muted);margin:0 0 24px;max-width:780px}
/* aperçu */
.overview{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:14px}
.ov{display:flex;flex-direction:column;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;text-decoration:none;color:inherit;transition:transform .15s,box-shadow .15s}
.ov:hover{transform:translateY(-2px);box-shadow:0 10px 30px rgba(10,26,58,.12)}
.ov-t{padding:12px 14px;font-size:15px}
.ov-t b{color:var(--muted);font-weight:600;margin-right:6px}
.ov-l,.ov-d{height:118px;display:flex;align-items:center;justify-content:center;padding:18px}
.ov-l{background:#fff;border-top:1px solid var(--line)}
.ov-d{background:var(--night)}
.ov-l img,.ov-d img{max-height:46px;max-width:100%}
.ov-i{display:flex;align-items:center;gap:10px;padding:14px;flex-wrap:wrap}
.ov-tag{flex:1 1 100%;font-size:13px;color:var(--muted);line-height:1.4}
/* concept */
.concept{background:var(--card);border:1px solid var(--line);border-radius:22px;padding:40px;margin:40px 0}
.c-head{display:flex;gap:22px;align-items:flex-start}
.c-num{font-size:15px;font-weight:700;color:#fff;background:var(--p);border-radius:10px;padding:8px 12px;line-height:1;margin-top:6px}
.c-tag{margin:8px 0 0;color:var(--muted);font-size:18px}
.intent{margin:22px 0 0;padding-left:20px;max-width:900px}
.intent li{margin:6px 0}
.intent li::marker{color:var(--a);font-weight:700}
.variants{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}
.pair{margin:0;display:flex;flex-direction:column;gap:8px}
.pair.span2{grid-column:span 2}
.duo{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));border-radius:12px;overflow:hidden;border:1px solid var(--line);flex:1}
.span2 .duo{grid-template-columns:1fr}
.span2.row .duo{grid-template-columns:1fr 1fr}
.span2.row .tile{min-height:120px}
.tile{display:flex;align-items:center;justify-content:center;padding:22px;min-height:160px}
.span2 .tile{min-height:132px}
.tile img.h{height:58px;max-width:100%;object-fit:contain}
.tile img.v{height:112px;max-width:100%;object-fit:contain}
.tile img.i{width:88px;height:88px}
.tile img.m{height:40px;max-width:100%;object-fit:contain}
figcaption{font-size:13px;color:var(--muted)}
.sizes{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.strip{display:flex;align-items:center;gap:10px;padding:18px 20px;border-radius:12px;border:1px solid var(--line);flex-wrap:wrap}
.strip span{font-size:12px;color:var(--muted);margin-right:12px}
.strip.dark span{color:#A9B6CE}
.strip img{flex:none}
.tabs{grid-column:1/-1;display:flex;gap:2px;background:#DEE1E7;padding:8px 8px 0;border-radius:12px 12px 0 0;max-width:520px}
.tab{display:flex;align-items:center;gap:8px;background:#fff;padding:8px 12px;border-radius:8px 8px 0 0;font-size:12px;min-width:0}
.tab span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tab.ghost{background:transparent;color:var(--muted)}
/* maquettes */
.mockups{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}
.mock{margin:0;display:flex;flex-direction:column;gap:8px}
.mock.web{grid-column:1/-1}
.browser{border:1px solid var(--line);border-radius:12px;overflow:hidden;background:#fff}
.chrome{display:flex;align-items:center;gap:6px;padding:10px 12px;background:#ECEEF2;border-bottom:1px solid var(--line)}
.chrome i{width:10px;height:10px;border-radius:50%;background:#C9CED8}
.chrome .url{flex:1;height:22px;background:#fff;border-radius:6px;margin-left:12px;max-width:420px}
.site-nav{display:flex;align-items:center;gap:24px;padding:16px 28px;border-bottom:1px solid var(--line);flex-wrap:wrap}
.site-nav img{height:38px;width:auto}
.links{display:flex;gap:22px;font-size:14px;color:#2B3445;margin-left:auto;flex-wrap:wrap}
.cta{background:var(--p);color:#fff;font-size:14px;font-weight:600;padding:10px 16px;border-radius:8px;white-space:nowrap}
.site-hero{display:flex;flex-direction:column;gap:10px;background:var(--night);color:#fff;padding:48px 28px 44px;position:relative}
.site-hero .eyebrow{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--a2)}
.site-hero .h{font-size:clamp(22px,3vw,34px);font-weight:700;line-height:1.15;max-width:640px}
.site-hero .sub{color:#C5D0E4;font-size:15px}
.site-hero .rule{display:block;width:120px;height:4px;background:var(--a2);margin-top:8px}
.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;padding:22px;background:#E9ECF1;border-radius:12px;flex:1;align-items:center}
.bc{aspect-ratio:85/55;border-radius:6px;box-shadow:0 1px 2px rgba(0,0,0,.08),0 8px 24px rgba(10,26,58,.14);position:relative;overflow:hidden;container-type:inline-size}
.bc.front{background:#fff}
.bc-in{position:absolute;inset:0;padding:9cqw 8cqw;display:flex;flex-direction:column;justify-content:space-between}
.bc-in img{height:15cqw;width:auto;max-width:78%;align-self:flex-start}
.who{display:flex;flex-direction:column;font-size:4.1cqw;line-height:1.35;color:#3B4556}
.who b{color:var(--p);font-size:5.2cqw}
.bc-rule{position:absolute;left:0;bottom:0;height:2.6cqw;width:38%;background:var(--a)}
.bc.back{background:var(--p);display:flex;align-items:center;justify-content:center}
.bc.back img{height:46cqw;width:auto;max-width:70%;object-fit:contain}
.ctr-wrap{justify-content:space-between}
.ctr{padding:26px 18px 30px;background:linear-gradient(#DCE3EC,#DCE3EC 78%,#B9C1CC 78%);border-radius:12px;flex:1;display:flex;align-items:center}
.ctr-side{position:relative;width:100%;aspect-ratio:6.06/2.59;background-color:var(--p);
  background-image:repeating-linear-gradient(90deg,rgba(255,255,255,.07) 0 7px,rgba(0,0,0,.16) 7px 9px,rgba(0,0,0,0) 9px 17px,rgba(255,255,255,.04) 17px 19px);
  box-shadow:inset 0 7px 0 rgba(0,0,0,.28),inset 0 -8px 0 rgba(0,0,0,.32),inset 6px 0 0 rgba(0,0,0,.22),inset -6px 0 0 rgba(0,0,0,.22),0 14px 18px -10px rgba(0,0,0,.45);
  display:flex;align-items:center;justify-content:center;container-type:inline-size}
.ctr-side img{width:52%;height:auto}
.ctr-code{position:absolute;right:5cqw;top:7cqw;font:600 2.3cqw/1.25 ui-monospace,Menlo,Consolas,monospace;color:#fff;letter-spacing:.06em;text-align:right;opacity:.92}
.cc{position:absolute;width:3.2cqw;height:3.2cqw;background:#00000055;border:1px solid #ffffff22}
.cc.tl{left:0;top:0}.cc.tr{right:0;top:0}.cc.bl{left:0;bottom:0}.cc.br{right:0;bottom:0}
.specs{display:grid;grid-template-columns:1fr 1fr;gap:40px;margin-top:8px}
.swatches{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px}
.sw{display:flex;flex-direction:column;gap:4px;font-size:13px;min-width:0}
.chip{height:64px;border-radius:10px;border:1px solid rgba(0,0,0,.08)}
.sw-name{font-weight:600;line-height:1.25}
.note{font-size:14px;color:var(--muted);max-width:620px}
.spec-img{background:var(--paper);border-radius:12px;padding:20px;border:1px solid var(--line)}
.spec-img svg{width:100%;height:auto;max-height:150px}
/* recommandation */
.reco{background:#0A1A3A;color:#E7ECF6;border-radius:22px;padding:44px;margin:40px 0}
.reco h2{color:#fff;margin-bottom:6px}
.reco .lead{font-size:19px;color:#fff;max-width:900px}
.reco-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.3fr);gap:36px;align-items:start;margin-top:22px}
.reco-logo{background:#fff;border-radius:16px;padding:36px;display:flex;flex-direction:column;gap:28px;align-items:center}
.reco-logo img{max-height:84px}
.reco h3{color:#9FB3D9}
.reco ul,.reco ol{padding-left:20px;margin:0}
.reco li{margin:8px 0}
.reco a{color:#9CC3FF}
footer{color:var(--muted);font-size:14px;padding:12px 0 48px}
@media (max-width:1100px){.overview{grid-template-columns:repeat(3,minmax(0,1fr))}.variants{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:820px){
  .wrap{padding:0 16px}.concept,.reco{padding:22px;border-radius:16px}
  .overview{grid-template-columns:1fr 1fr}.mockups,.specs,.sizes,.reco-grid{grid-template-columns:1fr}
  .pair.span2{grid-column:auto}.variants{grid-template-columns:1fr}
  .swatches{grid-template-columns:repeat(3,minmax(0,1fr))}.site-nav .links{display:none}
  .c-head{gap:14px}h2{font-size:24px}
}
@media (max-width:520px){.overview{grid-template-columns:1fr}.cards{grid-template-columns:1fr}}
"""

RECO = """
<section class="reco" id="recommandation" aria-labelledby="t-reco">
  <h2 id="t-reco">Recommandation : concept 05, Ligne de charge</h2>
  <p class="lead">C'est le seul signe qui porte à la fois le nom (une ligne), le métier (le maritime) et la promesse
  (la sécurité, la conformité). Il le fait avec deux formes et deux couleurs.</p>
  <div class="reco-grid">
    <div class="reco-logo">
      <img src="logos/concept-05/logo-horizontal.svg" alt="Concept 05, logo horizontal">
      <img src="logos/concept-05/icon.svg" alt="Concept 05, icône" style="width:96px">
    </div>
    <div>
      <h3>Pourquoi</h3>
      <ul>
        <li><strong>Le sens juste.</strong> Le disque de Plimsoll est la ligne de charge que chaque navire marchand
        s'engage à respecter. Pour un transitaire et commissionnaire en douane, dire « nous respectons la ligne »,
        c'est dire fiabilité et conformité. Les importateurs ne cherchent pas autre chose.</li>
        <li><strong>« Blue Line » sans littéralité.</strong> La ligne est le sujet du signe, mais ce n'est ni une vague
        ni un soulignement : c'est un repère technique, compris des gens du métier, et qui reste abstrait et
        élégant pour les autres.</li>
        <li><strong>La meilleure tenue technique.</strong> Deux demi-anneaux et une ligne : le signe reste net à 16 px,
        se peint au pochoir sur un conteneur, se brode et se tamponne. L'orange international reste visible de loin
        sur la tôle comme sur un écran.</li>
        <li><strong>Prêt pour l'Algérie.</strong> Readex Pro couvre le latin et l'arabe : documents douaniers,
        factures, signalétique et ERP bilingues avec une seule typographie.</li>
      </ul>
      <h3>Itérations proposées</h3>
      <ol>
        <li><strong>Antériorité.</strong> Recherche INAPI (Algérie), OMPI (Global Brand Database) et
        CNIPA (Chine), avec une attention particulière aux cocardes « anneau + barre », celle du métro de
        Londres en tête. La ligne asymétrique et l'anneau coupé nous en éloignent, mais il faut le vérifier.</li>
        <li><strong>Optique fine.</strong> Ajuster le rapport ligne/anneau (0,6 à 0,7), la coupure et la longueur
        de la ligne selon le support. Dessiner une variante favicon 16 px dédiée (ligne plus épaisse, coupure
        fermée).</li>
        <li><strong>Version bilingue.</strong> Composer « بلو لاين للشحن » en Readex Pro, puis les lockups FR/AR
        horizontal et vertical pour les camions, les documents et l'enseigne.</li>
        <li><strong>Système graphique.</strong> Faire de la ligne orange un élément récurrent (en-têtes de documents,
        séparateurs, statuts de l'ERP, bande sur les conteneurs) et fixer les équivalents Pantone, RAL et CMJN
        sur échantillons peints.</li>
        <li><strong>Tests terrain.</strong> Pochoir à l'échelle 1 sur conteneur, flanc de camion, tampon
        douanier, broderie, en-tête et favicon de l'ERP.</li>
      </ol>
      <p class="note" style="color:#B9C6DE">Deuxième choix : le <a href="#concept-01">concept 01, Horizon</a>,
      le plus robuste en petite taille. On peut garder son idée de coupe pochoir pour les marquages de
      conteneurs.</p>
    </div>
  </div>
</section>
"""


def main():
    sections = "".join(concept_section(c, i) for i, c in enumerate(CONCEPTS))
    cards = "".join(overview_card(c) for c in CONCEPTS)
    chips = "".join(f'<a href="#{c.dir}">{c.num} · {esc(c.name)}</a>' for c in CONCEPTS)
    html = f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Blue Line Shipping — Concepts de logo</title>
<meta name="description" content="Cinq concepts de logo pour Blue Line Shipping, logistique maritime Chine → Algérie.">
<link rel="icon" href="logos/concept-05/icon.svg" type="image/svg+xml">
<style>{CSS}</style>
</head>
<body>
<header class="top">
  <div class="wrap">
    <p class="kicker">Blue Line Shipping SARL · Identité visuelle · Exploration</p>
    <h1>Cinq concepts de logo</h1>
    <p>Logistique maritime Chine → Algérie : transport conteneurisé, transit, dédouanement. Un bleu profond
    dominant, un accent par concept, une ligne comme fil conducteur. Chaque variante est montrée sur fond
    clair et sur fond sombre, en petite taille et en situation.</p>
    <nav class="chips" aria-label="Concepts">{chips}<a href="#recommandation">Recommandation</a></nav>
  </div>
</header>
<main class="wrap">
  <section class="block" id="apercu" aria-labelledby="t-apercu">
    <h2 id="t-apercu">Les cinq concepts côte à côte</h2>
    <p>Logo horizontal sur fond clair puis sur fond sombre, et icône à 48 px et à 24 px.</p>
    <div class="overview">{cards}</div>
  </section>
  {sections}
  {RECO}
</main>
<footer class="wrap">
  Fichiers source : <code>brand/logos/concept-0X/</code>. Tout est régénérable avec
  <code>brand/tools/build_logos.py</code> et <code>build_index.py</code> (voir <code>brand/README.md</code>).
  Polices Google Fonts sous licence SIL OFL 1.1.
</footer>
</body>
</html>
"""
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(html)
    print("index.html: ok")


if __name__ == "__main__":
    main()
