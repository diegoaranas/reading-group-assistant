---
description: Export a session's Markdown output (summary or synthesis) to PDF
argument-hint: <session-folder | path-to-.md>
---

Turn one of a session's Markdown artifacts into a shareable PDF with pandoc.

Target: **$ARGUMENTS**

## Resolve what to export

- If given a **path to a `.md` file**, export that file.
- If given a **session folder** (e.g. `sessions/0001-foo`), default to
  `04-synthesis.md` (the usual thing to hand out). If it doesn't exist yet, fall
  back to `01-summary.md`. If both exist and it's ambiguous which I want, ask.
- The output PDF goes next to the source file, same name with a `.pdf`
  extension (e.g. `04-synthesis.md` → `04-synthesis.pdf`).

## Convert

Run pandoc with the LaTeX engine — `xelatex` handles Unicode (curly quotes,
em-dashes, accented author names) that a plain engine chokes on:

```
pandoc "<file>.md" -o "<file>.pdf" --pdf-engine=xelatex -V geometry:margin=1in
```

Optional niceties — add them **only if I ask**:

- Table of contents: `--toc`
- Numbered sections: `--number-sections`
- A different font: `-V mainfont="Georgia"` (any font installed on this machine)

## If pandoc or the engine is missing

- `pandoc` not found → tell me to install it (https://pandoc.org/installing.html)
  and stop; don't try to hand-roll a PDF another way.
- pandoc runs but errors with "pdflatex/xelatex not found" → a LaTeX engine is
  needed. On Windows that's MiKTeX (https://miktex.org/download); show me the
  error and the hint rather than working around it.

## After

Confirm the PDF path and its size. Note that generated PDFs land under
`sessions/*`, which is gitignored (only `0000-EXAMPLE` is tracked) — so exported
PDFs stay local, same as the source texts and transcripts.
