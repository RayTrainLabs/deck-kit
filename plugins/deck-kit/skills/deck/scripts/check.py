#!/usr/bin/env python3
"""
Pre ship check for a generated deck. Runs on the bytes on disk, never on a draft.

    python3 check.py <deck-dir>

Exits 1 on any FAIL. WARN is advisory and does not block.
Checks deck structure, contrast collisions, table capacity, checkpoint
placement and the writing rules.
"""
import re, sys, os

FAIL, WARN = [], []
def fail(m): FAIL.append(m)
def warn(m): WARN.append(m)

AI_LINGO = ["delve", "tapestry", "pivotal", "navigate", "landscape", "realm",
            "testament", "crucial", "unlock", "seamless", "robust", "harness",
            "leverage"]

def visible_text(html):
    """Everything the room actually reads. Comments, CSS and JS removed, so
    box drawing characters and CSS custom property names cannot false positive."""
    h = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
    h = re.sub(r"<style.*?</style>", " ", h, flags=re.S)
    h = re.sub(r"<script.*?</script>", " ", h, flags=re.S)
    h = re.sub(r"<[^>]+>", " ", h)
    return h

def main(d, outline=False):
    idx = os.path.join(d, "index.html")
    if not os.path.exists(idx):
        fail("index.html missing"); return report()
    html = open(idx, encoding="utf-8").read()

    # ---- companions ------------------------------------------------
    for f in ("FACILITATOR.md", "FAQ.md", "RUNSHEET.md", "EVIDENCE.md"):
        p = os.path.join(d, f)
        if not os.path.exists(p):
            fail(f"{f} missing. A deck without the other four is half the deliverable.")
        elif os.path.getsize(p) < 400:
            fail(f"{f} is {os.path.getsize(p)} bytes. That is a stub, not a document.")

    # ---- evidence ---------------------------------------------------
    # Every number a room could repeat on Monday has to survive somebody
    # looking it up on Tuesday. EVIDENCE.md is where that happens: one line
    # per claim, with where it came from and when it was measured.
    #
    # The check is deliberately shallow. It cannot tell whether a source is
    # any good. It can tell whether the research was done at all, and a deck
    # built without it fails this and nothing else, which is the point.
    ep = os.path.join(d, "EVIDENCE.md")
    if os.path.exists(ep):
        ev = open(ep, encoding="utf-8").read()
        urls = set(re.findall(r"https?://[^\s)\]]+", ev))
        if len(urls) < 5:
            fail(f"EVIDENCE.md cites {len(urls)} distinct sources. Five is the floor for "
                 "a deck that puts numbers on a slide. Search, read, and write the line "
                 "down with the URL and the month it was published.")
        undated = [u for u in urls
                   if not re.search(r"20[12]\d", ev[max(0, ev.find(u) - 220):ev.find(u) + 220])]
        if undated:
            warn(f"{len(undated)} source(s) in EVIDENCE.md with no year within sight of the "
                 "URL. A number with no date is a number with no shelf life.")
        # Our own numbers are models until somebody clears them. The deck says
        # so on the slide; EVIDENCE.md says which is which.
        if not re.search(r"\bmodel, not a case study\b|\bnot cleared\b|\bcleared\b", ev, re.I):
            warn("EVIDENCE.md never marks anything cleared or uncleared. Say which claims "
                 "are ours and unproven, and keep those off the slides.")


    # ---- writing rules, on visible text only -----------------------
    text = visible_text(html)
    for pat, label in ((r"—", "em dash"), (r"–", "en dash"),
                       (r"(?<=\w) - (?=\w)", "space hyphen space"),
                       (r"(?<!-)--(?!-)", "double hyphen")):
        for m in re.finditer(pat, text):
            fail(f"{label} in slide text: ...{text[max(0,m.start()-45):m.start()+45].strip()}...")
    for w in AI_LINGO:
        for m in re.finditer(rf"\b{w}\w*\b", text, re.I):
            warn(f"AI lingo '{m.group(0)}': ...{text[max(0,m.start()-40):m.start()+40].strip()}...")

    # A worked example is the third leg of analogy, mechanism, example. A
    # placeholder in the example teaches the room that the numbers do not
    # matter, which is the opposite of the lesson.
    # "bar" is deliberately absent: a quality bar is a real phrase and banning
    # it cost a clean deck two false fails. foo and baz never occur in English.
    for pat in (r"\bfoo\b", r"\bbaz\b", r"\bfoobar\b",
                r"lorem ipsum", r"\bAcme\b", r"\bWidgets? Inc\b",
                r"<your[^>]{0,24}here>", r"\bTODO\b", r"\bXXX\b",
                r"\bexample\.com\b", r"\bJohn Doe\b", r"\bJane Doe\b"):
        for m in re.finditer(pat, text, re.I):
            fail(f"placeholder '{m.group(0)}' on a slide. Examples carry real names "
                 f"and real numbers: ...{text[max(0,m.start()-40):m.start()+40].strip()}...")

    # ---- structure --------------------------------------------------
    # Theme is inferred from the font link, because that is the one thing a
    # theme cannot omit. daylight substitutes Caladea for Cambria and Carlito
    # for Calibri; paper substitutes Gelasio for Georgia.
    # Each theme's link carries one family no other theme uses, so the marker
    # below is the whole detection. Adding a theme means adding a marker here
    # and a stray list below, and forgetting the second is the failure that
    # lets a deck ship with two themes' slides in it.
    MARKERS = [
        ("daylight",  "family=Caladea"),
        ("paper",     "family=Gelasio"),
        ("sage",      "family=Outfit"),
        ("boardroom", "family=Source+Serif+4"),
        ("navy",      "family=Archivo"),
        ("crimson",   "family=Libre+Franklin"),
        ("slate",     "family=Inter+Tight"),
        ("mist",      "family=Manrope"),
        ("moss",      "family=Nunito+Sans"),
        ("linen",     "family=Epilogue"),
        ("plum",      "family=Sora"),
    ]
    # Detection runs on comment stripped bytes. shell.html carries a comment
    # listing every theme's font link, so a raw scan matches whichever marker
    # is first in the list and calls every deck daylight.
    no_comments = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
    no_comments = re.sub(r"/\*.*?\*/", " ", no_comments, flags=re.S)
    theme = None
    for t, marker in MARKERS:
        if "fonts.googleapis.com/css2?" in no_comments and marker in no_comments:
            theme = t
            break
    if theme is None:
        fail("font link missing or unrecognised. daylight wants Caladea, Carlito and Figtree; "
             "paper wants Gelasio; sage wants Outfit and Figtree; boardroom wants Source Serif 4 "
             "and IBM Plex Sans; navy wants Archivo and IBM Plex Sans; crimson wants Libre "
             "Franklin; slate wants Inter Tight; mist wants Manrope and Figtree; moss wants "
             "Nunito Sans and Figtree; linen wants Epilogue and Figtree; plum wants Sora "
             "and Figtree.")

    # A font from another theme in the markup means a slide was pasted across
    # themes, which renders as one slide in a different typeface and is almost
    # impossible to see in a browser that has neither font installed. Comments
    # are stripped first: shell.html records every font link in a comment on
    # purpose, and each theme's stylesheet explains itself by naming the fonts
    # it is not.
    # One rule when adding a family here: never pick a name that is a
    # prefix of another theme's. plum was briefly given Inter while slate
    # has Inter Tight, and the search below matched "Inter" inside "Inter
    # Tight" and failed every slate deck. The guard is right to be
    # suspicious; the fix is a family name that cannot be confused.
    FAMILIES = {
        "daylight":  ["Caladea", "Carlito", "Figtree"],
        "paper":     ["Gelasio"],
        "sage":      ["Outfit", "Figtree"],
        "boardroom": ["Source Serif 4", "IBM Plex Sans"],
        "navy":      ["Archivo", "IBM Plex Sans"],
        "crimson":   ["Libre Franklin"],
        "slate":     ["Inter Tight"],
        "mist":      ["Manrope", "Karla"],
        "moss":      ["Nunito Sans", "Mulish"],
        "linen":      ["Epilogue", "Lora"],
        "plum":      ["Sora", "DM Sans"],
    }
    if theme:
        mine = set(FAMILIES[theme])
        for other, fams in FAMILIES.items():
            if other == theme:
                continue
            for fam in fams:
                if fam in mine:
                    continue
                if re.search(r"(?<![A-Za-z+])" + re.escape(fam) + r"(?![A-Za-z])",
                             no_comments):
                    fail(f"{theme} deck references {fam}, which is {other}'s. "
                         f"{theme} is {' and '.join(FAMILIES[theme])} and nothing else. "
                         "A slide was pasted in from another theme.")
    if "@page" not in html:
        fail("@page rule missing. Print to PDF will not produce one slide per page.")
    if "--stage-w" not in html:
        fail("--stage-w missing. Geometry will not be proportional to the source deck.")

    slides = re.findall(r'<section class="slide">.*?</section>', html, flags=re.S)
    if not slides:
        fail("no slides found"); return report()
    n = len(slides)
    cm = re.search(r'id="counter">\s*1\s*/\s*(\d+)', html)
    if cm and int(cm.group(1)) != n:
        fail(f"nav counter says {cm.group(1)} slides, there are {n}")

    # paper's cover headline grows upward from a fixed baseline and has room
    # for three lines. Georgia sets about 42 characters to the line at 30pt
    # across the 8.95in measure, so past ~126 the fourth line reaches the
    # eyebrow. Found by rendering the cover, not by reading the CSS.
    if theme == "paper":
        h1 = re.search(r'class="t-h1">(.*?)</h1>', html, flags=re.S)
        if h1:
            t = re.sub(r"<[^>]+>", "", h1.group(1)).strip()
            if len(t) > 118:
                fail(f"cover headline is {len(t)} characters. On paper that is a fourth line, "
                     "and the fourth line runs into the eyebrow. Three lines is the ceiling.")

    # .chapnum is a small tracked label on paper and a 92pt numeral on
    # daylight and sage. A deck written for paper says "Chapter 01" in it,
    # which set at 92pt fills half the slide. Found by rendering a paper
    # deck under sage and looking at it.
    if theme in ("daylight", "sage"):
        for i, s in enumerate(slides, 1):
            m = re.search(r'class="chapnum">(.*?)</', s, flags=re.S)
            if m:
                t = re.sub(r"<[^>]+>", "", m.group(1)).strip()
                if len(t) > 3:
                    warn(f"slide {i}: chapnum reads {t!r}. On {theme} that is a 92pt numeral, "
                         "not a label. Use the number alone and put the word in the eyebrow.")

    covers = sum(1 for s in slides if "t-h1" in s)
    if covers != 1: fail(f"{covers} cover slides. There is exactly one, and it is slide 1.")
    elif "t-h1" not in slides[0]: fail("the cover is not slide 1")

    has_prompt = has_tiers = has_honesty = has_checkpoint = False
    seen_page = []
    soft_slides = []

    for i, s in enumerate(slides, 1):
        st = visible_text(s)
        tag = f"slide {i}"

        # The cover and a full bleed image slide are the two that carry no
        # eyebrow, and for the same reason: there is no category line to
        # write because the slide is one thing at full size. Found by
        # building the probe deck, which failed its own full bleed slide.
        if "t-h1" not in s and 'class="full"' not in s and "eyebrow" not in s:
            fail(f"{tag}: no eyebrow. Every slide has one.")
        eb = re.search(r'class="eyebrow">(.*?)<', s, flags=re.S)
        if eb:
            e = eb.group(1).strip()
            if e != e.upper() and not re.search(r"[.!?]$", e):
                pass  # rendered uppercase by CSS, source case is free
            if re.search(r"[.!?]\s*$", e):
                fail(f"{tag}: eyebrow '{e}' is a sentence. It is a category.")

        ti = re.search(r'class="title">(.*?)</h2>', s, flags=re.S)
        if ti:
            t = re.sub(r"<[^>]+>", "", ti.group(1)).strip()
            if len(t.split()) < 2:
                warn(f"{tag}: title '{t}' is one word. Titles are claims.")
            if t.endswith(":"):
                fail(f"{tag}: title '{t}' ends in a colon. That is a label, not a claim.")

        if s.count('class="band"') > 1:
            fail(f"{tag}: two bands. The band appears once, or not at all.")

        # Six items max. Counted per container: cards on the slide, list
        # items within one card. The shipped Do/Don't slide is two cards of
        # five bullets, so 2 + 10 is not ten items, it is two of five.
        n_cards = len(re.findall(r'class="card"', s))
        if n_cards > 6:
            fail(f"{tag}: {n_cards} cards. No slide carries more than six.")
        for ul in re.findall(r"<ul>(.*?)</ul>", s, flags=re.S):
            n_li = len(re.findall(r"<li>", ul))
            if n_li > 6:
                fail(f"{tag}: a list of {n_li}. No list runs past six.")
        n_rows = len(re.findall(r"<tr>", s))
        if n_rows > 7:  # header plus six
            fail(f"{tag}: table of {n_rows - 1} rows. Six is the ceiling.")
        # The kicker and the page number sit at fixed heights that assume a
        # short table. Found by rendering, not by reading the CSS: five rows
        # put the last row under the kicker, six rows of wrapping cells put it
        # under the page number.
        n_body = n_rows - 1 if n_rows else 0
        if n_body >= 5 and 'class="kicker"' in s:
            fail(f"{tag}: a {n_body} row table and a kicker. The kicker is positioned for a short table and lands on the last row. Drop one or the other.")
        if n_body >= 6:
            long_cells = [c for c in re.findall(r"<td>(.*?)</td>", s, flags=re.S)
                          if len(re.sub(r"<[^>]+>", "", c).strip()) > 38]
            if long_cells:
                warn(f"{tag}: a six row table with {len(long_cells)} cells near the wrap point. A wrapped line here runs into the page number. Render this page and look at it before shipping.")
        for c in re.findall(r"<p>(.*?)</p>", s, flags=re.S):
            body = re.sub(r"<[^>]+>", "", c).strip()
            if len(body) > 240:
                warn(f"{tag}: card body is {len(body)} chars, that is four lines or more. Cut it.")

        # The band is 3.7125 tall by at least 1.0125, so it occupies
        # everything down to 4.725. The kicker at 4.31 and the source at
        # 4.55 both sit inside that. kicker against band was already
        # known; source against band was not, and a close slide shipped
        # with its contact line printing underneath the band where
        # nobody could read it. Found by rendering the page.
        if 'class="band"' in s and 'class="source"' in s:
            fail(f"{tag}: a band and a source line. The band runs from 3.7125 to "
                 "4.725 and the source sits at 4.55, underneath it. Move the "
                 "citation to a slide without a band, or drop the band.")
        # The stack runs to 4.4375, past the kicker at 4.31. It is the
        # layout for bodies a card cannot hold, so it owns the page the
        # way a chart does and does not share it with a closing line.
        if 'class="stack"' in s and 'class="kicker"' in s:
            fail(f"{tag}: a stack and a kicker. The stack ends at 4.4375 and the "
                 "kicker sits at 4.31, inside it. The rows are the content on a "
                 "stack slide; put the line in the last row or drop it.")

        if 'class="strip"' in s and 'class="pageno"' in s:
            fail(f"{tag}: carries the recovery strip and a slide number. Strip slides drop the number.")
        pn = re.search(r'class="pageno">(\d+)<', s)
        if pn: seen_page.append((i, int(pn.group(1))))

        if 'class="prompt"' in s:
            has_prompt = True
            if 'class="checkpoint"' not in s:
                fail(f"{tag}: hands on slide with no checkpoint.")
            if "Type this" not in s and "TYPE THIS" not in s:
                warn(f"{tag}: hands on slide with no TYPE THIS block.")
            if not re.search(r"\d+\s*(min|minute)", st, re.I):
                fail(f"{tag}: hands on slide with no clock. The time is always on the slide.")
            # The prompt box starts at 1.45in and the note starts at 3.22in, so
            # the box owns 1.77in. The tag and the box padding take 0.71in of
            # that, leaving four lines of 12pt mono, and the 3.82in measure sets
            # 38 characters to the line. Past that the note prints on top of the
            # box. Without a note the floor is the checkpoint at 4.86in, which is
            # ten lines. Both numbers were found by rendering the page twice and
            # looking at it: the arithmetic said 53 characters and was wrong.
            bx = re.search(r'class="box">(.*?)</div>', s, flags=re.S)
            if bx:
                n_ch = len(re.sub(r"<[^>]+>", "", bx.group(1)).strip())
                ceiling = 130 if 'class="note"' in s else 360
                if n_ch > ceiling:
                    fail(f"{tag}: TYPE THIS box is {n_ch} characters against a ceiling of "
                         f"{ceiling}. It overruns and the next element prints on top of it. "
                         "Cut the prompt, do not shrink the type.")
        # An analogy is never the payload. A slide with no mechanism on it
        # (no table, no prompt, no list, no cards) is one half of a pair, and
        # the mechanism is the very next slide. Two soft slides in a row means
        # the metaphor was never cashed out.
        soft = not re.search(r'class="(tbl|prompt|card|stack|figure|shot|split|full|'
                             r'flow|spine|fishbone|funnel|venn|matrix|swim|layers|'
                             r'waterfall|linechart|stackbar|multiples|rings)"|<ul>', s)
        soft_slides.append((i, soft))

        if 'class="checkpoint"' in s: has_checkpoint = True
        if re.search(r"Run it|Lite|Watch|Cowork|route [ABC]", st) and s.count('class="card"') == 3:
            has_tiers = True
        if re.search(r"where (this|it) breaks|watching for|get wrong|honest|fails", st, re.I):
            has_honesty = True

    for (a, sa), (b, sb) in zip(soft_slides, soft_slides[1:]):
        if sa and sb and a != 1:
            warn(f"slides {a} and {b}: two slides in a row with no mechanism on them. "
                 "An analogy or a claim is followed immediately by the real terms, "
                 "not by another analogy or claim.")

    # ---- shape and rhythm -------------------------------------------
    # These three rules exist because a deck passed every other check in this
    # file and was still dull to look at. Rendered as a contact sheet, thirty
    # pages showed seventeen that were the same object: an eyebrow, a claim,
    # and a row of bordered boxes. Nothing in the grammar was broken. The
    # grammar was just used the same way seventeen times.
    #
    # The deck is judged as a sheet of thumbnails, not as one slide at a time,
    # because that is how a room experiences it over ninety minutes.
    def shape(s):
        """The one thing a slide is, in the order a reader notices it."""
        if "t-h1" in s:              return "cover"
        if "chapnum" in s:           return "chapter"
        if 'class="statement"' in s: return "statement"
        if 'class="prompt"' in s:    return "prompt"
        if 'class="full"' in s:      return "full"
        if 'class="shot"' in s:      return "shot"
        if 'class="figure"' in s:    return "figure"
        if 'class="split"' in s:     return "split"
        if 'class="flow"' in s:      return "flow"
        if 'class="spine"' in s:     return "spine"
        if 'class="fishbone"' in s:  return "fishbone"
        if 'class="funnel"' in s:    return "funnel"
        if 'class="venn"' in s:      return "venn"
        if 'class="matrix"' in s:    return "matrix"
        if 'class="swim"' in s:      return "swim"
        if 'class="layers"' in s:    return "layers"
        if 'class="waterfall"' in s: return "waterfall"
        if 'class="linechart"' in s: return "line"
        if 'class="stackbar"' in s:  return "stackbar"
        if 'class="multiples"' in s: return "multiples"
        if 'class="rings"' in s:     return "rings"
        if 'class="chart"' in s:     return "chart"
        if 'class="stack"' in s:     return "stack"
        if 'class="tbl"' in s:       return "table"
        if 'class="timeline"' in s:  return "timeline"
        if 'class="tree"' in s:      return "tree"
        if 'class="card"' in s:      return "grid"
        return "plain"

    shapes = [(i, shape(s)) for i, s in enumerate(slides, 1)]
    body = [(i, k) for i, k in shapes if k not in ("cover", "chapter")]

    if len(body) >= 8:
        grids = [i for i, k in body if k == "grid"]
        if len(grids) * 100 > 55 * len(body):
            fail(f"{len(grids)} of {len(body)} content slides are card grids "
                 f"({len(grids)*100//len(body)}%). The ceiling is 55. A grid is one "
                 "move, not the deck. Turn the ones carrying a relationship into a "
                 "tree or a timeline, the ones carrying a comparison into a table, "
                 "and the ones carrying a turn into a statement.")

    # Four of anything in a row reads as one long slide. A chapter divider
    # resets the count: it is a full page of its own and the room does see it.
    run, longest, where = 0, 0, None
    prev = None
    for i, k in shapes:
        if k in ("cover", "chapter"):
            run, prev = 0, None
            continue
        run = run + 1 if k == prev else 1
        prev = k
        if run > longest:
            longest, where = run, (k, i)
    if longest > 3:
        k, i = where
        fail(f"{longest} {k} slides in a row, ending at slide {i}. Three is the "
             "ceiling. Break the run with a different shape, do not reorder it.")

    # The band, the dark inversion, the statement and the strip are the four
    # places the room stops reading and looks up. SKILL.md has said "roughly
    # one slide in five" since the first version and nothing enforced it, which
    # is how a deck shipped with two runs of five flat pages in the middle.
    # Chapter dividers count: they are dark, and they do break the run.
    def looks_up(s):
        return ("stage dark" in s or 'class="band"' in s
                or 'class="statement"' in s or 'class="strip"' in s)
    quiet, worst, at = 0, 0, None
    for i, s in enumerate(slides, 1):
        if looks_up(s):
            quiet = 0
        else:
            quiet += 1
            if quiet > worst:
                worst, at = quiet, i
    if worst > 4:
        fail(f"{worst} consecutive slides with nothing to look up at, ending at "
             f"slide {at}. One in five carries a band, a dark inversion, a "
             "statement or a strip. Put one in the middle of that run.")

    # ---- evidence on the slides -------------------------------------
    # A deck can cite five sources in a companion document and still put
    # nothing on the screen worth writing down. These rules are about the
    # slides, not the research behind them.
    n_chart = sum(1 for s in slides if 'class="chart"' in s)
    n_stat = sum(1 for s in slides if 'class="stat"' in s)
    if n >= 14 and n_chart + n_stat == 0:
        fail("no chart and no numbers anywhere in the deck. A room remembers a shape "
             "and a figure, and forgets a paragraph. At least one slide carries either.")
    for i, s in enumerate(slides, 1):
        # Six bars is the ceiling: a seventh row runs from 1.32 past 3.7125
        # and the band prints on the chart. Measured, not guessed.
        n_bar = len(re.findall(r'class="ch-row"', s))
        if n_bar > 6:
            fail(f"slide {i}: a chart of {n_bar} bars. Six is the ceiling, and past it "
                 "the chart reaches the band.")
        if n_bar and 'class="band"' in s:
            fail(f"slide {i}: a chart and a band. The chart owns the middle of the page.")
        # The sceptic in row three gets a source or the number is decoration.
        if (re.search(r'class="(chart|stat|waterfall|linechart|stackbar|multiples|rings)"', s)
                and 'class="source"' not in s):
            fail(f"slide {i}: numbers with no source line. Any figure from outside this "
                 "room carries where it came from and when, on the slide, in 8pt.")

    # The shortcut is the reason they came rather than reading the docs. One
    # per block. The ceiling stops it becoming a colour rather than a signal.
    n_tip = sum(s.count('class="card tip"') for s in slides)
    n_chap = sum(1 for _, k in shapes if k == "chapter")
    if n >= 14:
        if n_tip < max(1, n_chap):
            fail(f"{n_tip} shortcut cards against {n_chap} blocks. Every block hands them "
                 "one thing they could not have read in the documentation: the default "
                 "worth changing, the flag that saves the afternoon, the two steps done "
                 "in the other order. Mark it with class=\"card tip\".")
        if n_tip * 3 > n:
            fail(f"{n_tip} shortcut cards in {n} slides. Past one slide in three it stops "
                 "reading as a shortcut and starts reading as a colour.")

    # Specificity. A deck of round claims and no figures is an opinion piece.
    with_num = sum(1 for s in slides if re.search(r"\d", visible_text(s).replace("&nbsp;", " ")))
    if n >= 14 and with_num * 3 < n:
        warn(f"only {with_num} of {n} slides carry a number. Concrete over abstract: a "
             "count, a duration, a cost, a date. Round claims are forgettable.")

    if n >= 20:
        n_stmt = sum(1 for _, k in shapes if k == "statement")
        if n_stmt < 2:
            fail(f"{n_stmt} statement slides in a {n} slide deck. A deck this long "
                 "turns at least twice, and the turn is a full bleed line, not "
                 "another row of cards.")

    for i, p in seen_page:
        if p != i:
            fail(f"slide {i}: page number reads {p}")

    if has_prompt and not has_tiers:
        fail("hands on blocks present but no three tier participation slide. Nobody gets stuck at the door.")
    if not has_honesty:
        fail("no honesty slide. Every deck names where it breaks, late, before the close.")
    if not has_checkpoint:
        fail("no checkpoint anywhere in the deck.")
    if n >= 8 and not any("chapnum" in s for s in slides):
        warn("no chapter dividers in a deck this long. Blocks should be visible.")



    # ---- is the block the right block ---------------------------------
    # A vocabulary of nineteen shapes is a way to be wrong in nineteen new
    # ways. Most of "which block" is judgment and stays in SKILL.md, but a
    # useful share of misuse is arithmetic and belongs here: a flow of two
    # is a sentence with an arrow in it, a 2x2 with nothing marked is four
    # boxes, a funnel whose bars do not narrow is a bar chart lying about
    # its own shape.
    for i, s in enumerate(slides, 1):
        tag = f"slide {i}"

        if 'class="flow"' in s:
            n_st = len(re.findall(r'class="fl-step"', s))
            if n_st < 3:
                fail(f"{tag}: a flow of {n_st}. Two boxes and an arrow is a "
                     "sentence. Three is where a sequence starts being a shape.")
            if n_st > 5:
                fail(f"{tag}: a flow of {n_st} steps. Five is the ceiling; past it "
                     "the boxes are too narrow to hold the words that explain them.")

        if 'class="venn"' in s:
            n_set = len(re.findall(r'class="vn-set"', s))
            if n_set > 3:
                fail(f"{tag}: a venn of {n_set} sets. Three is the ceiling, because "
                     "four circles cannot show all their intersections and the one "
                     "you care about stops being visible.")

        if 'class="matrix"' in s:
            if 'class="mx-q hi"' not in s:
                fail(f"{tag}: a 2x2 with no quadrant marked. A matrix exists to say "
                     "which quadrant is the answer. Unmarked it is four boxes with "
                     "axes drawn round them. Add hi to one.")
            if 'class="mx-x"' not in s or 'class="mx-y"' not in s:
                fail(f"{tag}: a 2x2 with an unlabelled axis. Both axes are named or "
                     "the reader is guessing what the position means.")

        if 'class="funnel"' in s:
            ws = [float(w) for w in re.findall(r'class="fn-bar"[^>]*--w:\s*([\d.]+)', s)]
            if ws and any(b > a for a, b in zip(ws, ws[1:])):
                fail(f"{tag}: a funnel whose bars widen. The widths are {ws}. A funnel "
                     "is a thing that loses volume at every stage; if yours gains, it "
                     "is a bar chart and should say so.")

        for cls, lim, why in (("sb-seg", 4, "segments in a stacked bar. Past four nobody "
                               "can match the legend to the stack and a table is honest"),
                              ("mu-cell", 6, "small multiples. Six is the ceiling and four "
                               "is better; past it each panel is too small to read"),
                              ("rg", 4, "rings on one slide. Past four they stop being "
                               "figures worth writing down and become a pattern")):
            for block in re.findall(r'class="(?:stackbar|multiples|rings)".*?(?=<div class="(?:kicker|source|pageno)"|</div></section>)', s, re.S):
                n_c = len(re.findall(rf'class="{cls}[ "]', block))
                if n_c > lim:
                    fail(f"{tag}: {n_c} {why}.")

        if 'class="shot"' in s and "--ar" not in s:
            fail(f"{tag}: a shot with no --ar. The box has to carry the image's own "
                 "aspect ratio or the pins land in the gutter beside the picture "
                 "instead of on it.")

        for block in re.findall(r'<img[^>]*>', s):
            if "alt=" not in block:
                warn(f"{tag}: an image with no alt text.")

        for cls, name, lim in (("spn-node", "spine", 3), ("ly-row", "layers", 3)):
            if f'class="{name}"' in s:
                # [ "] and not a closing quote: ly-row hi is still a
                # ly-row. Counting class="ly-row" exactly saw two of four
                # and failed a correct slide. This is the third time this
                # exact mistake has cost something in this repo.
                n_r = len(re.findall(rf'class="{cls}[ "]', s))
                if n_r < lim:
                    fail(f"{tag}: a {name} of {n_r}. Under three there is no sequence "
                         "to show and two cards say it more plainly.")

        if 'class="fishbone"' in s:
            if 'class="fb-head"' not in s:
                fail(f"{tag}: a fishbone with no effect at the end of the spine. The "
                     "causes have to feed something or it is four labels on a line.")
            n_rib = len(re.findall(r'class="fb-rib', s))
            if n_rib < 3:
                fail(f"{tag}: a fishbone with {n_rib} ribs. Under three, the causes are "
                     "a list and the diagram is decoration.")

    # ---- does the deck show anything ---------------------------------
    # This rule exists because a deck passed every other check in this
    # file with thirty slides and not one picture in it. The shape rules
    # above count the arrangement of text containers, so a deck can vary
    # its boxes perfectly and still be words from end to end, and the
    # contact sheet does not catch it either: thirty varied text slides
    # look varied.
    #
    # A slide is the one medium that can show a thing. A deck that never
    # does is a document read aloud, and the room would rather have the
    # document.
    VISUAL = ("figure", "shot", "split", "full", "flow", "spine", "fishbone",
              "funnel", "venn", "matrix", "swim", "layers", "chart",
              "waterfall", "line", "stackbar", "multiples", "rings")
    shown = [i for i, k in shapes if k in VISUAL]
    if n >= 14 and not shown:
        fail(f"{n} slides and not one of them shows anything. No picture, no "
             "diagram, no chart. The shape rules above only count how the text "
             "is boxed, so a deck can pass all of them and still be words from "
             "end to end. Ask which slide is a pipeline, a comparison of two "
             "axes, a screenshot with the thing circled on it, and build that "
             "one first.")
    elif n >= 20 and len(shown) < 2:
        warn(f"only {len(shown)} slide in {n} shows a picture or a diagram. In a "
             "deck this long that is close to none.")


    # ---- does the deck deliver its own promise ------------------------
    # The one thing about an argument that is actually checkable. A deck
    # opens by saying what the room walks out with and closes by handing
    # something over. If those two share no content words at all, the
    # deck promised one thing and delivered another, and that is a real
    # defect rather than a matter of taste.
    #
    # It cannot tell you the argument is wrong. It can tell you the deck
    # forgot what it opened with, which in practice is most of the cases
    # where a close lands flat.
    STOP = set("""the a an and or but of to in on for with from that this it is are was
    were be been being you your yours we our us they them their what which who how why
    when where can will would could should not no yes all any some one two three each
    every more most much many into out up down over under after before then than as at
    by if so do does did have has had here there now new own same other else about""".split())
    def words(t):
        return {w for w in re.findall(r"[a-z]{4,}", t.lower()) if w not in STOP}
    stand = re.search(r'class="t-stand">(.*?)</div>', html, flags=re.S)
    if stand:
        promise = words(re.sub(r"<[^>]+>", " ", stand.group(1)))
        delivered = words(visible_text(slides[-1]))
        shared = promise & delivered
        if promise and not shared:
            warn("the close shares no content word with the cover's promise. The cover "
                 f"says {sorted(promise)[:6]} and the close says none of it. Either the "
                 "deck drifted from what it opened with, or the close is handing over "
                 "something the room was not told to expect.")

    # ---- the argument, made readable ---------------------------------
    # Not a rule. The titles read in sequence are the argument, and the
    # only way to judge whether it holds is to read them in sequence,
    # which nobody does because they are spread over thirty pages.
    if outline:
        print("\nTHE ARGUMENT, in order. Read it as prose; if it does not hold "
              "here it will not hold in the room.\n")
        for i, sl in enumerate(slides, 1):
            k = shape(sl)
            t = re.search(r'class="(?:t-h1|title)">(.*?)</(?:h1|h2)>', sl, flags=re.S)
            if not t:
                t = re.search(r'class="(?:chapter|statement)">\s*<h2>(.*?)</h2>', sl, flags=re.S)
            raw = re.sub(r"<br\s*/?>", " ", t.group(1)) if t else ""
            txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", raw)).strip() if t else "-"
            print(f"  {i:>2}  {k:<10} {txt}")
        print()

    # ---- the close is a transfer and a CTA --------------------------
    close = visible_text(slides[-1])
    for pat, why in (
        (r"\bthank you\b|\bthanks\b", "a thank you. The close is a transfer, not gratitude"),
        (r"\bany questions\b|^\s*questions\??\s*$", "'any questions'. That is not a CTA"),
        (r"connect with me on|follow me on|\blet'?s connect\b",
         "'let us connect'. That is a CTA for you, not for them, and the room can tell"),
    ):
        if re.search(pat, close, re.I | re.M):
            fail(f"the close slide ends on {why}.")

    # One action, dated, and it comes back to you. The imperative is the part
    # that is actually detectable; the other two are worth a warn each.
    imperative = (r"\b(run|send|bring|write|pick|take|open|start|book|try|ship|post|"
                  r"reply|share|screenshot|do|use|put|add|delete|measure|ask|show|"
                  r"email|message|build|fix|test|check)\b")
    if not re.search(rf"(?:^|[.!?]\s+|>\s*){imperative}", close, re.I | re.M):
        fail("the close slide carries no CTA. One card is an imperative: the single "
             "thing they do next, dated, doable alone, and it comes back to you.")
    else:
        if not re.search(r"\b(today|tonight|tomorrow|monday|tuesday|wednesday|thursday|"
                         r"friday|this week|next week|before|by the|within|in the next)\b",
                         close, re.I):
            warn("the close slide has a CTA with no date on it. 'Soon' is not a date.")
        if not re.search(r"\b(send me|bring|reply|post it|share it|email me|show me|"
                         r"bring it|message me)\b", close, re.I):
            warn("the close slide has a CTA with no return path. A CTA that does not "
                 "come back to you gives you no signal about whether the day worked.")

    return report()

def report():
    for w in WARN: print("WARN  " + w)
    for f in FAIL: print("FAIL  " + f)
    print(f"\n{len(FAIL)} fail, {len(WARN)} warn")
    return 1 if FAIL else 0

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("deck_dir", nargs="?", default=".")
    ap.add_argument("--outline", action="store_true",
                    help="print the eyebrow and title of every slide in order, so the "
                         "argument can be read as prose in half a minute")
    a = ap.parse_args()
    sys.exit(main(a.deck_dir, a.outline))
