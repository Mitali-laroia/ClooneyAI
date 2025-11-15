"""Main cloning workflow using LangGraph."""

from langgraph.graph import END, START, StateGraph

from src.workflows.state import CloneState


def create_clone_workflow() -> StateGraph:
	"""Create the main cloning workflow graph.

	Returns:
		StateGraph: Compiled workflow graph
	"""
	# Initialize the graph with the state schema
	workflow = StateGraph(CloneState)

	# Add edges from START to END
	workflow.add_edge(START, END)

	# Compile the graph
	return workflow.compile()


# Create the compiled graph instance
clone_graph = create_clone_workflow()
