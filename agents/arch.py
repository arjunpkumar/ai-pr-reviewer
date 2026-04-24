from state import AgentState, AgentReport
from utils.llm_factory import SMART_MODEL
from typing import cast

ARCH_PROMPT = """
You are a Principal Software Architect. Review the following code diff for structural integrity.

Focus Areas:
1. SOLID Principles: Are any classes becoming too bloated?
2. Pattern Consistency: Does this follow standard design patterns (e.g., Repository, Bloc/Provider for Flutter)?
3. Dependency Direction: Is the business logic importing low-level implementation details?

Output Format (JSON): 
{
  "agent": "Architecture",
  "status": "PASS/FAIL",
  "findings": "Detail any architectural drift or pattern violations.",
  "severity": "CRITICAL/MEDIUM/LOW"
}
"""

def run_arch_agent(state: AgentState):
    # SPECIFIC TYPE FIX: Change 'dict' to 'AgentReport'
    structured_llm = SMART_MODEL.with_structured_output(AgentReport)
    
    raw_response = structured_llm.invoke([
        ("system", ARCH_PROMPT),
        ("human", f"Diff: {state['pr_diff']}")
    ])

     # 2. Force the type so Pylance sees .model_dump()
    response = cast(AgentReport, raw_response)
    
     # 3. Safely convert to dict
    response_dict = response.model_dump()
    response_dict["agent"] = "Architecture"
    
    return {
        "reports": [response],
        "pr_diff": state["pr_diff"],           
        "pr_description": state["pr_description"] 
    }