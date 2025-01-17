.PHONY: build clean test lint run install fmt fmt-check deps all

# Python parameters
POETRY=poetry
BINARY_NAME=video-summarizer

# Default model parameters (should match config.py)
DEFAULT_LLAMA_MODEL=llama3.1:8b

# Default target
all: clean install

# Install the project
install:
	$(POETRY) install

# Install with macOS optimizations
install-macos:
	$(POETRY) install -E macos

regenerate-lock:
	$(POETRY) lock --regenerate

# Clean build files
clean:
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.opus" -delete
	find . -type f -name "*.txt" -delete

# Run linting
lint:
	$(POETRY) run ruff check .

# Format code
fmt:
	$(POETRY) run ruff format .

# Check code formatting
fmt-check:
	$(POETRY) run ruff format --check .

# Install dependencies
deps:
	$(POETRY) install

# Build distribution
build:
	$(POETRY) build

# Run examples
run-example:
	$(POETRY) run $(BINARY_NAME) \
		--url "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

run-example-uk:
	$(POETRY) run $(BINARY_NAME) \
		--whisper-model large \
		--llama-model $(DEFAULT_LLAMA_MODEL) \
		--language uk \
		--url "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

run-url:
	$(POETRY) run $(BINARY_NAME) \
		--url $(url)

run-url-language:
	$(POETRY) run $(BINARY_NAME) \
		--url $(url) \
		--language $(language)

run-file:
	$(POETRY) run $(BINARY_NAME) \
		--file $(file)

run-url-with-transcript:
	$(POETRY) run $(BINARY_NAME) \
		--url $(url) \
		--show-transcript

run-example-with-transcript:
	$(POETRY) run $(BINARY_NAME) \
		--whisper-model large \
		--llama-model $(DEFAULT_LLAMA_MODEL) \
		--language uk \
		--show-transcript \
		--url "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Check all (format, lint)
check: fmt-check lint
