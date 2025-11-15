"""LangGraph workflow nodes."""

import asyncio

from src.browser.scraper import scrape_page
from src.utils.storage import save_scraped_data
from src.workflows.state import CloneState


async def scraper_node(state: CloneState) -> CloneState:
	"""Scrape the webpage and extract DOM, CSS, and screenshots.

	Args:
		state: Current workflow state

	Returns:
		Updated state with scraped data
	"""
	url = state["url"]

	try:
		# Scrape the page (includes screenshots for mobile, tablet, desktop)
		scraped_data = await scrape_page(url)

		# Save to JSON file
		output_file = save_scraped_data(
			url=url,
			dom=scraped_data["dom"],
			css=scraped_data["css"],
			dom_simplified=scraped_data["dom_simplified"],
			screenshots=scraped_data["screenshots"],
		)

		# Update state
		return {
			**state,
			"status": "scraped",
			"dom": scraped_data["dom"],
			"dom_simplified": scraped_data["dom_simplified"],
			"css": scraped_data["css"],
			"screenshots": scraped_data["screenshots"],
			"output_file": output_file,
			"error": None,
		}

	except Exception as e:
		return {
			**state,
			"status": "failed",
			"error": str(e),
			"dom": None,
			"dom_simplified": None,
			"css": None,
			"screenshots": None,
			"output_file": None,
		}


def scraper_node_sync(state: CloneState) -> CloneState:
	"""Synchronous wrapper for the scraper node.

	Args:
		state: Current workflow state

	Returns:
		Updated state with scraped data
	"""
	return asyncio.run(scraper_node(state))
