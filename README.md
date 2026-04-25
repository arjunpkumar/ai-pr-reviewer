# AI PR Reviewer

AI PR Reviewer is a FastAPI webhook service that reviews GitHub pull requests using a LangGraph multi-agent workflow and posts a structured summary back to the PR.

## How It Works

When GitHub sends a `pull_request` webhook (`opened`, `synchronize`, `reopened`), the service:

1. Marks the PR commit status as `pending`.
2. Fetches the PR diff from GitHub.
3. Runs a LangGraph workflow with multiple agents:
   - `Sanity` (basic correctness and risk signals)
   - `Architecture` (design and structure)
   - `Style` (maintainability/readability)
   - `Testing` (test coverage and testability, conditional)
4. Builds a markdown summary table and deployment verdict.
5. Updates commit status to `success`/`failure`.
6. Posts the final summary as a PR comment.

Main implementation files:
- `main.py` - FastAPI server and GitHub integration
- `graph.py` - workflow routing and orchestration
- `agents/` - individual agent prompts and execution
- `state.py` - shared state schema

## Architecture

Workflow path:

`START -> smart_router -> sanity -> arch -> style -> (test or evaluator) -> evaluator -> END`

Routing behavior:
- Non-code changes can skip directly to evaluator.
- UI-only style changes can skip test generation.
- Final deploy readiness is decided in evaluator output.

## Requirements

- Python 3.10+
- `pip`
- GitHub repository webhook access
- API keys in `.env`

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Create `.env` in the project root:

```env
GITHUB_TOKEN=your_github_token
OPENAI_API_KEY=your_openrouter_or_openai_compatible_key
# Optional if switching provider in utils/llm_factory.py:
GROQ_API_KEY=your_groq_key
```

Notes:
- The current OpenRouter configuration reads `OPENAI_API_KEY`.
- `.env` is gitignored.

## Run Locally

```bash
uvicorn main:server --host 0.0.0.0 --port 8080 --reload
```

Alternative:

```bash
python main.py
```

Server endpoint:
- `POST /webhook`

## GitHub Webhook Setup

In your GitHub repository:

1. Go to Settings -> Webhooks -> Add webhook.
2. Set Payload URL to your service URL + `/webhook`.
3. Set Content type to `application/json`.
4. Select event: `Pull requests`.
5. Save.

The service expects a standard GitHub pull request webhook payload (including `pull_request.diff_url`, `pull_request.head.sha`, and `repository.full_name`).

## Quick Local Endpoint Check

You can verify the endpoint accepts payloads:

```bash
curl -X POST http://localhost:8080/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "action": "opened",
    "number": 1,
    "repository": {"full_name": "owner/repo"},
    "pull_request": {
      "body": "Test PR",
      "issue_url": "https://api.github.com/repos/owner/repo/issues/1",
      "diff_url": "https://github.com/owner/repo/pull/1.diff",
      "head": {"sha": "abc123"}
    }
  }'
```

Expected immediate response for valid actions:

```json
{"status":"processing"}
```

## LLM Provider Selection

Provider/model wiring is controlled in `utils/llm_factory.py`.

Current default:
- `SMART_MODEL = get_smart_openrouter_model()`
- `FAST_MODEL = get_fast_openrouter_model()`

To use Groq, switch to the Groq lines in that file and set `GROQ_API_KEY`.

## Utility Scripts

OpenRouter utilities:

```bash
python utils/models/open_router/list_free_models.py
python utils/models/open_router/check_open_router_health.py
```

Groq utilities:

```bash
python utils/models/groq/list_free_models.py
python utils/models/groq/check_groq_health.py
```

## Project Layout

```text
ai-pr-reviewer/
├─ main.py
├─ graph.py
├─ state.py
├─ requirements.txt
├─ agents/
│  ├─ base.py
│  ├─ sanity.py
│  ├─ arch.py
│  ├─ style.py
│  ├─ test_gen.py
│  └─ evaluator.py
└─ utils/
   ├─ llm_factory.py
   └─ models/
      ├─ open_router/
      └─ groq/
```

## Screenshots

| Description | Image |
|-------------|-------|
| Adding comments in a PR | ![Adding comments in PR](screenshots/adding_comments_in_PR.png) |
| Agent review in progress | ![Agent review in progress](screenshots/agent_review_in_progress.png) |
| AI-generated comments | ![AI comments](screenshots/ai_comments.png) |
| Checks failed | ![Checks failed](screenshots/checks_failed.png) |
| Checks succeeded | ![Checks success](screenshots/checks_success.png) |
| Console view | ![Console view](screenshots/console_view.png) |

## Testing

There is currently no committed automated test suite in this repository. If you add tests, include instructions here.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
