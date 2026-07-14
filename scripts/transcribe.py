#!/usr/bin/env python3
"""Transcribe a discussion audio file to a Markdown transcript.

Two modes:
  - default: faster-whisper, fast, no speaker labels, no token needed.
  - --diarize: whisperX, adds speaker labels (SPEAKER_00, SPEAKER_01, ...).
        Requires `pip install whisperx` and a HuggingFace token with access to
        the pyannote speaker-diarization model (free, but gated - see README).

Both modes run locally and need ffmpeg on PATH.

Usage:
    python scripts/transcribe.py AUDIO [--out transcript.md] [--model small]
                                       [--language en]
    python scripts/transcribe.py AUDIO --diarize [--hf-token TOKEN]
                                       [--min-speakers N] [--max-speakers N]

If --out is omitted, writes `transcript.md` next to the audio file.
The token may be supplied via --hf-token, the HF_TOKEN environment variable, or an
`HF_TOKEN=...` line in a git-ignored `.env` at the project root (loaded automatically).
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def load_dotenv() -> None:
    """Populate os.environ from a project-root .env file (without overriding).

    Keeps secrets like HF_TOKEN out of the shell and out of git: paste the token
    into .env (git-ignored) and it's picked up automatically. Existing environment
    variables win, so an explicitly exported HF_TOKEN still takes precedence.
    No dependency on python-dotenv — the format we need is just KEY=VALUE lines.
    """
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def fmt_ts(seconds: float) -> str:
    """Format seconds as [HH:MM:SS]."""
    total = int(seconds)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"[{h:02d}:{m:02d}:{s:02d}]"


def header(audio_name: str, engine_note: str) -> list[str]:
    return [
        f"# Transcript: {audio_name}",
        "",
        f"> {engine_note}",
        "",
    ]


def transcribe_plain(audio: Path, model_size: str, language: str | None) -> list[str]:
    """faster-whisper path: timestamped lines, no speaker labels."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print(
            "ERROR: faster-whisper is not installed.\n"
            "Install it with:  pip install faster-whisper\n"
            "You also need ffmpeg on your PATH.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    print(f"Loading model '{model_size}' (first run downloads it)...", file=sys.stderr)
    # CPU + int8 keeps this runnable on a laptop without a GPU.
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    print(f"Transcribing {audio.name}...", file=sys.stderr)
    segments, info = model.transcribe(str(audio), language=language, vad_filter=True)

    lines = header(
        audio.name,
        f"Auto-transcribed with faster-whisper (`{model_size}`). "
        f"Detected language: {info.language} "
        f"({info.language_probability:.0%} confidence). No speaker labels.",
    )
    for seg in segments:
        text = seg.text.strip()
        if text:
            lines.append(f"{fmt_ts(seg.start)} {text}")
    return lines


def _load_diarization_pipeline(hf_token: str, device: str):
    """Import the diarization pipeline, tolerating whisperX API moves across versions."""
    try:  # newer whisperX
        from whisperx.diarize import DiarizationPipeline
    except ImportError:
        from whisperx import DiarizationPipeline  # older whisperX
    # whisperX >=3.8 renamed the token kwarg from `use_auth_token` to `token`.
    try:
        return DiarizationPipeline(token=hf_token, device=device)
    except TypeError:
        return DiarizationPipeline(use_auth_token=hf_token, device=device)


def transcribe_diarized(
    audio_path: Path,
    model_size: str,
    language: str | None,
    hf_token: str,
    min_speakers: int | None,
    max_speakers: int | None,
) -> list[str]:
    """whisperX path: transcribe -> align -> diarize -> assign speakers."""
    try:
        import whisperx
    except ImportError:
        print(
            "ERROR: whisperx is not installed (needed for --diarize).\n"
            "Install it with:  pip install whisperx\n"
            "You also need ffmpeg on your PATH and a HuggingFace token (see README).",
            file=sys.stderr,
        )
        raise SystemExit(2)

    device = "cpu"
    print(f"Loading whisperX model '{model_size}'...", file=sys.stderr)
    audio = whisperx.load_audio(str(audio_path))
    model = whisperx.load_model(model_size, device, compute_type="int8", language=language)

    print(f"Transcribing {audio_path.name}...", file=sys.stderr)
    result = model.transcribe(audio, batch_size=16)
    lang = result.get("language", language or "??")

    print("Aligning word timestamps...", file=sys.stderr)
    align_model, metadata = whisperx.load_align_model(language_code=lang, device=device)
    result = whisperx.align(
        result["segments"], align_model, metadata, audio, device, return_char_alignments=False
    )

    print("Diarizing speakers (this is the slow part)...", file=sys.stderr)
    diarize_pipeline = _load_diarization_pipeline(hf_token, device)
    diarize_kwargs = {}
    if min_speakers is not None:
        diarize_kwargs["min_speakers"] = min_speakers
    if max_speakers is not None:
        diarize_kwargs["max_speakers"] = max_speakers
    diarize_segments = diarize_pipeline(audio, **diarize_kwargs)
    result = whisperx.assign_word_speakers(diarize_segments, result)

    lines = header(
        audio_path.name,
        f"Auto-transcribed with whisperX (`{model_size}`) + pyannote diarization. "
        f"Language: {lang}. Speakers are labelled `SPEAKER_NN` in order of "
        f"appearance — find-and-replace with real names if you like.",
    )
    last_speaker = None
    for seg in result["segments"]:
        text = (seg.get("text") or "").strip()
        if not text:
            continue
        speaker = seg.get("speaker", "SPEAKER_??")
        # Only repeat the timestamp+speaker prefix when the speaker changes,
        # to keep the transcript readable.
        if speaker != last_speaker:
            lines.append(f"{fmt_ts(seg['start'])} {speaker}: {text}")
            last_speaker = speaker
        else:
            lines.append(text)
    return lines


def main() -> int:
    # Load .env before argparse so HF_TOKEN's default picks it up.
    load_dotenv()
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("audio", help="Path to the audio file")
    parser.add_argument("--out", help="Output Markdown path (default: next to audio)")
    parser.add_argument(
        "--model",
        default="small",
        help="Whisper model size: tiny, base, small, medium, large-v3 (default: small)",
    )
    parser.add_argument(
        "--language",
        default=None,
        help="Language code (e.g. en). Default: auto-detect.",
    )
    parser.add_argument(
        "--diarize",
        action="store_true",
        help="Add speaker labels via whisperX (needs whisperx + HuggingFace token).",
    )
    parser.add_argument(
        "--hf-token",
        default=os.environ.get("HF_TOKEN"),
        help="HuggingFace token for the pyannote model (or set HF_TOKEN). --diarize only.",
    )
    parser.add_argument(
        "--min-speakers", type=int, default=None, help="Diarization hint: fewest speakers."
    )
    parser.add_argument(
        "--max-speakers", type=int, default=None, help="Diarization hint: most speakers."
    )
    args = parser.parse_args()

    audio = Path(args.audio)
    if not audio.exists():
        print(f"ERROR: audio file not found: {audio}", file=sys.stderr)
        return 1

    if args.diarize and not args.hf_token:
        print(
            "ERROR: --diarize needs a HuggingFace token.\n"
            "Pass --hf-token TOKEN or set the HF_TOKEN environment variable.\n"
            "Get one (free) at https://huggingface.co/settings/tokens and accept the\n"
            "model terms at https://huggingface.co/pyannote/speaker-diarization-3.1",
            file=sys.stderr,
        )
        return 2

    out = Path(args.out) if args.out else audio.with_name("transcript.md")
    out.parent.mkdir(parents=True, exist_ok=True)

    if args.diarize:
        lines = transcribe_diarized(
            audio, args.model, args.language, args.hf_token, args.min_speakers, args.max_speakers
        )
    else:
        lines = transcribe_plain(audio, args.model, args.language)

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote transcript: {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
