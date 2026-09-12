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
             or block(r'class="statement">\s*<h2>(.*?)</h2>', s)
             # A full bleed slide carries its title inside .fu-say, which
             # is why it exported as "(untitled)" with the headline
             # repeated below as a bold line.
             or block(r'class="fu-say">\s*<h2>(.*?)</h2>', s))
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


    # ---- the nineteen visual blocks -----------------------------------
    # Every one of these was dropped silently until 2026-09-12. A flow
    # came out of here as its title and its kicker, with the three stages
    # gone, which means anyone taking deck.md into Gamma or a document got
    # the captions and not the argument.
    #
    # It is the same mistake as the shortcut card before it: the export
    # was fixed for the blocks that existed, then nineteen more were added
    # and nobody came back. So this section is written as one table of
    # handlers rather than as scattered loops, because the next block
    # added has to have an obvious place to be registered.

    def pairs(container, row_cls, a="b", b="span"):
        """Rows of <b>heading</b><span>body</span>, the shape most blocks use."""
        got = []
        # (.*?)</div> and not </div></div>: an fl-step closes with
        # </span></div>, not two divs, so requiring a nested pair matched
        # nothing and every flow exported as its title and kicker alone.
        for r in re.findall(rf'class="{row_cls}[^"]*"[^>]*>(.*?)</div>',
                            container, re.S):
            head, rest = block(rf"<{a}>(.*?)</{a}>", r), block(rf"<{b}>(.*?)</{b}>", r)
            if head or rest:
                got.append((head, rest))
        return got

    def whole(cls):
        """The inner html of a block, matched by depth so nesting is safe."""
        m = re.search(rf'<div class="{cls}"[^>]*>', s)
        if not m:
            return ""
        depth, j = 1, m.end()
        for t in re.finditer(r"<div\b[^>]*>|</div>", s[m.end():]):
            depth += 1 if t.group(0).startswith("<div") else -1
            if depth == 0:
                j = m.end() + t.start(); break
        return s[m.end():j]

    # flow, spine, layers: an ordered or plain list of heading plus body
    for cls, row, bullet in (("flow", "fl-step", True),
                             ("spine", "spn-node", True),
                             ("layers", "ly-row", True),
                             ("stack", "st-row", True)):
        inner = whole(cls)
        if not inner:
            continue
        if cls == "stack":
            for r in re.findall(r'class="st-row">(.*?)</div>\s*</div>', inner, re.S):
                num = block(r'class="st-num">(.*?)</div>', r)
                head = block(r"<b>(.*?)</b>", r)
                body = block(r"<span>(.*?)</span>", r)
                out.append(f"- **{num} {head}** {body}".replace("**  ", "**"))
        else:
            for head, body in pairs(inner, row):
                out.append(f"- **{head}** {body}".rstrip())

    # fishbone: the effect, then the causes feeding it
    fb = whole("fishbone")
    if fb:
        head = block(r'class="fb-head">(.*?)</div>', fb)
        if head:
            out.append(f"**Effect:** {head}")
        for r in re.findall(r'class="fb-rib[^"]*"[^>]*>(.*?)</div>', fb, re.S):
            b_, sp = block(r"<b>(.*?)</b>", r), block(r"<span>(.*?)</span>", r)
            if b_:
                out.append(f"- **{b_}** {sp}".rstrip())

    # funnel and rings: a value and what it is of
    fn = whole("funnel")
    if fn:
        for r in re.findall(r'class="fn-row">(.*?)</div>\s*</div>', fn, re.S):
            v = block(r'class="fn-bar"[^>]*>(.*?)</div>', r)
            b_, sp = block(r"<b>(.*?)</b>", r), block(r"<span>(.*?)</span>", r)
            out.append(f"- **{v}** {b_}. {sp}".rstrip(". "))
    rg = whole("rings")
    if rg:
        for r in re.findall(r'class="rg">(.*?)</div>\s*(?=<div class="rg">|$)', rg, re.S):
            n = block(r'class="rg-num"[^>]*>(.*?)</text>', r)
            b_, sp = block(r"<b>(.*?)</b>", r), block(r"<span>(.*?)</span>", r)
            out.append(f"- **{n}** {b_}. {sp}".rstrip(". "))

    # venn: the sets, then the note under them
    vn = whole("venn")
    if vn:
        for t in re.findall(r'class="vn-set">(.*?)</div>', vn, re.S):
            out.append(f"- {txt(t)}")
        note = block(r'class="vn-note">(.*?)</div>', vn)
        if note:
            out.append(f"> {note}")

    # matrix: two axes and four quadrants, as a table
    mx = whole("matrix")
    if mx:
        qs = [(("* " if "hi" in c else "") + block(r"<b>(.*?)</b>", q),
               block(r"<span>(.*?)</span>", q))
              for c, q in re.findall(r'class="mx-q([^"]*)">(.*?)</div>\s*(?=<div|$)', mx, re.S)]
        ax = block(r'class="mx-x">(.*?)</div>', s)
        ay = block(r'class="mx-y">(.*?)</div>', s)
        if ax or ay:
            out.append(f"*Axes: {ay or '?'} against {ax or '?'}. The starred quadrant is the answer.*")
        for head, body in qs:
            out.append(f"- **{head}** {body}".rstrip())

    # swim: lanes against phases, as a table
    sw = whole("swim")
    if sw:
        heads = [txt(h) for h in re.findall(r'class="sw-h">(.*?)</div>', sw, re.S)]
        lanes = re.findall(r'class="sw-lane">(.*?)</div>', sw, re.S)
        cells = [(c, txt(t)) for c, t in re.findall(r'class="sw-cell([^"]*)">(.*?)</div>', sw, re.S)]
        if heads and lanes:
            w = len(heads) - 1 or 1
            lines = ["| " + " | ".join(heads) + " |", "|" + "---|" * len(heads)]
            for i, lane in enumerate(lanes):
                row = cells[i * w:(i + 1) * w]
                lines.append("| " + txt(lane) + " | " +
                             " | ".join(("**" + v + "**") if "on" in c and v else v
                                        for c, v in row) + " |")
            out.append("\n".join(lines))

    # waterfall: the bridge, as value and label
    wf = whole("waterfall")
    if wf:
        for c, attrs, inner in re.findall(r'class="wf-col([^"]*)"([^>]*)>(.*?)$', wf, re.S):
            pass
        for col in re.findall(r'<div class="wf-col[^"]*"[^>]*>(.*?)</div>\s*(?=<div class="wf-col|$)', wf, re.S):
            v = block(r'class="wf-val">(.*?)</span>', col)
            lab = block(r'class="wf-lab">(.*?)</span>', col)
            if v or lab:
                out.append(f"- **{v}** {lab}".rstrip())

    # stackbar and multiples: a row per thing
    sb = whole("stackbar")
    if sb:
        for r in re.findall(r'class="sb-row">(.*?)</div>\s*</div>', sb, re.S):
            lab = block(r'class="sb-lab">(.*?)</div>', r)
            segs = [txt(x) for x in re.findall(r'class="sb-seg[^"]*"[^>]*>(.*?)</div>', r, re.S)]
            out.append(f"- **{lab}** " + " / ".join(segs))
        key = whole("sb-key") or block(r'class="sb-key">(.*?)</div>\s*<div', s)
        if key:
            out.append("*" + re.sub(r"\s+", " ", txt(key)).strip() + "*")
    mu = whole("multiples")
    if mu:
        for c in re.findall(r'class="mu-cell">(.*?)$', mu, re.S)[:1] or []:
            pass
        for cell in re.findall(r'<div class="mu-cell">(.*?)(?=<div class="mu-cell">|$)', mu, re.S):
            h = block(r'class="mu-head">(.*?)</div>', cell)
            n = block(r'class="mu-num">(.*?)</div>', cell)
            f_ = block(r'class="mu-foot">(.*?)</div>', cell)
            if h or n:
                out.append(f"- **{h} {n}** {f_}".rstrip())

    # linechart: the series and their values, which is what the picture is
    lc = re.search(r'<div class="linechart"([^>]*)>', s)
    if lc:
        xs = re.search(r'data-x="([^"]*)"', lc.group(1))
        for cls, attrs, label in re.findall(
                r'<div class="ln-series([^"]*)"([^>]*)>(.*?)</div>', s, re.S):
            v = re.search(r'data-v="([^"]*)"', attrs)
            if v:
                out.append(f"- **{txt(label)}** {v.group(1)}"
                           + (f"  ({xs.group(1)})" if xs else ""))

    # figure, shot, split, full: the picture, its caption, and its pins
    for cls in ("figure", "shot", "split", "full"):
        inner = whole(cls)
        if not inner:
            continue
        alt = re.search(r'<img[^>]*alt="([^"]*)"', inner)
        src = re.search(r'<img[^>]*src="([^"]{0,60})', inner)
        if alt or src:
            out.append(f"![{alt.group(1) if alt else 'image'}]"
                       f"({'embedded image' if not src or src.group(1).startswith('data:') else src.group(1)})")
        cap = block(r'class="fig-cap">(.*?)</div>', inner)
        if cap:
            out.append(cap)
        pins = re.findall(r'class="pin[^"]*"[^>]*>(.*?)</span>', inner, re.S)
        if pins:
            out.append("*Callouts: " + ", ".join(txt(p) for p in pins) + ". See the source line.*")
        for tag, pre in (("b", "**"), ("span", "")):
            for t in re.findall(rf'class="sl-text">.*?<{tag}>(.*?)</{tag}>', inner, re.S):
                out.append(f"{pre}{txt(t)}{pre}")
        fp = block(r'class="fu-say">.*?<p>(.*?)</p>', inner)
        if fp:
            out.append(fp)


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
