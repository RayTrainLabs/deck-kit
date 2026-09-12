#!/usr/bin/env python3
"""
Assemble index.html from the shell, a theme stylesheet and a slides fragment.

    python3 build.py <deck-dir> [--theme daylight|paper|sage|boardroom|navy|crimson|slate] [--footer "acme . B8"]

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
import base64, os, re, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FONTS = {
    "daylight": ("css2?family=Caladea:wght@400;700&family=Carlito:wght@400;700"
                 "&family=Figtree:wght@400;600;700;800&display=swap"),
    "paper":    "css2?family=Gelasio:ital,wght@0,400;0,700;1,400;1,700&display=swap",
    "sage":     ("css2?family=Outfit:wght@400;600;700&family=Figtree:wght@400;500;600;700"
                 "&display=swap"),
    # The four generated themes. Their stylesheets and the query strings below
    # are produced by the same run, so a font added to a palette and not copied
    # here shows up as a theme that silently renders in the fallback stack.
    # Keep the two in step. Each stylesheet's header names its own two families.
    "boardroom": ("css2?family=IBM+Plex+Sans:wght@400;500;600"
                  "&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700"
                  "&display=swap"),
    "navy":     ("css2?family=Archivo:wght@500;600;700"
                 "&family=IBM+Plex+Sans:wght@400;500;600&display=swap"),
    "crimson":  "css2?family=Libre+Franklin:wght@400;500;600;700&display=swap",
    "slate":    "css2?family=Inter+Tight:wght@400;500;600;700&display=swap",
    # The quiet four. Same generator, tinted ground instead of white, and
    # since 2026-09-12 a body face of their own rather than Figtree for all
    # four: sharing a body across five themes was most of why they read as
    # one template recoloured. Each still keeps a heading family no other
    # theme uses, and that part is not taste: check.py identifies a deck's
    # theme by finding the one family unique to it, so two themes sharing
    # both families are two themes the checker cannot tell apart.
    "mist":     "css2?family=Manrope:wght@500;600;700&family=Karla:wght@400;500;600;700&display=swap",
    "moss":     "css2?family=Nunito+Sans:wght@500;600;700&family=Mulish:wght@400;500;600;700&display=swap",
    "linen":     "css2?family=Epilogue:wght@500;600;700&family=Lora:wght@400;500;600;700&display=swap",
    "plum":     "css2?family=Sora:wght@500;600;700&family=DM+Sans:wght@400;500;600;700&display=swap",
}

# Each theme's working accent, copied from the token its own stylesheet
# defines. daylight calls it --teal and the other six call it --accent, which
# is the same divergence that makes sage rather than daylight the base for a
# generated theme. A mismatch here is visible only in the browser tab, so it
# is worth reading the stylesheet rather than trusting this table.
ACCENTS = {
    "daylight":  "#028090",
    "paper":     "#B85042",
    "sage":      "#37604A",
    "boardroom": "#04564E",
    "navy":      "#1A4F8A",
    "crimson":   "#B3141A",
    "slate":     "#3A4552",
    "mist":      "#2F5C6E",
    "moss":      "#4A6B39",
    "linen":     "#7A5C3E",
    "plum":      "#5A4374",
}

def favicon(theme):
    """A rounded square in the theme accent carrying a white r, as a data URI.

    Deliberately not a file. index.html is one self contained document and a
    linked favicon.ico would resolve only when the deck is served from a web
    root, which is one of the three ways these decks actually get opened.

    The SVG is minified by hand and the # in the hex is percent encoded,
    because an unescaped # inside a data: URI starts a fragment and silently
    truncates the icon to nothing. The letter is set in a generic sans stack
    rather than the theme's heading font: a data URI cannot pull a web font,
    and at 16 pixels the difference is not visible anyway.
    """
    a = ACCENTS[theme].replace("#", "%23")
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'>"
           f"<rect width='32' height='32' rx='7' fill='{a}'/>"
           f"<text x='16' y='23' font-family='Helvetica,Arial,sans-serif' "
           f"font-size='21' font-weight='700' fill='%23fff' "
           f"text-anchor='middle'>r</text></svg>")
    return f'<link rel="icon" href="data:image/svg+xml,{svg}">'

LOGO_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
              ".svg": "image/svg+xml", ".webp": "image/webp", ".gif": "image/gif"}

def logo(path):
    """The client's mark, inlined as a data URI, or nothing at all.

    Whose brand goes on a delivered deck is a business decision and it was
    made once: the client's mark takes the cover position and the content
    slide corner, and ours stays as the small footer mark. So this does three
    things together, and they only make sense together.

      1. On the cover, the client's logo replaces our wordmark at the same
         origin. The text is not deleted, it is set to zero and painted over,
         so an existing deck picks this up with no change to its markup.
      2. On every other slide, a small version sits bottom left, where the
         footer mark used to be.
      3. Our footer mark therefore moves to the right, next to the page
         number, because the left corner now belongs to the client.

    The file is inlined rather than linked because index.html is one self
    contained document. A linked logo is a broken image the first time the
    deck is opened from a USB stick in a room with no wifi, which is the room
    this template exists for.

    Not painted on dark slides. A client logo is almost always dark ink on
    transparency, and on a dark chapter divider that is an invisible smudge.
    Hiding it there is the safe default; a reversed mark would need a second
    file and that is a decision nobody has asked for yet.
    """
    if not path:
        return ""
    ext = os.path.splitext(path)[1].lower()
    if ext not in LOGO_TYPES:
        sys.exit(f"--logo {path}: want one of {', '.join(sorted(LOGO_TYPES))}")
    if not os.path.exists(path):
        sys.exit(f"--logo {path}: no such file")
    raw = open(path, "rb").read()
    if len(raw) > 1_000_000:
        sys.exit(f"--logo {path}: {len(raw)//1024}KB. Over 1MB is a source file, "
                 "not a logo. Export it at the size it prints, a few hundred "
                 "pixels tall, and try again.")
    # The hard limit alone is too loose to be useful. A 609KB photograph
    # passed it in testing and turned a 53KB deck into 860KB, which is a
    # sixteen fold increase nobody asked for and nobody would notice until
    # they mailed it. The logo is inlined once, but that once is in every
    # copy of the file that ever gets sent.
    if len(raw) > 150_000:
        print(f"  note: {os.path.basename(path)} is {len(raw)//1024}KB and is "
              "inlined into the deck. A logo is line art: a few hundred pixels "
              "tall as PNG or SVG is usually under 40KB.", file=sys.stderr)
    uri = f"data:{LOGO_TYPES[ext]};base64,{base64.b64encode(raw).decode()}"
    # Geometry, all of it read off the stylesheet rather than chosen:
    # .t-mark sits at .62/.46, the checkpoint ends at 5.235, the page number
    # sits at 9.075/5.28 and the stage is 5.625 tall. The content slide logo
    # is .24in tall from 5.28, which clears the checkpoint by .045in and stays
    # inside the stage. Verified by rendering a slide that carries a
    # checkpoint, not by trusting this comment.
    return (
        f':root{{--logo:url("{uri}")}}'
        '.t-mark{font-size:0;width:calc(2.9 * var(--in));'
        'height:calc(.62 * var(--in));'
        'background:var(--logo) left center/contain no-repeat}'
        '.stage:not(:has(.t-h1))::before{content:"";position:absolute;'
        'left:var(--margin);top:calc(5.28 * var(--in));'
        'width:calc(1.6 * var(--in));height:calc(.24 * var(--in));'
        'background:var(--logo) left center/contain no-repeat}'
        '.stage.dark::before{content:none}'
        '.stage::after{left:auto;right:calc(1.1 * var(--in))}'
    )

IMG_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
             ".svg": "image/svg+xml", ".webp": "image/webp", ".gif": "image/gif"}

def inline_images(slides, d):
    """Turn <img src="shot.png"> into <img src="data:image/png;base64,...">.

    A deck is one self contained file. An <img> pointing at a sibling file
    is a broken image the moment the html is mailed on its own, which is
    the normal way a deck travels, so the picture has to live inside it.

    Only relative paths are touched. A data: URI is already inlined and an
    http: one is somebody's deliberate choice to depend on a network.

    Resolved against the deck directory, not the working directory, so the
    same slides.html builds from anywhere.
    """
    total = [0]
    def sub(m):
        pre, src, post = m.group(1), m.group(2), m.group(3)
        if src.startswith(("data:", "http:", "https:", "//")):
            return m.group(0)
        path = src if os.path.isabs(src) else os.path.join(d, src)
        if not os.path.exists(path):
            sys.exit(f"{src}: no such image, referenced by slides.html")
        ext = os.path.splitext(path)[1].lower()
        if ext not in IMG_TYPES:
            sys.exit(f"{src}: want one of {', '.join(sorted(IMG_TYPES))}")
        raw = open(path, "rb").read()
        total[0] += len(raw)
        return (f'{pre}data:{IMG_TYPES[ext]};base64,'
                f'{base64.b64encode(raw).decode()}{post}')
    out = re.sub(r'(<img[^>]*\ssrc=")([^"]+)(")', sub, slides)
    if total[0]:
        n = len(re.findall(r"<img", out))
        print(f"  {n} image(s) inlined, {total[0]//1024}KB before base64")
        # Base64 adds a third. A deck past about 8MB stops being mailable
        # and starts being a file people decline to open.
        if total[0] > 6_000_000:
            print(f"  WARNING: {total[0]//1024//1024}MB of images. Export them at "
                  "the size they print, around 1600px on the long edge.",
                  file=sys.stderr)
    return out

def waterfall(slides):
    """Compute a bridge chart's bars from its values.

    The first version made the author type --base and --h as percentages
    for every column, which is the deck asking a person to do arithmetic
    that the deck already has the numbers for. Get one base wrong by two
    and the bridge no longer bridges, and nothing catches it: the slide
    renders, it is just quietly lying.

    So the markup carries values and labels only:

        <div class="waterfall">
          <div class="wf-col" data-v="9"    data-tot>Baseline</div>
          <div class="wf-col" data-v="+4">Split on headings</div>
          <div class="wf-col" data-v="-1">Cheaper embedding</div>
          <div class="wf-col" data-v="17"   data-tot>After one week</div>
        </div>

    A column with data-tot is an absolute: it stands on the floor and its
    height is its value. Everything else is a delta that floats on the
    running total, above it when positive and below it when negative.

    The scale is the largest value or cumulative, mapped to 82 percent,
    which leaves the value label room above the tallest bar rather than
    letting it print off the top of the block.
    """
    def one(open_tag, inner):
        cols = re.findall(r'<div class="wf-col([^"]*)"([^>]*)>(.*?)</div>', inner, re.S)
        if not cols:
            return open_tag + inner + '</div>'
        run, rows, peak = 0.0, [], 0.0
        for cls, attrs, label in cols:
            mv = re.search(r'data-v="([+-]?[\d.]+)"', attrs)
            if not mv:
                sys.exit("a wf-col with no data-v. Every column carries its value.")
            v = float(mv.group(1))
            if "data-tot" in attrs:
                # Compare before overwriting. The first version set run = v
                # and then checked run against v further down, which is a
                # comparison that can never fail, so a bridge declaring 99
                # against deltas summing to 17 built without complaint.
                if rows and abs(v - run) > 0.005:
                    sys.exit(f"waterfall does not close: the deltas sum to {run:g} "
                             f"but the closing total says {v:g}. Fix the numbers, "
                             "not the chart.")
                base, h, run = 0.0, v, v
            elif v >= 0:
                base, h = run, v
                run += v
            else:
                run += v
                base, h = run, -v
            rows.append((cls, mv.group(1), label, base, h))
            peak = max(peak, base + h)
        if peak <= 0:
            sys.exit("waterfall values sum to nothing")
        k = 82.0 / peak
        out = []
        for cls, raw, label, base, h in rows:
            val = raw if raw.startswith(("+", "-")) else raw
            out.append(
                f'<div class="wf-col{cls}" style="--base:{base*k:.2f};--h:{h*k:.2f}">'
                f'<span class="wf-val">{val}</span><span class="wf-bar"></span>'
                f'<span class="wf-lab">{label.strip()}</span></div>')
        return open_tag + "".join(out) + "</div>"

    # Depth scan, not a regex. A non greedy </div> matches the first
    # column's closing tag rather than the block's, so the first version
    # of this silently rewrote nothing and the chart came out empty.
    out, i = [], 0
    while True:
        m = re.compile(r'<div class="waterfall"[^>]*>').search(slides, i)
        if not m:
            out.append(slides[i:]); break
        out.append(slides[i:m.start()])
        depth, j = 1, m.end()
        for t in re.finditer(r'<div\b[^>]*>|</div>', slides[m.end():]):
            depth += 1 if t.group(0).startswith("<div") else -1
            if depth == 0:
                j = m.end() + t.start(); break
        out.append(one(m.group(0), slides[m.end():j]))
        i = j + len("</div>")
    return "".join(out)

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

def main(d, theme, footer=None, logo_path=None):
    if theme not in FONTS:
        sys.exit(f"unknown theme {theme!r}. Built themes: {', '.join(FONTS)}")
    shell = open(os.path.join(HERE, "assets", "shell.html"), encoding="utf-8").read()
    css = open(os.path.join(HERE, "assets", f"{theme}.css"), encoding="utf-8").read()
    slides = open(os.path.join(d, "slides.html"), encoding="utf-8").read()
    slides = inline_images(slides, d)
    slides = waterfall(slides)

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
                .replace("{{FAVICON}}", favicon(theme))
                .replace("{{N}}", str(n))
                .replace("{{FOOTMARK}}", footmark(footer))
                .replace("{{LOGO}}", logo(logo_path))
                .replace("{{CSS}}", css)
                .replace("{{SLIDES}}", slides))
    for stray in re.findall(r"\{\{[A-Z_]+\}\}", out):
        sys.exit(f"placeholder {stray} left unfilled")

    path = os.path.join(d, "index.html")
    open(path, "w", encoding="utf-8").write(out)
    print(f"{path}: {n} slides, theme {theme}, "
          f"footer {footer or 'none'}, logo {os.path.basename(logo_path) if logo_path else 'none'}, "
          f"{len(out)} bytes")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("deck_dir", nargs="?", default=".")
    p.add_argument("--theme", default="daylight")
    p.add_argument("--footer", default=None,
                   help='footer mark opposite the page number, e.g. "acme \u00b7 B8"')
    p.add_argument("--logo", default=None,
                   help="client logo, inlined. Takes the cover position and the "
                        "content slide corner; our footer mark moves right")
    a = p.parse_args()
    main(a.deck_dir, a.theme, a.footer, a.logo)
