# auth.py - API Key Authentication Middleware
# =============================================
# Validates X-API-Key header on protected endpoints
#
# To implement:
#   - Use FastAPI Security dependency with APIKeyHeader
#   - Compare incoming header value against API_KEY from config
#   - Return 401 HTTPException if missing or invalid
#   - Return the key if valid (allows chaining as a Depends)
#
# Dependencies: fastapi (Security, HTTPException, APIKeyHeader)
# Usage: Add as Depends() on protected routes in main.py
