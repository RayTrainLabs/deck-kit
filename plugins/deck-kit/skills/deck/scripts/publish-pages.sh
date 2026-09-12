#!/usr/bin/env bash
# New PUBLIC repo, push, enable GitHub Pages, print the URL.
#
#     ./publish-pages.sh <deck-dir> <repo-name> [owner]
#
# owner falls back to $DECK_GH_OWNER, then to your own GitHub account.
#
# Pages on the Free plan publishes only from public repos, so this repo is
# public and so is everything in <deck-dir>. Put nothing in that directory you
# would not hand to a stranger: facilitator notes, client names, unreleased
# material and anything under NDA stay out of it. Copy the slides and the PDF
# into a clean directory and publish that.
#
# Commits are authored with your own git identity. If you have no global
# user.name and user.email set, git will say so and this will stop.
set -euo pipefail

DIR="$(cd "${1:?usage: publish-pages.sh <deck-dir> <repo-name> [owner]}" && pwd)"
REPO="${2:?usage: publish-pages.sh <deck-dir> <repo-name> [owner]}"

command -v gh >/dev/null || { echo "gh not found. Install the GitHub CLI: https://cli.github.com" >&2; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "gh is not logged in. Run: gh auth login" >&2; exit 1; }

OWNER="${3:-${DECK_GH_OWNER:-$(gh api user --jq .login)}}"

[ -f "$DIR/index.html" ] || { echo "no index.html in $DIR. Run build.py first." >&2; exit 1; }

echo "About to create the PUBLIC repo $OWNER/$REPO from $DIR"
echo "Contents:"
ls -1 "$DIR" | sed 's/^/  /'
printf 'Publish these files publicly? [y/N] '
read -r OK
case "$OK" in y|Y|yes|YES) ;; *) echo "nothing published"; exit 1 ;; esac

cd "$DIR"
git init -q 2>/dev/null || true
git add -A
git commit -q -m "Deck: $REPO" || true
git branch -M main
gh repo create "$OWNER/$REPO" --public --source=. --push
gh api -X POST "repos/$OWNER/$REPO/pages" -f 'source[branch]=main' -f 'source[path]=/' >/dev/null
echo "https://$(printf '%s' "$OWNER" | tr 'A-Z' 'a-z').github.io/$REPO/  (first build takes about a minute)"
