# main.py - Jarvis MCP Server (FastAPI Application)
# ====================================================
# Entry point for the Jarvis sandbox execution server
#
# Endpoints to implement:
#
# GET /
#   - Simple root message confirming server is online
#   - No auth required
#
# GET /health
#   - Returns: status, service name, version, supported languages, max timeout
#   - No auth required
#   - Response model: HealthResponse
#
# POST /run
#   - Accepts: ScriptRequest (language, script, parameters?, timeout?)
#   - Returns: ScriptResponse (executionId, success, exitCode, stdout, stderr, executionTime)
#   - Auth required: API key via X-API-Key header (use auth.py dependency)
#   - Calls executor.execute_script()
#
# Pydantic models to define:
#   - ScriptRequest: language (str), script (str), parameters (dict|None), timeout (int|None)
#   - ScriptResponse: executionId (str), success (bool), exitCode (int), stdout (str), stderr (str), executionTime (float)
#   - HealthResponse: status (str), service (str), version (str), supportedLanguages (list), maxTimeout (int)
#
# Dependencies: fastapi, pydantic
# Imports: auth.verify_api_key, executor.execute_script, config.*
#
# Run with: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
# OpenAPI docs auto-available at: /docs (Swagger) and /openapi.json

# import os, json, hmac
# from datetime import datetime, timezone

import os
import hmac
from mcp.server import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from executor import execute_script

mcp = FastMCP(
    "jarvis-sandbox",
    host=os.environ.get("HOST", "127.0.0.1"),
    port=int(os.environ.get("PORT", 8000)),
    stateless_http=True
)

@mcp.tool()
def run_script(language: str, script: str, parameters: dict | None = None, timeout: int = 60) -> dict:
    """Run a Python script in an isolated sandbox. Returns exit code, stdout, stderr."""
    return execute_script(language, script, parameters, timeout)

@mcp.custom_route("/health", methods=["GET"])
async def health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})

#TODO: Will expose this custom route later
# @mcp.custom_route("/logs", methods=["GET"])
# async def get_logs(request: Request) -> JSONResponse:
#     key = request.headers.get("X-API-Key", "")
#     if not hmac.compare_digest(key, os.environ["JARVIS_API_KEY"]):
#         return JSONResponse({"error": "unauthorized"}, status_code=401)

#     date = request.query_params.get("date") or datetime.now(timezone.utc).strftime("%Y-%m-%d")
#     limit = min(int(request.query_params.get("limit", 50)), 500)
#     try:
#         datetime.strptime(date, "%Y-%m-%d")   # also blocks path tricks like ../../etc
#     except ValueError:
#         return JSONResponse({"error": "date must be YYYY-MM-DD"}, status_code=400)

#     path = f"logs/{date}.jsonl"
#     if not os.path.exists(path):
#         return JSONResponse({"entries": []})
#     with open(path, encoding="utf-8") as f:
#         lines = f.readlines()[-limit:]
#     return JSONResponse({"entries": [json.loads(l) for l in lines]})

class APIKeyMiddleware:
    """Rejects HTTP requests that lack the right X-API-Key header"""

    def __init__(self, app, api_key: str, open_paths=("/health",)):
        self.app = app
        self.api_key = api_key.encode()
        self.open_paths = open_paths

    async def __call__(self, scope, receive, send):
        # Only guard HTTP requests; startup/shutdown ("lifespan") events pass through
        if scope["type"] != "http" or scope["path"] in self.open_paths:
            return await self.app(scope, receive, send)

        headers = dict(scope["headers"])
        supplied = headers.get(b"x-api-key", b"")
        if not hmac.compare_digest(supplied, self.api_key):
            resp = JSONResponse({"error": "unauthorized"}, status_code=401)
            return await resp(scope, receive, send)

        await self.app(scope, receive, send)

if __name__ == "__main__":
    import uvicorn
    api_key = os.environ.get("JARVIS_API_KEY")

    if not api_key:
        raise SystemExit("JARVIS_API_KEY is not set; refusing to start without auth.")

    app = mcp.streamable_http_app()
    app.add_middleware(APIKeyMiddleware, api_key=api_key)
    uvicorn.run(app, host=mcp.settings.host, port=mcp.settings.port)