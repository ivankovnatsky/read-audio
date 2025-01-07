import sys
from pathlib import Path
import tempfile
import shutil
import click

from video_summarizer.download import youtube
from video_summarizer.transcribe import whisper
from video_summarizer.summarize import llama
from video_summarizer.config import (
    DEFAULT_WHISPER_MODEL,
    DEFAULT_LLAMA_MODEL,
    DEFAULT_LANGUAGE,
)
from video_summarizer.logger import logger


@click.command()
@click.option(
    "--url",
    help="YouTube video URL to summarize",
)
@click.option(
    "--file",
    type=click.Path(exists=True, path_type=Path),
    help="Local video file to summarize",
)
@click.option(
    "-o", "--output",
    type=click.Path(path_type=Path),
    default=Path("/tmp"),
    help="Output directory for generated files",
)
@click.option(
    "--whisper-model",
    default=DEFAULT_WHISPER_MODEL,
    help=f"Whisper model to use (default: {DEFAULT_WHISPER_MODEL})",
)
@click.option(
    "--llama-model",
    default=DEFAULT_LLAMA_MODEL,
    help=f"LLaMA model to use (default: {DEFAULT_LLAMA_MODEL})",
)
@click.option(
    "--language",
    default=DEFAULT_LANGUAGE,
    help=f"Video language (default: {DEFAULT_LANGUAGE})",
)
def main(url: str | None, file: Path | None, output: Path, whisper_model: str, llama_model: str, language: str) -> int:
    """Generate video summaries using Whisper and LLaMA."""
    if not url and not file:
        raise click.UsageError("Either --url or --file must be provided")
    if url and file:
        raise click.UsageError("Cannot use both --url and --file")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Handle input source
            if url:
                logger.info("Downloading audio...")
                audio_path = youtube.download_audio(url, temp_path)
            else:
                # At this point, file must be a Path since we've validated the inputs
                assert file is not None
                logger.info("Processing local video...")
                audio_path = temp_path / file.name
                shutil.copy2(file, audio_path)
            
            logger.info("Transcribing audio...")
            transcript_path = whisper.transcribe(
                audio_path,
                temp_path,
                language=language,
                model_name=whisper_model,
            )
            
            logger.info("Generating summary...")
            summary = llama.summarize(
                transcript_path,
                model_name=llama_model,
            )
            
            # Write summary to output directory
            output_path = output / f"{audio_path.stem}_summary.txt"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(summary)
                
            logger.info(f"\nSummary saved to: {output_path}")
            
        return 0

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
