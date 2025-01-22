from pathlib import Path
import yt_dlp


def download_audio(url: str, output_dir: Path, use_cloud: bool = False) -> Path:
    """
    Download audio from a video URL.

    Args:
        url: Video URL (currently supports YouTube)
        output_dir: Directory to save the audio file
        use_cloud: If True, use mp3 format for cloud Whisper compatibility

    Returns:
        Path to the downloaded audio file
    """
    preferred_codec = "mp3" if use_cloud else "opus"
    
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": preferred_codec,
            }
        ],
        "outtmpl": str(output_dir / "%(id)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info is None:
                raise RuntimeError("Failed to extract video information")
            
            video_id = info["id"]
            ydl.download([url])
            return output_dir / f"{video_id}.{preferred_codec}"

    except Exception as e:
        raise RuntimeError(f"Failed to download audio: {e}") from e
