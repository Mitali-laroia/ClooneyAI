"""Browser-based login automation with AI-guided element identification."""

import asyncio
import json
from typing import Any

from playwright.async_api import Page, async_playwright

from src.config import settings
from src.services.openai_service import openai_service


class LoginError(Exception):
	"""Custom exception for login failures."""

	pass


async def ai_guided_login(
	url: str, email: str | None = None, password: str | None = None, max_attempts: int = 3
) -> dict[str, Any]:
	"""Perform AI-guided login using OpenAI to identify form elements.

	Args:
		url: The login page URL
		email: Email/username (defaults to settings.ASANA_EMAIL_ID)
		password: Password (defaults to settings.ASANA_PASSWORD)
		max_attempts: Maximum number of login attempts

	Returns:
		Dictionary with login result and metadata

	Raises:
		LoginError: If login fails after max attempts
	"""
	# Use credentials from settings if not provided
	if email is None:
		email = settings.ASANA_EMAIL_ID
	if password is None:
		password = settings.ASANA_PASSWORD

	if not email or not password:
		raise LoginError("Email and password must be provided or set in environment")

	async with async_playwright() as p:
		browser = await p.chromium.launch(headless=False)  # Visible for debugging
		context = await browser.new_context(
			viewport={"width": 1920, "height": 1080}
		)
		page = await context.new_page()

		try:
			print(f"🌐 Navigating to login page: {url}")
			await page.goto(url, wait_until="domcontentloaded", timeout=60000)
			await page.wait_for_timeout(2000)  # Let page fully load

			for attempt in range(1, max_attempts + 1):
				print(f"\n🔄 Login attempt {attempt}/{max_attempts}")

				# Step 1: Get current page HTML
				print("📄 Extracting page HTML...")
				html_content = await page.content()

				# Step 2: Use AI to identify login elements
				print("🤖 Using AI to identify login form elements...")
				identification_result = openai_service.identify_login_elements(
					html_content
				)

				if not identification_result["success"]:
					print(
						f"❌ AI identification failed: {identification_result.get('error')}"
					)
					if attempt < max_attempts:
						await asyncio.sleep(2)
						continue
					raise LoginError(
						f"Failed to identify login elements: {identification_result.get('error')}"
					)

				selectors = identification_result["data"]
				print(f"✅ Elements identified (confidence: {selectors.get('confidence')})")
				print(f"   📧 Email selector: {selectors.get('email_selector')}")
				print(f"   🔒 Password selector: {selectors.get('password_selector')}")
				print(f"   🔘 Submit selector: {selectors.get('submit_selector')}")
				print(f"   💭 Reasoning: {selectors.get('reasoning')}")
				print(
					f"   🎯 Tokens used: {identification_result.get('tokens_used', 0)}"
				)

				# Step 3: Fill in credentials
				try:
					print("\n📝 Filling in credentials...")

					# Fill email
					email_selector = selectors.get("email_selector")
					if not email_selector:
						raise LoginError("No email selector identified")

					await page.fill(email_selector, email)
					print(f"   ✅ Email entered")
					await asyncio.sleep(0.5)

					# Fill password
					password_selector = selectors.get("password_selector")
					if not password_selector:
						raise LoginError("No password selector identified")

					await page.fill(password_selector, password)
					print(f"   ✅ Password entered")
					await asyncio.sleep(0.5)

					# Click submit button
					submit_selector = selectors.get("submit_selector")
					if not submit_selector:
						raise LoginError("No submit button selector identified")

					print("\n🖱️  Clicking login button...")
					await page.click(submit_selector)
					print("   ✅ Login button clicked")

					# Wait for navigation or error
					await page.wait_for_timeout(3000)

				except Exception as e:
					print(f"❌ Error during form interaction: {str(e)}")
					if attempt < max_attempts:
						print("   Retrying with AI re-analysis...")
						await asyncio.sleep(2)
						continue
					raise LoginError(f"Failed to interact with login form: {str(e)}")

				# Step 4: Verify login success
				print("\n🔍 Verifying login success...")
				current_url = page.url
				page_title = await page.title()
				verification_html = await page.content()

				# Get a snippet of HTML (first 5000 chars to save tokens)
				html_snippet = verification_html[:5000]

				verification_result = openai_service.verify_login_success(
					current_url, page_title, html_snippet
				)

				if not verification_result["success"]:
					print(
						f"❌ AI verification failed: {verification_result.get('error')}"
					)
					if attempt < max_attempts:
						await asyncio.sleep(2)
						continue
					raise LoginError(
						f"Failed to verify login: {verification_result.get('error')}"
					)

				verification = verification_result["data"]
				print(
					f"📊 Verification result (confidence: {verification.get('confidence')})"
				)
				print(f"   {'✅' if verification.get('login_successful') else '❌'} Login successful: {verification.get('login_successful')}")
				print(f"   💭 Reasoning: {verification.get('reasoning')}")
				print(
					f"   🎯 Tokens used: {verification_result.get('tokens_used', 0)}"
				)

				if verification.get("login_successful"):
					print("\n🎉 Login successful!")

					# Take screenshot of logged-in state
					screenshot_path = "output/screenshots/login_success.png"
					await page.screenshot(path=screenshot_path, full_page=True)
					print(f"📸 Screenshot saved: {screenshot_path}")

					return {
						"success": True,
						"url": current_url,
						"page_title": page_title,
						"screenshot": screenshot_path,
						"attempts": attempt,
						"total_tokens": identification_result.get("tokens_used", 0)
						+ verification_result.get("tokens_used", 0),
						"page": page,  # Return page for further use
						"browser": browser,
						"context": context,
					}

				else:
					print(
						f"❌ Login failed: {verification.get('suggested_next_action')}"
					)
					if attempt < max_attempts:
						print("   Retrying...")
						await asyncio.sleep(2)
						continue

			# All attempts failed
			await browser.close()
			raise LoginError(
				f"Login failed after {max_attempts} attempts. Last reason: {verification.get('reasoning')}"
			)

		except Exception as e:
			await browser.close()
			raise LoginError(f"Login process failed: {str(e)}")


async def cleanup_login_session(
	browser: Any = None, context: Any = None, page: Any = None
) -> None:
	"""Clean up browser resources.

	Args:
		browser: Playwright browser instance
		context: Playwright context instance
		page: Playwright page instance
	"""
	try:
		if page:
			await page.close()
		if context:
			await context.close()
		if browser:
			await browser.close()
		print("✅ Browser session cleaned up")
	except Exception as e:
		print(f"⚠️  Warning: Error during cleanup: {str(e)}")
