import sys
import warnings
from pathlib import Path
import tempfile
import shutil
from typing import Optional
import click
from read_audio.helpers.cli import percentage_type

# Suppress pydub's invalid escape sequence warnings
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pydub.utils")

from read_audio.download import youtube
from read_audio.transcribe import whisper
from read_audio.constants import (
    DEFAULT_WHISPER_MODEL,
    DEFAULT_LLAMA_MODEL,
    DEFAULT_LANGUAGE,
    MODEL_MAPPING,
    DEFAULT_CONDENSE_PROMPT,
    DEFAULT_CONDENSE_PERCENTAGE,
)
from read_audio.logger import logger
from .providers import get_provider


@click.command()
@click.option(
    "--mode",
    type=click.Choice(["summary", "condense"]),
    default="summary",
    help="Processing mode: summary (200-250 words) or condense (5% length)",
)
@click.option(
    "--url",
    help="URL of the video to summarize",
    type=str,
    default=None,
)
@click.option(
    "--file",
    type=click.Path(exists=True, path_type=Path),
    help="Path to local video file",
    default=None,
)
@click.option(
    "--transcript",
    type=click.Path(exists=True, path_type=Path),
    help="Path to existing transcript file",
    default=None,
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default=Path("/tmp"),
    help="Output directory for processed files",
)
@click.option(
    "--whisper-model",
    default=DEFAULT_WHISPER_MODEL,
    help=f"Whisper model to use (default: {DEFAULT_WHISPER_MODEL})",
)
@click.option(
    "--provider",
    type=click.Choice(["openai", "anthropic", "ollama"]),
    default="ollama",
    help="AI provider to use for summarization",
)
# FIXME: Handle provider/model mapping correctly.
@click.option(
    "--model",
    help="Model to use for summarization",
    default=DEFAULT_LLAMA_MODEL,
)
@click.option(
    "--language",
    default=DEFAULT_LANGUAGE,
    help="Language of the video",
)
@click.option(
    "--show-transcript",
    is_flag=True,
    help="Show transcript in output",
)
@click.option(
    "--show-processed-text",
    is_flag=True,
    help="Show processed text (summary or condensed) in output",
)
@click.option(
    "--use-cloud-whisper",
    is_flag=True,
    help="Use OpenAI's Whisper cloud API for transcription",
)
@click.option(
    "--condense-percentage",
    type=percentage_type,
    default=DEFAULT_CONDENSE_PERCENTAGE,
    help="Percentage of original length for condensed output (1-100%)",
)
def main(
    mode: str,
    url: Optional[str],
    file: Optional[Path],
    transcript: Optional[Path],
    output: Path,
    whisper_model: str,
    provider: str,
    model: str,
    language: str,
    show_transcript: bool,
    show_processed_text: bool,
    use_cloud_whisper: bool,
    condense_percentage: int,
) -> None:
    """Generate summaries or condensed versions of video content"""

    # Validate input parameters
    if sum(bool(x) for x in [url, file, transcript]) != 1:
        raise click.UsageError(
            "Exactly one of --url, --file, or --transcript must be provided"
        )

    # Get the correct model for the provider
    if model == DEFAULT_LLAMA_MODEL:  # If using the default model
        model = MODEL_MAPPING[provider]  # Use the provider's default model
    
    # Create temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        audio_path: Optional[Path] = None

        # Handle input sources
        if transcript:
            transcript_path = transcript
        else:
            if url:
                logger.info("Downloading audio...")
                audio_path = youtube.download_audio(
                    url, temp_path, use_cloud=use_cloud_whisper
                )
            elif file:
                logger.info("Processing local video...")
                audio_path = temp_path / file.name
                shutil.copy2(str(file), str(audio_path))

            if not audio_path:
                raise click.UsageError("Failed to get audio file")

            logger.info("Transcribing audio...")
            transcript_path = whisper.transcribe(
                audio_path=audio_path,
                output_dir=temp_path,
                language=language,
                model_name=whisper_model,
                use_cloud=use_cloud_whisper,
            )

            # Save transcript to output directory
            transcript_output_path = output / f"{audio_path.stem}_transcript.txt"
            shutil.copy2(transcript_path, transcript_output_path)
            logger.info(f"Transcript saved to: {transcript_output_path}")

        # Generate output
        ai_provider = get_provider(provider, model)
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript_text = f.read()

            if show_transcript:
                logger.info("\nTranscript:")
                logger.info(transcript_text)

        # Update the condense prompt with the specified percentage if in condense mode
        if mode == "condense":
            input_length = len(transcript_text)
            target_length = int(input_length * condense_percentage / 100)
            formatted_prompt = DEFAULT_CONDENSE_PROMPT.format(
                percentage=condense_percentage,
                input_length=input_length,
                target_length=target_length
            )
            logger.info(f"Using condense prompt: {formatted_prompt}")
            result = ai_provider.process_text(transcript_text, mode, prompt=formatted_prompt)
        else:
            result = ai_provider.process_text(transcript_text, mode)

        # Prepare output
        suffix = "summary" if mode == "summary" else "condensed"
        output_file = output / f"{transcript_path.stem}_{suffix}.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result)

            if show_processed_text:
                logger.info(f"\n{suffix.capitalize()}:")
                logger.info(result)

        logger.info(f"{suffix.capitalize()} written to {output_file}")


if __name__ == "__main__":
    sys.exit(main())
