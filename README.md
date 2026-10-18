# Jarvis MCP Server

Sandbox script execution engine for the Jarvis AI Agent (Copilot Studio).

## Project Structure

```
jarvis-mcp/
├── main.py              # FastAPI app - endpoints (/health, /run)
├── executor.py          # Script execution engine (subprocess-based)
├── auth.py              # API key authentication middleware
├── config.py            # Settings loaded from .env
├── requirements.txt     # Python dependencies
├── render.yaml          # Render.com deployment config
├── .env.example         # Environment variables template (copy to .env)
└── README.md            # This file
```

## Architecture

```
Copilot Studio Agent (Jarvis)
        |
        | HTTPS POST /run { language, script, parameters, timeout }
        v
  Render.com (Free Tier)
  ┌──────────────────────────┐
  │  FastAPI Server           │
  │  ├─ Auth (API Key)        │
  │  ├─ Blocked command check │
  │  ├─ subprocess.run()      │
  │  └─ Return results        │
  └──────────────────────────┘
        |
        | { executionId, success, exitCode, stdout, stderr, executionTime }
        v
  Jarvis responds to Kunal with results
```

## Local Setup

1. Copy `.env.example` to `.env` and set your API key
2. `pip install -r requirements.txt`
3. `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
4. Test: `curl http://localhost:8000/health`

## Deploy to Render.com (Free, No Credit Card)

1. Push to GitHub
2. Sign up at render.com with GitHub
3. New > Web Service > connect repo
4. Set JARVIS_API_KEY in env vars
5. Deploy - get public HTTPS URL
6. Register /openapi.json in Copilot Studio

## Security Notes

- API key required on /run endpoint
- Blocked command scanner prevents destructive operations
- Script timeout enforced (default 120s)
- Output truncated at 512KB
- All executions logged to ./logs/ as daily JSONL

## TODO

- [ ] Implement config.py
- [ ] Implement auth.py
- [ ] Implement executor.py (blocked commands, subprocess, logging)
- [ ] Implement main.py (FastAPI endpoints, Pydantic models)
- [ ] Finalize render.yaml with actual values
- [ ] Deploy to Render
- [ ] Register in Copilot Studio as custom action
- [ ] Test end-to-end: Jarvis -> Render -> execute -> return results
