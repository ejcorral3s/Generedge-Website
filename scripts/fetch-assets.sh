#!/usr/bin/env bash
#
# Pull the original images off the WordPress site before it goes away, and
# write them into assets/img/ under the names the new site expects.
#
#   bash scripts/fetch-assets.sh
#
# Run this while generedge.com is still served by the old host. Once Isaac's
# hosting is switched off these URLs are gone for good.
#
# Requires: curl. Optional: ImageMagick (`magick` or `convert`) to downscale,
# and `cwebp` if you later want WebP versions.

set -euo pipefail

BASE="https://generedge.com/wp-content/uploads"
DEST="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/assets/img"
mkdir -p "$DEST"

# source path on WordPress  ->  filename in this repo
FILES=(
  "2023/07/logo-color-transparent-800.png|logo.png"
  "2023/10/Hands-Heart-1024x657.png|hands-heart.png"
  "2026/02/Tracey-New.jpg|tracey-wiseman.jpg"
  "2024/08/Stephen-Pool.jpeg|stephen-pool.jpg"
  "2024/05/57237323-view-of-an-architect-and-worker-handshaking-on-construction-site.jpg|handshake.jpg"
)

fail=0
for entry in "${FILES[@]}"; do
  src="${entry%%|*}"
  out="${entry##*|}"
  url="$BASE/$src"
  printf '  %-24s <- %s\n' "$out" "$src"
  if curl -fsSL --max-time 60 -o "$DEST/$out.tmp" "$url"; then
    mv "$DEST/$out.tmp" "$DEST/$out"
  else
    echo "    !! FAILED — $url" >&2
    rm -f "$DEST/$out.tmp"
    fail=1
  fi
done

echo
if [ "$fail" -ne 0 ]; then
  echo "Some downloads failed. There are no placeholders — the committed copies of"
  echo "those files are unchanged, so the site still works. If the old host is"
  echo "already off, restore them from git or from the WordPress backup."
  exit 1
fi

echo "All images downloaded to assets/img/"

# ---------------------------------------------------------------------------
# Optional: downscale the large photos. The layout never renders them wider
# than ~900px, so anything bigger is wasted bytes on every page load.
# ---------------------------------------------------------------------------
if command -v magick >/dev/null 2>&1; then IM=magick
elif command -v convert >/dev/null 2>&1; then IM=convert
else IM=""; fi

if [ -n "$IM" ]; then
  echo "Optimising with ImageMagick..."
  "$IM" "$DEST/tracey-wiseman.jpg" -resize '800x800>' -strip -quality 82 "$DEST/tracey-wiseman.jpg"
  "$IM" "$DEST/stephen-pool.jpg"   -resize '800x800>' -strip -quality 82 "$DEST/stephen-pool.jpg"
  "$IM" "$DEST/handshake.jpg"      -resize '900x900>' -strip -quality 82 "$DEST/handshake.jpg"
  "$IM" "$DEST/hands-heart.png"    -resize '900x900>' -strip "$DEST/hands-heart.png"
  echo "Done."
else
  echo "ImageMagick not found — skipping optimisation (install with: brew install imagemagick)."
fi

echo
echo "og-default.png and apple-touch-icon.png are generated, not hand-made:"
echo "  python3 scripts/make-social-images.py     (needs Pillow)"
echo
echo "If the optimisation step above resized anything, the width/height"
echo "attributes in src/ no longer match the files. Run:"
echo "  python3 scripts/build.py && python3 scripts/check.py"
echo "check.py compares every declared image ratio against the real file and"
echo "will name anything that drifted."
ls -la "$DEST"
