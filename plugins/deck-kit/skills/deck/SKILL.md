---
name: deck
description: Build a workshop deck as a single self contained HTML file in one of three measured themes, plus a PDF and a published link. Use for any training deck, workshop, session or talk. Trigger with /deck.
---

# deck

Takes a topic, a slide count, an audience and a theme. Produces one HTML file that opens in any browser, prints to a pixel faithful PDF, and publishes as a link.

```
/deck "Prompt engineering for marketers" slides=14 audience=mixed theme=daylight duration=90
```

| Parameter | Values | Default |
|---|---|---|
| topic | free text | required |
| slides | 8 to 40 | 14 |
| audience | `non-tech` `mixed` `tech` `exec` | `mixed` |
| theme | `daylight` `paper` `sage` `boardroom` `navy` `crimson` `slate` `mist` `moss` `linen` `plum` | `daylight` |
| duration | minutes in the room | 90 |
| session | "Session 2 of 3" | omitted |

**Offer the parameters before you infer them.** Audience, theme and slide count each change what gets built, so put them to the user as a choice at the start rather than picking and mentioning it afterwards. Duration and session are safe to infer.

**Render the sampler and show it in the conversation before you ask which theme.** Not a link, not a filename, not a list of names: the image, in front of them, in the message that asks the question. This is as non negotiable as asking the exits question in step 6, and for the same reason. `sage`, `mist`, `daylight` and `slate` mean something once you have seen a deck in them and nothing at all before that, so a list of names is asking somebody to pick a colour with their eyes shut.

```bash
python3 <skill>/scripts/sampler.py <somewhere>   # writes themes.png
```

Then read `themes.png` back yourself and attach it to the question. One labelled panel per built theme, each showing the page ground, a plain card, the shortcut card's tint and rule, the accent, and the band with white type on it. Putting it in a README or a docs page instead does not count: the person choosing is in this conversation, not in the repo.

`references/THEMES.md` is the theme and layout menu. Read it before writing anything.

| theme | Reach for it when |
|---|---|
| `daylight` | hands on workshops where people are typing along. It owns that vocabulary: prompt boxes, file trees, checkpoints, recovery strips |
| `paper` | conceptual teaching, frameworks, an argument that is a progression rather than a task list. Executive rooms |
| `sage` | calm subjects, strategy and policy, rooms being asked to think rather than type. Do not use it for anything printed in black and white: the structure is carried by gradients and greyscale flattens all of it |
| `boardroom` | the synthesis deck. A board, an investment committee, a steering group. Serif titles over a sans body, deep green, and no gradient anywhere |
| `navy` | the evidence deck. One blue in three values, so a chart carries rank by depth of colour rather than by five hues |
| `crimson` | the recommendation deck, and only when it is short. One family, one red. The red is not rationed by the stylesheet, so past about fifteen slides it stops emphasising and starts shouting |
| `slate` | rooms where colour would be read as a claim. Regulators, auditors, legal, a supplier review. The only theme that survives a black and white photocopier |
| `mist` | the same rooms as `sage`, when green is wrong. Sage's calm with the hue turned to a dusty blue, on a pale blue grey ground. Reach for it for a second session that should not look like the first |
| `moss` | what people mean when they ask for a lighter sage. Pale green ground, a warmer olive accent, and flat, so unlike `sage` it survives being printed |
| `linen` | warm paper and a soft clay accent. The quiet end of the warm range, where `paper` is the loud end. The easiest of the eleven to read for an hour, so reach for it for long form teaching |
| `plum` | the deck that has to not look like every other deck in the day. Muted violet, the highest contrast accent in the kit. It differentiates rather than argues, so not for a sceptical room |

The eight generated themes are flat by construction: no gradient on the dark slides, no gradient on the band, a small tracked chapter label instead of a 92pt numeral, and hairline rules on the cards. That is the departure from `sage`, and it is deliberate. A gradient is the first thing a projector in a badly lit room turns into a smear.

Each generated stylesheet carries its own contrast table in its header, computed before the file was written. Fifteen pairs per theme, every one cleared. The header also records why none of them is named after a consulting firm: the published hex values for those firms contradict each other, none is official, and a deck that wears another firm's identity is passing itself off.

The generated eight come in two groups, and the difference is the ground they stand on. `boardroom`, `navy`, `crimson` and `slate` stand on white and are built for a pack that gets printed and passed around. `mist`, `moss`, `linen` and `plum` stand on a tinted ground, which is what makes them read as `sage` variants rather than as consulting decks.

Two things about the quiet four that only showed up in the render, not in the CSS:

- **`linen` and `plum` set wider.** Epilogue and Sora both run longer than Manrope and Nunito Sans at the same size, so a cover headline or a title that sits on one line in `mist` takes two in those. Moving a finished deck between them is not free. Re render before you present it.
- **The accent in this group is never light, and it cannot be.** It carries small type on a pale ground and has to clear 4.5:1 there. "Light sage green" as an accent fails outright. What lifts is the page and the card; the theme reads light because three quarters of the slide is the ground.

## Step 0, do the research. Before the block plan, not after.

**Search the web first, every time, even on a topic you know well.** A deck built from what the model already knows is a deck of round claims, and a room can tell within two slides. The research is what produces the numbers, the trend and the shortcuts, and none of those can be invented.

Four searches is the floor:

1. **The size of the problem.** A survey, a benchmark, an industry report from the last eighteen months. This is the number on the early slide that makes the room sit up.
2. **The trend.** The same measure at two or three points in time, so the chart has a direction and not just a height.
3. **What practitioners actually complain about.** Engineering blogs, incident write ups, conference talks. This is where the shortcuts come from, and they are worth more than the survey.
4. **The counter evidence.** Somebody credible who says the opposite. It goes on the honesty slide and it is the reason the room believes the other twenty nine.

Write what you find into `EVIDENCE.md` in the deck directory, one line per claim, before writing a single slide:

```markdown
| Claim | Number | Source | Published | Cleared |
|---|---|---|---|---|
| Most pilots never reach production | 42% | Name of report, publisher | 2026-03 | yes, external |
| Our own audit time | 1 hour | Raygency, B8 sessions | 2026-09 | no, a model not a case study |
```

`check.py` requires the file, five distinct sources, and a year within sight of each URL.

**Three rules about numbers, and they are not negotiable.**

- A number goes on a slide only if it has a line in `EVIDENCE.md`. The slide carries a `source` line in 8pt saying where and when.
- Anything of ours that has not been cleared stays off the slides and goes in the facilitator notes. Uncleared proof on a slide is the one mistake that costs the room permanently.
- Every cost figure we produce is a model, not a case study, and the slide says so in those words.

**The shortcuts.** Three or four per deck, one per block, and they come out of search step 3 rather than out of the textbook. A shortcut is the default worth changing, the flag that saves an afternoon, the two steps worth doing in the other order, the thing that only shows up after somebody has run this in anger. If it reads like documentation, it is not one. They go on the slides as `class="card tip"`, not only in the notes: the room came for these.

## Step 1, plan the blocks. Do not open the HTML yet.

A deck is scaffolding for a session that is mostly not the deck. Sixty minutes of slides is fifteen minutes of slides plus forty five of building.

Write the block plan in the chat and get it agreed before generating:

1. **Blocks, not topics.** Each block is one claim, one proof of the claim, then the room doing it themselves. Budget one block per 20 to 25 minutes.
2. **Write each block's single claim before any content.** One sentence. If you cannot write it, the block is not ready, and no amount of slide polish fixes that.
3. **Pick one extended metaphor for the whole deck** and check it still holds three concepts later. One per deck. Never mix two.
4. **Decide the hands on blocks** and what real input the room brings to each. Real, from their own week, never hypothetical.
5. **Decide the honesty slide.** Where this breaks. Late, before the close. `check.py` fails the deck without one.
6. **Decide the transfer.** What they carry out that still works after the room empties.

## Step 2, budget the slides

| Slides | Shape |
|---|---|
| 8 | cover, agenda, 4 content, statement, close |
| 14 | cover, agenda, 3 chapters, 6 content, tiers, prompt, statement, close |
| 20 | cover, agenda, 4 chapters, 9 content, 2 tiers, 2 prompt, statement, close |
| 30+ | as above, one chapter per block, never more than 7 content slides per block |

Fixed rules regardless of count, each one enforced by `check.py`:

- Exactly one cover, and it is slide 1.
- The close is a transfer and it ends on a call to action. Never a thank you slide. `check.py` fails a close that says thank you, asks for questions, or invites people to connect, and fails one with no imperative on it. Make the CTA one action, put a date on it, keep it small enough to do without anyone's permission, and give it a way back to you.
- No placeholders on slides. `foo`, `Acme Corp`, `lorem ipsum` and `John Doe` all fail. A fake number teaches the room that the numbers do not matter.
- Every hands on block is preceded by a tiers slide, so nobody is stuck at the door.
- At least one honesty slide, positioned late.
- One or two dark inversion slides in the whole deck, reserved for the turn of the argument.
- The accent band appears only where the room should stop reading and look up. Once per slide at most, roughly one slide in five.

### Step 2b, budget the shapes before you write a word of them

A deck is read as a sheet of thumbnails, not one slide at a time. This section exists because a deck once passed every other rule in this file and was still dull to look at: seventeen of its twenty five content slides were the same object, an eyebrow, a claim and a row of bordered boxes. Nothing was broken. One move was used seventeen times.

Write the shape next to each slide in the plan, before the content. `check.py` fails the deck on all four of these.

| Rule | Number |
|---|---|
| Card grids, as a share of content slides | 55 percent, ceiling |
| The same shape in a row, chapter dividers resetting the count | 3, ceiling |
| Consecutive slides with nothing to look up at | 4, ceiling |
| Statement slides in a deck of 20 or more | 2, floor |

The grid is the default because it is the easiest thing to write, which is exactly why it needs a cap. Before reaching for one, ask what the slide is actually carrying:

| The slide carries | The shape |
|---|---|
| Two options weighed against each other | `tbl`, two columns, not two cards |
| A sequence, a pipeline, a thing that happens in order | `timeline` or `tree` |
| One claim the whole block turns on | `statement`, full bleed, dark |
| A set of three or four parallel things | `grid`, and only here |
| A thing they type | `prompt` |

Something to look up at means a band, a dark inversion, a statement, a strip or a chapter divider. Five flat pages in a row is the point where a room stops reading the slides and starts reading their phone.

## Step 3, write the slides

Copy blocks out of `assets/layouts.html`. Never invent a class. If a slide will not fit a layout, the slide is wrong, not the kit.

Per slide:

- **The cover wordmark ships as `your<em>brand</em>`.** Replace both halves with the presenter's own. The `<em>` half picks up the theme accent, so pick the split point deliberately: it is the whole design of the mark.
- **Eyebrow** is a category, not a sentence. "Round 1", "The moment", "Where this breaks".
- **Title is a claim.** "Four boring facts. One real problem." not "The scenario". A title ending in a colon is a label and fails the check.
- **An analogy is never the payload.** A slide carrying the metaphor is followed immediately by the slide carrying the mechanism: the real terms, the table, the numbers, the command. Adjacent, in that order, nothing in between. Then the analogy retires.
- **Six items maximum**, per container. Card bodies run two or three lines; four means the card is doing too much.
- **TYPE THIS is verbatim**, exactly what they copy off the screen, never a paraphrase.
- **Every hands on slide carries a clock**, one rule not a list, an escape hatch, and a checkpoint.
- **The recovery strip** says what to do when their run did not produce what the slide just promised. A slide carrying the strip drops the slide number.

### Putting the evidence on the page

The research from Step 0 is worth nothing in a file nobody opens. Three blocks carry it onto the slides, and `check.py` counts all three.

| Block | Use it when | Rules |
|---|---|---|
| `chart` | the shape of the numbers is the argument, not the height of any one of them | six bars is the ceiling, values are percentages of the widest bar and not of a hundred, never on a slide that also carries a band |
| `stat` inside a card | one number per card, three or four cards, the numbers are parallel measures of the same thing | the numeral keeps its heading. A numeral with no heading is a quiz |
| `card tip` | the shortcut: the default worth changing, the flag that saves the afternoon | one per block, never more than one slide in three |

Every slide carrying a `chart` or a `stat` carries a `source` line under it, 8pt, italic, naming the publisher and the year. `check.py` fails the slide without one. A deck of fourteen slides or more with no chart and no numbers anywhere fails outright: it is an opinion, not a deck.

If the point survives being said in a sentence, say it in a sentence. A chart of three bars that all mean the same thing is decoration.

### The audience parameter picks a track, not a deck

Generate one deck and two tracks, never three decks.

| audience | On the slides | In the notes |
|---|---|---|
| `non-tech` | standard track, more checkpoints, more analogies | advanced depth, verbal only |
| `mixed` | standard track | one advanced line per block, plus what tells you to reach for it |
| `tech` | advanced track promoted onto the slides | standard track compressed to one recap line |
| `exec` | standard track, hands on becomes watch and discuss | trade off table and risk slide get more room |

If even a third of the room is non technical, keep the standard examples on the slides and add the depth verbally.

### Voice

Second person, present tense, contractions. Short declaratives for the landings. Concrete over abstract, always: not "busy professionals" but "a 32 year old data engineer in Berlin, 7pm Tuesday, fridge half empty". Real numbers. Name the hard thing before it is hard.

No dashes as punctuation. No AI lingo. Active voice. `check.py` fails the deck on the first three.

## Step 4, assemble

```
<deck-dir>/
├── slides.html       your <section class="slide"> blocks, nothing else
└── index.html        built from slides.html by build.py
```

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/deck/scripts/build.py <deck-dir> --theme paper
```

`build.py` pours `slides.html` into `assets/shell.html`, inlines the theme stylesheet whole and unedited, sets the matching font link, and takes the deck title off the cover headline.

Do not add rules to a theme stylesheet. If a slide needs CSS that is not in the file, stop and say so instead of inventing it.

`--footer "acme · B8"` sets the mark that prints opposite the page number on every slide but the cover, which already carries the wordmark at full size. The page then reads the mark on the left and the slide number on the right, on one baseline. Omit the flag and no mark prints. Pass it: a footer carrying the presenter and the module is most of what makes a printed page read as a document rather than a loose slide, and it costs one flag.

Most decks are worth four companion documents beside the HTML: facilitator notes with the timings and the answers, an FAQ of what the room actually asks, a runsheet for the day, and `EVIDENCE.md`, the sourced claims from Step 0. `check.py` expects `FACILITATOR.md`, `FAQ.md`, `RUNSHEET.md` and `EVIDENCE.md` in the deck directory and fails if any is missing or is a stub.

### Putting the client's logo on it

A deck delivered into somebody else's room wears their mark, not ours. That decision is made and it is not per deck:

```bash
python3 <skill>/scripts/build.py <deck-dir> --theme daylight \
        --footer "raygency \u00b7 B8" --logo path/to/client-logo.png
```

Three things move together, which is why it is one flag and not three:

1. On the cover, the client's logo takes our wordmark's position. The markup does not change, so an existing deck picks it up on the next build.
2. On every other light slide, a small version sits bottom left.
3. Our footer mark moves right, next to the page number, because the left corner now belongs to them.

It is inlined as a data URI, not linked, because `index.html` is one self contained file and a linked logo is a broken image the first time the deck is opened from a USB stick in a room with no wifi.

**It is not painted on dark slides.** A client logo is almost always dark ink on transparency, and on a dark chapter divider that is an invisible smudge. If the client has a reversed mark and wants it there, that is a second file and a change to this script, not something to fake with opacity.

Give it line art a few hundred pixels tall, PNG or SVG. The build warns past 150KB and refuses past 1MB, because whatever you pass is inlined into every copy of the deck that ever gets sent. A 609KB photograph turned a 53KB deck into 860KB in testing.

## Step 5, check on the bytes that ship

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/deck/scripts/check.py <deck-dir>
```

It reads the files off disk, not your draft. Fix every FAIL and re run. Do not report the deck as finished on a check you did not run or did not pass. WARNs are advisory, judge them.

Then look at it, and look at all of it. The whole deck as one sheet, not two pages you picked:

```bash
${CLAUDE_PLUGIN_ROOT}/skills/deck/scripts/export-pdf.sh <deck-dir>
python3 ${CLAUDE_PLUGIN_ROOT}/skills/deck/scripts/contact.py <deck-dir>  # writes contact.png
pdftoppm -png -r 90 -f 4 -l 4 <deck-dir>/deck.pdf /tmp/p                 # one page, close up
```

**Open `contact.png` and read it before you report the deck as finished.** This step is not optional and it is not the same as the check. The check catches rule breaks. It does not catch a slide that is ugly, a claim that does not land, or thirty pages that are the same page. A contact sheet catches all three in about four seconds, which is why it exists.

What you are looking for, in this order: can you tell two slides apart with the eyebrows covered; does the accent appear anywhere other than the chapter numerals; is there a run of flat pages in the middle; and is the cover the best page in the deck or the weakest.

## Step 6, the exits

**Ask with AskUserQuestion, `multiSelect: true`, all four options, every time.** Not prose at the end of a message, not a question the user has to answer in words, and never a choice of one. The four exits are not alternatives: a link, a PDF, a Markdown file and a Gamma are different deliverables for different rooms, and the common answer is all of them.

```
question:    "How do you want this deck out? Pick as many as you need."
header:      "Exits"
multiSelect: true
options:     GitHub Pages  |  PDF  |  Markdown  |  Gamma
```

**GitHub Pages**, the live link:

```bash
${CLAUDE_PLUGIN_ROOT}/skills/deck/scripts/publish-pages.sh <deck-dir> <repo-name> [owner]
```

`owner` defaults to `$DECK_GH_OWNER`, then to your own GitHub account. The script creates a **public** repo and enables Pages, because Pages on the Free plan publishes only from public repos. Confirm with the user before pushing anything with client names or unreleased material in it, and keep facilitator notes out of the published directory.

**PDF**, when the design has to survive the handoff. `export-pdf.sh`, above. It verifies the page count matches the slide count and fails loudly if not.

**Markdown**, the text of the deck as a file the user can read, diff or paste into another generator:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/deck/scripts/export-md.py <deck-dir>
```

Writes `<deck-dir>/deck.md`, one section per slide in running order, carrying the words and the structure and nothing else. It is an export, not a source: edits belong in `slides.html`, and running it again overwrites `deck.md`. It is also the hand route into Gamma when the user would rather paste than run a script, so offer it alongside Gamma rather than instead of it.

**Gamma**, only after the HTML is final. Gamma's URL import rejects GitHub Pages, so the route is the deck's text content, which produces a **new, separate** artifact in Gamma's own look. Gamma cannot edit an existing gamma and cannot round trip back. Say that plainly rather than implying a sync.

```bash
${CLAUDE_PLUGIN_ROOT}/skills/deck/scripts/gamma.sh <deck-dir>
```

**Never ask the user to paste an API key into the chat, and never accept one if they offer.** A key in the conversation is a key in the transcript, which is a key on disk. The script prompts for it silently, uses it for one request, and unsets it. It writes the key nowhere. That is why this exit is a command the user runs rather than a tool call you make.

If the user would rather you did it, the Gamma connector uses their existing authorisation and needs no key at all. Offer that as the alternative, not a key in a message.

## Feedback loop

Feedback lands on the HTML, which is the source of truth. Edit `slides.html`, re run `build.py`, re run the check, re publish to the same repo. The Gamma copy, if one exists, does not update; regenerate it or leave it.
