from langgraph.graph import StateGraph, START, END
from state import AgentState

# Import your agent functions
# Ensure these filenames and function names match your actual files!
from agents.sanity import run_sanity_agent
from agents.arch import run_arch_agent
from agents.style import run_style_agent
from agents.test_gen import run_test_agent

# --- 1. Evaluator Node ---
def orchestrator_evaluator(state: AgentState):
    """
    Final node that aggregates all agent reports.
    It decides if the PR is safe to merge.
    """
    reports = state.get("reports", [])
    
    # Logic: If any agent found a CRITICAL issue, deployment_ready = False
    is_ready = True
    if any(r.get("severity") == "CRITICAL" for r in reports):
        is_ready = False

    # Create a nice Markdown summary for the GitHub Comment
    summary = "### 📋 AI Agent Review Summary\n\n"
    summary += "| Agent | Status | Severity | Findings |\n"
    summary += "| :--- | :--- | :--- | :--- |\n"
    
    for r in reports:
        status_icon = "✅" if r['status'] == "PASS" else "❌"
        summary += f"| **{r['agent']}** | {status_icon} {r['status']} | {r['severity']} | {r['findings']} |\n"

    summary += "\n---\n"
    if is_ready:
        summary += "🚀 **Verdict:** No critical issues found. Ready for human review."
    else:
        summary += "⚠️ **Verdict:** Critical issues detected. Please fix before merging."

    return {
        "final_summary": summary, 
        "deployment_ready": is_ready
    }

# --- 2. Build the Graph ---
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("sanity_agent", run_sanity_agent)
workflow.add_node("arch_agent", run_arch_agent)
workflow.add_node("style_agent", run_style_agent)
workflow.add_node("test_agent", run_test_agent)
workflow.add_node("evaluator", orchestrator_evaluator)

# # Define the Flow
# # Start: Run all 4 agents in parallel
# workflow.add_edge(START, "sanity_agent")
# workflow.add_edge(START, "arch_agent")
# workflow.add_edge(START, "style_agent")
# workflow.add_edge(START, "test_agent")

# # End: All agents must finish, then move to the Evaluator
# workflow.add_edge("sanity_agent", "evaluator")
# workflow.add_edge("arch_agent", "evaluator")
# workflow.add_edge("style_agent", "evaluator")
# workflow.add_edge("test_agent", "evaluator")

# # Close the loop
# workflow.add_edge("evaluator", END)

# 1. Define the flow as a single chain
# Start -> Sanity -> Arch -> Style -> Test -> Evaluator -> End
workflow.add_edge(START, "sanity_agent")
workflow.add_edge("sanity_agent", "arch_agent")
workflow.add_edge("arch_agent", "style_agent")
workflow.add_edge("style_agent", "test_agent")
workflow.add_edge("test_agent", "evaluator")
workflow.add_edge("evaluator", END)

# Compile the graph
app = workflow.compile()