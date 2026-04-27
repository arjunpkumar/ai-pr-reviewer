import os
import httpx
import json
import asyncio
import logging
from fastapi import FastAPI, Request, BackgroundTasks, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from graph import app as agent_workflow
from state import AgentState

load_dotenv()

# --- Aggressive Log Filtering for Streamlit ---
class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return "_stcore" not in record.getMessage()

logging.getLogger("uvicorn.access").addFilter(EndpointFilter())
# Set httpx logging to WARNING to hide the POST/200 OK info messages
logging.getLogger("httpx").setLevel(logging.WARNING)

server = FastAPI()

server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@server.middleware("http")
async def ignore_streamlit_noise(request: Request, call_next):
    if "_stcore" in request.url.path:
        return Response(status_code=204)
    return await call_next(request)

latest_reports = []

# --- STATUS HELPER ---
async def set_github_status(repo_full_name: str, sha: str, state: str, description: str):
    token = os.getenv("GITHUB_TOKEN")
    url = f"https://api.github.com/repos/{repo_full_name}/statuses/{sha}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    data = {
        "state": state,
        "description": description[:140],
        "context": "AI-Agent-Reviewer"
    }

    async with httpx.AsyncClient() as client:
        try:
            print(f"📡 Sending '{state}' status to GitHub for {sha[:7]}...")
            response = await client.post(url, json=data, headers=headers)
            if response.status_code != 201:
                print(f"❌ Status Error: {response.status_code} - {response.text}")
            else:
                print(f"✅ GitHub Status updated to: {state}")
        except Exception as e:
            print(f"⚠️ Failed to update GitHub status: {e}")

# --- COMMENT HELPER ---
async def post_github_comment(issue_url: str, summary: str):
    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    async with httpx.AsyncClient() as client:
        print(f"💬 Posting review to: {issue_url}/comments")
        response = await client.post(f"{issue_url}/comments", json={"body": summary}, headers=headers)
        if response.status_code == 201:
            print("✅ Comment posted successfully!")
        else:
            print(f"❌ Comment Error: {response.status_code} - {response.text}")

# --- REVIEW LOGIC ---
async def run_ai_review(payload: dict):
    global latest_reports
    try:
        pr_data = payload.get("pull_request", {})
        repo_name = payload.get("repository", {}).get("full_name")
        # SHA MUST come from head.sha for the check to show on the PR
        sha = pr_data.get("head", {}).get("sha")
        diff_url = pr_data.get("diff_url")
        issue_url = pr_data.get("issue_url")
        token = os.getenv("GITHUB_TOKEN")

        if not all([repo_name, sha, diff_url]):
            print(f"❌ Missing data: Repo={repo_name}, SHA={sha}, Diff={diff_url}")
            return 

        # 1. SET PENDING STATUS
        await set_github_status(repo_name, sha, "pending", "Agents are auditing code...")

        # 2. FETCH DIFF
        async with httpx.AsyncClient() as client:
            api_diff_url = diff_url.replace("github.com", "api.github.com/repos").replace("/pull/", "/pulls/")
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3.diff",
                "User-Agent": "FastAPI-AI-Reviewer"
            }
            diff_response = await client.get(api_diff_url, headers=headers)
            diff_text = diff_response.text

        print(f"📊 Diff size: {len(diff_text)} characters")

        # 3. RUN AI
        initial_state: AgentState =  {
            "pr_diff": diff_text,
            "pr_description": pr_data.get("body") or "No description.",
            "reports": [],
            "final_summary": "",
            "deployment_ready": False
        }

        print("🧠 Starting Multi-Agent Review Flow (Sequential)...")
        result = agent_workflow.invoke(initial_state)
        
        # 4. FINAL STATUS & COMMENT
        latest_reports = result.get("reports", [])
        final_summary = result.get("final_summary", "Review complete.")
        is_ready = result.get("deployment_ready", False)

        # Update to SUCCESS or FAILURE
        final_state = "success" if is_ready else "failure"
        await set_github_status(repo_name, sha, final_state, "AI Agents have finished.")

        if issue_url:
            await post_github_comment(issue_url, final_summary)
        
        print("🏁 All agents finished successfully.")

    except Exception as e:
        print(f"🔥 Error during AI Review: {str(e)}")
        if 'repo_name' in locals() and 'sha' in locals():
            await set_github_status(repo_name, sha, "error", f"AI Review Error: {str(e)[:50]}")

@server.post("/webhook")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    action = payload.get("action")
    if action in ["opened", "synchronize", "reopened"]:
        print(f"🚀 Triggering AI Review for PR #{payload.get('number')}...")
        background_tasks.add_task(run_ai_review, payload)
        return {"status": "processing"}
    return {"status": "ignored"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(server, host="0.0.0.0", port=8080)