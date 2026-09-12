#!/usr/bin/env python3
"""
Write <deck-dir>/deck.md from the deck's index.html.

    python3 export-md.py <deck-dir>

One markdown section per slide, in running order, carrying the words and the
structure and nothing else. It exists so the deck can be pasted into Gamma or
any other generator without retyping it, and so the text is reviewable in a
diff. It is an export, not a source: edits belong in slides.html, and running
this again overwrites deck.md.
"""
import html as _html, os, re, sys

def txt(s):
    s = re.sub(r"<br\s*/?>", " ", s)
    s = re.sub(r"<[^>]+>", "", s)
    return _html.unescape(s).replace(" ", " ").strip()

def block(pat, s, flags=re.S):
    m = re.search(pat, s, flags)
    return txt(m.group(1)) if m else ""

def slide_md(s):
    out = []
    eyebrow = block(r'class="t-eyebrow">(.*?)</div>', s) or block(r'class="eyebrow">(.*?)</div>', s)
    title = (block(r'class="t-h1">(.*?)</h1>', s)
             or block(r'class="title">(.*?)</h2>', s)
             or block(r'class="chapter">\s*<h2>(.*?)</h2>', s)
             or block(r'class="statement">\s*<h2>(.*?)</h2>', s))
    out.append(f"## {title}" if title else "## (untitled)")
    if eyebrow:
        out.append(f"*{eyebrow}*")

    for pat in (r'class="t-stand">(.*?)</div>',
                r'class="chapter">.*?<p>(.*?)</p>',
                r'class="statement">.*?<p>(.*?)</p>'):
        t = block(pat, s)
        if t:
            out.append(t)

    for row in re.findall(r'class="tl-row">(.*?)</div></div>', s, re.S):
        t = block(r'class="tl-time">(.*?)</div>', row)
        head = block(r"<b>(.*?)</b>", row)
        rest = block(r"<span>(.*?)</span>", row)
        out.append(f"- **{t}** {head}. {rest}".rstrip("."))

    # Cards are split on their own opening tag rather than matched as
    # balanced divs, because a card contains a nested badge div and the
    # shipped markup puts a whole card on one line. Each part is then cut
    # at the first element that cannot be inside a card.
    #
    # The class pattern has to be open ended. Matching class="card" exactly
    # meant class="card tip" was never a split point, so the shortcut card
    # was swallowed into the card before it: its body appended to the wrong
    # card and its heading dropped, because the h3 taken was the previous
    # card's. The shortcut is the one card the room came for, and it was the
    # one the export lost.
    for part in re.split(r'<div class="card[^"]*">', s)[1:]:
        c = re.split(r'<div class="(?:band|kicker|checkpoint|strip|note|pageno|prompt|tree|source)"',
                     part)[0]
        badge = block(r'class="badge[^"]*">(.*?)</div>', c)
        stat = block(r'class="stat">(.*?)</div>', c)
        head = block(r"<h3>(.*?)</h3>", c)
        body = " ".join(txt(p) for p in re.findall(r"<p>(.*?)</p>", c, re.S))
        items = [txt(li) for li in re.findall(r"<li>(.*?)</li>", c, re.S)]
        label = " / ".join(x for x in (badge if not badge.isdigit() else "", stat, head) if x)
        if label:
            out.append(f"- **{label}**" + (f" {body}" if body else ""))
        elif body:
            out.append(f"- {body}")
        for it in items:
            out.append(f"  - {it}")

    # The whole table is one block. Blocks are joined with a blank line
    # between them, and a blank line between two rows stops being a table.
    for tbl in re.findall(r'<table class="tbl">(.*?)</table>', s, re.S):
        lines = []
        for i, r in enumerate(re.findall(r"<tr>(.*?)</tr>", tbl, re.S)):
            cells = [txt(c) for c in re.findall(r"<t[hd]>(.*?)</t[hd]>", r, re.S)]
            lines.append("| " + " | ".join(cells) + " |")
            if i == 0:
                lines.append("|" + "---|" * len(cells))
        out.append("\n".join(lines))

    # The chart is the one element whose whole content is numbers, so an
    # export that drops it turns the deck's only evidence slide into its
    # kicker. The bar width is presentation and does not survive; the label
    # and the value are the argument and do.
    for row in re.findall(r'class="ch-row">(.*?)</div>', s, re.S):
        lab = block(r'class="ch-lab">(.*?)</span>', row)
        val = block(r'class="ch-val">(.*?)</span>', row)
        out.append(f"- **{lab}** {val}".rstrip())

    box = block(r'class="box">(.*?)</div>', s)
    if box:
        out.append("**Type this**\n\n```\n" + box + "\n```")
    tree = re.search(r'class="tree">(.*?)</div>', s, re.S)
    if tree:
        out.append("```\n" + txt(tree.group(1)) + "\n```")

    for lbl, pat in (("", r'class="note">(.*?)</div>'),
                     ("", r'class="kicker">(.*?)</div>'),
                     ("Checkpoint:", r'class="checkpoint">(.*?)</div>'),
                     ("If yours missed it:", r'class="strip">(.*?)</div>')):
        t = block(pat, s)
        if t:
            t = re.sub(r"^(Checkpoint|If yours missed it)\s*", "", t)
            out.append(f"**{lbl}** {t}".strip() if lbl else f"> {t}")

    b = re.search(r'class="band">(.*?)</div>\s*<', s, re.S)
    if b:
        head = block(r"<b>(.*?)</b>", b.group(1))
        rest = block(r"<span>(.*?)</span>", b.group(1))
        out.append(f"**{head}** {rest}".strip())

    # The source line goes last because it is last on the slide, and it goes
    # in at all because a number without its citation is the one thing this
    # export must not hand to another generator. It was missing entirely,
    # which meant every figure in the markdown was unattributable.
    src = block(r'class="source">(.*?)</div>', s)
    if src:
        out.append(f"*{src}*")

    return "\n\n".join(out)

def main(d):
    idx = os.path.join(d, "index.html")
    if not os.path.exists(idx):
        sys.exit(f"{idx} missing. Run build.py first.")
    h = open(idx, encoding="utf-8").read()
    title = block(r"<title>(.*?)</title>", h) or os.path.basename(os.path.abspath(d))
    slides = re.findall(r'<section class="slide">(.*?)</section>', h, re.S)
    if not slides:
        sys.exit("no slides found")
    body = "\n\n---\n\n".join(slide_md(s) for s in slides)
    out = os.path.join(d, "deck.md")
    open(out, "w", encoding="utf-8").write(f"# {title}\n\n{body}\n")
    print(f"{out}: {len(slides)} slides, {os.path.getsize(out)} bytes")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
