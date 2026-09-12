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

The sample slide is chosen to carry the most colour information in one page: the
page ground, a card, the shortcut card's tint and rule, the accent on an eyebrow
and on a numeral, ink on a title, and the band with white type on it. A cover
would be prettier and would show almost none of that.

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

# One slide. Deliberately not the cover: a cover shows the ground and the
# wordmark and nothing else, and the thing people are actually choosing
# between is what a working content slide looks like.
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
                f.write(SAMPLE)
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
            page = sorted(glob.glob(os.path.join(d, "s-*.png")))[0]
            panels.append((name, Image.open(page).convert("RGB")))

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
    print(f"{path}: {len(panels)} themes, {cols} across, "
          f"{sheet.size[0]}x{sheet.size[1]}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("out_dir", nargs="?", default=".")
    p.add_argument("--cols", type=int, default=4)
    p.add_argument("--dpi", type=int, default=60)
    a = p.parse_args()
    main(a.out_dir, a.cols, a.dpi)
