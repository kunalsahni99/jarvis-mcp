# config.py - Jarvis MCP Server Configuration
# ==============================================
# Loads settings from .env file
# 
# Settings to implement:
#   - API_KEY: Secret key for authenticating requests
#   - MAX_TIMEOUT: Maximum script execution time in seconds (default: 120)
#   - MAX_OUTPUT_SIZE: Truncate stdout/stderr beyond this in bytes (default: 524288 = 512KB)
#   - ALLOWED_LANGUAGES: List of permitted languages e.g. ["python"]
#   - LOG_EXECUTIONS: Boolean - whether to log each execution to disk
#
# Dependencies: python-dotenv, os
# Usage: import settings from this module into other files
