from utils.llm_factory import SMART_MODEL
from state import AgentState, AgentReport

STYLE_PROMPT = """
You are a Code Quality & DX Engineer. Your goal is maintainability and consistency.

Focus Areas:
1. Documentation: Are new functions or classes missing docstrings?
2. Naming: Are variable names descriptive or confusing? (e.g., PascalCase for classes, camelCase for variables).
3. Readability: Is the logic too complex or deeply nested?

Output Format (JSON):
{
  "agent": "Style",
  "status": "PASS/WARNING",
  "findings": "List documentation gaps or naming inconsistencies.",
  "severity": "LOW"
}
"""

def run_style_agent(state: AgentState):
    # SPECIFIC TYPE FIX: Swap 'dict' for 'AgentReport'
    structured_llm = SMART_MODEL.with_structured_output(AgentReport)
    
    response = structured_llm.invoke([
        ("system", STYLE_PROMPT),
        ("human", f"Diff: {state['pr_diff']}")
    ])
    
    # Force the agent name in case the model hallucinates a different one
    response["agent"] = "Style"
    
    return {
        "reports": [response],
        "pr_diff": state["pr_diff"],
        "pr_description": state["pr_description"]
    }