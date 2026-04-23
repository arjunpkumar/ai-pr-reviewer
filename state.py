from typing import Annotated, List, TypedDict
import operator

class AgentReport(TypedDict):
    agent: str
    status: str
    findings: str
    severity: str

class AgentState(TypedDict):
    pr_diff: str
    pr_description: str
    # Use operator.add to handle the list merging
    reports: Annotated[List[AgentReport], operator.add] 
    final_summary: str
    deployment_ready: bool