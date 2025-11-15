"""State definitions for LangGraph workflows."""

from typing import TypedDict


class CloneState(TypedDict):
	"""State for the website cloning workflow."""

	url: str
	status: str
	error: str | None
