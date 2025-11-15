"""OpenAI API service for AI-powered element identification."""

import json
from typing import Any

from openai import OpenAI

from src.config import settings


class OpenAIService:
	"""Service for interacting with OpenAI API."""

	def __init__(self):
		"""Initialize OpenAI client."""
		self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
		self.mini_model = settings.OPENAI_MINI_MODEL

	def identify_login_elements(self, html_content: str) -> dict[str, Any]:
		"""Use AI to identify login form elements in HTML.

		Args:
			html_content: The HTML DOM content to analyze

		Returns:
			Dictionary with element selectors and metadata
		"""
		from src.prompts.login_element_identification import (
			get_login_identification_prompt,
		)

		prompt = get_login_identification_prompt(html_content)

		raw_content = None
		try:
			response = self.client.chat.completions.create(
				model=self.mini_model,
				messages=[
					{
						"role": "system",
						"content": "You are an expert at analyzing HTML and identifying login form elements. Always respond with valid JSON only.",
					},
					{"role": "user", "content": prompt},
				],
				temperature=0.1,  # Low temperature for consistent outputs
				response_format={"type": "json_object"},
			)

			raw_content = response.choices[0].message.content
			print(f"🔍 Raw OpenAI Response (first 500 chars):\n{raw_content[:500]}\n")

			result = json.loads(raw_content)
			return {
				"success": True,
				"data": result,
				"tokens_used": response.usage.total_tokens,
			}

		except json.JSONDecodeError as e:
			print(f"❌ JSON Decode Error: {e}")
			if raw_content:
				print(f"Raw content (first 1000 chars): {raw_content[:1000]}")
			return {
				"success": False,
				"error": f"Invalid JSON response: {str(e)}",
				"data": None,
				"tokens_used": 0,
			}
		except Exception as e:
			print(f"❌ OpenAI API Error: {e}")
			import traceback

			traceback.print_exc()
			return {
				"success": False,
				"error": str(e),
				"data": None,
				"tokens_used": 0,
			}

	def verify_login_success(
		self, current_url: str, page_title: str, html_content: str
	) -> dict[str, Any]:
		"""Use AI to verify if login was successful.

		Args:
			current_url: Current page URL
			page_title: Current page title
			html_content: HTML snippet from current page

		Returns:
			Dictionary with verification result and metadata
		"""
		from src.prompts.login_element_identification import get_login_verification_prompt

		prompt = get_login_verification_prompt(current_url, page_title, html_content)

		try:
			response = self.client.chat.completions.create(
				model=self.mini_model,
				messages=[
					{
						"role": "system",
						"content": "You are an expert at verifying login success by analyzing page state. Always respond with valid JSON only.",
					},
					{"role": "user", "content": prompt},
				],
				temperature=0.1,
				response_format={"type": "json_object"},
			)

			result = json.loads(response.choices[0].message.content)
			return {
				"success": True,
				"data": result,
				"tokens_used": response.usage.total_tokens,
			}

		except Exception as e:
			return {
				"success": False,
				"error": str(e),
				"data": None,
				"tokens_used": 0,
			}


# Singleton instance
openai_service = OpenAIService()
