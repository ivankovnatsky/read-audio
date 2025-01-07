# video-summarizer

A Python utility to summarize videos using local ML models.

## Features

- Cross-platform support (macOS and Windows)
- Efficient transcription using Whisper
  - Optimized for Apple Silicon with mlx-whisper
- Local summarization using LLaMA via Ollama
- Multi-language support
- Progress reporting

## Requirements

- Python 3.12 or later
- FFmpeg (for audio extraction)
- Ollama (with LLaMA model installed)
- On macOS with Apple Silicon: mlx-whisper (optional, for better performance)

## Installation

### Using Nix Flakes

Enable flakes in your nix configuration and run:

```console
# For development environment
nix develop

# Or install globally
nix profile install
```

### Manual Installation

```console
# Install dependencies
poetry install

# On macOS, install with Apple Silicon optimizations
poetry install -E macos
```

## Usage

Show help:
```console
video-summarizer --help
```

Basic usage:
```console
video-summarizer "https://www.youtube.com/watch?v=VIDEO_ID"
```

With specific models and language:
```console
video-summarizer \
    --whisper-model large \
    --llama-model llama3.1:8b \
    --language uk \
    "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Available Options

- `--whisper-model`: Choose Whisper model size (tiny, base, small, medium, large)
- `--llama-model`: Specify LLaMA model in Ollama
- `--language`: Set video language (e.g., "en", "uk")
- `-o, --output`: Set output directory for intermediate files
- `-v, --verbose`: Enable verbose output

## Development

Format code:
```console
make fmt
```

Run linting:
```console
make lint
```

## Examples

Run basic example:
```console
make run-example
```

Run example with Ukrainian language:
```console
make run-example-uk
```

## Project Configuration

```console
gh repo create video-summarizer --public
direnv allow
```

## TODO

- [ ] Replace all multiline strings with newline chars \n, variables with appropriate multiline definitions
- [ ] Research if we can use Cloud models for faster summarization
- [ ] Replace argparse with click
