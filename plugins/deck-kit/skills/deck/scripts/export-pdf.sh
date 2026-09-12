#!/usr/bin/env bash
# Design faithful PDF. Headless Chrome, not a screenshot tool.
#
#     ./export-pdf.sh <deck-dir> [out.pdf]
#
# Set $CHROME to override the browser. Any Chromium build works: Chrome,
# Chromium, Brave, Edge. Firefox and Safari do not, because neither one has
# a headless print to PDF that honours the @page rule the way this needs.
set -euo pipefail
DIR="$(cd "${1:-.}" && pwd)"
OUT="${2:-$DIR/deck.pdf}"

find_chrome() {
  [ -n "${CHROME:-}" ] && { printf '%s' "$CHROME"; return; }
  for c in \
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    "/Applications/Chromium.app/Contents/MacOS/Chromium" \
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" \
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" \
    google-chrome google-chrome-stable chromium chromium-browser brave-browser microsoft-edge
  do
    if [ -x "$c" ]; then printf '%s' "$c"; return; fi
    if command -v "$c" >/dev/null 2>&1; then command -v "$c"; return; fi
  done
}

BROWSER="$(find_chrome)"
[ -n "$BROWSER" ] || {
  echo "No Chromium based browser found. Install Google Chrome, or set CHROME to the binary:" >&2
  echo "  CHROME=/path/to/chrome ./export-pdf.sh $DIR" >&2
  exit 1
}

"$BROWSER" --headless --disable-gpu --no-pdf-header-footer \
  --virtual-time-budget=9000 --print-to-pdf="$OUT" "file://$DIR/index.html" 2>/dev/null

EXPECT=$(grep -c '<section class="slide">' "$DIR/index.html")
GOT=$(python3 -c "import sys;d=open(sys.argv[1],'rb').read();print(d.count(b'/Type /Page')-d.count(b'/Type /Pages'))" "$OUT")
echo "$OUT: $GOT pages, expected $EXPECT"
[ "$GOT" = "$EXPECT" ] || { echo "FAIL page count mismatch"; exit 1; }
