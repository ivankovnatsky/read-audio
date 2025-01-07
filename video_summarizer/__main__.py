import argparse
import sys
from pathlib import Path
import tempfile
import shutil

from video_summarizer.download import youtube
from video_summarizer.transcribe import whisper
from video_summarizer.summarize import llama
from video_summarizer.config import (
    DEFAULT_WHISPER_MODEL,
    DEFAULT_LLAMA_MODEL,
    DEFAULT_LANGUAGE,
)
from video_summarizer.logger import logger


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate video summaries using Whisper and LLaMA"
    )

    # Create a mutually exclusive group for input source
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--url",
        type=str,
        help="YouTube video URL to summarize",
    )
    input_group.add_argument(
        "--file",
        type=Path,
        help="Local video file to summarize",
    )
    
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("/tmp"),
        help="Output directory for generated files",
    )
    parser.add_argument(
        "--whisper-model",
        type=str,
        default=DEFAULT_WHISPER_MODEL,
        help=f"Whisper model to use (default: {DEFAULT_WHISPER_MODEL})",
    )
    parser.add_argument(
        "--llama-model",
        type=str,
        default=DEFAULT_LLAMA_MODEL,
        help=f"LLaMA model to use (default: {DEFAULT_LLAMA_MODEL})",
    )
    parser.add_argument(
        "--language",
        type=str,
        default=DEFAULT_LANGUAGE,
        help=f"Video language (default: {DEFAULT_LANGUAGE})",
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Handle input source
            if args.url:
                logger.info("Downloading audio...")
                audio_path = youtube.download_audio(args.url, temp_path)
            else:
                logger.info("Processing local video...")
                # Copy to temp dir to ensure consistent naming
                audio_path = temp_path / args.file.name
                shutil.copy2(args.file, audio_path)
            
            logger.info("Transcribing audio...")
            transcript_path = whisper.transcribe(
                audio_path,
                temp_path,
                language=args.language,
                model_name=args.whisper_model,
            )
            
            logger.info("Generating summary...")
            summary = llama.summarize(
                transcript_path,
                model_name=args.llama_model,
            )
            
            # Write summary to output directory
            output_path = args.output / f"{audio_path.stem}_summary.txt"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(summary)
                
            logger.info(f"\nSummary saved to: {output_path}")
            
        return 0

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
