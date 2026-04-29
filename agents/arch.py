import os
from typing import cast
from agents.base import safe_agent_call
from state import AgentState, AgentReport
from utils.llm_factory import SMART_MODEL
from utils.mcp.server import read_project_file
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage

# 1. Updated Prompt to encourage investigation
ARCH_PROMPT = """
You are a Principal Software Architect with the ability to explore the codebase.

Review the following code diff. If the diff doesn't provide enough context to verify 
architectural integrity (e.g., you need to see how a BLoC is provided or check 
an existing interface), use the 'read_project_file' tool.

Focus Areas:
1. SOLID Principles: Are classes becoming too bloated?
2. Pattern Consistency: Does this follow standard design patterns (BLoC/Provider)?
3. Dependency Direction: Does business logic depend on UI or low-level details?

FINAL OUTPUT RULE: Once you have finished your investigation, you must output 
your final report in this JSON format:
{
  "agent": "Architecture",
  "status": "PASS/FAIL",
  "findings": "Detail any architectural drift. Include which files you investigated.",
  "severity": "CRITICAL/MEDIUM/LOW"
}
"""

def run_arch_agent(state: AgentState):
    # 1. Bind tools to the model (Don't use with_structured_output yet)
    tools = {"read_project_file": read_project_file}
    llm_with_tools = SMART_MODEL.bind_tools([read_project_file])

    messages = [
        SystemMessage(content=ARCH_PROMPT),
        HumanMessage(content=f"Description: {state['pr_description']}\n\nDiff: {state['pr_diff']}")
    ]

    # 2. The Tool Loop (allows the AI to actually use the MCP server)
    for _ in range(3):  # Limit to 3 investigation steps
        response = cast(AIMessage, safe_agent_call(llm_with_tools, messages))
        
        if not response.tool_calls:
            break
            
        messages.append(response)
        
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            print(f"🛠️  MCP TOOL CALL: {tool_name} with args: {tool_args}")
            
            observation = tools[tool_name](**tool_args)
            
            print(f"👁️  MCP OBSERVATION: Read {len(str(observation))} characters.")
            
            messages.append(ToolMessage(
                tool_call_id=tool_call["id"],
                content=str(observation)
            ))

    # 3. Final Pass: Get structured output
    # Now that investigation is done, force the model to format the result
    final_structured_llm = SMART_MODEL.with_structured_output(AgentReport)
    final_report = cast(AgentReport, safe_agent_call(final_structured_llm, messages))

    return {
        "reports": [final_report],
        "pr_diff": state["pr_diff"],
        "pr_description": state["pr_description"]
    }