import os
import httpx
import json
import asyncio
from fastapi import FastAPI, Request, BackgroundTasks, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import your graph logic
from graph import app as agent_workflow

load_dotenv()

server = FastAPI()

# 1. Enable CORS for Flutter/Web access
server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. SILENCE STREAMLIT NOISE
# This middleware intercepts the /_stcore/ health checks from old browser tabs
@server.middleware("http")
async def ignore_streamlit_noise(request: Request, call_next):
    if "_stcore" in request.url.path:
        # Return "No Content" immediately without logging an error
        return Response(status_code=204)
    return await call_next(request)

# Global storage for the Flutter dashboard
latest_reports = []

async def post_github_comment(issue_url: str, summary: str):
    """Posts the AI summary back to the GitHub PR as a comment."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("⚠️ No GITHUB_TOKEN found. Skipping GitHub comment.")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    comment_data = {"body": summary}
    
    async with httpx.AsyncClient() as client:
        print(f"💬 Posting review to GitHub: {issue_url}/comments")
        response = await client.post(
            f"{issue_url}/comments", 
            json=comment_data, 
            headers=headers
        )
        
        if response.status_code == 201:
            print("✅ Successfully posted comment to GitHub!")
        else:
            print(f"❌ GitHub API Error: {response.status_code} - {response.text}")

async def run_ai_review(payload: dict):
    """The background task that runs the Multi-Agent System."""
    global latest_reports
    
    try:
        pr_data = payload.get("pull_request", {})
        diff_url = pr_data.get("diff_url")
        issue_url = pr_data.get("issue_url")
        token = os.getenv("GITHUB_TOKEN")

        if not diff_url:
            print("❌ No diff_url found.")
            return 

        # 1. Fetch the raw code diff
        async with httpx.AsyncClient() as client:
            print(f"📡 Fetching diff from: {diff_url}")
            # We add the token here so we can read private repository code
            api_diff_url = diff_url.replace("github.com", "api.github.com/repos")
            api_diff_url = api_diff_url.replace("/pull/", "/pulls/")
            
            print(f"📡 Requesting API diff from: {api_diff_url}")

            headers = {
                "Authorization": f"token {os.getenv('GITHUB_TOKEN')}",
                "Accept": "application/vnd.github.v3.diff", # This forces the API to return the DIFF text
                "User-Agent": "FastAPI-AI-Reviewer"        # GitHub requires a User-Agent header
            }
            
            diff_response = await client.get(api_diff_url, headers=headers)
            diff_text = diff_response.text

        # DEBUG PRINT: If this is 0, the AI has nothing to read!
        print(f"📊 Diff size: {len(diff_text)} characters")

        if len(diff_text.strip()) < 10:
            print("⚠️ Diff is empty or too small. Agent review might be inaccurate.")

        # 2. Prepare the Agent State
        initial_state = {
            "pr_diff": diff_text,
            "pr_description": pr_data.get("body") or "No description.",
            "reports": [],
            "final_summary": "",
            "deployment_ready": False
        }

        # 3. Invoke the LangGraph workflow (Synchronous .invoke for stability)
        print("🧠 Starting Multi-Agent Review Flow (Sequential)...")
        # We use .invoke() to avoid signature issues on some Python 3.13 builds
        result = agent_workflow.invoke(initial_state)
        
        # 4. Update state and post result
        latest_reports = result.get("reports", [])
        final_summary = result.get("final_summary", "Review completed.")
        
        if issue_url:
            await post_github_comment(issue_url, final_summary)
        
        print("🏁 All agents finished successfully.")

    except Exception as e:
        print(f"🔥 Error during AI Review: {str(e)}")

@server.post("/webhook")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    """The entry point for GitHub Webhooks."""
    payload = await request.json()
    action = payload.get("action")
    
    # Process when a PR is opened, synchronized (new push), or reopened
    if action in ["opened", "synchronize", "reopened"]:
        print(f"🚀 Triggering AI Agents for PR #{payload.get('number')}...")
        background_tasks.add_task(run_ai_review, payload)
        return {"status": "processing"}
    
    return {"status": "ignored", "action": action}

@server.get("/reports")
async def get_reports():
    """Endpoint for your Flutter dashboard."""
    return latest_reports

if __name__ == "__main__":
    import uvicorn
    # log_level="info" will show your print statements but ignore the streamlit 204s
    print("✨ Server starting on http://localhost:8080")
    uvicorn.run(server, host="0.0.0.0", port=8080, log_level="info")