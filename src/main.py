"""Main entry point for Clooney AI."""

from src.workflows import clone_graph


def main() -> None:
	"""Run the main application."""
	print("🤖 Welcome to Clooney AI - Website Cloning Tool")

	# Example: Initialize the workflow with state
	initial_state = {
		"url": "https://example.com",
		"status": "initialized",
		"error": None,
	}

	# Invoke the workflow
	result = clone_graph.invoke(initial_state)

	print(f"✅ Workflow completed: {result}")


if __name__ == "__main__":
	main()
