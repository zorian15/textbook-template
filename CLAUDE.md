# CLAUDE.md — textbook template (design note)

**Status: BUILT (v1.2.0), extracted at N=2 from `../llm-textbook` and
`../foundation-models-bio`; exercised by `../calculus-intuitively` and
`../shape-of-statistical-theory`.** The working [copier](https://copier.app/)
template lives in `template/` with its questions in `copier.yml`; `README.md` is
the user-facing guide. Engine changes are tagged (semver) and pulled into books
with `copier update`. Releases: v1.1.0 bumped the `deploy.yml` GitHub Actions to
their Node-24 majors. v1.2.0 promoted the **interactive-figure engine**
(`assets/widgets.js` runtime + `build.py` injection + `.widget` CSS + one worked
`example-slider` widget) after it proved out, hand-added, in the calculus and
statistics books — the N=2-for-widgets signal. Existing books already carry a
hand-added copy of the engine, so they do not need this update; new books get it
built in. This file is kept as the *design rationale* — why copier, the
engine/content seam, the repo-topology decision, and the conventions promoted
into the template. Read `README.md` to use the template; read on here for why it
is shaped the way it is.

What actually shipped that this note only sketched: `style.css` needed to become
the *superset* of both books (the amber probing callout was unified into a single
`probe` type, and the glossary CSS is always present); the glossary is an
*optional* feature gated on a `use_glossary` copier flag; and an **AI-generated
disclosure** was added net-new to both the README and the preface (neither source
book had one). Only `.jinja`-suffixed files are rendered (`_templates_suffix`),
which keeps the brace-heavy `build.py`/`style.css` safe from Jinja.

## The idea

`../llm-textbook` (*Foundations of Large Language Models*) is a static,
bookdown-style textbook generated from Markdown by a small Python build. Its
machinery is almost entirely topic-agnostic: the same engine and the same
authoring conventions could produce a textbook on any topic the author wants to
learn by synthesizing with an LLM. The goal here is to extract that engine +
conventions into a reusable template so each new topic starts as a fresh,
independently-deployed book that still obeys all the rules we worked out.

## Why copier (not cookiecutter)

The engine is still *live* — it keeps improving (e.g. quiz balancing/shuffle was
a recent change). When a fix lands in the engine, every book should be able to
pull it. Copier records the template version each book was generated from and
re-applies later template changes as a three-way merge (`copier update`).
Cookiecutter is copy-once-and-forget, which loses this.

## The engine / content seam (verified against llm-textbook on 2026-07-14)

Reusable **engine** (travels into the template, mostly verbatim):

- `build.py` — only the identity constants are book-specific: `BOOK_TITLE`,
  `BOOK_SUBTITLE`, the `SITE_NAME`/`SITE_URL`/`CANONICAL_BASE`/`DRAFT` config
  block, and `apple-mobile-web-app-title`. Everything else is machinery.
- `assets/style.css` — pure look, verbatim.
- `figures/make_figures.py` **infrastructure** only: palette constants, save
  helpers, `fig_cover`/`fig_icon`, and the `FIGURES` tuple mechanism. The
  topic-specific `fig_*()` functions do NOT travel (ship one worked example).
- The `Chapter` / `Part` / `Question` / `Reference` dataclasses — the *schema*.
- `.github/workflows/deploy.yml`, `.gitignore`.
- **CLAUDE.md's authoring conventions** — voice/style, callouts, quizzes,
  citations, **sourcing & currency**, figures rules, code prefs. This is the
  highest-value reusable asset; it is entirely topic-agnostic.

Topic-specific **content** (reset to empty-with-one-example in the template):

- The `BOOK` / `APPENDICES` data in `toc.py`.
- `content/*.md`.
- `_ENTRIES` in `references.py`, `_QUIZZES` in `quizzes.py`.
- The specific `fig_*()` functions in `make_figures.py`.
- The identity constants above.
- CLAUDE.md's top matter (what-this-book-is, audience, content status).

The happy surprise: only a handful of files need Jinja treatment. `build.py`,
`style.css`, and the figure infra travel almost verbatim — just the identity
constants and the four data modules vary.

## Conventions to promote into the template

These emerged while planning book #2 (`foundation-models-bio`) and are
topic-agnostic, so they belong in the template's shared CLAUDE.md, not any one
book:

- **Research SOTA before drafting; verify references.** Fan out web research on a
  chapter's key claims before writing (fields move; memory goes stale), prefer
  primary sources, and verify every citation against the actual paper before it
  lands in `references.py`. Already added to `../llm-textbook/CLAUDE.md` as the
  "Sourcing and currency" convention — lift that text into the template verbatim.
- **Glossary on first use** (candidate, not yet in book 1). Define every jargon
  term/abbreviation inline on first use and collect it into an auto-built
  glossary. Book #2 needs this; if it proves general, promote it — and note it
  requires a build mechanism (see the `build-glossary` skill).
- **Configurable "Interview"/"Collaborator" box framing.** Book 1 frames the
  probing callout as an interview question; book 2 as a collaborator's question.
  The admonition *type* is engine; its *title/framing* should be a per-book
  variable rather than hard-coded.
- **Draft batches of chapters by fanning out subagents.** One research-and-draft
  agent per chapter (they parallelize — each writes its own content file); each
  researches current SOTA first and returns its contributions to the shared
  single-source modules as data; the orchestrator integrates and builds. Added to
  `../foundation-models-bio/CLAUDE.md` as "Drafting a batch of chapters with
  subagents" — lift that section into the template.
- **Verify a drafted batch before shipping.** Agent-drafted chapters are done
  when verified, not when they build. After integrating a batch and before
  commit/push, fan out (1) a reference-verification + dedup pass — one agent per
  reference, each checked against the real paper, same-paper duplicates merged and
  citations updated — (2) a domain-correctness skeptic review, one agent per
  chapter, applying clear factual fixes and surfacing judgment calls — and (3) a
  **visual figure-QA pass**: render each figure to an image and look at it, one
  agent per figure in an isolated worktree, fixing overlapping/overflowing text
  that syntax and runtime checks cannot catch. Added to
  `../foundation-models-bio/CLAUDE.md` as "Verifying a drafted batch before it
  ships" — lift it into the template.
- **Ship each drafted section as a PR.** After a Part is drafted and both
  verification passes are clean, create a feature branch, commit, push to the
  book's own GitHub repo, and open a pull request so the author reviews and merges
  sections in order. Never push unverified work to `main` (merging auto-deploys).
  Added to `../foundation-models-bio/CLAUDE.md` as "Shipping a drafted section as
  a PR" — lift it into the template.

## Sketched template layout

```
textbook-template/
  copier.yml                       # questions: book_title, subtitle, slug,
                                   #   author, repo_url, canonical_base
  template/
    build.py.jinja                 # only identity constants are {{ vars }}
    toc.py.jinja                   # ONE example Part/Chapter, not real content
    references.py.jinja            # empty _ENTRIES + one worked example
    quizzes.py.jinja               # empty _QUIZZES + one worked example
    content/introduction.md        # starter chapter showing every callout type
    figures/make_figures.py.jinja  # infra + fig_cover/fig_icon + one example fig_*
    assets/style.css               # verbatim
    CLAUDE.md.jinja                # generic conventions verbatim; topic header = vars
    .github/workflows/deploy.yml
    _exclude: [docs/, .mypy_cache/]
```

## Version control model

- This template: its own git repo, tagged with semver (`v1.0.0`). Engine
  changes bump the tag.
- Each book: an *independent* repo, its own GitHub Pages deploy, carrying a
  `.copier-answers.yml` that records its inputs + the template version it is on.
- Engine improvement → tag template → `copier update` in each book → review the
  merge → commit.

## When to build this (important discipline)

**Extract at N=2, not N=1.** Building the template speculatively against a single
book bakes in LLM-shaped assumptions we can't yet see. Let the *second* topic
drive the extraction: the real variation between book #1 and book #2 is the
signal for what is genuinely a parameter vs. what was incidentally LLM-specific
(e.g. is "ace a 2026 engineering interview" a per-book variable, or does every
book get its own framing?). Scaffolding `copier.yml` early is fine; finalizing
the template before a second topic exists is not.

## Open decision (revisit when building)

Repo topology, leaning **copier + one repo per book**:

- **Copier + one repo per book** (leaning this) — independent repos and Pages
  sites; propagation via `copier update`. Costs a manual update step per book.
- **Monorepo** `books/<topic>/` sharing one engine — zero propagation friction
  (fix the engine once, all books rebuild), but books share git history and
  publishing each to its own site needs a matrix deploy to subpaths.

Decide based on whether independent per-book sites matter more than effortless
engine sync.

## Next steps when ready to start book #2

1. Pick the second topic; use it to pressure-test the seam above.
2. `pip install copier`, write `copier.yml` with the questions listed.
3. Copy the engine files from `../llm-textbook` into `template/`, Jinja-ify only
   the identity constants, and gut the four data modules down to one worked
   example each.
4. Split `../llm-textbook/CLAUDE.md`: conventions → template verbatim; topic
   header → copier variables.
5. `copier copy` into a fresh repo for book #2; iterate until it builds clean.
6. Backport: run `copier copy`/`update` semantics against llm-textbook itself as
   a sanity check that the template reproduces the original.
