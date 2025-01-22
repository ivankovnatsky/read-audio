from pathlib import Path
import platform

import whisper
from read_audio.logger import logger
from read_audio.constants import (
    DEFAULT_WHISPER_MODEL,
    DEFAULT_MLX_WHISPER_MODEL_REPO,
)
from read_audio.utils.audio import split_audio_file


def _is_apple_silicon() -> bool:
    """Check if we're running on Apple Silicon."""
    return platform.system() == "Darwin" and platform.machine() == "arm64"


def _transcribe_with_mlx(
    audio_path: Path, output_dir: Path, language: str | None = None
) -> Path:
    """
    Transcribe audio using mlx-whisper (optimized for Apple Silicon).
    If language is None, it will be auto-detected.
    """
    output_path = output_dir / f"{audio_path.stem}.txt"

    try:
        import mlx_whisper  # type: ignore

        logger.info("Using MLX-Whisper for transcription...")

        result = mlx_whisper.transcribe(
            str(audio_path),
            path_or_hf_repo=DEFAULT_MLX_WHISPER_MODEL_REPO,
            language=language,
        )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result["text"])

        return output_path

    except ImportError as e:
        raise ImportError("mlx-whisper not available") from e
    except Exception as e:
        raise RuntimeError(f"mlx-whisper transcription failed: {e}") from e


def _transcribe_with_whisper(
    audio_path: Path,
    output_dir: Path,
    language: str | None = None,
    model_name: str = DEFAULT_WHISPER_MODEL,
) -> Path:
    """
    Transcribe audio using OpenAI's Whisper.
    If language is None, it will be auto-detected.
    """
    output_path = output_dir / f"{audio_path.stem}.txt"

    try:
        model = whisper.load_model(model_name)

        result = model.transcribe(
            str(audio_path),
            language=language,  # None means auto-detect
            verbose=False,
        )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result["text"])

        return output_path

    except Exception as e:
        raise RuntimeError(f"Whisper transcription failed: {e}") from e


def _transcribe_with_whisper_cloud(
    audio_path: Path,
    output_dir: Path,
    language: str | None = None,
) -> Path:
    """
    Transcribe audio using OpenAI's Whisper cloud API.
    If language is None, it will be auto-detected.
    """
    from read_audio.utils.audio import split_audio_file

    output_path = output_dir / f"{audio_path.stem}.txt"
    all_transcripts = []

    try:
        from openai import OpenAI

        client = OpenAI()

        # Process each chunk
        for chunk_path in split_audio_file(audio_path, output_dir):
            logger.info(f"Transcribing chunk: {chunk_path.name}")

            with open(chunk_path, "rb") as audio_file:
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="text",
                )
                # response is already a string when response_format="text"
                all_transcripts.append(response)

            # Clean up chunk if it's not the original file
            if chunk_path != audio_path:
                chunk_path.unlink()

        # Combine all transcripts
        combined_transcript = " ".join(all_transcripts)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(combined_transcript)

        return output_path

    except Exception as e:
        raise RuntimeError(f"Whisper cloud transcription failed: {e}") from e


def transcribe(
    audio_path: Path,
    output_dir: Path,
    language: str | None = None,
    model_name: str = DEFAULT_WHISPER_MODEL,
    use_cloud: bool = False,
) -> Path:
    """
    Transcribe audio using the most appropriate method.
    On Apple Silicon, tries mlx-whisper first, falls back to OpenAI Whisper.
    On other platforms, uses OpenAI Whisper directly.
    If use_cloud is True, uses OpenAI's Whisper cloud API.

    If language is None (default), the language will be auto-detected.
    """
    if use_cloud:
        logger.info("Using OpenAI Whisper cloud API...")
        return _transcribe_with_whisper_cloud(audio_path, output_dir, language)

    if platform.system() == "Darwin":
        try:
            return _transcribe_with_mlx(audio_path, output_dir, language)
        except (ImportError, RuntimeError) as e:
            logger.warning(f"MLX-Whisper not available: {e}")
            logger.info("Falling back to OpenAI Whisper...")
            return _transcribe_with_whisper(
                audio_path, output_dir, language, model_name
            )
    else:
        logger.info("Using OpenAI Whisper...")

    return _transcribe_with_whisper(audio_path, output_dir, language, model_name)
