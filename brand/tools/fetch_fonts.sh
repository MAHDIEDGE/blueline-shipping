#!/usr/bin/env bash
# Télécharge les polices Google Fonts (SIL Open Font License 1.1) utilisées par build_logos.py.
# Les fichiers vont dans tools/.fonts/ (ignoré par git).
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)/.fonts"
mkdir -p "$DIR"
CSS_URL='https://fonts.googleapis.com/css2?family=Manrope:wght@500;800&family=Space+Grotesk:wght@500;700&family=Outfit:wght@400;600&family=Sora:wght@400;600&family=Readex+Pro:wght@400;600'
# Sans User-Agent de navigateur, l'API renvoie des fichiers TrueType complets.
curl -fsSL "$CSS_URL" | python3 -c '
import re, sys
css = sys.stdin.read()
for fam, w, url in re.findall(r"font-family: .([^\x27]+).;\s*font-style: normal;\s*font-weight: (\d+);\s*src: url\(([^)]+)\)", css):
    print(fam.replace(" ", "") + "-" + w + ".ttf", url)
' | while read -r name url; do
  curl -fsSL -o "$DIR/$name" "$url"
  echo "  $name"
done
