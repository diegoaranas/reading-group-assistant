# Reading Group Assistant

This project helps a single **facilitator** run a reading group. Each session is
built around one text. Claude powers the summarize, transcribe, and synthesize
stages (plus relabeling diarized speakers); humans do the rest. This file
documents the conventions so any Claude Code session can operate the workflow
without further explanation.

## The five-stage workflow

1. **Summarize (Claude).** Ingest the text → write a reader-facing summary that
   helps members *before* they read. Command: `/summarize`.
2. **Annotate, then Discuss + record (humans).** Everything the humans do.
   Beforehand, each reader sends remarks/questions in whatever format (email,
   chat, files) and the facilitator drops them into the session's
   `02-annotations/` folder, untouched — input is intentionally messy. At the
   meeting, the group talks and the facilitator records audio into
   `03-discussion/`.
3. **Transcribe (Claude).** Turn the recording into `03-discussion/transcript.md`
   with `/transcribe` — plain, or `--diarize` for anonymous `SPEAKER_NN` labels
   (or drop a `transcript.md` in by hand).
4. **Label speakers (humans + Claude) — only if Stage 3 was diarized.** Diarization
   gives consistent but *anonymous* labels. The **facilitator identifies** who
   each `SPEAKER_NN` is (only a human can — Claude must never guess a speaker's
   name); **Claude then relabels** the transcript by find-and-replace. Any speaker
   the facilitator can't place stays `SPEAKER_NN`. Handled as a mode of
   `/transcribe`, not a separate command.
5. **Synthesize (Claude).** Read the annotations + transcript → write a synthesis
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
├── 03-discussion/       # audio file(s) + transcript.md (Stages 3–4)
└── 04-synthesis.md      # Stage 5 output
```

The `01`–`04` prefixes number the *artifacts*, not the workflow stages, so they
don't track the five-stage count — `04-synthesis.md` is the Stage 5 output.

`sessions/0000-EXAMPLE/` is a reference session for testing — don't treat it as
real.

## Commands (in `.claude/commands/`)

| Command | Stage | Does |
|---|---|---|
| `/new-session "Title"` | — | Scaffold the next numbered session folder + `meta.md`. |
| `/summarize <session-or-source> [--lang L]` | 1 | Read the text, write `01-summary.md` per `templates/summary.md`. |
| `/transcribe <audio-file> [--diarize]` | 3–4 | Run `scripts/transcribe.py`, write `03-discussion/transcript.md`; with `--diarize`, also relabel `SPEAKER_NN` to member names the facilitator identifies. |
| `/synthesize <session> [--lang L]` | 5 | Normalize annotations, read transcript, write `04-synthesis.md` (authoritative summary + the discussion's contribution) per `templates/synthesis.md`. |
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
  Stage 5 doesn't care how the transcript was produced.

## Conventions for Claude

- Never invent reader attributions in annotations — if you can't tell who wrote
  something, label it `Unattributed`.
- The same rule extends to diarized transcripts: never guess which member a
  `SPEAKER_NN` is. Relabel a speaker only from a mapping the facilitator gives you
  (Stage 4); leave any unidentified speaker as `SPEAKER_NN`.
- Before synthesizing, note whether the transcript is name-labeled,
  diarized-but-unidentified (`SPEAKER_NN`), or unlabeled, and attribute Part II
  contributions only as precisely as that allows — named readers when names exist,
  otherwise anonymous speakers or thematic points, never a manufactured name.
- Keep summaries oriented to *pre-reading*: help a reader know what to look for,
  not replace the reading.
- Synthesis is *text-centered*, not a recap of the meeting. Part I is an
  authoritative, discussion-free summary of the text; Part II measures what the
  readers *added* to understanding it (new angles, connections, objections,
  defenses, open questions). Be honest when a category produced nothing — a thin
  discussion should read as thin.
- **Output language.** `/summarize` and `/synthesize` write in the language set by
  a `--lang <language>` flag, else the session `meta.md`'s `Language:` field, else
  English. Translate the prose and headings, but keep source quotes and readers'
  verbatim remarks/questions in their original language. This is independent of
  the language of the source text or the discussion.
