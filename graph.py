from langgraph.graph import StateGraph, START, END
from state import AgentState
from agents.sanity import run_sanity_agent
from agents.arch import run_arch_agent
from agents.style import run_style_agent
from agents.test_gen import run_test_agent
import logging

# Set httpx logging to WARNING to hide the POST/200 OK info messages
logging.getLogger("httpx").setLevel(logging.WARNING)

# --- 🚦 STEP 0: Entry Router ---
def smart_router(state: AgentState):
    """Skips technical agents for non-code changes (Docs/Assets)."""
    print("\n--- 🚦 ENTRY ROUTING ---")
    diff = state.get("pr_diff", "").lower()
    
    code_extensions = [".dart", ".py", ".js", ".kt", ".swift"]
    if not any(ext in diff for ext in code_extensions):
        print("📝 Non-code change. Skipping to Evaluator.")
        return "evaluator"
    
    return "sanity_agent"

# --- 🚦 STEP 3.5: UI-Test Router ---
def ui_test_router(state: AgentState):
    """Skips Test Agent if changes are strictly UI/Widget related."""
    print("\n--- 🚦 TEST ROUTING ---")
    diff = state.get("pr_diff", "")
    
    # Folders that require logic/unit testing
    logic_paths = ["lib/logic/", "lib/src/application/bloc/", "lib/providers/"]
    
    needs_tests = any(path in diff for path in logic_paths)
    
    if not needs_tests:
        print("🎨 UI/Widget changes only. Skipping Test Agent.")
        return "evaluator"
    
    print("🧠 Logic changes detected. Routing to Test Agent.")
    return "test_agent"

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

# --- 🛠️ STEP 5: Evaluator (With Table Fix) ---
def orchestrator_evaluator(state: AgentState):
    print("\n--- 🔍 STEP 5: Evaluator ---") 
    reports = state.get("reports", [])
    
    # Helper for Hybrid Access (Dict or Pydantic)
    def get_field(obj, field_name, default=""):
        if isinstance(obj, dict):
            return obj.get(field_name, default)
        return getattr(obj, field_name, default)

    summary = "### 📋 AI Agent Review Summary\n\n"
    
    if not reports:
        summary += "✅ **No technical code changes detected.** Logic checks skipped.\n"
        return {"final_summary": summary, "deployment_ready": True}

    summary += "| Agent | Status | Severity | Findings |\n"
    summary += "| :--- | :--- | :--- | :--- |\n"
    
    is_ready = True
    for r in reports:
        if not r: continue
        
        # 1. Clean data for Markdown Table Stability
        agent_name = get_field(r, "agent", "Unknown")
        severity = get_field(r, "severity", "LOW")
        
        # CRITICAL: Replace newlines with <br> and escape pipes to prevent displacement
        raw_findings = get_field(r, "findings", "N/A")
        clean_findings = raw_findings.replace("\n", "<br>").replace("|", "\\|")
        
        raw_status = str(get_field(r, 'status', 'UNKNOWN')).upper()
        status_display = "❌ **FAIL**" if "FAIL" in raw_status else "✅ **PASS**"
        
        if severity == "CRITICAL":
            is_ready = False
            
        summary += f"| {agent_name} | {status_display} | {severity} | {clean_findings} |\n"
    
    summary += "\n---\n"
    summary += "### 🚀 **Verdict: Ready**" if is_ready else "### 🛑 **Verdict: Critical Issues Found**"
    
    return {"final_summary": summary, "deployment_ready": is_ready}

# --- 🏗️ BUILD THE GRAPH ---
workflow = StateGraph(AgentState)

# Nodes
workflow.add_node("sanity_agent", sanity_node)
workflow.add_node("arch_agent", arch_node)
workflow.add_node("style_agent", style_node)
workflow.add_node("test_agent", test_node)
workflow.add_node("evaluator", orchestrator_evaluator)

# Conditional Edges
workflow.add_conditional_edges(
    START,
    smart_router,
    {"sanity_agent": "sanity_agent", "evaluator": "evaluator"}
)

workflow.add_edge("sanity_agent", "arch_agent")
workflow.add_edge("arch_agent", "style_agent")

workflow.add_conditional_edges(
    "style_agent",
    ui_test_router,
    {"test_agent": "test_agent", "evaluator": "evaluator"}
)

workflow.add_edge("test_agent", "evaluator")
workflow.add_edge("evaluator", END)

app = workflow.compile()