# Themes and layouts

Three themes and eleven layouts. Pick a theme by name, pick layouts by name.

Every theme uses the same geometry, expressed proportionally: `--stage-w` is the stage width, `--in` is one tenth of it, and `--pt` is `--in / 72`. All geometry is `calc(N * var(--in))` and all type is `calc(Npt * var(--pt))`. A deck is therefore dimensionally identical at any viewport, and prints at any paper size without a single fixed pixel.

---

## Themes

### `daylight`

**Looks like:** white ground, teal `#028090`, mint `#02C39A` on the dark turns, one burnt orange `#C1440E` band where the room should look up. Caladea headings, Carlito body, Courier New for anything typed.

**Use it for:** hands on workshops where people are typing along. It has the vocabulary for that: checkpoints, recovery strips, prompt boxes, file trees.

### `paper`

**Looks like:** warm paper `#FAF7F2` with `#E5DFD5` rules, near black `#1A1A1A` text, and one accent family in three weights: brick `#B85042` on light, darkened brick `#9E4238` for filled shapes and the band, lightened brick `#E08B6F` on the dark slides. Gelasio throughout, one family, hierarchy from weight and colour rather than a second typeface. Chapters numbered top left. Comparison tables with hairline rules instead of cards.

Two working rules, both arithmetic rather than taste:

- The band is `#9E4238` with white type, 6.38:1. The same ground on light and dark slides, because the band is meant to interrupt the page rather than belong to it.
- `#B85042` is 3.28:1 on the warm dark ground `#24201C` and unreadable there. Dark slides use `#E08B6F`, which is 6.23:1 on that ground and 5.24:1 on a dark card. Never use `#E08B6F` on light paper.

**Use it for:** conceptual teaching, frameworks, anything where the argument is a progression rather than a task list. This is the one for executive rooms.

### `sage`

**Looks like:** pale sage `#F2F5F1` ground, one green family, no second hue anywhere. Gradients on exactly three surfaces: the dark slides, a soft wash in the bottom right corner of the cover, and the band. Everything else is flat, because a gradient under body text moves the contrast ratio around while the reader is still inside the sentence. Outfit for headings, Figtree for body, so this is the only theme with no serif in it.

Every colour was picked by computing the ratio first:

| Job | Colour | Ratio |
|---|---|---|
| Ink on the page | `#14201A` | 15.27:1 |
| Body and card text | `#5C6B62` | 5.12 on page, 4.65 on card |
| Accent, small text on light | `#37604A` | 6.51 on page, 5.92 on card |
| Filled shapes, white type | `#2F5742` | 8.19:1 |
| Band on light, gradient | `#2F5742` to `#47795C`, white type | 8.19 falling to 5.05 |
| Band on dark, gradient | `#9CC9AE` to `#C6E0D0`, ink type | 8.43 against the ground, 9.09 for the type |
| Accent on the dark ground | `#9CC9AE` | 8.43 on ground, 6.34 on a dark card |

Two working rules:

- **The band inverts on dark slides.** Dark on dark it sits at 1.6:1 against the ground: perfectly legible, and completely invisible as an interruption, which is the band's only job. Pale field, ink type.
- **The gradient stops at `#47795C`.** One step lighter, `#4E8263`, drops white type to 4.47 and fails. That is a ceiling, not a preference.

**Use it for:** calm subjects, strategy and policy sessions, anything where the room is being asked to think rather than type.
**Do not use it for:** decks that get printed in black and white. The structure is carried by three gradients and a single hue, and greyscale flattens all of it.

---

## Layouts

The same eleven names work in all three themes. A deck is a list of these. Copy the markup out of `assets/layouts.html` and never invent a class.

| Name | What it is | Holds |
|---|---|---|
| `cover` | Opening slide: wordmark, series line, headline, rule, standfirst, presenter, date | 1 headline, 1 standfirst |
| `agenda` | Timeline rows, time in the left column, what happens in the right | 4 to 6 rows |
| `chapter` | Full bleed divider. Block label, one word title, one line of setup. Nothing else | 3 lines |
| `three-up` | Three numbered cards | 3 cards, 2 to 3 lines each |
| `four-up` | Four numbered cards. Reads well inverted | 4 cards, 2 lines each |
| `two-up` | Two columns, usually do and don't | 2 lists, 4 to 6 items |
| `prompt` | Prompt box on the left, file tree or output on the right, note underneath | 1 prompt, 1 tree |
| `table` | Comparison grid with column headers and hairline rules | 4 columns, 5 rows |
| `rules` | Numbered rule list, each rule with an example underneath | 3 to 5 rules |
| `statement` | One large claim, one paragraph. Usually dark. The turn of the argument | 1 claim |
| `close` | Three cards: what happened, what to do next, where to reach you | 3 cards |

## Elements

Drop into any layout. All three themes define them.

| Name | What it does | Rule |
|---|---|---|
| `band` | Full width emphasis bar in the accent colour | Never twice on a slide. Roughly 1 slide in 5 |
| `strip` | Thin bordered strip under the band, holding the recovery instruction | Only under a `band`, only on hands on slides |
| `checkpoint` | Label plus a question to the room, on one row | Only where the room has just done something |
| `kicker` | One line of interpretation at the bottom | Instead of a `band`, never as well |

## Collisions worth knowing

Each of these was found by rendering a page and looking at it, not by reading the CSS. `check.py` catches all four.

- `.strip` and `.checkpoint` sit at almost the same height and must never appear on the same slide.
- A table with five or more body rows collides with a `.kicker`.
- Six rows of wrapping cells run into the page number.
- On `daylight` and `sage`, `.chapnum` is a 92pt numeral. Put the number alone in it and the word in the eyebrow. On `paper` it is a small tracked label and takes more.
- A `paper` cover headline past about 118 characters reaches a fourth line and runs into the eyebrow.

---

## How to call it

```
/deck  topic="Agents for regulatory affairs"
       slides=18
       audience=mixed
       theme=daylight
```

Leave `theme` off and it uses `daylight`. Audience changes the writing, not the geometry: `tech` gets `prompt` and `table` slides and real commands, `exec` gets `statement` and `rules` and no code, `non-tech` gets more `three-up` and heavier use of `checkpoint`, `mixed` alternates.
