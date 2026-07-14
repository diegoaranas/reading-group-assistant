---
description: Stage 3 — transcribe a discussion audio recording
argument-hint: <session-folder | path-to-audio>
---

Stage 3 of the reading-group workflow: turn the recorded discussion audio into a
text transcript that Stage 4 can read.

Target: **$ARGUMENTS**

## Resolve the audio

- If given a session folder, look in `03-discussion/` for an audio file
  (`.mp3`, `.m4a`, `.wav`, `.ogg`, etc.). If there are several, list them and
  ask which one.
- If given a direct path to an audio file, use it and confirm which session
  folder to write the transcript into.

## Transcribe

Run the local transcription script. Default (fast, no speaker labels):

```
python scripts/transcribe.py "<audio-path>" --out "<session>/03-discussion/transcript.md"
```

**With speaker labels** (whisperX diarization) — use this when I ask for "who
said what". Needs `whisperx` installed and a HuggingFace token:

```
python scripts/transcribe.py "<audio-path>" --out "<session>/03-discussion/transcript.md" \
  --diarize --max-speakers <number-of-members-if-known>
```

The token is read from an `HF_TOKEN=...` line in the git-ignored `.env` at the
project root (loaded automatically), or the `HF_TOKEN` environment variable, or
`--hf-token`. If I tell you how many people were in the discussion, pass it as
`--max-speakers` (and optionally `--min-speakers`) to improve accuracy.

- Both modes run locally and require `ffmpeg`.
- If the script errors because faster-whisper, whisperx, ffmpeg, or the token
  isn't set up, show me the error and the install hint from the README — don't
  try to work around it.

## After

Confirm the transcript path and its length.

- **Default mode:** the transcript has **no speaker labels**; Stage 4 works
  thematically regardless. If I want labels, offer to re-run with `--diarize`.
- **Diarized mode:** speakers are labelled `SPEAKER_00`, `SPEAKER_01`, … in order
  of appearance. Offer to map those to real member names (from `meta.md`) with a
  find-and-replace if I can identify who's who.

Reminder: I can also skip this command entirely and hand-place
`03-discussion/transcript.md` myself — Stage 4 only needs the text.
