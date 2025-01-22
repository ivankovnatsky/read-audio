from pathlib import Path
import os
from typing import Iterator
from pydub import AudioSegment
from read_audio.logger import logger

# 25MB in bytes (leaving some margin for safety)
MAX_FILE_SIZE = 24 * 1024 * 1024  # ~24MB

def split_audio_file(audio_path: Path) -> Iterator[Path]:
    """Split large audio files into smaller chunks based on file size."""
    if os.path.getsize(audio_path) <= MAX_FILE_SIZE:
        yield audio_path
        return

    logger.info(f"Audio file {audio_path} is too large, splitting into chunks...")
    audio = AudioSegment.from_file(audio_path)
    
    # Calculate approximate duration per chunk based on file size ratio
    total_size = os.path.getsize(audio_path)
    size_ratio = MAX_FILE_SIZE / total_size
    chunk_duration = int(len(audio) * size_ratio)
    
    # Calculate number of chunks needed
    total_duration = len(audio)
    num_chunks = (total_duration + chunk_duration - 1) // chunk_duration
    
    for i in range(num_chunks):
        start = i * chunk_duration
        end = min((i + 1) * chunk_duration, total_duration)
        
        chunk = audio[start:end]
        chunk_path = audio_path.parent / f"{audio_path.stem}_chunk_{i:03d}{audio_path.suffix}"
        chunk.export(chunk_path, format=audio_path.suffix.lstrip('.'))
        
        # Verify chunk size
        if os.path.getsize(chunk_path) > MAX_FILE_SIZE:
            logger.warning(f"Chunk {i} is still too large, may fail API upload")
        
        yield chunk_path


def detect_silence(
    audio_segment: AudioSegment,
    silence_threshold: float = -50.0,
    min_silence_duration: int = 500,
) -> list[tuple[int, int]]:
    """
    Detect ranges of silence in an audio segment.

    Args:
        audio_segment: The audio segment to analyze
        silence_threshold: The threshold (in dB) below which is considered silence
        min_silence_duration: Minimum silence duration in milliseconds

    Returns:
        List of (start_ms, end_ms) tuples indicating silence ranges
    """
    silence_ranges = []
    current_silence_start = None

    # Analyze in 10ms chunks
    chunk_size = 10

    for i in range(0, len(audio_segment), chunk_size):
        chunk = audio_segment[i : i + chunk_size]
        if chunk.dBFS < silence_threshold:
            if current_silence_start is None:
                current_silence_start = i
        elif current_silence_start is not None:
            if i - current_silence_start >= min_silence_duration:
                silence_ranges.append((current_silence_start, i))
            current_silence_start = None

    # Handle silence at the end
    if current_silence_start is not None:
        silence_ranges.append((current_silence_start, len(audio_segment)))

    return silence_ranges
