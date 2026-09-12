#!/usr/bin/env python3
"""
Assemble index.html from the shell, a theme stylesheet and a slides fragment.

    python3 build.py <deck-dir> [--theme daylight|paper]

Reads <deck-dir>/slides.html, writes <deck-dir>/index.html. The deck title is
the first <h1 class="t-h1"> on the cover, with tags stripped. Renumbers nothing
and validates nothing: that is check.py's job. This exists so the theme swap is
one flag and not a paste.
"""
import os, re, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FONTS = {
    "daylight": ("css2?family=Caladea:wght@400;700&family=Carlito:wght@400;700"
                 "&family=Figtree:wght@400;600;700;800&display=swap"),
    "paper":    "css2?family=Gelasio:ital,wght@0,400;0,700;1,400;1,700&display=swap",
    "sage":     ("css2?family=Outfit:wght@400;600;700&family=Figtree:wght@400;500;600;700"
                 "&display=swap"),
}

def main(d, theme):
    if theme not in FONTS:
        sys.exit(f"unknown theme {theme!r}. Built themes: {', '.join(FONTS)}")
    shell = open(os.path.join(HERE, "assets", "shell.html"), encoding="utf-8").read()
    css = open(os.path.join(HERE, "assets", f"{theme}.css"), encoding="utf-8").read()
    slides = open(os.path.join(d, "slides.html"), encoding="utf-8").read()

    n = len(re.findall(r'<section class="slide">', slides))
    if not n:
        sys.exit("no slides in slides.html")
    m = re.search(r'class="t-h1">(.*?)</h1>', slides, flags=re.S)
    title = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else "Untitled deck"
    title = re.sub(r"\s+", " ", title)

    # Substitution order matters: the CSS and the slides can contain braces,
    # so every placeholder is replaced exactly once, largest payload last.
    out = (shell.replace("{{DECK_TITLE}}", title)
                .replace("{{FONTS}}", FONTS[theme])
                .replace("{{N}}", str(n))
                .replace("{{CSS}}", css)
                .replace("{{SLIDES}}", slides))
    for stray in re.findall(r"\{\{[A-Z_]+\}\}", out):
        sys.exit(f"placeholder {stray} left unfilled")

    path = os.path.join(d, "index.html")
    open(path, "w", encoding="utf-8").write(out)
    print(f"{path}: {n} slides, theme {theme}, {len(out)} bytes")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("deck_dir", nargs="?", default=".")
    p.add_argument("--theme", default="daylight")
    a = p.parse_args()
    main(a.deck_dir, a.theme)
