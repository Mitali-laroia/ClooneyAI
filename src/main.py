"""Main entry point for Clooney AI."""

from src.workflows import clone_graph


def main() -> None:
	"""Run the main application."""
	print("🤖 Welcome to Clooney AI - Website Cloning Tool")
	print("=" * 60)

	# Initialize the workflow with state
	initial_state = {
		"url": "https://asana.com/",
		"status": "initialized",
		"error": None,
		"dom": None,
		"dom_simplified": None,
		"css": None,
		"output_file": None,
		"screenshots": None,
	}

	print(f"\n📍 Target URL: {initial_state['url']}")
	print("🔄 Starting scraping process...\n")

	# Invoke the workflow
	result = clone_graph.invoke(initial_state)

	# Display results
	print("=" * 60)
	print(f"✅ Status: {result['status'].upper()}")
	print("=" * 60)

	if result["error"]:
		print(f"\n❌ Error: {result['error']}")
	else:
		print("\n📊 Scraped Data:")
		print(f"  📄 Full DOM: {len(result['dom']) if result['dom'] else 0:,} chars")
		print(
			f"  🧹 Simplified DOM: {len(result['dom_simplified']) if result['dom_simplified'] else 0:,} chars"
		)
		print(f"  🎨 CSS: {len(result['css']) if result['css'] else 0:,} chars")

		if result["screenshots"]:
			print(f"\n📸 Screenshots captured:")
			for viewport, path in result["screenshots"].items():
				print(f"  • {viewport.capitalize()}: {path}")

		print(f"\n💾 Data saved to: {result['output_file']}")
		print("\n✨ Ready for AI processing!")


if __name__ == "__main__":
	main()
