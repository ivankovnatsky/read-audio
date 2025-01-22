# read-audio

A Python utility to summarize videos using various AI providers (local and cloud-based).

## Features

- Multiple input sources support:
  - YouTube URLs
  - Local video files
  - Existing transcript files
- Two processing modes:
  - Summary: Generate a 200-250 word summary
  - Condense: Create a shorter version with configurable length (1-100%)
- Flexible AI provider options:
  - Local: Ollama
  - Cloud: OpenAI, Anthropic
- Efficient transcription using Whisper
  - Optimized for Apple Silicon with mlx-whisper
- Multi-language support
- Transcript and processed text output

## Requirements

- Python 3.12 or later
- FFmpeg (for audio extraction)
- One of the following AI providers:
  - Ollama (for local processing)
  - OpenAI API key
  - Anthropic API key
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

Run basic summary example:

```console
make run-example
```

Run Ukrainian language example with condensing:

```console
make run-example-uk-condense
```

## Options

```console
poetry run read-audio --help
Usage: read-audio [OPTIONS]

  Generate summaries or condensed versions of video content

Options:
  --mode [summary|condense]       Processing mode: summary (200-250 words) or
                                  condense (5% length)
  --url TEXT                      URL of the video to summarize
  --file PATH                     Path to local video file
  --transcript PATH               Path to existing transcript file
  --output PATH                   Output directory for processed files
  --whisper-model TEXT            Whisper model to use (default: base)
  --provider [openai|anthropic|ollama]
                                  AI provider to use for summarization
  --model TEXT                    Model to use for summarization
  --language TEXT                 Language of the video
  --show-transcript               Show transcript in output
  --show-processed-text           Show processed text (summary or condensed)
                                  in output
  --use-cloud-whisper             Use OpenAI's Whisper cloud API for
                                  transcription
  --condense-percentage PERCENTAGE_TYPE
                                  Percentage of original length for condensed
                                  output (1-100%)
  --help                          Show this message and exit.
```

## Development

Format code:

```console
make fmt
```

Run linting:

```console
make lint
```

## Project Configuration

```console
gh repo create read-audio --public
direnv allow
```

## TODO
