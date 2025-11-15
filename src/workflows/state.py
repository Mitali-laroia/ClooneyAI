"""State definitions for LangGraph workflows."""

from typing import TypedDict


class CloneState(TypedDict):
	"""State for the website cloning workflow."""

	url: str
	status: str
	error: str | None
	dom: str | None
	dom_simplified: str | None
	css: str | None
	output_file: str | None
	screenshots: dict[str, str] | None  # viewport -> file path mapping
