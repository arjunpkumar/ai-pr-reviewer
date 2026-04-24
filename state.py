from typing import Annotated, List, TypedDict
import operator
from pydantic import BaseModel, Field

class AgentReport(BaseModel):
    agent: str = Field(description="Name of the agent")
    status: str = Field(description="PASS, FAIL, or WARNING")
    findings: str = Field(description="Detailed findings from the review")
    severity: str = Field(description="LOW, MEDIUM, or HIGH")

class AgentState(TypedDict):
    pr_diff: str
    pr_description: str
    reports: Annotated[List[AgentReport], operator.add] 
    final_summary: str
    deployment_ready: bool