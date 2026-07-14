# Reading Group Assistant

A Claude Code project that helps a facilitator run a text-based reading group.
Claude does the two AI-heavy steps (summarizing a text, then synthesizing the
text together with what the discussion added to it); you do the human steps in
between. Each session is a tidy folder of artifacts.

## Workflow

| Stage | Who | Command | Output |
|---|---|---|---|
| 1. Summarize the text | Claude | `/summarize <session>` | `01-summary.md` |
| 2. Annotate, then discuss + record | you + readers | — (drop files in) | `02-annotations/`, `03-discussion/` audio |
| 3. Transcribe the discussion | you / Claude | `/transcribe <session>` | `03-discussion/transcript.md` |
| 4. Label speakers (only if diarized) | you + Claude | `/transcribe <session> --diarize` | relabeled transcript |
| 5. Synthesize text + discussion | Claude | `/synthesize <session>` | `04-synthesis.md` |

## Quickstart

1. **Start a session:** `/new-session "The Title of the Text"`
   → creates `sessions/NNNN-slug/`.
2. **Add the text:** put the PDF/EPUB in that session's `source/`, or save its
   URL in `source/source.url`.
3. **Summarize:** `/summarize sessions/NNNN-slug` → share `01-summary.md` with
   members so they know what to look for.
4. **Members read & annotate.** Collect their remarks however they arrive and
   drop the files into `02-annotations/` (any format — including PDFs marked up
   with highlights/comments; it's all normalized later). See
   [Annotations](#annotations-stage-2).
5. **Discuss & record.** After the meeting, put the audio in `03-discussion/`
   and run `/transcribe sessions/NNNN-slug` (or hand-place a `transcript.md`).
6. **Synthesize:** `/synthesize sessions/NNNN-slug` → `04-synthesis.md`.
7. **(Optional) Export:** `/export sessions/NNNN-slug` → a PDF of the synthesis to
   hand out. See [Export to PDF](#export-to-pdf).

## One-time setup

**Prerequisites:** [Claude Code](https://claude.com/claude-code) (the commands in
this project are run from inside it) and **Python 3.8+** on your PATH.

Install the Python dependencies once with `pip install -r requirements.txt`
(audio transcription + the annotated-PDF extractor). Source-text reading uses
Claude Code's native PDF/web reading; the extras below are per-feature.

```bash
pip install -r requirements.txt   # faster-whisper + pdf-annotations-to-markdown

# Stage 3 (audio transcription) also needs ffmpeg on your PATH:
#   https://ffmpeg.org/download.html

# Optional: speaker labels (Stages 3–4, diarized)
pip install whisperx              # local; uses pyannote for diarization

# Optional: EPUB texts (Stage 1) and PDF export (/export)
# install pandoc:  https://pandoc.org/installing.html
# /export additionally needs a LaTeX engine (xelatex):
#   Windows → MiKTeX https://miktex.org/download ; else TeX Live
```

`requirements.txt` pulls in `pdf-annotations-to-markdown`, which `/synthesize`
uses to extract highlights/comments (with author) from annotated PDFs dropped in
`02-annotations/` — the plain reader can't recover comment text or who wrote it.

If you don't want to set up transcription, skip `/transcribe` and just create
`03-discussion/transcript.md` yourself — Stage 5 only needs the text.

### Transcribe manually

```bash
python scripts/transcribe.py path/to/audio.m4a --out sessions/NNNN-slug/03-discussion/transcript.md
```

Model sizes: `tiny`/`base`/`small`/`medium`/`large-v3` (bigger = slower, more
accurate). Default is `small`.

### Speaker labels (diarization)

By default the transcript has no speaker labels — Stage 5 works fine without
them. To get "who said what", use `--diarize`:

```bash
python scripts/transcribe.py path/to/audio.m4a \
  --out sessions/NNNN-slug/03-discussion/transcript.md \
  --diarize --max-speakers 4
```

One-time setup for diarization:

1. `pip install whisperx`
2. Create a free HuggingFace token: https://huggingface.co/settings/tokens
3. Accept the model terms (one click) at
   https://huggingface.co/pyannote/speaker-diarization-3.1
4. Make the token available, e.g. `export HF_TOKEN=hf_xxx`
   (PowerShell: `$env:HF_TOKEN = "hf_xxx"`), or pass `--hf-token hf_xxx`.

Pass `--max-speakers` (and optionally `--min-speakers`) with your group size to
improve accuracy. Speakers come out anonymous — `SPEAKER_00`, `SPEAKER_01`, … in
order of appearance. Putting real names on them is **Stage 4 (label speakers)**:
you say who each one is (only you can — it's your group's voices) and Claude does
the find-and-replace; run `/transcribe <session> --diarize` and it walks you
through it. Diarization is noticeably slower than plain transcription and the
first run downloads the pyannote model.

## Annotations (Stage 2)

Readers' remarks are intentionally messy — drop them in `02-annotations/` in
whatever form they arrive and let `/synthesize` normalize them. Accepted today:

- **Pasted email / chat / plain text / Markdown** — just save the file.
- **Annotated PDFs** — a reader who marks up the text itself (highlights, margin
  comments) can send back the PDF. `/synthesize` runs `extract-pdf-annotations`
  on it first, pulling each highlight's quoted text **and** comment into Markdown.
  (The plain reader sees only a picture of the page, so comment text and
  authorship would otherwise be lost.)

**Attribution depends on the reader's PDF software.** PDF annotations carry an
author field, and the extractor groups comments by it — but only if the reader's
viewer actually stamped their name. Many viewers leave it blank, in which case
those marks land under **`Unattributed`** (we never guess a name). To keep
attributions intact, ask members to set their display name in their PDF reader
before annotating:

- **Adobe Acrobat / Reader:** Preferences → Commenting → "Author name" (or
  Preferences → Identity).
- **Apple Preview (macOS):** uses your macOS account full name — set it in
  System Settings → Users & Groups.
- **Foxit / PDF-XChange / most others:** look for an "Author" or "Identity"
  setting under commenting/preferences.

If a member can't (or forgot to) set a name, a reliable fallback is to put their
name in the **filename** (e.g. `ada-markup.pdf`) and mention it — or just have
them paste their notes as text instead.

## What `/synthesize` produces (Stage 5)

The synthesis is **text-centered**, not a recap of the meeting. `04-synthesis.md`
has two parts:

1. **The text** — an authoritative, discussion-free summary of what the text
   argues (thesis · the argument · how it proceeds). Written as if the meeting
   never happened.
2. **What the discussion contributed** — what the readers *added* to
   understanding the text, organized by kind: new angles on the thesis,
   connections drawn, objections, stronger defenses, and open questions. It is
   deliberately honest about absence: a category that produced nothing says so,
   and a thin discussion reads as thin.

The point is to capture how the group advanced (or didn't advance) understanding
of the text — drawing on both the written annotations and the recorded
discussion. `sessions/0000-EXAMPLE/04-synthesis.md` is a worked example.

## Working in another language

The two Claude-written outputs — the summary (Stage 1) and the synthesis
(Stage 5) — can be produced in any language. Two ways to choose it:

- **Per run:** add a `--lang` flag, e.g. `/summarize sessions/0001-foo --lang Spanish`
  or `/synthesize sessions/0001-foo --lang French`.
- **Per session:** set `Language:` in the session's `meta.md` (the `/new-session`
  template seeds it to `English`), and both commands honor it without a flag. A
  `--lang` flag on the command still overrides it.

The output language is independent of the source text's language — a German text
can get an English summary, or vice versa. Quoted passages from the source and
readers' verbatim questions are left in their original language; only the written
prose and headings are translated. (This is about the two AI-written outputs;
transcription follows the audio's own language.)

## Export to PDF

Any Markdown artifact — most often the synthesis, sometimes the summary — can be
turned into a shareable PDF:

```
/export sessions/NNNN-slug          # → 04-synthesis.pdf (falls back to the summary)
/export sessions/NNNN-slug/01-summary.md
```

Under the hood this is pandoc with the `xelatex` engine (chosen so curly quotes,
em-dashes, and accented author names render correctly). The PDF is written next
to its source `.md`. Ask for extras like a table of contents (`--toc`), numbered
sections, or a specific font and the command will add them.

**Setup:** install [pandoc](https://pandoc.org/installing.html) **and** a LaTeX
engine — [MiKTeX](https://miktex.org/download) on Windows, TeX Live elsewhere.
Both must be on your PATH. (Generated PDFs live under `sessions/*`, which is
gitignored, so they stay local like the source texts.)

## Layout

See `CLAUDE.md` for the full folder/command conventions. `sessions/0000-EXAMPLE/`
is a scratch session for testing — it includes an annotated-PDF reader
(`dara-markup.pdf`) so you can see the Stage 2 → Stage 5 PDF path end to end.
