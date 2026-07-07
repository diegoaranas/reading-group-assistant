---
description: Stage 1 — produce a reader-facing summary of the session's text
argument-hint: <session-folder | path-to-text | URL> [--lang <language>]
---

Stage 1 of the reading-group workflow: produce a summary that helps members
**before** they read the text.

Target: **$ARGUMENTS**

## Resolve the source

- If the argument is a session folder (e.g. `sessions/0001-foo`), look inside
  `source/` for the text. A `source.url` file means the text is a web page.
- If it's a direct path or URL, use that and note which session folder to write
  the output into (ask me if ambiguous).

## Resolve the output language

Decide what language to write `01-summary.md` in, in this order:

1. A `--lang <language>` (or `--language <language>`) flag in the arguments wins.
2. Otherwise, the `Language:` field in the session's `meta.md`, if present.
3. Otherwise, default to **English**.

This is the language of the *summary you write* — it's independent of the
language the source text happens to be in (a German text can get an English
summary, or vice versa).

## Ingest the text

- **PDF / Markdown / plain text** → use the `Read` tool.
- **Web URL** → use `WebFetch` to retrieve the readable content.
- **EPUB** → run `pandoc <file>.epub -o source/source.md`, then `Read` the
  Markdown. If pandoc is missing, tell me and stop.

## Write the summary

Write `01-summary.md` in the session folder, following `templates/summary.md`.
Write it in the resolved output language — all prose and the section headings —
but keep quoted passages from the source in their **original** language (add a
translation in parentheses only if it helps). Keep it oriented to pre-reading —
help a reader know what to look for; do not replace the reading. Fill every
section of the template:

- TL;DR (2–4 sentences)
- Central claims / arguments
- Section-by-section outline
- Glossary of key terms
- A few notable quotes **with locations** (page/section)
- 3–5 orienting questions to read with

After writing, give me a one-line confirmation with the file path, word count,
and the output language used.
