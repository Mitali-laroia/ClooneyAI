"""Main cloning workflow using LangGraph."""

from langgraph.graph import END, START, StateGraph

from src.workflows.nodes import scraper_node_sync
from src.workflows.state import CloneState


def create_clone_workflow() -> StateGraph:
	"""Create the main cloning workflow graph.

	Returns:
		StateGraph: Compiled workflow graph
	"""
	# Initialize the graph with the state schema
	workflow = StateGraph(CloneState)

	# Add nodes
	workflow.add_node("scraper", scraper_node_sync)

	# Add edges
	workflow.add_edge(START, "scraper")
	workflow.add_edge("scraper", END)

	# Compile the graph
	return workflow.compile()


# Create the compiled graph instance
clone_graph = create_clone_workflow()
