from utils.llm_factory import SMART_MODEL
from state import AgentState, AgentReport
from typing import cast

TEST_GEN_PROMPT = """
You are a Quality Assurance Automation Engineer. Your mission is to ensure code is testable and tested.

Focus Areas:
1. Missing Tests: Did the developer add new logic/files without adding corresponding tests in the 'test/' directory?
2. Testability: Is the code written in a way that is easy to test (e.g., dependency injection used)?
3. Logic Complexity: If the logic is complex (many if/else branches), does it have unit tests?

Output Format (JSON):
{
  "agent": "Testing",
  "status": "PASS/FAIL",
  "findings": "Identify if tests are missing or if the code is hard to test.",
  "severity": "MEDIUM/LOW"
}
"""

def run_test_agent(state: AgentState):
    # We use SMART_MODEL because judging 'testability' requires deeper reasoning
    structured_llm = SMART_MODEL.with_structured_output(AgentReport)
    
    raw_response = structured_llm.invoke([
        ("system", TEST_GEN_PROMPT),
        ("human", f"PR Description: {state['pr_description']}\n\nDiff: {state['pr_diff']}")
    ])

    response = cast(AgentReport, raw_response)

    # 3. Safely convert to dict
    response_dict = response.model_dump()
    response_dict["agent"] = "Testing"
  
    
    return {
        "reports": [response],
        "pr_diff": state["pr_diff"],
        "pr_description": state["pr_description"]
    }