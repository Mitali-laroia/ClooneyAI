"""State definitions for LangGraph workflows."""

from typing import Any, TypedDict


class CloneState(TypedDict):
	"""State for the website cloning workflow."""

	url: str  # Target URL (login page)
	status: str  # Current workflow status
	error: str | None  # Error message if any

	# Iterative login fields
	current_step: str  # Current login step: "init" | "find_email" | "enter_email" | "find_email_continue" | "click_email_continue" | "find_password" | "enter_password" | "find_submit" | "click_submit" | "verify_login" | "completed" | "failed"
	iteration_count: int  # Number of iterations (max 10)
	last_action: str | None  # Description of last action taken
	ai_guidance: dict[str, Any] | None  # Latest AI guidance/response
	last_error: str | None  # Last error message for AI to learn from
	step_retry_count: int  # Number of retries for current step (max 3 per step)

	# Credentials
	email: str | None  # Email to use for login
	password: str | None  # Password to use for login

	# Login results
	login_successful: bool | None  # Whether login succeeded
	login_url: str | None  # URL after login
	login_screenshot: str | None  # Screenshot of logged-in state
	total_tokens_used: int  # Total OpenAI tokens used

	# Browser session (stored as dict to avoid serialization issues)
	browser_session: dict[str, Any] | None  # Browser, context, page references

	# Page data
	current_dom: str | None  # Current page DOM
	current_css: str | None  # Current page CSS (all stylesheets combined)
	current_page_url: str | None  # Current page URL

	# Future: Scraping fields (to be added back later)
	dom: str | None  # Full DOM/HTML content
	dom_simplified: str | None  # Simplified DOM (cleaned)
	css: str | None  # CSS content
	output_file: str | None  # Path to saved JSON file
	screenshots: dict[str, str] | None  # Viewport -> screenshot path mapping
