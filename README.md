# Deck Kit

A Claude Code plugin that builds a workshop deck as **one self contained HTML file**. No build step, no node_modules, no slide app. It opens in any browser, prints to a pixel faithful PDF, and publishes as a link.

Three themes, eleven layouts, and a pre ship check that reads the bytes on disk rather than the model's draft.

## Install

```
/plugin marketplace add RayTrainLabs/deck-kit
/plugin install deck-kit@raytrain
```

Then, in any project:

```
/deck "Prompt engineering for marketers" slides=14 audience=mixed theme=paper duration=90
```

That is the whole install. The plugin has no dependencies beyond **python3**, and a **Chromium based browser** (Chrome, Chromium, Brave, Edge) if you want the PDF export.

## What you get

```
<deck-dir>/
├── index.html      the deck. One file, opens anywhere, works offline
├── slides.html     your slides, the thing you edit
└── deck.pdf        one page per slide, optional
```

| | |
|---|---|
| **Three themes** | `daylight` for hands on workshops, `paper` for executive rooms and conceptual arcs, `sage` for strategy and policy. Every colour in every theme clears WCAG AA at its size, and the ratios are written next to the tokens in the CSS |
| **Proportional geometry** | Everything is expressed in `--in`, one tenth of the stage width. No fixed pixels anywhere, so a deck is dimensionally identical at any viewport and prints at any paper size |
| **Eleven layouts** | cover, agenda, chapter, three-up, four-up, two-up, prompt, table, rules, statement, close. Copy the markup, never invent a class |
| **A real check** | `check.py` reads the files off disk and fails on structure, contrast collisions, over full tables, missing checkpoints and lazy titles. Every collision it knows about was found by rendering a page and looking at it |
| **Three exits** | a GitHub Pages link, a PDF, or a rebuild in Gamma. They are not alternatives, and the skill asks you as a multi select |

## Keys: keep them to hand, keep them out of any repo

Nothing here holds an API key, and nothing here ever should. Not a `.env`, not a commented out example, and above all not a key pasted into a chat, which lands in a transcript, which lands on disk.

You need one key, and only for one thing:

| Key | What needs it | How it gets used |
|---|---|---|
| Gamma API key | `scripts/gamma.sh`, the Gamma exit | The script prompts with `read -rsp`, so it does not echo and does not enter your shell history. Used for one request, then unset. Written nowhere |

Two routes out of the Gamma exit, and neither puts a key in a repo or a message:

1. Run `gamma.sh <deck-dir>` yourself, in your own terminal, and paste at the prompt.
2. Use the Gamma connector in Claude Code, which runs on your existing authorisation and needs no key at all.

You do not need an LLM key. Claude Code already has your authentication, and nothing in this plugin reads a model key by itself.

**Never paste a key into a chat, and never accept one if someone offers.**

## Publishing is public

`publish-pages.sh` creates a **public** repo, because GitHub Pages on the Free plan publishes from public repos only. The script prints the directory contents and asks before it does anything.

Keep facilitator notes, client names, pricing and anything under NDA out of the directory you publish. Copy the slides and the PDF into a clean folder and publish that one.

The repo owner comes from the third argument, then `$DECK_GH_OWNER`, then your own GitHub account. Commits use your own git identity.

## Where things are

| Path | What it is |
|---|---|
| `skills/deck/SKILL.md` | The procedure. Six steps, from block plan to exits |
| `skills/deck/references/THEMES.md` | The eleven themes, the thirteen layouts, and the collisions worth knowing |
| `skills/deck/assets/*.css` | One file per theme. Inlined whole into the deck, never edited |
| `skills/deck/assets/shell.html` | The page the slides get poured into |
| `skills/deck/assets/layouts.html` | Every layout. Copy from here |
| `skills/deck/scripts/build.py` | Assembles `index.html` from shell, theme and `slides.html` |
| `skills/deck/scripts/check.py` | Pre ship check. Runs on the bytes on disk. Exits 1 on any FAIL |
| `skills/deck/scripts/export-pdf.sh` | Headless Chrome print to PDF, verifies page count against slide count |
| `skills/deck/scripts/publish-pages.sh` | Public repo, Pages enabled, confirms first |
| `skills/deck/scripts/gamma.sh` | The Gamma exit. Run it yourself |

## What is deliberately not here

This kit is the grammar: the themes, the layouts, the geometry and the checks. The teaching method that decides what goes on a slide and in what order is Raygency's, and it is not in this repo.

A deck built with this will look right. Making it teach is still your job.

---

Built by [Raygency](https://raygency.com).
