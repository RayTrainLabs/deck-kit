#!/usr/bin/env python3
"""
Assemble index.html from the shell, a theme stylesheet and a slides fragment.

    python3 build.py <deck-dir> [--theme daylight|paper|sage] [--footer "acme . B8"]

Reads <deck-dir>/slides.html, writes <deck-dir>/index.html. The deck title is
the first <h1 class="t-h1"> on the cover, with tags stripped. Renumbers nothing
and validates nothing: that is check.py's job. This exists so the theme swap is
one flag and not a paste.

--footer sets the mark that prints opposite the page number on every slide but
the cover, which already carries the wordmark at full size. Omit it and no mark
prints. There is no default string here on purpose: this script ships to people
who are not us, and a brand baked into a build tool is a brand on somebody
else's slides. It is written as a one line stylesheet after the theme, because
the theme file is inlined whole and unedited and nothing rewrites it.
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

def footmark(text):
    """The footer string as a CSS declaration, or nothing at all.

    The text is restricted to letters, digits, space, dot, middot and hyphen,
    because it lands inside a CSS string in a stylesheet and a stray quote or
    brace there would close the rule and take the rest of the sheet with it.
    Anything else is a mistake worth stopping for rather than escaping around.
    """
    if not text:
        return ""
    if not re.fullmatch(r"[A-Za-z0-9 .\u00b7\-]{1,32}", text):
        sys.exit(f"--footer {text!r}: letters, digits, space, dot, middot and "
                 "hyphen only, 32 characters max")
    # The middot is written as a CSS escape with two spaces after it, not one.
    # An escape is terminated by a space and that space is consumed, so
    # "\00b7 B8" prints as ".B8" with no gap. The first space closes the
    # escape, the second one is the space you can see.
    return ':root{--footmark:"' + text.replace("\u00b7", "\\00b7 ") + '"}'

def main(d, theme, footer=None):
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
                .replace("{{FOOTMARK}}", footmark(footer))
                .replace("{{CSS}}", css)
                .replace("{{SLIDES}}", slides))
    for stray in re.findall(r"\{\{[A-Z_]+\}\}", out):
        sys.exit(f"placeholder {stray} left unfilled")

    path = os.path.join(d, "index.html")
    open(path, "w", encoding="utf-8").write(out)
    print(f"{path}: {n} slides, theme {theme}, "
          f"footer {footer or 'none'}, {len(out)} bytes")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("deck_dir", nargs="?", default=".")
    p.add_argument("--theme", default="daylight")
    p.add_argument("--footer", default=None,
                   help='footer mark opposite the page number, e.g. "acme \u00b7 B8"')
    a = p.parse_args()
    main(a.deck_dir, a.theme, a.footer)
