---
description: Stage 4 — normalize annotations and synthesize the text + the discussion's contribution
argument-hint: <session-folder>
---

Stage 4 of the reading-group workflow. The synthesis is **text-centered**: it
gives an authoritative account of the text on its own terms, then records what
the discussion *contributed* to understanding that text. The goal is to capture
how the readers advanced (or failed to advance) understanding — **not** to
recount the meeting blow-by-blow.

Session: **$ARGUMENTS**

## Step 1 — Normalize the annotations

### 1a. Extract annotated PDFs first

If `<session>/02-annotations/` contains any `*.pdf` files, a reader has likely
sent the text back with highlights/comments. The plain `Read` tool renders a PDF
as images and **silently loses comment text and per-annotation authorship** — the
exact content you need. So convert each annotated PDF to Markdown first:

```bash
extract-pdf-annotations "<session>/02-annotations/<file>.pdf" \
  --out "<session>/02-annotations/<file>.annotations.md" --group-by author
```

(Installed via `requirements.txt`. If the command is missing, tell me to
`pip install -r requirements.txt` and stop.) Notes:

- Output is grouped by annotation author; un-authored marks come out under
  `Unattributed` — keep that label, never guess a name.
- If a PDF yields `No annotations found.`, it's a clean copy of the text, not an
  annotation — skip it (don't treat the whole text as a reader's remarks).
- Read the generated `*.annotations.md` files (not the source PDFs) in step 1b.

### 1b. Read and consolidate

Read **every** remaining file in `<session>/02-annotations/` (skip `normalized.md`
itself, and the source PDFs you just extracted — use their `*.annotations.md`).
Input is messy and mixed-format (pasted emails, chat snippets, text files,
extracted PDF annotations) — be tolerant.

Produce `<session>/02-annotations/normalized.md`:

- Attribute each remark to a reader when the source makes it clear. If you can't
  tell, label it `Unattributed` — never guess a name.
- Group remarks by reader, and within that, tag each with the part of the text it
  refers to (page/section) when discernible.
- Preserve questions verbatim where possible; lightly clean obvious typos.

## Step 2 — Read the rest of the session

- `<session>/03-discussion/transcript.md` (the recorded discussion). If it's
  missing, tell me and stop — Stage 4 needs it (or a hand-placed transcript).
- `<session>/01-summary.md` for context, and the source text in `<session>/source/`
  if you need to ground Part I (re-ingest per the Stage 1 ingestion rules in
  `CLAUDE.md` if necessary).

## Step 3 — Write the synthesis

Write `<session>/04-synthesis.md` following `templates/synthesis.md`. It has two
parts:

**Part I — The text.** A fresh, authoritative summary of what the text argues, on
its own terms. Write it as if the discussion never happened: no annotations, no
opinions from the room. This is *not* a copy of `01-summary.md` (that one is a
pre-reading "what to look for" aid) — write a definitive post-reading account:
thesis, the argument, and how the text proceeds.

**Part II — What the discussion contributed.** Drawing on the normalized
annotations **and** the transcript, record what the readers *added* to
understanding the text, organized by **type of contribution**:

- New angles on the thesis (readings/reframings that changed understanding)
- Connections drawn (to other texts, thinkers, events, ideas)
- Objections and challenges (gaps, counterexamples, weaknesses surfaced)
- Stronger defenses proposed (ways the readers shored up or extended the argument)
- Questions left open
- Overall contribution (a candid verdict on how much was added)

Rules for Part II:

- Attribute contributions to readers by name where the source supports it;
  `Unattributed` otherwise.
- **Be honest about absence.** If a category produced nothing, say so plainly
  ("Nothing substantive here") rather than padding. A thin discussion should read
  as thin — that candor is the point of this stage.
- Measure contributions against the text (Part I), not against the meeting. The
  test is "did this change/deepen how we understand the text?", not "was it said?"

End with a one-line confirmation of the output path.
