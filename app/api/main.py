import os
import httpx

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse

from sqlalchemy import select

from app.db.models import User, Calendar
from app.db.session import SessionLocal

from app.services.google_account.service import GoogleAccountService
from app.services.google_calendar.service import GoogleCalendarService
from app.services.telegram.service import TelegramService

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


load_dotenv()

app = FastAPI()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


@app.get("/")
async def root():
    return {"status": "ok"}


# -------------------------
# START OAUTH
# -------------------------
@app.get("/auth/google/start")
async def google_auth_start(telegram_user_id: int):

    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "state": str(telegram_user_id),
        "response_type": "code",
        "scope": "openid https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/calendar",
        "access_type": "offline",
        "prompt": "consent",
    }

    url = GOOGLE_AUTH_URL + "?" + "&".join(f"{k}={v}" for k, v in params.items())

    return RedirectResponse(url)


# -------------------------
# CALLBACK
# -------------------------
@app.get("/auth/google/callback")
async def google_auth_callback(request: Request):

    code = request.query_params.get("code")
    state = request.query_params.get("state")

    if not code or not state:
        return {"error": "Missing code/state"}

    telegram_user_id = int(state)

    # 1. GET TOKENS
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )

        tokens = token_response.json()

        access_token = tokens.get("access_token")
        if not access_token:
            return {"error": "No access token"}

        userinfo = (await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )).json()

    # 2. SAVE USER + ACCOUNT
    with SessionLocal() as session:

        user = session.execute(
            select(User).where(User.telegram_user_id == telegram_user_id)
        ).scalar_one_or_none()

        if not user:
            return {"error": "User not found"}

        GoogleAccountService.create_or_update(
            session,
            telegram_user_id=user.telegram_user_id,
            google_email=userinfo["email"],
            access_token=access_token,
            refresh_token=tokens.get("refresh_token"),
            expires_in=tokens.get("expires_in"),
        )

        session.commit()
        user_id = user.id

    # 3. SYNC CALENDARS (NO DELETE!)
    with SessionLocal() as session:

        google_calendars = await GoogleCalendarService.fetch_calendars(session, telegram_user_id)

        for cal in google_calendars:

            exists = session.execute(
                select(Calendar).where(
                    Calendar.user_id == user_id,
                    Calendar.google_calendar_id == cal["id"]
                )
            ).scalar_one_or_none()

            if not exists:
                session.add(Calendar(
                    user_id=user_id,
                    google_calendar_id=cal["id"],
                    name=cal.get("summary", "Unnamed"),
                    is_default=False
                ))

        session.commit()

        db_calendars = session.execute(
            select(Calendar).where(Calendar.user_id == user_id)
        ).scalars().all()

    # 4. SEND TELEGRAM KEYBOARD
    keyboard = [
        [
            InlineKeyboardButton(
                text=cal.name,
                callback_data=f"calendar:{cal.id}"
            )
        ]
        for cal in db_calendars
    ]

    await TelegramService.send_message(
        chat_id=telegram_user_id,
        text="📅 Оберіть календар:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return HTMLResponse("""
        <html>
            <body style="text-align:center;margin-top:80px;">
                <h2>✅ Google Calendar підключено</h2>
                <p>Поверніться в Telegram</p>
            </body>
        </html>
    """)