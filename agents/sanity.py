from state import AgentState, AgentReport # Import the TypedDict schema
from utils.llm_factory import SMART_MODEL

SANITY_PROMPT = """
You are a Senior Software Engineer specializing in Security and Bug Prevention. 
Your goal is to act as the first line of defense against functional regressions and vulnerabilities.

CRITICAL RULE: You must analyze the DIFF provided. 

If the DIFF contains:
1. Empty classes or "Blank" pages with no logic.
2. Syntax errors or missing imports.
3. Hardcoded secrets/keys.
4. Code that doesn't match the PR description.

You MUST set STATUS to 'FAIL'. Do not be polite. 
If the diff is truly empty, report 'FAIL' because there is nothing to merge.

Output Format (JSON):
{
  "agent": "Sanity",
  "status": "PASS/FAIL",
  "findings": "List specific issues.",
  "severity": "CRITICAL/MEDIUM/LOW"
}
"""

def run_sanity_agent(state: AgentState):
    # Specify the TypedDict 'AgentReport' instead of 'dict' 
    # to fix the signature error
    structured_llm = SMART_MODEL.with_structured_output(AgentReport)
    
    response = structured_llm.invoke([
        ("system", SANITY_PROMPT),
        ("human", f"PR Description: {state['pr_description']}\n\nDiff: {state['pr_diff']}")
    ])
    
    # Ensure 'agent' is explicitly set in case the LLM forgets
    response["agent"] = "Sanity"
    
    return {"reports": [response]}