#!/usr/bin/env bash
# Generate a Gamma presentation from a finished deck.
#
#     ${CLAUDE_PLUGIN_ROOT}/skills/deck/scripts/gamma.sh <deck-dir>
#
# RUN THIS YOURSELF, IN YOUR OWN TERMINAL. Not through Claude Code.
#
# The key is read from a silent prompt into a shell variable, used for one
# request, and unset. It is never written to a file, never exported to a child
# process's environment beyond curl's own header, never echoed, and never put on
# a command line where it would land in shell history or an agent transcript.
# That is the whole reason this is a script you run and not a tool call.
#
# Gamma cannot edit an existing gamma and cannot import a GitHub Pages URL.
# This produces a NEW, SEPARATE artifact in Gamma's own look. It does not sync
# back. The HTML deck stays the source of truth.
set -euo pipefail

DIR="${1:?usage: gamma.sh <deck-dir>}"
IDX="$DIR/index.html"
[ -f "$IDX" ] || { echo "no index.html in $DIR" >&2; exit 1; }

# Slide text, one card per slide, separated the way Gamma expects.
TEXT="$(python3 - "$IDX" <<'PY'
import re, sys, html
src = open(sys.argv[1], encoding="utf-8").read()
out = []
for s in re.findall(r'<section class="slide">.*?</section>', src, flags=re.S):
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    s = re.sub(r"<br\s*/?>", " ", s)
    s = re.sub(r"</(h1|h2|h3|p|li|div|td|tr)>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    lines = [re.sub(r"\s+", " ", l).strip() for l in s.split("\n")]
    lines = [l for l in lines if l]
    if lines:
        out.append("\n".join(lines))
print("\n\n---\n\n".join(out))
PY
)"

CARDS="$(grep -c '<section class="slide">' "$IDX")"
echo "$DIR: $CARDS slides, $(printf '%s' "$TEXT" | wc -c | tr -d ' ') characters of text."
echo

read -rsp "Paste your Gamma API key (input hidden, nothing is stored): " GAMMA_KEY
echo
[ -n "$GAMMA_KEY" ] || { echo "no key given, nothing sent" >&2; exit 1; }

BODY="$(TEXT="$TEXT" CARDS="$CARDS" python3 - <<'PY'
import json, os
print(json.dumps({
    "inputText": os.environ["TEXT"],
    "textMode": "preserve",
    "format": "presentation",
    "numCards": int(os.environ["CARDS"]),
    "cardSplit": "inputTextBreaks",
}))
PY
)"

RESP="$(curl -sS -X POST https://public-api.gamma.app/v0.2/generations \
  -H "X-API-KEY: $GAMMA_KEY" \
  -H "Content-Type: application/json" \
  -d "$BODY")"

ID="$(printf '%s' "$RESP" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("generationId",""))' 2>/dev/null || true)"
if [ -z "$ID" ]; then
  echo "Gamma did not return a generation id. Raw response:" >&2
  printf '%s\n' "$RESP" >&2
  unset GAMMA_KEY
  exit 1
fi

echo "generation $ID, polling"
for _ in $(seq 1 60); do
  sleep 5
  S="$(curl -sS "https://public-api.gamma.app/v0.2/generations/$ID" -H "X-API-KEY: $GAMMA_KEY")"
  ST="$(printf '%s' "$S" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("status",""))' 2>/dev/null || true)"
  [ "$ST" = "completed" ] && { printf '%s\n' "$S" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("gammaUrl",""))'; break; }
  [ "$ST" = "failed" ] && { echo "generation failed:" >&2; printf '%s\n' "$S" >&2; break; }
  printf '.'
done

unset GAMMA_KEY
echo
echo "The key was not written anywhere. Nothing to clean up."
