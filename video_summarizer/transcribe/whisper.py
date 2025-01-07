from pathlib import Path
import platform

import whisper


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
        import mlx_whisper

        print("Using MLX-Whisper for transcription...")

        result = mlx_whisper.transcribe(
            str(audio_path),
            path_or_hf_repo="mlx-community/whisper-turbo",
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
    model_name: str = "base",
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


def transcribe(
    audio_path: Path,
    output_dir: Path,
    language: str | None = None,  # Changed default to None for auto-detection
    model_name: str = "base",
) -> Path:
    """
    Transcribe audio using the most appropriate method.
    On Apple Silicon, tries mlx-whisper first, falls back to OpenAI Whisper.
    On other platforms, uses OpenAI Whisper directly.

    If language is None (default), the language will be auto-detected.
    """
    if _is_apple_silicon():
        try:
            return _transcribe_with_mlx(audio_path, output_dir, language)
        except (ImportError, RuntimeError) as e:
            print(f"MLX-Whisper not available: {e}")
            print("Falling back to OpenAI Whisper...")
            return _transcribe_with_whisper(
                audio_path, output_dir, language, model_name
            )
    else:
        print("Using OpenAI Whisper...")

    return _transcribe_with_whisper(audio_path, output_dir, language, model_name)
