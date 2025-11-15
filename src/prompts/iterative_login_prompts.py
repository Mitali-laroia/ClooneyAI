"""Step-by-step prompts for iterative login process."""

FIND_EMAIL_INPUT_PROMPT = """You are analyzing a login page to find the email/username input field.

Analyze the HTML and identify the CSS selector for the email or username input field.

Return ONLY a JSON object with this structure:
{{
    "selector": "CSS selector for the email input",
    "confidence": "high/medium/low",
    "reasoning": "Brief explanation"
}}

Examples:

Example 1:
HTML:
<input type="email" id="email" name="email" placeholder="Email address">

Response:
{{
    "selector": "input[type='email']#email",
    "confidence": "high",
    "reasoning": "Clear email input with type='email' and id"
}}

Example 2:
HTML:
<input type="text" name="username" placeholder="Email or username" autocomplete="username">

Response:
{{
    "selector": "input[autocomplete='username']",
    "confidence": "high",
    "reasoning": "Input with autocomplete='username' is standard for email/username fields"
}}

Now analyze this HTML:

{html_content}

Return ONLY the JSON object:"""


FIND_EMAIL_CONTINUE_PROMPT = """You are analyzing a login page after email entry to find the Continue/Next button.

Many login forms have a two-step process: first enter email, then click Continue to proceed to password.

Analyze the HTML and identify the CSS selector for the Continue/Next button after email entry.

IMPORTANT: Use only standard CSS selectors. DO NOT use jQuery selectors like :contains(), :visible, etc.
Valid CSS selector types: element, .class, #id, [attribute], [attribute='value'], :nth-child(), etc.

Return ONLY a JSON object with this structure:
{{
    "selector": "CSS selector for the continue button",
    "confidence": "high/medium/low",
    "reasoning": "Brief explanation"
}}

Examples:

Example 1:
HTML:
<button type="submit" class="continue-btn">Continue</button>

Response:
{{
    "selector": "button[type='submit'].continue-btn",
    "confidence": "high",
    "reasoning": "Submit button with 'Continue' text after email field"
}}

Example 2:
HTML:
<button class="primary-button">Next</button>

Response:
{{
    "selector": "button.primary-button",
    "confidence": "high",
    "reasoning": "Primary button with 'Next' text, standard for email continuation"
}}

Example 3:
HTML:
<div role="button" class="action-button">Continue with email</div>

Response:
{{
    "selector": "div.action-button[role='button']",
    "confidence": "medium",
    "reasoning": "Div with button role containing continue text"
}}

Now analyze this HTML:

{html_content}

Return ONLY the JSON object:"""


FIND_PASSWORD_INPUT_PROMPT = """You are analyzing a login page to find the password input field.

Analyze the HTML and identify the CSS selector for the password input field.

Return ONLY a JSON object with this structure:
{{
    "selector": "CSS selector for the password input",
    "confidence": "high/medium/low",
    "reasoning": "Brief explanation"
}}

Examples:

Example 1:
HTML:
<input type="password" id="password" name="password" placeholder="Password">

Response:
{{
    "selector": "input[type='password']#password",
    "confidence": "high",
    "reasoning": "Clear password input with type='password'"
}}

Example 2:
HTML:
<input type="password" autocomplete="current-password" class="form-input">

Response:
{{
    "selector": "input[type='password'][autocomplete='current-password']",
    "confidence": "high",
    "reasoning": "Password input with autocomplete attribute"
}}

Now analyze this HTML:

{html_content}

Return ONLY the JSON object:"""


FIND_SUBMIT_BUTTON_PROMPT = """You are analyzing a login page to find the submit/login button.

Analyze the HTML and identify the CSS selector for the login/submit button.

Return ONLY a JSON object with this structure:
{{
    "selector": "CSS selector for the submit button",
    "confidence": "high/medium/low",
    "reasoning": "Brief explanation"
}}

Examples:

Example 1:
HTML:
<button type="submit" class="login-btn">Log in</button>

Response:
{{
    "selector": "button[type='submit'].login-btn",
    "confidence": "high",
    "reasoning": "Submit button with 'Log in' text"
}}

Example 2:
HTML:
<button class="primary-button">Continue</button>

Response:
{{
    "selector": "button.primary-button",
    "confidence": "medium",
    "reasoning": "Primary button with 'Continue' text, likely the submit button"
}}

Now analyze this HTML:

{html_content}

Return ONLY the JSON object:"""


VERIFY_LOGIN_PROMPT = """You are verifying if a login attempt was successful.

Analyze the current page state (URL, title, HTML) and determine if the user is now logged in.

Return ONLY a JSON object with this structure:
{{
    "logged_in": true/false,
    "confidence": "high/medium/low",
    "reasoning": "Brief explanation",
    "next_action": "What to do next"
}}

Examples:

Example 1 - Success:
URL: https://app.asana.com/0/home
Title: Home - Asana
HTML: <div class="UserProfile">John Doe</div>

Response:
{{
    "logged_in": true,
    "confidence": "high",
    "reasoning": "URL changed to /home with user profile visible",
    "next_action": "Login successful, proceed to next step"
}}

Example 2 - Failed:
URL: https://app.asana.com/-/login
Title: Log in - Asana
HTML: <div class="error">Invalid credentials</div>

Response:
{{
    "logged_in": false,
    "confidence": "high",
    "reasoning": "Still on login page with error message",
    "next_action": "Login failed, check credentials"
}}

Example 3 - Needs more time:
URL: https://app.asana.com/-/login
Title: Log in - Asana
HTML: <div class="loading">Signing you in...</div>

Response:
{{
    "logged_in": false,
    "confidence": "low",
    "reasoning": "Loading state visible, authentication in progress",
    "next_action": "Wait and check again"
}}

Now analyze the current state:

URL: {url}
Title: {title}
HTML (first 3000 chars):
{html_content}

Return ONLY the JSON object:"""


def get_find_email_prompt(html_content: str, last_error: str | None = None, css_content: str | None = None) -> str:
	"""Get prompt for finding email input.

	Args:
		html_content: Page HTML
		last_error: Previous error to avoid, if any
		css_content: Page CSS for additional context

	Returns:
		Formatted prompt
	"""
	error_note = ""
	if last_error:
		error_note = f"\n\n⚠️ IMPORTANT: {last_error}\nPlease choose a DIFFERENT selector using standard CSS syntax.\n"

	css_note = ""
	if css_content:
		css_note = f"\n\nAvailable CSS classes and styles (first 3000 chars):\n{css_content[:3000]}\n"

	return FIND_EMAIL_INPUT_PROMPT.format(html_content=html_content[:5000]) + css_note + error_note


def get_find_email_continue_prompt(html_content: str, last_error: str | None = None) -> str:
	"""Get prompt for finding email continue button.

	Args:
		html_content: Page HTML
		last_error: Previous error to avoid, if any

	Returns:
		Formatted prompt
	"""
	error_note = ""
	if last_error:
		error_note = f"\n\n⚠️ IMPORTANT: {last_error}\nPlease choose a DIFFERENT selector that uses standard CSS syntax (not jQuery selectors like :contains). Use valid CSS selectors like button[type='submit'], .class-name, #id, or [aria-label='text'].\n"
	return FIND_EMAIL_CONTINUE_PROMPT.format(html_content=html_content[:5000]) + error_note


def get_find_password_prompt(html_content: str, last_error: str | None = None) -> str:
	"""Get prompt for finding password input.

	Args:
		html_content: Page HTML
		last_error: Previous error to avoid, if any

	Returns:
		Formatted prompt
	"""
	error_note = ""
	if last_error:
		error_note = f"\n\n⚠️ IMPORTANT: {last_error}\nPlease choose a DIFFERENT selector using standard CSS syntax.\n"
	return FIND_PASSWORD_INPUT_PROMPT.format(html_content=html_content[:5000]) + error_note


def get_find_submit_prompt(html_content: str, last_error: str | None = None) -> str:
	"""Get prompt for finding submit button.

	Args:
		html_content: Page HTML
		last_error: Previous error to avoid, if any

	Returns:
		Formatted prompt
	"""
	error_note = ""
	if last_error:
		error_note = f"\n\n⚠️ IMPORTANT: {last_error}\nPlease choose a DIFFERENT selector using standard CSS syntax.\n"
	return FIND_SUBMIT_BUTTON_PROMPT.format(html_content=html_content[:5000]) + error_note


def get_verify_login_prompt(url: str, title: str, html_content: str) -> str:
	"""Get prompt for verifying login.

	Args:
		url: Current URL
		title: Page title
		html_content: Page HTML

	Returns:
		Formatted prompt
	"""
	return VERIFY_LOGIN_PROMPT.format(
		url=url, title=title, html_content=html_content[:3000]
	)
