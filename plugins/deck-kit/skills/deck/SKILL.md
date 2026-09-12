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
| theme | `daylight` `paper` `sage` | `daylight` |
| duration | minutes in the room | 90 |
| session | "Session 2 of 3" | omitted |

**Offer the parameters before you infer them.** Audience, theme and slide count each change what gets built, so put them to the user as a choice at the start rather than picking and mentioning it afterwards. Duration and session are safe to infer.

`references/THEMES.md` is the theme and layout menu. Read it before writing anything.

| theme | Reach for it when |
|---|---|
| `daylight` | hands on workshops where people are typing along. It owns that vocabulary: prompt boxes, file trees, checkpoints, recovery strips |
| `paper` | conceptual teaching, frameworks, an argument that is a progression rather than a task list. Executive rooms |
| `sage` | calm subjects, strategy and policy, rooms being asked to think rather than type. Do not use it for anything printed in black and white: the structure is carried by gradients and greyscale flattens all of it |

## Step 1, plan the blocks. Do not open the HTML yet.

A deck is scaffolding for a session that is mostly not the deck. Sixty minutes of slides is fifteen minutes of slides plus forty five of building.

Write the block plan in the chat and get it agreed before generating:

1. **Blocks, not topics.** Each block is one claim, one proof of the claim, then the room doing it themselves. Budget one block per 20 to 25 minutes.
2. **Write the one point to land for every block before any content.** One sentence. If you cannot write it, the block is not ready, and no amount of slide polish fixes that.
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
- The close is a transfer. Never a thank you slide.
- Every hands on block is preceded by a tiers slide, so nobody is stuck at the door.
- At least one honesty slide, positioned late.
- One or two dark inversion slides in the whole deck, reserved for the turn of the argument.
- The accent band appears only where the room should stop reading and look up. Once per slide at most, roughly one slide in five.

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

### The audience parameter picks a track, not a deck

Generate one deck and two tracks, never three decks.

| audience | On the slides | In the notes |
|---|---|---|
| `non-tech` | standard track, more checkpoints, more analogies | advanced depth, verbal only |
| `mixed` | standard track | one advanced line per block plus its pivot signal |
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

`build.py` pours `slides.html` into `assets/shell.html`, inlines the theme stylesheet whole and unedited, sets the matching font link, and takes the deck title off the cover headline. Do not add rules to a theme stylesheet. If a slide needs CSS that is not in the file, stop and say so instead of inventing it.

Most decks are worth three companion documents beside the HTML: facilitator notes with the timings and the answers, an FAQ of what the room actually asks, and a runsheet for the day. `check.py` expects `FACILITATOR.md`, `FAQ.md` and `RUNSHEET.md` in the deck directory and fails if any is missing or is a stub.

## Step 5, check on the bytes that ship

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/deck/scripts/check.py <deck-dir>
```

It reads the files off disk, not your draft. Fix every FAIL and re run. Do not report the deck as finished on a check you did not run or did not pass. WARNs are advisory, judge them.

Then look at it. Render a few pages to images and read them back:

```bash
${CLAUDE_PLUGIN_ROOT}/skills/deck/scripts/export-pdf.sh <deck-dir>
pdftoppm -png -r 90 -f 4 -l 4 <deck-dir>/deck.pdf /tmp/p
```

The check catches rule breaks. It does not catch a slide that is ugly or a claim that does not land. Only looking does.

## Step 6, the exits

**Ask with AskUserQuestion, `multiSelect: true`, all three options, every time.** Not prose at the end of a message, not a question the user has to answer in words, and never a choice of one. The three exits are not alternatives: a link, a PDF and a Gamma are different deliverables for different rooms, and the common answer is all of them.

```
question:    "How do you want this deck out? Pick as many as you need."
header:      "Exits"
multiSelect: true
options:     GitHub Pages  |  PDF  |  Gamma
```

**GitHub Pages**, the live link:

```bash
${CLAUDE_PLUGIN_ROOT}/skills/deck/scripts/publish-pages.sh <deck-dir> <repo-name> [owner]
```

`owner` defaults to `$DECK_GH_OWNER`, then to your own GitHub account. The script creates a **public** repo and enables Pages, because Pages on the Free plan publishes only from public repos. Confirm with the user before pushing anything with client names or unreleased material in it, and keep facilitator notes out of the published directory.

**PDF**, when the design has to survive the handoff. `export-pdf.sh`, above. It verifies the page count matches the slide count and fails loudly if not.

**Gamma**, only after the HTML is final. Gamma's URL import rejects GitHub Pages, so the route is the deck's text content, which produces a **new, separate** artifact in Gamma's own look. Gamma cannot edit an existing gamma and cannot round trip back. Say that plainly rather than implying a sync.

```bash
${CLAUDE_PLUGIN_ROOT}/skills/deck/scripts/gamma.sh <deck-dir>
```

**Never ask the user to paste an API key into the chat, and never accept one if they offer.** A key in the conversation is a key in the transcript, which is a key on disk. The script prompts for it silently, uses it for one request, and unsets it. It writes the key nowhere. That is why this exit is a command the user runs rather than a tool call you make.

If the user would rather you did it, the Gamma connector uses their existing authorisation and needs no key at all. Offer that as the alternative, not a key in a message.

## Feedback loop

Feedback lands on the HTML, which is the source of truth. Edit `slides.html`, re run `build.py`, re run the check, re publish to the same repo. The Gamma copy, if one exists, does not update; regenerate it or leave it.
