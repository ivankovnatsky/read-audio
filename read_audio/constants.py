"""Default configuration for read-audio."""

DEFAULT_SUMMARY_PROMPT = (
    "Below is a audio transcript. "
    "Provide a concise summary (200-250 words) that captures the main points and important details. "
    "To conclude list the key points and issues discussed.  "
    "Use the same language as the source transcript. "
)

DEFAULT_CONDENSE_PROMPT = (
    "Below is a audio transcript. "
    "Your task is to condense this text while maintaining EXACTLY {percentage}% of the original length. "
    "The input text is {input_length} characters long, so your response should be {target_length} characters. "
    "Use the same language as the source transcript. "
)

DEFAULT_CONDENSE_PERCENTAGE = 5

# Model configurations
DEFAULT_WHISPER_MODEL = "base"
DEFAULT_WHISPER_CLOUD_MODEL = "whisper-1"
DEFAULT_MLX_WHISPER_MODEL_REPO = "mlx-community/whisper-turbo"
DEFAULT_LANGUAGE = "en"

OLLAMA_HOST = "http://localhost:11434"

DEFAULT_LLAMA_MODEL = "llama3.1:8b"
DEFAULT_ANTRHOPIC_MODEL = "claude-3-5-sonnet-20241022"
DEFAULT_OPENAI_MODEL = "gpt-4o"

MODEL_MAPPING = {
    "ollama": DEFAULT_LLAMA_MODEL,
    "anthropic": DEFAULT_ANTRHOPIC_MODEL,
    "openai": DEFAULT_OPENAI_MODEL,
}
