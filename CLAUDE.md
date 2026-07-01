# Reading Group Assistant

This project helps a single **facilitator** run a reading group. Each session is
built around one text. Claude powers two stages; humans do the rest. This file
documents the conventions so any Claude Code session can operate the workflow
without further explanation.

## The four-stage workflow

1. **Summarize (Claude).** Ingest the text → write a reader-facing summary that
   helps members *before* they read. Command: `/summarize`.
2. **Annotate (humans).** Each reader sends remarks/questions in whatever format
   (email, chat, files). The facilitator drops them into the session's
   `02-annotations/` folder, untouched. Input is intentionally messy.
3. **Discuss + record (humans).** The group talks; the facilitator records audio.
   Transcribe it with `/transcribe` (or drop a `transcript.md` in by hand).
4. **Synthesize (Claude).** Read the annotations + transcript → write a synthesis
   that (Part I) summarizes the text on its own terms and (Part II) records what
   the discussion *contributed* to understanding it. Command: `/synthesize`.

## Folder conventions

Every session lives in `sessions/NNNN-slug/` (4-digit zero-padded, increasing):

```
sessions/NNNN-slug/
├── meta.md              # title, source, date, members
├── source/              # the PDF/EPUB, or a source.url file holding a URL
├── 01-summary.md        # Stage 1 output
├── 02-annotations/      # raw reader files (any format) + normalized.md
├── 03-discussion/       # audio file(s) + transcript.md
└── 04-synthesis.md      # Stage 4 output
```

`sessions/0000-EXAMPLE/` is a reference session for testing — don't treat it as
real.

## Commands (in `.claude/commands/`)

| Command | Stage | Does |
|---|---|---|
| `/new-session "Title"` | — | Scaffold the next numbered session folder + `meta.md`. |
| `/summarize <session-or-source>` | 1 | Read the text, write `01-summary.md` per `templates/summary.md`. |
| `/transcribe <audio-file>` | 3 | Run `scripts/transcribe.py`, write `03-discussion/transcript.md`. |
| `/synthesize <session>` | 4 | Normalize annotations, read transcript, write `04-synthesis.md` (authoritative summary + the discussion's contribution) per `templates/synthesis.md`. |
| `/export <session-or-.md>` | — | Convert a Markdown output (summary/synthesis) to a shareable PDF via `pandoc --pdf-engine=xelatex`. |

## Ingestion rules (Stage 1)

- **PDF / Markdown / plain text** → use the `Read` tool directly.
- **Web URL** (in `source/source.url`) → use `WebFetch`.
- **EPUB** → convert first: `pandoc source/book.epub -o source/source.md`, then
  `Read` the Markdown. (Requires pandoc installed.)

## Dependencies

- **faster-whisper** (pip) + **ffmpeg** on PATH — default `/transcribe`. Local, no API key.
- **whisperx** (pip) + a **HuggingFace token** (`HF_TOKEN`) — only for diarized
  `/transcribe --diarize`, which adds `SPEAKER_NN` labels. Slower; first run
  downloads the pyannote model.
- **pandoc** (optional) — EPUB → Markdown (Stage 1) and `/export` (Markdown →
  PDF). The latter also needs a **LaTeX engine** (`xelatex`, from MiKTeX on
  Windows / TeX Live elsewhere) on PATH.
- **pdf-annotations-to-markdown** (pip, in `requirements.txt`) — provides the
  `extract-pdf-annotations` command. `/synthesize` uses it to pull
  highlights/comments **with their author** out of annotated PDFs in
  `02-annotations/`; the plain `Read` tool can't (it renders the PDF as images and
  drops comment text + authorship). Pulls in pymupdf.
- If transcription isn't set up, you can always hand-place `03-discussion/transcript.md`;
  Stage 4 doesn't care how the transcript was produced.

## Conventions for Claude

- Never invent reader attributions in annotations — if you can't tell who wrote
  something, label it `Unattributed`.
- Keep summaries oriented to *pre-reading*: help a reader know what to look for,
  not replace the reading.
- Synthesis is *text-centered*, not a recap of the meeting. Part I is an
  authoritative, discussion-free summary of the text; Part II measures what the
  readers *added* to understanding it (new angles, connections, objections,
  defenses, open questions). Be honest when a category produced nothing — a thin
  discussion should read as thin.
