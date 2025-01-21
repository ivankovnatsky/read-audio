from pathlib import Path
import os
from typing import Iterator
from pydub import AudioSegment
from video_summarizer.logger import logger

# 25MB in bytes (leaving some margin for safety)
MAX_FILE_SIZE = 24 * 1024 * 1024  
# 10 minutes in milliseconds
CHUNK_DURATION = 10 * 60 * 1000  

def split_audio_file(audio_path: Path, output_dir: Path) -> Iterator[Path]:
    """
    Split large audio files into smaller chunks that can be processed by Whisper API.
    Uses PyDub to split audio intelligently near silence to avoid mid-sentence breaks.
    
    Args:
        audio_path: Path to the input audio file
        output_dir: Directory to save the chunks
        
    Yields:
        Paths to the chunk files
    """
    if os.path.getsize(audio_path) <= MAX_FILE_SIZE:
        yield audio_path
        return

    logger.info(f"Audio file {audio_path} is too large, splitting into chunks...")
    
    # Load the audio file
    audio = AudioSegment.from_file(audio_path)
    
    # Calculate number of chunks needed
    total_duration = len(audio)
    chunk_count = (total_duration // CHUNK_DURATION) + 1
    
    for i in range(chunk_count):
        start_time = i * CHUNK_DURATION
        end_time = min((i + 1) * CHUNK_DURATION, total_duration)
        
        # Get the chunk
        chunk = audio[start_time:end_time]
        
        # Try to find silence near the end of the chunk to avoid mid-sentence breaks
        if i < chunk_count - 1:  # Don't adjust the last chunk
            silence_threshold = -50  # dB
            silence_duration = 500  # ms
            
            # Look for silence in the last second of the chunk
            analysis_window = chunk[-1000:]
            silent_ranges = detect_silence(
                analysis_window, 
                silence_threshold, 
                silence_duration
            )
            
            if silent_ranges:
                # Adjust chunk end to the middle of the first silence
                silence_start = silent_ranges[0][0]
                chunk = chunk[:-1000 + silence_start]
        
        # Export the chunk
        chunk_path = output_dir / f"{audio_path.stem}_chunk_{i:03d}{audio_path.suffix}"
        chunk.export(chunk_path, format=audio_path.suffix.lstrip('.'))
        
        yield chunk_path

def detect_silence(
    audio_segment: AudioSegment,
    silence_threshold: float = -50.0,
    min_silence_duration: int = 500
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
        chunk = audio_segment[i:i + chunk_size]
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
