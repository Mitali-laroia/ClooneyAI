"""Storage utilities for saving scraped data."""

import json
from datetime import datetime
from pathlib import Path

from src.config import settings


def save_scraped_data(
	url: str,
	dom: str,
	css: str,
	dom_simplified: str | None = None,
	screenshots: dict[str, str] | None = None,
	output_dir: str | None = None,
) -> str:
	"""Save scraped DOM, CSS, and screenshots to a JSON file.

	Args:
		url: The URL that was scraped
		dom: The HTML/DOM content
		css: The CSS content
		dom_simplified: Simplified/cleaned DOM
		screenshots: Dictionary of viewport -> screenshot path
		output_dir: Directory to save the file (defaults to settings.OUTPUT_DIR)

	Returns:
		Path to the saved file
	"""
	# Use settings default if not provided
	if output_dir is None:
		output_dir = settings.OUTPUT_DIR

	# Create output directory
	output_path = Path(output_dir)
	output_path.mkdir(parents=True, exist_ok=True)

	# Generate filename with timestamp
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	domain = url.replace("https://", "").replace("http://", "").replace("/", "_")
	filename = f"{domain}_{timestamp}.json"
	filepath = output_path / filename

	# Create data structure
	data = {
		"url": url,
		"scraped_at": datetime.now().isoformat(),
		"dom": dom,
		"dom_simplified": dom_simplified,
		"css": css,
		"screenshots": screenshots or {},
		"metadata": {
			"dom_size": len(dom) if dom else 0,
			"dom_simplified_size": len(dom_simplified) if dom_simplified else 0,
			"css_size": len(css) if css else 0,
			"viewports": list(screenshots.keys()) if screenshots else [],
		},
	}

	# Save to JSON
	with open(filepath, "w", encoding="utf-8") as f:
		json.dump(data, f, indent=2, ensure_ascii=False)

	return str(filepath)
