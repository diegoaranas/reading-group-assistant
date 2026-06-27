---
description: Scaffold a new numbered reading-group session folder
argument-hint: "Text Title"
---

Create a new session folder for the reading group.

Title for this session: **$ARGUMENTS**

Steps:

1. Look in `sessions/` and find the highest existing `NNNN-*` folder number.
   The new session number is that + 1, zero-padded to 4 digits. (If only
   `0000-EXAMPLE` exists, the first real session is `0001`.)
2. Build a slug from the title: lowercase, spaces → hyphens, strip punctuation.
3. Create `sessions/NNNN-slug/` with these subfolders:
   - `source/`
   - `02-annotations/`
   - `03-discussion/`
4. Write `sessions/NNNN-slug/meta.md` from this template, filling in the title
   and today's date, leaving the rest as placeholders:

   ```markdown
   # <Title>

   - **Session:** NNNN
   - **Date:** <today's date>
   - **Source:** <path under source/ or URL — fill in>
   - **Members:** <comma-separated, fill in>

   ## Notes
   <anything worth remembering about this session>
   ```

5. Tell me the new folder path and remind me to (a) put the text in `source/`
   (or a URL in `source/source.url`) and (b) run `/summarize <folder>`.

Do not create the numbered output files yet — the stage commands create those.
