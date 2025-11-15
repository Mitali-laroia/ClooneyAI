"""Main cloning workflow using LangGraph."""

from langgraph.graph import END, START, StateGraph

from src.workflows.nodes import login_node_sync, openai_node_sync
from src.workflows.state import CloneState


def should_continue(state: CloneState) -> str:
	"""Determine which node to go to next based on current step.

	Args:
		state: Current workflow state

	Returns:
		Name of next node: "login", "openai", or "end"
	"""
	step = state["current_step"]
	iteration = state["iteration_count"]

	# Check max iterations
	if iteration >= 10:
		print("\n⚠️  Max iterations (10) reached")
		return "end"

	# Check if completed or failed
	if step == "completed":
		print("\n✅ Login completed successfully")
		return "end"

	if step == "failed":
		print("\n❌ Login failed")
		return "end"

	# Steps that need AI analysis
	if step in [
		"find_email",
		"find_email_continue",
		"find_password",
		"find_submit",
		"verify_login",
	]:
		return "openai"

	# Steps that need browser action
	if step in [
		"init",
		"enter_email",
		"click_email_continue",
		"enter_password",
		"click_submit",
	]:
		return "login"

	# Unknown step, end
	print(f"\n⚠️  Unknown step: {step}")
	return "end"


def create_clone_workflow() -> StateGraph:
	"""Create the main cloning workflow graph with iterative login.

	Flow:
		START -> login (init)
		login <-> openai (iterative, max 10 times)
		-> END

	Returns:
		StateGraph: Compiled workflow graph
	"""
	# Initialize the graph with the state schema
	workflow = StateGraph(CloneState)

	# Add nodes
	workflow.add_node("login", login_node_sync)
	workflow.add_node("openai", openai_node_sync)

	# Start with login node (initialization)
	workflow.add_edge(START, "login")

	# Conditional edges for iteration
	workflow.add_conditional_edges(
		"login", should_continue, {"login": "login", "openai": "openai", "end": END}
	)

	workflow.add_conditional_edges(
		"openai", should_continue, {"login": "login", "openai": "openai", "end": END}
	)

	# Compile the graph
	return workflow.compile()


# Create the compiled graph instance
clone_graph = create_clone_workflow()
