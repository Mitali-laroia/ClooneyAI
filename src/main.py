"""Main entry point for Clooney AI."""

from src.config import settings
from src.workflows import clone_graph
from src.workflows.nodes import cleanup_browser, cleanup_event_loop, get_event_loop


def main() -> None:
	"""Run the main application."""
	print("🤖 Welcome to Clooney AI - Website Cloning Tool")
	print("=" * 60)
	print("🎯 Phase: Iterative AI-Guided Login")
	print("=" * 60)

	# Initialize the workflow with state
	initial_state = {
		"url": settings.TEST_URL,
		"status": "initialized",
		"error": None,
		# Iterative login fields
		"current_step": "init",
		"iteration_count": 0,
		"last_action": None,
		"ai_guidance": None,
		"last_error": None,
		"step_retry_count": 0,
		# Credentials
		"email": settings.ASANA_EMAIL_ID,
		"password": settings.ASANA_PASSWORD,
		# Login results
		"login_successful": None,
		"login_url": None,
		"login_screenshot": None,
		"total_tokens_used": 0,
		# Browser session
		"browser_session": None,
		# Page data
		"current_dom": None,
		"current_css": None,
		"current_page_url": None,
		# Future scraping fields
		"dom": None,
		"dom_simplified": None,
		"css": None,
		"output_file": None,
		"screenshots": None,
	}

	print(f"\n📍 Login URL: {initial_state['url']}")
	print(f"📧 Email: {settings.ASANA_EMAIL_ID}")
	print("🔄 Starting iterative login process (max 10 iterations)...\n")

	result = None
	try:
		# Invoke the workflow
		result = clone_graph.invoke(initial_state)

		# Display results
		print("\n" + "=" * 60)
		print(f"📊 FINAL RESULTS")
		print("=" * 60)
		print(f"Status: {result['status']}")
		print(f"Final Step: {result['current_step']}")
		print(f"Iterations: {result['iteration_count']}")
		print(f"Total Tokens Used: {result['total_tokens_used']:,}")

		if result["error"]:
			print(f"\n❌ Error: {result['error']}")
		elif result.get("login_successful"):
			print("\n✅ Login Results:")
			print(f"  🎉 Login Successful!")
			print(f"  🌐 Post-Login URL: {result['login_url']}")
			print(f"  📸 Screenshot: {result['login_screenshot']}")
			print(f"  📝 Last Action: {result['last_action']}")
			print("\n✨ Ready to scrape dashboard!")
		else:
			print("\n❌ Login Failed")
			if result.get("last_action"):
				print(f"   Last Action: {result['last_action']}")

	finally:
		# Clean up browser and event loop
		print("\n🧹 Cleaning up resources...")
		loop = get_event_loop()
		if result and result.get("browser_session"):
			loop.run_until_complete(cleanup_browser(result))
		cleanup_event_loop()
		print("✅ Cleanup complete")


if __name__ == "__main__":
	main()
