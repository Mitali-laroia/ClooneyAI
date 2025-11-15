.PHONY: setup

setup:
	@echo "Checking if uv is installed..."
	@if ! command -v uv &> /dev/null; then \
		echo "uv not found. Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		export PATH="$$HOME/.cargo/bin:$$PATH"; \
	else \
		echo "uv is already installed."; \
	fi
	@echo "Running uv sync..."
	@uv sync
	@uv run playwright install
	@echo "Setup complete!"
