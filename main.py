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
