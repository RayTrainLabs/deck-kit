#!/usr/bin/env python3
"""
Render the whole deck as one contact sheet, so it can be judged the way a room
judges it: all at once.

    python3 contact.py <deck-dir> [--cols 5] [--dpi 48]

Writes <deck-dir>/contact.png from <deck-dir>/deck.pdf, every page numbered.
Run export-pdf.sh first.

This exists because check.py cannot see dullness. A deck can pass every rule in
that file and still be seventeen copies of the same slide, and the only way that
becomes obvious is thirty thumbnails side by side. Open the sheet and look at it
before you ship. If you can cover the eyebrows with your thumb and not tell two
slides apart, the deck needs a different shape, not better words.

Needs pdftoppm (poppler) and Pillow. ImageMagick is deliberately not used: it is
absent on a stock macOS and this is one page of Pillow.
"""
import glob, os, shutil, subprocess, sys, tempfile

def main(d, cols, dpi):
    pdf = os.path.join(d, "deck.pdf")
    if not os.path.exists(pdf):
        sys.exit(f"{pdf} missing. Run export-pdf.sh first.")
    if not shutil.which("pdftoppm"):
        sys.exit("pdftoppm not found. brew install poppler")
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        sys.exit("Pillow not found. pip3 install pillow")

    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdftoppm", "-png", "-r", str(dpi), pdf,
                        os.path.join(tmp, "p")], check=True)
        files = sorted(glob.glob(os.path.join(tmp, "p-*.png")))
        if not files:
            sys.exit("pdftoppm produced no pages")
        ims = [Image.open(f).convert("RGB") for f in files]
        w, h = ims[0].size
        rows = (len(ims) + cols - 1) // cols
        pad, lab = 10, 14
        sheet = Image.new("RGB",
                          (cols * (w + pad) + pad, rows * (h + pad + lab) + pad),
                          "#2a2a2a")
        draw = ImageDraw.Draw(sheet)
        for i, im in enumerate(ims):
            x = pad + (i % cols) * (w + pad)
            y = pad + (i // cols) * (h + pad + lab)
            draw.text((x + 2, y + 1), str(i + 1), fill="#dddddd")
            sheet.paste(im, (x, y + lab))
        out = os.path.join(d, "contact.png")
        sheet.save(out)
    print(f"{out}: {len(ims)} pages, {cols} across, {sheet.size[0]}x{sheet.size[1]}")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("deck_dir", nargs="?", default=".")
    p.add_argument("--cols", type=int, default=5)
    p.add_argument("--dpi", type=int, default=48)
    a = p.parse_args()
    main(a.deck_dir, a.cols, a.dpi)
