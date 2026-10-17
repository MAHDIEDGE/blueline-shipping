#!/usr/bin/env node
/*
 * Exporte reveal.html image par image (60 i/s) puis encode avec ffmpeg.
 *
 *   node brand/motion/tools/render.js                    # tout
 *   node brand/motion/tools/render.js dark-16x9 mockup   # certains rendus seulement (mockup = les 3 images fixes)
 *
 * Chaque image est calculée par window.BLS.renderAt(t) avec t = i / 60 : aucune
 * dépendance à l'horloge du navigateur, donc aucune image sautée ni dupliquée.
 * Les images PNG intermédiaires vont dans brand/motion/.frames/ (ignoré par git).
 */
'use strict';

const fs = require('fs');
const path = require('path');
const { spawnSync, execSync } = require('child_process');

function loadPlaywright() {
  try { return require('playwright'); } catch (_) { /* installation globale ? */ }
  try { return require(path.join(execSync('npm root -g').toString().trim(), 'playwright')); } catch (_) { /* rien */ }
  console.error('Playwright est introuvable : npm install --no-save playwright');
  process.exit(1);
}
const { chromium } = loadPlaywright();

const MOTION = path.resolve(__dirname, '..');
const LOGOS = path.resolve(MOTION, '..', 'logos', 'concept-05');
const FRAMES = path.join(MOTION, '.frames');
const FPS = 60;

// Version claire (fond Écume constant), version sombre (Bleu Coque → Marine nuit), et les fins conteneur, port
// et navire (version sombre).
const JOBS = {
  'light-16x9':     { query: 'format=16x9', W: 1920, H: 1080, mp4: 'reveal-light-16x9.mp4' },
  'light-1x1':      { query: 'format=1x1', W: 1080, H: 1080, mp4: 'reveal-light-1x1.mp4' },
  'dark-16x9':      { query: 'format=16x9&theme=dark', W: 1920, H: 1080, mp4: 'reveal-dark-16x9.mp4', gif: 'reveal-dark.gif' },
  'dark-1x1':       { query: 'format=1x1&theme=dark', W: 1080, H: 1080, mp4: 'reveal-dark-1x1.mp4' },
  'container-16x9': { query: 'format=16x9&theme=dark&ending=container', W: 1920, H: 1080,
                      mp4: 'reveal-container-16x9.mp4', gif: 'reveal-container.gif' },
  'port-16x9':      { query: 'format=16x9&theme=dark&ending=port', W: 1920, H: 1080,
                      mp4: 'reveal-port-16x9.mp4', gif: 'reveal-port.gif' },
  'port-1x1':       { query: 'format=1x1&theme=dark&ending=port', W: 1080, H: 1080, mp4: 'reveal-port-1x1.mp4' },
  'ship-16x9':      { query: 'format=16x9&theme=dark&ending=ship', W: 1920, H: 1080,
                      mp4: 'reveal-ship-16x9.mp4', gif: 'reveal-ship.gif' },
  'ship-1x1':       { query: 'format=1x1&theme=dark&ending=ship', W: 1080, H: 1080, mp4: 'reveal-ship-1x1.mp4' },
};
// Images fixes (générées par build_container.py et build_scenes.py), rendues en PNG 2000 px
const MOCKUPS = ['container-dark', 'port-night', 'ship-night'].map((n) => ({
  svg: path.resolve(MOTION, '..', 'mockups', `${n}.svg`), W: 2000, H: 1125,
}));

// GIF (signatures e-mail, messageries) : 800 px, 30 i/s.
// Il commence sur l'image finale (logo, ou conteneur) : Outlook pour Windows n'affiche que la première image
// d'un GIF, et une boucle qui part de l'image finale est sans couture (fin → retour au début → animation → fin).
// Une palette par image (stats_mode=single, new=1) : le fond qui change de couleur à chaque image
// garde sa teinte exacte, sans marches ni tramage.
// Fins port et navire : à partir de l'apparition des étoiles (et pour la tenue initiale), une palette commune de
// 256 couleurs, calculée sur ces images-là : une étoile fixe garde exactement la même couleur d'une image à
// l'autre (avec une palette par image, elle changerait de quelques niveaux tant que la scène bouge : scintillement).
const GIF = { width: 800, fps: 30, hold: 1.5, fade: 0.5 };

const pad = (n) => String(n).padStart(4, '0');

function run(cmd, args) {
  console.log('  $ ' + [cmd, ...args.map((a) => (/[\s;,\[\]]/.test(a) ? `"${a}"` : a))].join(' '));
  const r = spawnSync(cmd, args, { stdio: ['ignore', 'inherit', 'inherit'] });
  if (r.status !== 0) { console.error(`${cmd} a échoué (code ${r.status})`); process.exit(1); }
}

async function capture(browser, name, job) {
  const dir = path.join(FRAMES, name);
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(dir, { recursive: true });
  const page = await browser.newPage({ viewport: { width: job.W, height: job.H }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  const url = 'file://' + path.join(MOTION, 'reveal.html') + `?export=1&${job.query}`;
  await page.goto(url);
  await page.waitForFunction(() => window.BLS);
  const { DURATION } = await page.evaluate(() => ({ DURATION: window.BLS.DURATION }));
  const total = Math.round(DURATION * FPS);
  const t0 = Date.now();
  const colors = [];
  for (let i = 0; i < total; i++) {
    colors.push(await page.evaluate((t) => { window.BLS.renderAt(t); return window.BLS.colorsAt(t); }, i / FPS));
    await page.screenshot({ path: path.join(dir, `f${pad(i)}.png`) });
  }
  // Images supplémentaires pour le GIF : retour au début (l'image finale s'efface, le fond reprend sa couleur de départ)
  if (job.gif) {
    const n = Math.round(GIF.fade * GIF.fps);
    for (let j = 0; j < n; j++) {
      await page.evaluate((u) => window.BLS.renderTail(u), (j + 1) / n);
      await page.screenshot({ path: path.join(dir, `fade${pad(j)}.png`) });
    }
  }
  fs.writeFileSync(path.join(dir, 'colors.json'), JSON.stringify({ frames: colors }));
  const L = await page.evaluate(() => window.BLS.layout());
  const S = await page.evaluate(() => window.BLS.scene());
  if (/ending=(container|port|ship)/.test(job.query)) {
    const C = await page.evaluate(() => window.BLS.container());
    fs.writeFileSync(path.join(dir, 'container.json'), JSON.stringify({ box: C.box, wall: C.wall, exclusion: C.exclusion, logo: C.logo, colors: C.colors, framing: C.framing }));
    if (S) fs.writeFileSync(path.join(dir, 'scene.json'), JSON.stringify(S));
  }
  await page.close();
  if (errors.length) { console.error(errors); process.exit(1); }
  console.log(`  ${total} images en ${((Date.now() - t0) / 1000).toFixed(1)} s`);

  // Références, à partir du fichier SVG livré (relu ici, indépendamment de reveal.html) :
  //  - reference.png     : ses <path> tels quels, même position, même échelle, même moteur → doit être identique
  //  - reference-img.png : le fichier affiché en <img>, comme sur un site → seuls les contours peuvent différer
  //                        (rééchantillonnage de l'image et arrondi CSS de la boîte au 1/64 px)
  const dark = job.query.includes('theme=dark');
  const svgFile = path.join(LOGOS, dark ? 'logo-horizontal-reverse.svg' : 'logo-horizontal.svg');   // sur L.C.bg
  const src = fs.readFileSync(svgFile, 'utf8');
  const paths = src.match(/<path [^>]*\/>/g).join('');
  const refs = {
    'reference.png': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${job.W} ${job.H}" width="${job.W}" height="${job.H}" style="display:block">`
      + `<rect width="${job.W}" height="${job.H}" fill="${L.C.bg}"/><g transform="translate(${L.X0} ${L.Y0}) scale(${L.k})">${paths}</g></svg>`,
    'reference-img.png': `<img src="file://${svgFile}" style="position:absolute;left:${L.X0}px;top:${L.Y0}px;width:${L.k * L.vb[0]}px;height:${L.k * L.vb[1]}px">`,
  };
  for (const [png, body] of Object.entries(refs)) {
    const html = path.join(dir, png.replace('.png', '.html'));
    fs.writeFileSync(html, `<!doctype html><html><body style="margin:0;background:${L.C.bg}">${body}</body></html>`);
    const rp = await browser.newPage({ viewport: { width: job.W, height: job.H }, deviceScaleFactor: 1 });
    await rp.goto('file://' + html);
    await rp.waitForFunction(() => [...document.images].every((i) => i.complete));
    await rp.screenshot({ path: path.join(dir, png) });
    await rp.close();
  }
  fs.writeFileSync(path.join(dir, 'layout.json'), JSON.stringify({ ...L, total }, null, 2));
  return { dir, total, shareFrom: S ? S.timeline.stars.start : null };
}

function encodeMp4(dir, out) {
  run('ffmpeg', [
    '-y', '-hide_banner', '-loglevel', 'error',
    '-framerate', String(FPS), '-i', path.join(dir, 'f%04d.png'),
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '12', '-tune', 'animation', '-profile:v', 'high',
    '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p',
    '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
    '-r', String(FPS), '-movflags', '+faststart', '-an',
    path.join(MOTION, out),
  ]);
}

function encodeGif(dir, total, out, shareFrom) {
  // Séquence à 30 i/s : image finale (tenue) → retour au début → animation (une image sur deux) → image finale
  const seq = path.join(FRAMES, 'gif-' + path.basename(dir));
  fs.rmSync(seq, { recursive: true, force: true });
  fs.mkdirSync(seq, { recursive: true });
  const step = FPS / GIF.fps;
  const files = [];
  for (let j = 0; j < Math.round(GIF.hold * GIF.fps); j++) files.push(`f${pad(total - 1)}.png`);
  for (let j = 0; j < Math.round(GIF.fade * GIF.fps); j++) files.push(`fade${pad(j)}.png`);
  for (let i = 0; i < total; i += step) files.push(`f${pad(i)}.png`);
  files.forEach((f, n) => fs.copyFileSync(path.join(dir, f), path.join(seq, `g${pad(n)}.png`)));
  if (shareFrom !== null && shareFrom !== undefined) {
    // tenue initiale [0, h) et fin [n0, …) : palette commune ; retour au début et animation [h, n0) : une par image
    const h = Math.round(GIF.hold * GIF.fps);
    const n0 = h + Math.round(GIF.fade * GIF.fps) + Math.ceil(shareFrom * FPS / step);
    const pal = path.join(seq, 'palette.png');
    run('ffmpeg', [
      '-y', '-hide_banner', '-loglevel', 'error', '-framerate', String(GIF.fps), '-i', path.join(seq, 'g%04d.png'),
      '-vf', `select='lt(n\\,${h})+gte(n\\,${n0})',scale=${GIF.width}:-1:flags=lanczos,palettegen=max_colors=256:stats_mode=full`,
      pal,
    ]);
    run('ffmpeg', [
      '-y', '-hide_banner', '-loglevel', 'error', '-framerate', String(GIF.fps), '-i', path.join(seq, 'g%04d.png'), '-i', pal,
      '-filter_complex',
      `[0:v]scale=${GIF.width}:-1:flags=lanczos,split=3[s1][s2][s3];[1:v]split[p1][p2];`
      + `[s1]trim=end_frame=${h},setpts=PTS-STARTPTS[a0];[a0][p1]paletteuse=dither=none[A];`
      + `[s2]trim=start_frame=${h}:end_frame=${n0},setpts=PTS-STARTPTS,split[b1][b2];`
      + '[b1]palettegen=max_colors=64:stats_mode=single[pb];[b2][pb]paletteuse=new=1:dither=none[B];'
      + `[s3]trim=start_frame=${n0},setpts=PTS-STARTPTS[c0];[c0][p2]paletteuse=dither=none[C];`
      + '[A][B][C]concat=n=3:v=1:a=0',
      '-gifflags', '-transdiff', '-loop', '0',
      path.join(MOTION, out),
    ]);
    return;
  }
  run('ffmpeg', [
    '-y', '-hide_banner', '-loglevel', 'error',
    '-framerate', String(GIF.fps), '-i', path.join(seq, 'g%04d.png'),
    '-vf', `scale=${GIF.width}:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=64:stats_mode=single[p];[b][p]paletteuse=new=1:dither=none`,
    '-gifflags', '-transdiff', '-loop', '0',   // transparence inter-images incompatible avec une palette par image
    path.join(MOTION, out),
  ]);
}

async function renderMockups(browser) {
  for (const M of MOCKUPS) {
    const out = M.svg.replace(/\.svg$/, '.png');
    const page = await browser.newPage({ viewport: { width: M.W, height: M.H }, deviceScaleFactor: 1 });
    await page.goto('file://' + M.svg);
    await page.screenshot({ path: out });
    await page.close();
    console.log(`mockup : ${path.relative(path.resolve(MOTION, '..'), out)} (${M.W} × ${M.H})`);
  }
}

(async () => {
  const only = process.argv.slice(2);
  const names = only.length ? only : [...Object.keys(JOBS), 'mockup'];
  const browser = await chromium.launch();
  for (const name of names) {
    if (name === 'mockup') { await renderMockups(browser); continue; }
    const job = JOBS[name];
    if (!job) { console.error(`Rendu inconnu : ${name}`); process.exit(1); }
    console.log(`${name} (${job.W}×${job.H}, ${FPS} i/s, ${job.query})`);
    const { dir, total, shareFrom } = await capture(browser, name, job);
    encodeMp4(dir, job.mp4);
    if (job.gif) encodeGif(dir, total, job.gif, shareFrom);
  }
  await browser.close();
  console.log('Terminé. Contrôle : python3 brand/motion/tools/verify.py');
})();
