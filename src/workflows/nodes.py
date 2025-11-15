"""LangGraph workflow nodes for iterative login process."""

import asyncio
import json

from playwright.async_api import Page, async_playwright

from src.config import settings
from src.prompts.iterative_login_prompts import (
	get_find_email_continue_prompt,
	get_find_email_prompt,
	get_find_password_prompt,
	get_find_submit_prompt,
	get_verify_login_prompt,
)
from src.services.openai_service import openai_service
from src.workflows.state import CloneState


async def extract_page_css(page: Page) -> str:
	"""Extract all CSS from the current page including inline and external stylesheets.

	Args:
		page: Playwright page object

	Returns:
		Combined CSS content as string
	"""
	try:
		css_content = await page.evaluate("""
			() => {
				let css = '';

				// Get all style tags
				const styleTags = document.querySelectorAll('style');
				styleTags.forEach((tag, index) => {
					css += `\\n/* <style> tag ${index + 1} */\\n`;
					css += tag.textContent + '\\n';
				});

				// Get all link stylesheets
				const linkTags = document.querySelectorAll('link[rel="stylesheet"]');
				linkTags.forEach((link, index) => {
					css += `\\n/* Linked stylesheet ${index + 1}: ${link.href} */\\n`;
					// Note: We can't access external CSS content due to CORS, but we log the URL
				});

				// Get inline styles (limited to important elements)
				const elementsWithStyle = document.querySelectorAll('[style]');
				if (elementsWithStyle.length > 0) {
					css += `\\n/* Inline styles found on ${elementsWithStyle.length} elements */\\n`;
					// Sample first 10 elements with inline styles
					Array.from(elementsWithStyle).slice(0, 10).forEach((el, index) => {
						css += `${el.tagName.toLowerCase()}: ${el.getAttribute('style')}\\n`;
					});
				}

				return css;
			}
		""")
		return css_content
	except Exception as e:
		print(f"⚠️  Failed to extract CSS: {e}")
		return ""


async def login_node(state: CloneState) -> CloneState:
	"""Execute login actions based on current step.

	This node performs browser automation based on the current step.
	"""
	step = state["current_step"]
	iteration = state["iteration_count"]

	print(f"\n{'='*60}")
	print(f"🔄 Iteration {iteration}/10 - Step: {step}")
	print(f"{'='*60}")

	try:
		# Initialize browser if needed
		if step == "init":
			print("🌐 Initializing browser and navigating to login page...")

			# Don't use context manager - keep browser alive
			playwright = await async_playwright().start()
			browser = await playwright.chromium.launch(headless=False)
			context = await browser.new_context(viewport={"width": 1920, "height": 1080})
			page = await context.new_page()

			# Navigate to login page
			await page.goto(state["url"], wait_until="domcontentloaded", timeout=60000)
			print("⏳ Waiting 3 seconds for page to fully load...")
			await page.wait_for_timeout(3000)

			# Get current state
			current_dom = await page.content()
			current_css = await extract_page_css(page)
			current_url = page.url

			print(f"✅ Page loaded: {current_url}")

			# Store browser session (note: these won't serialize, use immediately)
			return {
				**state,
				"current_step": "find_email",
				"iteration_count": iteration + 1,
				"last_action": "Initialized browser and loaded login page",
				"browser_session": {
					"playwright": playwright,
					"browser": browser,
					"context": context,
					"page": page,
				},
				"current_dom": current_dom,
				"current_css": current_css,
				"current_page_url": current_url,
				"error": None,
			}

		# Get browser session
		browser_session = state.get("browser_session")
		if not browser_session or not browser_session.get("page"):
			return {
				**state,
				"current_step": "failed",
				"error": "Browser session lost",
			}

		page = browser_session["page"]

		# Execute based on current step
		if step == "enter_email":
			print("📧 Entering email address...")
			ai_guidance = state.get("ai_guidance", {})
			selector = ai_guidance.get("selector")

			if not selector:
				return {
					**state,
					"current_step": "failed",
					"error": "No email selector from AI",
				}

			try:
				# Try to fill with timeout
				print(f"   Filling email field with selector: {selector}")
				await page.fill(selector, state["email"], timeout=5000)
				print(f"✅ Email entered using selector: {selector}")
			except Exception as e:
				error_msg = str(e)
				print(f"⚠️  Fill failed: {error_msg}")
				
				# Retry with AI if under retry limit
				retry_count = state.get("step_retry_count", 0)
				if retry_count < 3:
					print(f"🔄 Retrying with different selector... (attempt {retry_count + 1}/3)")
					return {
						**state,
						"current_step": "find_email",  # Go back to AI
						"last_error": f"Previous selector '{selector}' failed: {error_msg}",
						"step_retry_count": retry_count + 1,
						"iteration_count": iteration + 1,
					}
				else:
					# Try keyboard typing as last resort
					print(f"⚠️  Trying keyboard fallback...")
					try:
						await page.focus(selector, timeout=5000)
						await page.keyboard.type(state["email"])
						print(f"✅ Email typed using selector: {selector}")
					except Exception as e2:
						return {
							**state,
							"current_step": "failed",
							"error": f"Failed to enter email after 3 attempts: {str(e2)}",
						}

			print("⏳ Waiting 3 seconds...")
			await page.wait_for_timeout(3000)

			# Get updated DOM and CSS
			current_dom = await page.content()
			current_css = await extract_page_css(page)
			current_url = page.url

			return {
				**state,
				"current_step": "find_email_continue",
				"iteration_count": iteration + 1,
				"last_action": f"Entered email using selector: {selector}",
				"current_dom": current_dom,
				"current_css": current_css,
				"current_page_url": current_url,
			}

		elif step == "click_email_continue":
			print("🖱️  Clicking Continue button after email...")
			ai_guidance = state.get("ai_guidance", {})
			selector = ai_guidance.get("selector")

			if not selector:
				return {
					**state,
					"current_step": "failed",
					"error": "No continue button selector from AI",
				}

			try:
				print(f"   Clicking continue button: {selector}")
				await page.click(selector, timeout=5000)
				print(f"✅ Continue button clicked using selector: {selector}")
			except Exception as e:
				error_msg = str(e)
				print(f"❌ Click failed: {error_msg}")

				# Retry with AI if under retry limit
				retry_count = state.get("step_retry_count", 0)
				if retry_count < 3:
					print(f"🔄 Retrying... (attempt {retry_count + 1}/3)")
					return {
						**state,
						"current_step": "find_email_continue",  # Go back to AI
						"last_error": f"Previous selector '{selector}' failed: {error_msg}",
						"step_retry_count": retry_count + 1,
						"iteration_count": iteration + 1,
					}
				else:
					# Max retries reached, fail
					return {
						**state,
						"current_step": "failed",
						"error": f"Failed to click continue button after 3 attempts: {error_msg}",
					}

			print("⏳ Waiting 3 seconds...")
			await page.wait_for_timeout(3000)

			# Get updated DOM and CSS
			current_dom = await page.content()
			current_css = await extract_page_css(page)
			current_url = page.url

			return {
				**state,
				"current_step": "find_password",
				"iteration_count": iteration + 1,
				"last_action": f"Clicked continue button: {selector}",
				"current_dom": current_dom,
				"current_css": current_css,
				"current_page_url": current_url,
				"last_error": None,  # Clear error on success
				"step_retry_count": 0,  # Reset retry count for next step
			}

		elif step == "enter_password":
			print("🔒 Entering password...")
			ai_guidance = state.get("ai_guidance", {})
			selector = ai_guidance.get("selector")

			if not selector:
				return {
					**state,
					"current_step": "failed",
					"error": "No password selector from AI",
				}

			try:
				print(f"   Filling password field with selector: {selector}")
				await page.fill(selector, state["password"], timeout=5000)
				print(f"✅ Password entered using selector: {selector}")
			except Exception as e:
				print(f"⚠️  Fill failed, trying type instead: {e}")
				await page.focus(selector, timeout=5000)
				await page.keyboard.type(state["password"])
				print(f"✅ Password typed using selector: {selector}")

			print("⏳ Waiting 3 seconds...")
			await page.wait_for_timeout(3000)

			# Get updated DOM and CSS
			current_dom = await page.content()
			current_css = await extract_page_css(page)
			current_url = page.url

			return {
				**state,
				"current_step": "find_submit",
				"iteration_count": iteration + 1,
				"last_action": f"Entered password using selector: {selector}",
				"current_dom": current_dom,
				"current_css": current_css,
				"current_page_url": current_url,
			}

		elif step == "click_submit":
			print("🖱️  Clicking login/submit button...")
			ai_guidance = state.get("ai_guidance", {})
			selector = ai_guidance.get("selector")

			if not selector:
				return {
					**state,
					"current_step": "failed",
					"error": "No submit button selector from AI",
				}

			try:
				print(f"   Clicking submit button: {selector}")
				await page.click(selector, timeout=5000)
				print(f"✅ Submit button clicked using selector: {selector}")
			except Exception as e:
				print(f"❌ Click failed: {e}")
				return {
					**state,
					"current_step": "failed",
					"error": f"Failed to click submit button: {str(e)}",
				}

			print("⏳ Waiting 5 seconds for login to process...")
			await page.wait_for_timeout(5000)

			# Get updated DOM and CSS
			current_dom = await page.content()
			current_css = await extract_page_css(page)
			current_url = page.url

			# Take screenshot
			screenshot_path = "output/screenshots/after_login_click.png"
			await page.screenshot(path=screenshot_path, full_page=True)
			print(f"📸 Screenshot saved: {screenshot_path}")

			return {
				**state,
				"current_step": "verify_login",
				"iteration_count": iteration + 1,
				"last_action": f"Clicked submit button: {selector}",
				"current_dom": current_dom,
				"current_css": current_css,
				"current_page_url": current_url,
				"login_screenshot": screenshot_path,
			}

		else:
			# Unknown step
			return {
				**state,
				"current_step": "failed",
				"error": f"Unknown step: {step}",
			}

	except Exception as e:
		print(f"❌ Error in login_node: {str(e)}")
		import traceback

		traceback.print_exc()
		return {
			**state,
			"current_step": "failed",
			"error": f"Login node error: {str(e)}",
		}


async def openai_node(state: CloneState) -> CloneState:
	"""Use OpenAI to analyze page and provide guidance for next action.

	This node analyzes the current DOM and provides CSS selectors or verification.
	"""
	step = state["current_step"]
	current_dom = state.get("current_dom", "")
	current_css = state.get("current_css", "")
	current_url = state.get("current_page_url", "")
	iteration = state["iteration_count"]
	tokens_used = state["total_tokens_used"]

	print(f"\n🤖 AI Analysis for step: {step}")

	try:
		if step == "find_email":
			print("   Analyzing page to find email input...")
			try:
				prompt = get_find_email_prompt(current_dom, state.get("last_error"), current_css)
				print(f"   📡 Calling OpenAI API ({settings.OPENAI_MINI_MODEL})...")

				response = openai_service.client.chat.completions.create(
					model=settings.OPENAI_MINI_MODEL,
					messages=[
						{
							"role": "system",
							"content": "You are an expert at finding email input fields in HTML. Return only valid JSON.",
						},
						{"role": "user", "content": prompt},
					],
					temperature=0.1,
					response_format={"type": "json_object"},
					timeout=30.0,  # 30 second timeout
				)

				print(f"   ✅ Received response from OpenAI")
				result = json.loads(response.choices[0].message.content)
				tokens_used += response.usage.total_tokens

				print(f"   ✅ Found email selector: {result.get('selector')}")
				print(f"   Confidence: {result.get('confidence')}")
				print(f"   Reasoning: {result.get('reasoning')}")

				return {
					**state,
					"current_step": "enter_email",
					"ai_guidance": result,
					"total_tokens_used": tokens_used,
				}

			except Exception as e:
				print(f"   ❌ OpenAI API call failed: {str(e)}")
				import traceback
				traceback.print_exc()
				return {
					**state,
					"current_step": "failed",
					"error": f"AI analysis failed for find_email: {str(e)}",
					"total_tokens_used": tokens_used,
				}

		elif step == "find_email_continue":
			print("   Checking if password field is already visible or continue button exists...")

			# First check if password field is already visible
			browser_session = state.get("browser_session")
			if browser_session and browser_session.get("page"):
				page = browser_session["page"]
				try:
					# Check if password input is visible
					password_visible = await page.locator("input[type='password']").count()
					if password_visible > 0:
						print(f"   ✅ Password field already visible, skipping continue button")
						return {
							**state,
							"current_step": "find_password",
							"total_tokens_used": tokens_used,
							"ai_guidance": {"note": "Password field already visible"},
						}
				except Exception:
					pass

			# If no password field, look for continue button
			print("   Analyzing page to find email continue button...")
			try:
				prompt = get_find_email_continue_prompt(current_dom, state.get("last_error"), current_css)
				print(f"   📡 Calling OpenAI API ({settings.OPENAI_MINI_MODEL})...")

				response = openai_service.client.chat.completions.create(
					model=settings.OPENAI_MINI_MODEL,
					messages=[
						{
							"role": "system",
							"content": "You are an expert at finding continue/next buttons in HTML. Return only valid JSON.",
						},
						{"role": "user", "content": prompt},
					],
					temperature=0.1,
					response_format={"type": "json_object"},
					timeout=30.0,
				)

				print(f"   ✅ Received response from OpenAI")
				result = json.loads(response.choices[0].message.content)
				tokens_used += response.usage.total_tokens

				print(f"   ✅ Found continue selector: {result.get('selector')}")
				print(f"   Confidence: {result.get('confidence')}")
				print(f"   Reasoning: {result.get('reasoning')}")

				return {
					**state,
					"current_step": "click_email_continue",
					"ai_guidance": result,
					"total_tokens_used": tokens_used,
				}

			except Exception as e:
				print(f"   ❌ OpenAI API call failed: {str(e)}")
				import traceback
				traceback.print_exc()
				return {
					**state,
					"current_step": "failed",
					"error": f"AI analysis failed for find_email_continue: {str(e)}",
					"total_tokens_used": tokens_used,
				}

		elif step == "find_password":
			print("   Analyzing page to find password input...")
			try:
				prompt = get_find_password_prompt(current_dom, state.get("last_error"), current_css)
				print(f"   📡 Calling OpenAI API ({settings.OPENAI_MINI_MODEL})...")

				response = openai_service.client.chat.completions.create(
					model=settings.OPENAI_MINI_MODEL,
					messages=[
						{
							"role": "system",
							"content": "You are an expert at finding password input fields in HTML. Return only valid JSON.",
						},
						{"role": "user", "content": prompt},
					],
					temperature=0.1,
					response_format={"type": "json_object"},
					timeout=30.0,
				)

				print(f"   ✅ Received response from OpenAI")
				result = json.loads(response.choices[0].message.content)
				tokens_used += response.usage.total_tokens

				print(f"   ✅ Found password selector: {result.get('selector')}")
				print(f"   Confidence: {result.get('confidence')}")
				print(f"   Reasoning: {result.get('reasoning')}")

				return {
					**state,
					"current_step": "enter_password",
					"ai_guidance": result,
					"total_tokens_used": tokens_used,
				}

			except Exception as e:
				print(f"   ❌ OpenAI API call failed: {str(e)}")
				import traceback
				traceback.print_exc()
				return {
					**state,
					"current_step": "failed",
					"error": f"AI analysis failed for find_password: {str(e)}",
					"total_tokens_used": tokens_used,
				}

		elif step == "find_submit":
			print("   Analyzing page to find submit button...")
			try:
				prompt = get_find_submit_prompt(current_dom, state.get("last_error"), current_css)
				print(f"   📡 Calling OpenAI API ({settings.OPENAI_MINI_MODEL})...")

				response = openai_service.client.chat.completions.create(
					model=settings.OPENAI_MINI_MODEL,
					messages=[
						{
							"role": "system",
							"content": "You are an expert at finding submit buttons in HTML. Return only valid JSON.",
						},
						{"role": "user", "content": prompt},
					],
					temperature=0.1,
					response_format={"type": "json_object"},
					timeout=30.0,
				)

				print(f"   ✅ Received response from OpenAI")
				result = json.loads(response.choices[0].message.content)
				tokens_used += response.usage.total_tokens

				print(f"   ✅ Found submit selector: {result.get('selector')}")
				print(f"   Confidence: {result.get('confidence')}")
				print(f"   Reasoning: {result.get('reasoning')}")

				return {
					**state,
					"current_step": "click_submit",
					"ai_guidance": result,
					"total_tokens_used": tokens_used,
				}

			except Exception as e:
				print(f"   ❌ OpenAI API call failed: {str(e)}")
				import traceback
				traceback.print_exc()
				return {
					**state,
					"current_step": "failed",
					"error": f"AI analysis failed for find_submit: {str(e)}",
					"total_tokens_used": tokens_used,
				}

		elif step == "verify_login":
			print("   Verifying login success...")
			try:
				browser_session = state.get("browser_session")
				if browser_session and browser_session.get("page"):
					page = browser_session["page"]
					title = await page.title()
				else:
					title = "Unknown"

				prompt = get_verify_login_prompt(current_url, title, current_dom)
				print(f"   📡 Calling OpenAI API ({settings.OPENAI_MINI_MODEL})...")

				response = openai_service.client.chat.completions.create(
					model=settings.OPENAI_MINI_MODEL,
					messages=[
						{
							"role": "system",
							"content": "You are an expert at verifying login success. Return only valid JSON.",
						},
						{"role": "user", "content": prompt},
					],
					temperature=0.1,
					response_format={"type": "json_object"},
					timeout=30.0,
				)

				print(f"   ✅ Received response from OpenAI")
				result = json.loads(response.choices[0].message.content)
				tokens_used += response.usage.total_tokens

				print(f"   {'✅' if result.get('logged_in') else '❌'} Logged in: {result.get('logged_in')}")
				print(f"   Confidence: {result.get('confidence')}")
				print(f"   Reasoning: {result.get('reasoning')}")

				if result.get("logged_in"):
					return {
						**state,
						"current_step": "completed",
						"ai_guidance": result,
						"total_tokens_used": tokens_used,
						"login_successful": True,
						"login_url": current_url,
						"status": "logged_in",
					}
				else:
					# If confidence is low, might need to wait more
					if result.get("confidence") == "low":
						return {
							**state,
							"current_step": "verify_login",  # Try again
							"ai_guidance": result,
							"total_tokens_used": tokens_used,
						}
					else:
						return {
							**state,
							"current_step": "failed",
							"ai_guidance": result,
							"total_tokens_used": tokens_used,
							"login_successful": False,
							"error": f"Login verification failed: {result.get('reasoning')}",
							"status": "login_failed",
						}

			except Exception as e:
				print(f"   ❌ OpenAI API call failed: {str(e)}")
				import traceback
				traceback.print_exc()
				return {
					**state,
					"current_step": "failed",
					"error": f"AI analysis failed for verify_login: {str(e)}",
					"total_tokens_used": tokens_used,
				}

		else:
			return {
				**state,
				"error": f"Unknown step for AI analysis: {step}",
			}

	except Exception as e:
		print(f"❌ Error in openai_node: {str(e)}")
		import traceback

		traceback.print_exc()
		return {
			**state,
			"current_step": "failed",
			"error": f"AI analysis error: {str(e)}",
		}


# Global event loop for persistent browser session
_event_loop = None


def get_event_loop():
	"""Get or create a persistent event loop."""
	global _event_loop
	if _event_loop is None or _event_loop.is_closed():
		_event_loop = asyncio.new_event_loop()
		asyncio.set_event_loop(_event_loop)
	return _event_loop


async def cleanup_browser(state: CloneState) -> None:
	"""Clean up browser resources."""
	browser_session = state.get("browser_session")
	if browser_session:
		try:
			if browser_session.get("context"):
				await browser_session["context"].close()
			if browser_session.get("browser"):
				await browser_session["browser"].close()
			if browser_session.get("playwright"):
				await browser_session["playwright"].stop()
		except Exception as e:
			print(f"⚠️  Error during cleanup: {e}")


def cleanup_event_loop():
	"""Close the persistent event loop."""
	global _event_loop
	if _event_loop and not _event_loop.is_closed():
		_event_loop.close()
		_event_loop = None


# Synchronous wrappers
def login_node_sync(state: CloneState) -> CloneState:
	"""Sync wrapper for login node."""
	loop = get_event_loop()
	return loop.run_until_complete(login_node(state))


def openai_node_sync(state: CloneState) -> CloneState:
	"""Sync wrapper for openai node."""
	loop = get_event_loop()
	return loop.run_until_complete(openai_node(state))
