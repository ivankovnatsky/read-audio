from pathlib import Path
import json
import requests
from typing import Optional

from video_summarizer.config import DEFAULT_LLAMA_MODEL
from video_summarizer.logger import logger


class OllamaError(Exception):
    """Base exception for Ollama-related errors."""

    pass


def summarize(
    transcript_path: Path,
    model_name: str = DEFAULT_LLAMA_MODEL,
    ollama_host: str = "http://localhost:11434",
    max_tokens: Optional[int] = None,
) -> str:
    """
    Summarize a transcript using LLaMA via Ollama.

    Args:
        transcript_path: Path to the transcript file
        model_name: Name of the LLaMA model to use
        ollama_host: Ollama API host URL
        max_tokens: Maximum number of tokens in the response (optional)

    Returns:
        Generated summary text

    Raises:
        OllamaError: If the API request fails
    """
    # Read the transcript
    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = f.read()

    # Prepare the system prompt
    system_prompt = (
        "Below is a transcript from a video. "
        "Provide a concise summary (200-250 words) that captures the main points "
        "and important details. At the end, list the key points and issues discussed."
    )

    # Construct the full prompt
    prompt = f"{system_prompt}\n\n---------------\n\n{transcript}"

    # Prepare the API request
    request_body = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
    }

    if max_tokens:
        request_body["options"] = {"num_predict": max_tokens}

    try:
        logger.info(f"Making Ollama API request to {ollama_host}")
        
        # Make the API request to Ollama
        response = requests.post(
            url=f"{ollama_host}/api/generate",
            json=request_body,
            timeout=None,
        )
        
        response.raise_for_status()

        # Extract the summary from the response
        response_data = response.json()
        summary = response_data.get("response", "")

        if not summary:
            raise OllamaError("Empty response from Ollama API")

        return summary

    except requests.exceptions.RequestException as e:
        raise OllamaError(f"Failed to communicate with Ollama API: {str(e)}") from e
    except (json.JSONDecodeError, KeyError) as e:
        raise OllamaError(f"Invalid response from Ollama API: {str(e)}") from e
