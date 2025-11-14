import os
from fastapi import Request, HTTPException

API_KEY = os.getenv("API_KEY")  # set this in Render / env or .env locally

def require_api_key(request: Request):
    """
    If API_KEY not set → no enforcement (useful for local dev).
    If API_KEY is set, require header 'x-api-key' to match it.
    """
    if not API_KEY:
        return
    header = request.headers.get("x-api-key")
    if header != API_KEY:
        raise HTTPException(status_code=401, detail="Missing or invalid API key")
