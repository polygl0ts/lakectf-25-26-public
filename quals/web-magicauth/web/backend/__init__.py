import logging
import os
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

import jwt
from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configuration
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
FLAG = os.getenv("FLAG")
DOMAIN = os.getenv("DOMAIN")
SMTP2HTTP_TOKEN = os.getenv("SMTP2HTTP_TOKEN")

if not FLAG or not DOMAIN or not SMTP2HTTP_TOKEN:
    logger.error("FLAG, DOMAIN, and SMTP2HTTP_TOKEN environment variables must be set")
    raise RuntimeError("Missing required environment variables")

# In-memory storage
users_db: Dict[str, str] = {}  # email -> role
pending_registrations: Dict[str, WebSocket] = {}  # token -> websocket
pending_logins: Dict[str, WebSocket] = {}  # token -> websocket

# Initialize admin user at startup
admin_email = "admin@auth.ctf.cx"
users_db[admin_email] = "admin"
logger.info(f"Admin user created: {admin_email}")

security = HTTPBearer()


class Address(BaseModel):
    address: str


class Addresses(BaseModel):
    from_: Address = Field(alias="from")
    to: Address


class EmailPayload(BaseModel):
    subject: str
    addresses: Addresses
    spf: str


def create_jwt_token(email: str, role: str) -> str:
    """Create a JWT token for the user"""
    payload = {
        "sub": email,
        "email": email,
        "role": role,
        "is_admin": role == "admin",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_jwt_token(token: str) -> dict:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get the current user from JWT token"""
    token = credentials.credentials
    return verify_jwt_token(token)


@app.get("/")
async def root():
    """Serve the main page"""
    return FileResponse(Path("/app/static/index.html"))


@app.websocket("/ws/auth")
async def websocket_auth(websocket: WebSocket):
    """WebSocket endpoint for registration and login"""
    await websocket.accept()
    logger.info("WebSocket connection established")

    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "register":
                # Generate a random token
                token = secrets.token_urlsafe(16)
                pending_registrations[token] = websocket

                # Create mailto link
                mailto_link = f"mailto:magic@{DOMAIN}?subject=register:{token}"

                await websocket.send_json({
                    "status": "pending",
                    "message": "Please send an email to complete registration",
                    "token": token,
                    "mailto_link": mailto_link,
                    "auth_email": f"magic@{DOMAIN}",
                    "subject": f"register:{token}"
                })
                logger.info(f"Registration pending, token={token}")

            elif action == "login":
                # Generate a random token
                token = secrets.token_urlsafe(16)
                pending_logins[token] = websocket

                # Create mailto link
                mailto_link = f"mailto:magic@{DOMAIN}?subject=login:{token}"

                await websocket.send_json({
                    "status": "pending",
                    "message": "Please send an email to complete login",
                    "token": token,
                    "mailto_link": mailto_link,
                    "auth_email": f"magic@{DOMAIN}",
                    "subject": f"login:{token}"
                })
                logger.info(f"Login pending, token={token}")

            else:
                await websocket.send_json({
                    "status": "error",
                    "message": "Unknown action"
                })

    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
        # Clean up pending requests for this websocket
        for token, ws in list(pending_registrations.items()):
            if ws == websocket:
                del pending_registrations[token]
        for token, ws in list(pending_logins.items()):
            if ws == websocket:
                del pending_logins[token]


@app.post("/api/email")
async def email_webhook(token: str, payload: EmailPayload):
    """Webhook endpoint to receive emails from smtp2http"""
    if token != SMTP2HTTP_TOKEN:
        return {"status": "Invalid token"}

    logger.info("Received email payload: %s", payload)

    # Check SPF
    if payload.spf != "pass":
        logger.warning(f"Email failed SPF check: {payload.spf}")
        return {"status": "Email rejected due to SPF failure"}

    # Parse the subject
    subject = payload.subject.strip()

    # Handle registration
    if subject.startswith("register:"):
        token = subject.split(":", 1)[1].strip()
        if token in pending_registrations:
            websocket = pending_registrations[token]
            email = payload.addresses.from_.address

            if email in users_db:
                try:
                    await websocket.send_json({
                        "status": "error",
                        "message": "Email already registered"
                    })
                except Exception as e:
                    logger.error(f"Failed to send to websocket: {e}")
                del pending_registrations[token]
                return {"status": "Email already registered"}
            
            if payload.addresses.to.address.lower() != f"magic@{DOMAIN}":
                try:
                    await websocket.send_json({
                        "status": "error",
                        "message": f"Email must be sent to magic@{DOMAIN}"
                    })
                except Exception as e:
                    logger.error(f"Failed to send to websocket: {e}")
                del pending_registrations[token]
                return {"status": f"Email must be sent to magic@{DOMAIN}"}

            # Store user with default role
            role = "user"
            users_db[email] = role

            # Generate JWT
            jwt_token = create_jwt_token(email, role)

            # Send JWT to websocket
            try:
                await websocket.send_json({
                    "status": "success",
                    "message": "Registration successful!",
                    "token": jwt_token,
                    "email": email,
                    "role": role,
                    "is_admin": False
                })
                logger.info(f"User registered: {email} -> {role}")
            except Exception as e:
                logger.error(f"Failed to send to websocket: {e}")

            # Clean up
            del pending_registrations[token]
        else:
            logger.warning(f"Unknown registration token: {token}")

    # Handle login
    elif subject.startswith("login:"):
        token = subject.split(":", 1)[1].strip()
        if token in pending_logins:
            websocket = pending_logins[token]
            email = payload.addresses.from_.address

            if email not in users_db:
                try:
                    await websocket.send_json({
                        "status": "error",
                        "message": "Email not registered"
                    })
                except Exception as e:
                    logger.error(f"Failed to send to websocket: {e}")
                del pending_logins[token]
                return {"status": "Email not registered"}

            role = users_db[email]

            # Generate JWT
            jwt_token = create_jwt_token(email, role)

            # Send JWT to websocket
            try:
                await websocket.send_json({
                    "status": "success",
                    "message": "Login successful!",
                    "token": jwt_token,
                    "email": email,
                    "role": role,
                    "is_admin": role == "admin"
                })
                logger.info(f"User logged in: {email}")
            except Exception as e:
                logger.error(f"Failed to send to websocket: {e}")

            # Clean up
            del pending_logins[token]
        else:
            logger.warning(f"Unknown login token: {token}")

    return {"status": "Email processed"}


@app.get("/api/flag")
async def get_flag(user: dict = Depends(get_current_user)):
    """Get the flag (only for admins)"""
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Only admins can access the flag")

    return {"flag": FLAG}


@app.get("/api/me")
async def get_me(user: dict = Depends(get_current_user)):
    """Get current user info"""
    return user


# Mount static files (frontend will be built here)
try:
    app.mount("/static", StaticFiles(directory="/app/static"), name="static")
except Exception as e:
    logger.warning(f"Static files not mounted: {e}")
