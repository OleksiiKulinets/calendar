import os
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import httpx

load_dotenv()

app = FastAPI()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


@app.get("/")
async def root():
    return {"status": "ok"}

@app.get("/auth/google/start")
async def google_auth_start():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/calendar",
        "access_type": "offline",
        "prompt": "consent",
    }

    url = (
        GOOGLE_AUTH_URL
        + "?"
        + "&".join([f"{k}={v}" for k, v in params.items()])
    )

    return RedirectResponse(url)


@app.get("/auth/google/callback")
async def google_auth_callback(request: Request):
    code = request.query_params.get("code")

    if not code:
        return {"error": "No code provided"}

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )

    tokens = resp.json()

    return {
        "message": "OAuth success",
        "tokens": tokens,
    }