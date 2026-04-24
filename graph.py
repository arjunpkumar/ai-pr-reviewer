from langgraph.graph import StateGraph, START, END
from state import AgentState
import operator

# Import your agent functions
from agents.sanity import run_sanity_agent
from agents.arch import run_arch_agent
from agents.style import run_style_agent
from agents.test_gen import run_test_agent

# --- DIAGNOSTIC NODE WRAPPERS ---
# These wrappers print exactly what is happening between agents

def sanity_node(state: AgentState):
    print("\n--- 🔍 STEP 1: Sanity Agent ---")
    if not state.get("pr_diff"):
        print("❌ CRITICAL: Sanity Agent received NO diff!")
    result = run_sanity_agent(state)
    print(f"✅ Sanity Finished. Reports returned: {len(result.get('reports', []))}")
    return result

def arch_node(state: AgentState):
    print("\n--- 🔍 STEP 2: Architecture Agent ---")
    if not state.get("pr_diff"):
        print("❌ CRITICAL: Arch Agent received NO diff! (The previous agent dropped it)")
    result = run_arch_agent(state)
    print(f"✅ Arch Finished. Reports returned: {len(result.get('reports', []))}")
    return result

def style_node(state: AgentState):
    print("\n--- 🔍 STEP 3: Style Agent ---")
    if not state.get("pr_diff"):
        print("❌ CRITICAL: Style Agent received NO diff!")
    result = run_style_agent(state)
    print(f"✅ Style Finished. Reports returned: {len(result.get('reports', []))}")
    return result

def test_node(state: AgentState):
    print("\n--- 🔍 STEP 4: Test Agent ---")
    if not state.get("pr_diff"):
        print("❌ CRITICAL: Test Agent received NO diff!")
    result = run_test_agent(state)
    print(f"✅ Test Finished. Reports returned: {len(result.get('reports', []))}")
    return result

# --- 1. Evaluator Node ---
def orchestrator_evaluator(state: AgentState):
    print("\n--- 🔍 STEP 5: Evaluator ---") 
    reports = state.get("reports")
    
    # This is likely where the 'NoneType' error is being triggered
    if reports is None:
        print("❌ ERROR: 'reports' is None in the Evaluator state!")
        return {"final_summary": "Error: Reports were lost.", "deployment_ready": False}

    is_ready = True
    if any(r.get("severity") == "CRITICAL" for r in reports if r):
        is_ready = False

    summary = "### 📋 AI Agent Review Summary\n\n"
    summary += "| Agent | Status | Severity | Findings |\n"
    summary += "| :--- | :--- | :--- | :--- |\n"
    
    for r in reports:
        if not r: continue
        raw_status = r.get('status', 'UNKNOWN').replace(":", "").strip().upper()
        status_display = "❌ **FAIL**" if "FAIL" in raw_status else "✅ **PASS**"
        summary += f"| {r['agent']} | {status_display} | {r['severity']} | {r['findings']} |\n"
    
    summary += "\n---\n"
    summary += "### 🚀 Verdict: Ready" if is_ready else "### 🛑 Verdict: Critical Issues"
    
    return {
        "final_summary": summary, 
        "deployment_ready": is_ready
    }

# --- 2. Build the Graph ---
workflow = StateGraph(AgentState)

# Add Nodes (Using our diagnostic wrappers)
workflow.add_node("sanity_agent", sanity_node)
workflow.add_node("arch_agent", arch_node)
workflow.add_node("style_agent", style_node)
workflow.add_node("test_agent", test_node)
workflow.add_node("evaluator", orchestrator_evaluator)

# Define the Flow
workflow.add_edge(START, "sanity_agent")
workflow.add_edge("sanity_agent", "arch_agent")
workflow.add_edge("arch_agent", "style_agent")
workflow.add_edge("style_agent", "test_agent")
workflow.add_edge("test_agent", "evaluator")
workflow.add_edge("evaluator", END)

app = workflow.compile()