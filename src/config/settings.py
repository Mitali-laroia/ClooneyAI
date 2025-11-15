"""Application settings loaded from environment variables."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
	"""Application configuration from environment variables."""

	# OpenAI Configuration
	OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
	OPENAI_MINI_MODEL: str = os.getenv("OPENAI_MINI_MODEL", "gpt-4o-mini")
	OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

	# E2B Configuration
	E2B_API_KEY: str = os.getenv("E2B_API_KEY", "")

	# Application Configuration
	TEST_URL: str = os.getenv("TEST_URL", "https://example.com")
	ASANA_EMAIL_ID: str = os.getenv("ASANA_EMAIL_ID", "")
	ASANA_PASSWORD: str = os.getenv("ASANA_PASSWORD", "")

	# Output directories
	OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "output")
	SCREENSHOT_DIR: str = os.getenv("SCREENSHOT_DIR", "output/screenshots")

	@classmethod
	def validate(cls) -> None:
		"""Validate required environment variables are set."""
		required_vars = []

		# Only validate API keys if they're actually needed
		if not cls.OPENAI_API_KEY:
			required_vars.append("OPENAI_API_KEY")
		if not cls.E2B_API_KEY:
			required_vars.append("E2B_API_KEY")

		if required_vars:
			raise ValueError(
				f"Missing required environment variables: {', '.join(required_vars)}"
			)


# Create a singleton instance
settings = Settings()
