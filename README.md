# textbook-template

A [copier](https://copier.app/) template for **AI-generated, self-hosted
textbooks** — static, bookdown-style books generated from Markdown by a small,
topic-agnostic Python build. Each book you generate is its own repository with
its own GitHub Pages site, and can pull later engine improvements with
`copier update`.

The engine and authoring conventions were extracted from two real books
(*Foundations of Large Language Models* and *Foundation Models for Biology*) once
a second topic existed to show what is genuinely a parameter versus what was
incidental — see `CLAUDE.md` for that design note.

## What you get

- A static-site generator (`build.py`) with per-chapter navigation, section and
  figure numbering, `[@key]` citations resolved from a single source of truth,
  interactive end-of-chapter quizzes, an optional auto-built glossary, an
  interactive-figure runtime for slider-driven widgets (`assets/widgets.js`,
  dependency-free and offline), and a responsive, offline-first design (no web
  fonts, no CDN except MathJax).
- A GitHub Actions workflow that rebuilds and deploys to GitHub Pages on push.
- A comprehensive authoring guide (`CLAUDE.md`) covering voice, callouts,
  citations, sourcing/verification, figures, and a subagent drafting+verification
  workflow — the highest-value reusable asset here.
- **An AI-generated disclosure baked into every book**, in both the README and
  the preface, since these books are written by an LLM to learn a field.

## Generating a book

```bash
pip install copier
copier copy gh:zorian15/textbook-template my-new-book
# answer the prompts (title, subtitle, audience, ...)
cd my-new-book
pip install markdown pymdown-extensions pygments matplotlib
python figures/make_figures.py && python build.py
python -m http.server -d docs          # preview at http://localhost:8000
```

Then read the generated `CLAUDE.md`, replace the one example Part/chapter in
`toc.py` with your book's real structure, and follow `DEPLOY.md` to publish.

## Pulling engine improvements

When this template improves, update any book generated from it:

```bash
cd my-existing-book
copier update            # three-way merge; review the diff, then commit
```

Each book records the template version it is on in `.copier-answers.yml`.

## Repository layout

```
copier.yml               The questions asked when generating a book.
template/                The book skeleton. Only *.jinja files are rendered;
                         everything else is copied verbatim.
  build.py.jinja         Generator (only identity constants are variables).
  toc.py.jinja           Structure — one example Part/Chapter to replace.
  references.py          Citation schema + one worked entry.
  quizzes.py             Quiz schema + one worked quiz.
  figures/make_figures.py.jinja   Figure infrastructure + cover/icons + example.
  content/               Preface (with the AI disclosure) + one worked chapter.
  assets/style.css       The full visual design, verbatim.
  CLAUDE.md.jinja        Authoring conventions (topic-agnostic) + book header.
CLAUDE.md                Design note: why copier, the engine/content seam.
```

## Versioning

This template is tagged with semver. Engine changes bump the tag; books pull them
via `copier update`.
