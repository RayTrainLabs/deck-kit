#!/usr/bin/env python3
"""
Render every built theme as one labelled sheet, so a theme is chosen by looking
at it rather than by reading its name.

    python3 sampler.py [out-dir] [--cols 4] [--dpi 60]

Writes <out-dir>/themes.png, one panel per theme, each panel labelled with the
name you pass to --theme.

Why this exists. The themes are called sage, mist, daylight, paper, slate. Those
names mean something once you have seen the deck and nothing at all before that,
so asking somebody to pick one from a list is asking them to guess. Every time
the theme question gets put to a user, this sheet goes with it.

Two panels per theme, because neither alone is honest. The working slide carries
the colour information: the page ground, a card, the shortcut card's tint and
rule, the accent, and the band with white type on it. The cover carries what
actually separates one theme's identity from another, which is the wave at its
foot and the type at display size. Show only the working slide and every theme
looks like the same slide recoloured, which was a fair criticism of this sheet
before the covers had a wave.

Needs pdftoppm (poppler) and Pillow, the same two the contact sheet needs.
"""
import glob, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(HERE, "scripts", "build.py")

# Kept in the order a person actually chooses in: the three with a source
# first, then the white grounds, then the tinted grounds.
ORDER = ["daylight", "paper", "sage",
         "boardroom", "navy", "crimson", "slate",
         "mist", "moss", "linen", "plum"]

# Two slides per theme, rendered as one deck so both come out of the same
# PDF: the cover, which is where the theme's identity lives, and a working
# content slide, which is where its colour decisions live.
#
# The placeholder names are neutral on purpose. This file is in
# SCRIPTS_VERBATIM, so unlike layouts.html nothing rewrites it on the way
# into the kit, and a wordmark typed here ships as somebody else's wordmark
# on somebody else's sampler. The leak gate caught exactly that once.
COVER = """<section class="slide"><div class="stage">
  <div class="t-mark">your<em>brand</em></div>
  <div class="t-eyebrow">Workshop &middot; Session 2 of 3</div>
  <h1 class="t-h1">What the cover looks like</h1>
  <div class="t-rule"></div>
  <div class="t-stand">One line saying what the room walks out able to do.</div>
  <div class="t-by">Your Name &middot; Your Company</div>
  <div class="t-meta">A date &nbsp; &middot; &nbsp; your site</div>
  <div class="pageno">1</div>
</div></section>
"""

SAMPLE = """<section class="slide"><div class="stage">
  <div class="eyebrow">The mechanism</div>
  <h2 class="title">What a working slide looks like</h2>
  <div class="grid three">
    <div class="card"><div class="badge">1</div><h3>A plain card</h3>
      <p>Body text on a card, at the size it is actually set.</p></div>
    <div class="card"><div class="badge">2</div><h3>A second card</h3>
      <p>Three of these is the most common slide in any deck.</p></div>
    <div class="card tip"><div class="badge">3</div><h3>The shortcut card</h3>
      <p>Tinted ground and an accent rule. This is the one the room came for.</p></div>
  </div>
  <div class="band">
    <b>The band, where the room stops reading and looks up.</b>
    <span>White type on the accent, once a slide at most.</span>
  </div>
  <div class="pageno">1</div>
</div></section>
"""


def main(out, cols, dpi):
    if not shutil.which("pdftoppm"):
        sys.exit("pdftoppm not found. brew install poppler")
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        sys.exit("Pillow not found. pip3 install pillow")

    panels = []
    with tempfile.TemporaryDirectory() as tmp:
        for name in ORDER:
            css = os.path.join(HERE, "assets", f"{name}.css")
            if not os.path.exists(css):
                print(f"  skipping {name}, no stylesheet")
                continue
            d = os.path.join(tmp, name)
            os.makedirs(d)
            with open(os.path.join(d, "slides.html"), "w", encoding="utf-8") as f:
                f.write(COVER + SAMPLE)
            subprocess.run([sys.executable, BUILD, d, "--theme", name],
                           check=True, stdout=subprocess.DEVNULL)
            # Chrome is what export-pdf.sh uses; going straight to PDF here
            # keeps the sheet identical to what the deck actually prints.
            subprocess.run([os.path.join(HERE, "scripts", "export-pdf.sh"), d],
                           check=True, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            subprocess.run(["pdftoppm", "-png", "-r", str(dpi),
                            os.path.join(d, "deck.pdf"), os.path.join(d, "s")],
                           check=True)
            pages = sorted(glob.glob(os.path.join(d, "s-*.png")))
            panels.append((f"{name}  cover", Image.open(pages[0]).convert("RGB")))
            panels.append((f"{name}  slide", Image.open(pages[1]).convert("RGB")))

    if not panels:
        sys.exit("no themes rendered")

    w, h = panels[0][1].size
    rows = (len(panels) + cols - 1) // cols
    pad, lab = 14, 22
    sheet = Image.new("RGB",
                      (cols * (w + pad) + pad, rows * (h + pad + lab) + pad),
                      "#2a2a2a")
    draw = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(panels):
        x = pad + (i % cols) * (w + pad)
        y = pad + (i // cols) * (h + pad + lab)
        draw.text((x + 3, y + 5), name, fill="#ffffff")
        sheet.paste(im, (x, y + lab))
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "themes.png")
    sheet.save(path)
    print(f"{path}: {len(panels) // 2} themes, {len(panels)} panels, "
          f"{cols} across, {sheet.size[0]}x{sheet.size[1]}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("out_dir", nargs="?", default=".")
    p.add_argument("--cols", type=int, default=4)  # two panels per theme
    p.add_argument("--dpi", type=int, default=60)
    a = p.parse_args()
    main(a.out_dir, a.cols, a.dpi)
