"""Few-shot prompting templates for login element identification."""

LOGIN_ELEMENT_IDENTIFICATION_PROMPT = """You are an expert at identifying login form elements in HTML DOM structures. Your task is to analyze the provided HTML and identify the CSS selectors for email/username input, password input, and the login/submit button.

Return your response as a JSON object with the following structure:
{
    "email_selector": "CSS selector for email/username input field",
    "password_selector": "CSS selector for password input field",
    "submit_selector": "CSS selector for login/submit button",
    "confidence": "high/medium/low",
    "reasoning": "Brief explanation of how you identified these elements"
}

Here are some examples:

Example 1:
HTML:
<form class="login-form">
    <input type="email" id="user-email" name="email" placeholder="Enter your email">
    <input type="password" id="user-password" name="password" placeholder="Enter your password">
    <button type="submit" class="btn-primary">Sign In</button>
</form>

Response:
{
    "email_selector": "input[type='email']#user-email",
    "password_selector": "input[type='password']#user-password",
    "submit_selector": "button[type='submit'].btn-primary",
    "confidence": "high",
    "reasoning": "Clear semantic HTML with proper input types and unique IDs. Submit button is clearly labeled 'Sign In'."
}

Example 2:
HTML:
<div class="auth-container">
    <div class="input-group">
        <label for="username">Email or Username</label>
        <input id="username" name="username" class="form-control">
    </div>
    <div class="input-group">
        <label for="pwd">Password</label>
        <input id="pwd" type="password" class="form-control">
    </div>
    <button class="login-btn" onclick="submitLogin()">Log In</button>
</div>

Response:
{
    "email_selector": "input#username.form-control",
    "password_selector": "input#pwd[type='password']",
    "submit_selector": "button.login-btn",
    "confidence": "high",
    "reasoning": "Username input identified by label text 'Email or Username' and id. Password input has type='password' and id 'pwd'. Login button has descriptive class and onclick handler."
}

Example 3:
HTML:
<form id="loginForm" data-testid="login-form">
    <input
        type="text"
        name="login"
        placeholder="Email address"
        aria-label="Email address"
        data-testid="email-input"
    >
    <input
        type="password"
        name="password"
        placeholder="Password"
        aria-label="Password"
        data-testid="password-input"
    >
    <button
        type="submit"
        aria-label="Sign in"
        data-testid="signin-button"
    >
        Continue
    </button>
</form>

Response:
{
    "email_selector": "input[data-testid='email-input']",
    "password_selector": "input[data-testid='password-input']",
    "submit_selector": "button[data-testid='signin-button']",
    "confidence": "high",
    "reasoning": "Using data-testid attributes provides the most reliable selectors. Email input identified by placeholder and aria-label. Password input has type='password'. Submit button identified by aria-label 'Sign in'."
}

Example 4:
HTML:
<div class="login-page">
    <div class="field-wrapper">
        <input class="text-input" placeholder="someone@example.com" autocomplete="username">
    </div>
    <div class="field-wrapper">
        <input class="text-input" type="password" autocomplete="current-password">
    </div>
    <a href="#" class="submit-link" role="button">Enter</a>
</div>

Response:
{
    "email_selector": "input.text-input[autocomplete='username']",
    "password_selector": "input.text-input[type='password'][autocomplete='current-password']",
    "submit_selector": "a.submit-link[role='button']",
    "confidence": "medium",
    "reasoning": "No IDs or data-testid attributes. Using autocomplete attributes for inputs which are reliable. Submit is an anchor tag with role='button' instead of a proper button element."
}

Example 5:
HTML:
<div class="SignupForm-container">
    <h1>Sign in to Asana</h1>
    <div class="TextInputField">
        <input
            type="email"
            name="e"
            class="TextInput TextInput--medium"
            placeholder="name@company.com"
            required
        >
    </div>
    <div class="TextInputField">
        <input
            type="password"
            name="p"
            class="TextInput TextInput--medium"
            placeholder="Password"
            required
        >
    </div>
    <button
        type="submit"
        class="ButtonThemed ButtonThemed--large ButtonThemed--fullWidth"
    >
        Log in
    </button>
</div>

Response:
{
    "email_selector": "input[type='email'][name='e'].TextInput",
    "password_selector": "input[type='password'][name='p'].TextInput",
    "submit_selector": "button[type='submit'].ButtonThemed--fullWidth",
    "confidence": "high",
    "reasoning": "Clear form structure with heading 'Sign in to Asana'. Email and password inputs have proper types and distinct name attributes. Submit button has type='submit' and clear text 'Log in'."
}

Now analyze the following HTML and identify the login form elements:

HTML:
{html_content}

Remember to:
1. Look for input fields with type="email", type="text", or autocomplete="username" for email/username
2. Look for input fields with type="password" for password
3. Look for buttons with type="submit", text like "Log in"/"Sign in"/"Continue", or form submit handlers
4. Prefer selectors with IDs, data-testid, or unique class names
5. Consider aria-labels, placeholders, and nearby label text
6. Return ONLY the JSON object, no additional text

Response:"""


LOGIN_VERIFICATION_PROMPT = """You are an expert at verifying successful login attempts. Analyze the current page state and determine if the login was successful.

Return your response as a JSON object:
{
    "login_successful": true/false,
    "confidence": "high/medium/low",
    "reasoning": "Brief explanation",
    "suggested_next_action": "What to do next if login failed"
}

Here are some examples:

Example 1 - Successful Login:
Current URL: https://app.asana.com/0/home
Page Title: Home - Asana
HTML snippet:
<div class="TopbarPageHeaderStructure">
    <button class="UserSettingsButton" aria-label="My Profile Settings">
        <span>John Doe</span>
    </button>
</div>

Response:
{
    "login_successful": true,
    "confidence": "high",
    "reasoning": "URL changed to app subdomain with /home path. Page shows user profile button with name. Clear indicators of authenticated session.",
    "suggested_next_action": "Proceed with next workflow step"
}

Example 2 - Failed Login (Wrong Credentials):
Current URL: https://app.asana.com/auth/login
Page Title: Log in - Asana
HTML snippet:
<div class="ErrorMessage" role="alert">
    <span>Incorrect email or password. Please try again.</span>
</div>

Response:
{
    "login_successful": false,
    "confidence": "high",
    "reasoning": "Still on login page with error message visible. Error explicitly states incorrect credentials.",
    "suggested_next_action": "Verify credentials in environment variables are correct"
}

Example 3 - Failed Login (CAPTCHA):
Current URL: https://app.asana.com/auth/login
Page Title: Log in - Asana
HTML snippet:
<div class="captcha-container">
    <iframe src="https://www.google.com/recaptcha/api2/anchor"></iframe>
</div>

Response:
{
    "login_successful": false,
    "confidence": "high",
    "reasoning": "CAPTCHA challenge appeared, blocking automated login.",
    "suggested_next_action": "CAPTCHA detected - may need manual intervention or CAPTCHA solving service"
}

Example 4 - Uncertain State (Loading):
Current URL: https://app.asana.com/auth/login
Page Title: Log in - Asana
HTML snippet:
<div class="LoadingSpinner" aria-label="Loading">
    <svg class="spinner"></svg>
</div>

Response:
{
    "login_successful": false,
    "confidence": "low",
    "reasoning": "Loading spinner visible, authentication may still be in progress.",
    "suggested_next_action": "Wait a few seconds and re-verify"
}

Example 5 - Successful Login (Dashboard):
Current URL: https://app.asana.com/0/1234567890/list
Page Title: My Tasks - Asana
HTML snippet:
<nav class="Sidebar">
    <a href="/home">Home</a>
    <a href="/my-tasks">My Tasks</a>
    <div class="UserProfile">
        <img src="avatar.jpg" alt="John Doe">
    </div>
</nav>

Response:
{
    "login_successful": true,
    "confidence": "high",
    "reasoning": "Redirected to authenticated dashboard showing tasks. Navigation sidebar with user profile visible.",
    "suggested_next_action": "Proceed with next workflow step"
}

Now analyze the current page state:

Current URL: {current_url}
Page Title: {page_title}
HTML snippet:
{html_content}

Return ONLY the JSON object, no additional text.

Response:"""


def get_login_identification_prompt(html_content: str) -> str:
	"""Get the login element identification prompt with HTML content.

	Args:
		html_content: The HTML DOM content to analyze

	Returns:
		Formatted prompt string
	"""
	return LOGIN_ELEMENT_IDENTIFICATION_PROMPT.format(html_content=html_content)


def get_login_verification_prompt(
	current_url: str, page_title: str, html_content: str
) -> str:
	"""Get the login verification prompt with page state.

	Args:
		current_url: Current page URL
		page_title: Current page title
		html_content: HTML snippet from current page

	Returns:
		Formatted prompt string
	"""
	return LOGIN_VERIFICATION_PROMPT.format(
		current_url=current_url, page_title=page_title, html_content=html_content
	)
