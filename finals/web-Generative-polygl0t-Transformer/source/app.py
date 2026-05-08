from __future__ import annotations

import os
import re
import secrets
import string
import uuid
from pathlib import Path
import bleach
from flask import Flask, g, jsonify, make_response, redirect, render_template, request, url_for
from itsdangerous import BadSignature, URLSafeSerializer
from werkzeug.security import check_password_hash, generate_password_hash

from db import (
    claim_next_bot_job,
    claim_next_human_chat,
    complete_bot_job,
    fail_bot_job,
    extend_claim,
    finalize_claim,
    finalize_expired_claims,
    release_claim,
    init_db,
    query_all,
    query_one,
    seconds_now,
    transaction,
)


BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)

ALLOWED_LOCALES = ("en", "fr", "it", "de", "rm")
ALLOWED_TAGS = [
    "b",
    "strong",
    "i",
    "em",
    "u",
    "p",
    "br",
    "h1",
    "h2",
    "h3",
    "h4",
    "ul",
    "ol",
    "li",
    "blockquote",
    "code",
]
USERNAME_RE = re.compile(r"^[a-z0-9_]{3,24}$")

PLAYER_COOKIE = "player_session"
LANG_COOKIE = "preferred_lang"
RATE_LIMIT_MAX = 8
RATE_LIMIT_WINDOW_SEC = 60
HUMAN_CLAIM_SECONDS = 90
DEFAULT_HUMAN_ANSWER = (
    "Thank you for your question. A polygl0ts member reviewed it and has no "
    "further guidance to share."
)
DEFAULT_BOT_ANSWER = "I'm sorry, I can't assist with that request."


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
app.config["DATABASE_PATH"] = str(INSTANCE_DIR / "fakegpt.db")
app.config["ADMIN_USERNAME"] = os.getenv("ADMIN_USERNAME", "admin")
app.config["ADMIN_PASSWORD"] = os.getenv("ADMIN_PASSWORD", "change-me-admin-password")
app.config["BOT_INTERNAL_TOKEN"] = os.getenv("BOT_INTERNAL_TOKEN", "bot-dev-token")

serializer = URLSafeSerializer(app.config["SECRET_KEY"], salt="auth-session")
init_db(app.config["DATABASE_PATH"])


def normalize_username(value: str) -> str:
    return (value or "").strip().lower()


def generate_random_password(length: int = 18) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def sanitize_html(value: str) -> str:
    return bleach.clean(value or "", tags=ALLOWED_TAGS, attributes={}, strip=True)


def current_locale() -> str:
    preferred = request.args.get("lang") or request.cookies.get(LANG_COOKIE) or "en"
    return preferred if preferred in ALLOWED_LOCALES else "en"


def client_ip() -> str:
    forwarded = request.headers.get("CF-Connecting-IP")
    if forwarded:
        return forwarded.split(",")[0].strip()
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()
    return request.remote_addr or "0.0.0.0"


def build_chat_path(chat_id: str) -> str:
    return url_for("chat_page", chat_id=chat_id)


def create_login_session(user_id: str) -> str:
    session_id = uuid.uuid4().hex
    now = seconds_now()
    with transaction(app.config["DATABASE_PATH"]) as conn:
        conn.execute(
            """
            INSERT INTO player_sessions (id, user_id, created_at, last_seen_at)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, user_id, now, now),
        )
    return session_id


def load_current_session():
    signed = request.cookies.get(PLAYER_COOKIE)
    if not signed:
        return None, None

    try:
        session_id = serializer.loads(signed)
    except BadSignature:
        return None, None

    row = query_one(
        app.config["DATABASE_PATH"],
        """
        SELECT ps.id AS session_id, u.id AS user_id, u.username, u.is_admin
        FROM player_sessions ps
        JOIN users u ON u.id = ps.user_id
        WHERE ps.id = ?
        """,
        (session_id,),
    )
    if row is None:
        return None, None

    with transaction(app.config["DATABASE_PATH"]) as conn:
        conn.execute(
            "UPDATE player_sessions SET last_seen_at = ? WHERE id = ?",
            (seconds_now(), session_id),
        )

    user = {
        "id": row["user_id"],
        "username": row["username"],
        "is_admin": bool(row["is_admin"]),
    }
    return session_id, user


def seed_admin_user() -> None:
    username = normalize_username(app.config["ADMIN_USERNAME"])
    password = app.config["ADMIN_PASSWORD"]
    now = seconds_now()
    password_hash = generate_password_hash(password)
    with transaction(app.config["DATABASE_PATH"]) as conn:
        row = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        if row is None:
            conn.execute(
                """
                INSERT INTO users (id, username, password_hash, is_admin, created_at, updated_at)
                VALUES (?, ?, ?, 1, ?, ?)
                """,
                (uuid.uuid4().hex, username, password_hash, now, now),
            )
        else:
            conn.execute(
                """
                UPDATE users
                SET password_hash = ?, is_admin = 1, updated_at = ?
                WHERE id = ?
                """,
                (password_hash, now, row["id"]),
            )


seed_admin_user()


def attach_cookies(response):
    if getattr(g, "player_session_id", None):
        response.set_cookie(
            PLAYER_COOKIE,
            serializer.dumps(g.player_session_id),
            max_age=60 * 60 * 24 * 30,
            httponly=True,
            samesite="Lax",
        )
    else:
        response.delete_cookie(PLAYER_COOKIE)

    response.set_cookie(
        LANG_COOKIE,
        g.locale,
        max_age=60 * 60 * 24 * 30,
        httponly=False,
        samesite="Lax",
    )
    return response


def render_page(template_name: str, **context):
    response = make_response(
        render_template(
            template_name,
            locale=g.locale,
            allowed_locales=ALLOWED_LOCALES,
            current_user=g.current_user,
            **context,
        )
    )
    return attach_cookies(response)


def json_error(error: str, status: int):
    return attach_cookies(jsonify({"error": error})), status


def redirect_home():
    return attach_cookies(make_response(redirect(url_for("index", lang=g.locale))))


def require_login_response():
    if g.current_user:
        return None
    if request.path.startswith("/api/"):
        return json_error("login_required", 401)
    return redirect_home()


def require_admin_response():
    auth_error = require_login_response()
    if auth_error:
        return auth_error
    if g.current_user["is_admin"]:
        return None
    if request.path.startswith("/api/"):
        return json_error("admin_required", 403)
    return redirect_home()


def user_can_access_chat(row) -> bool:
    if not g.current_user or row is None:
        return False
    return g.current_user["is_admin"] or row["owner_user_id"] == g.current_user["id"]


def limit_or_429(action: str):
    now = seconds_now()
    window = RATE_LIMIT_WINDOW_SEC
    bucket = now - (now % window)
    max_count = RATE_LIMIT_MAX
    ip = client_ip()
    with transaction(app.config["DATABASE_PATH"]) as conn:
        row = conn.execute(
            """
            SELECT count
            FROM rate_limits
            WHERE ip = ? AND action = ? AND window_start = ?
            """,
            (ip, action, bucket),
        ).fetchone()
        if row and row["count"] >= max_count:
            retry_after = bucket + window - now
            return (
                attach_cookies(
                    jsonify(
                        {
                            "error": "rate_limited",
                            "retry_after": retry_after,
                        }
                    )
                ),
                429,
            )
        conn.execute(
            """
            INSERT INTO rate_limits (ip, action, window_start, count)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(ip, action, window_start)
            DO UPDATE SET count = count + 1
            """,
            (ip, action, bucket),
        )
    return None


def require_bot_token() -> None:
    if request.headers.get("X-Bot-Token") != app.config["BOT_INTERNAL_TOKEN"]:
        raise PermissionError("invalid bot token")


def chat_row(chat_id: str):
    return query_one(
        app.config["DATABASE_PATH"],
        """
        SELECT c.*,
               ps.user_id AS owner_user_id,
               u.username AS owner_username,
               q.status AS queue_status,
               q.claimed_by,
               q.claim_until,
               q.claim_token,
               d.content_source AS draft_source,
               d.content_html AS draft_html
        FROM chats c
        JOIN player_sessions ps ON ps.id = c.session_id
        LEFT JOIN users u ON u.id = ps.user_id
        LEFT JOIN queue_items q ON q.chat_id = c.id
        LEFT JOIN drafts d ON d.chat_id = c.id
        WHERE c.id = ?
        """,
        (chat_id,),
    )


def queue_position(chat_id: str) -> int | None:
    row = query_one(
        app.config["DATABASE_PATH"],
        """
        SELECT position FROM (
            SELECT q1.chat_id,
                   ROW_NUMBER() OVER (ORDER BY q1.created_at ASC) AS position
            FROM queue_items q1
            WHERE q1.status = 'queued'
        ) ranked
        WHERE ranked.chat_id = ?
        """,
        (chat_id,),
    )
    return row["position"] if row else None


def bot_queue_position(chat_id: str) -> int | None:
    row = query_one(
        app.config["DATABASE_PATH"],
        """
        SELECT position FROM (
            SELECT id,
                   ROW_NUMBER() OVER (ORDER BY dispatched_at ASC, created_at ASC) AS position
            FROM chats
            WHERE target = 'bot' AND status IN ('bot_pending', 'bot_processing')
        ) ranked
        WHERE ranked.id = ?
        """,
        (chat_id,),
    )
    return row["position"] if row else None


def session_history_rows(user_id: str):
    return query_all(
        app.config["DATABASE_PATH"],
        """
        SELECT c.id, c.locale, c.target, c.status, c.created_at, c.updated_at
        FROM chats c
        JOIN player_sessions ps ON ps.id = c.session_id
        WHERE ps.user_id = ?
        ORDER BY c.created_at DESC
        LIMIT 20
        """,
        (user_id,),
    )


def expire_claims() -> None:
    now = seconds_now()
    fallback_source = DEFAULT_HUMAN_ANSWER
    fallback_html = sanitize_html(fallback_source)
    finalize_expired_claims(
        app.config["DATABASE_PATH"],
        now,
        fallback_source,
        fallback_html,
        "polygl0ts",
    )


@app.before_request
def hydrate_request():
    g.locale = current_locale()
    g.player_session_id = None
    g.current_user = None
    session_id, user = load_current_session()
    g.player_session_id = session_id
    g.current_user = user
    expire_claims()


@app.get("/")
def index():
    return render_page("index.html")


@app.get("/auth")
def auth_page():
    if g.current_user:
        return redirect_home()
    mode = request.args.get("mode", "register")
    if mode not in {"register", "login"}:
        mode = "register"
    return render_page("auth.html", auth_mode=mode)


@app.get("/chat/<chat_id>")
def chat_page(chat_id: str):
    row = chat_row(chat_id)
    if row is None:
        return redirect_home()
    return render_page("chat.html", chat_id=chat_id, raw_lang=request.args.get("lang"))


@app.get("/dashboard")
def dashboard():
    if (response := require_admin_response()):
        return response
    return render_page("dashboard.html")


@app.post("/logout")
def logout():
    g.player_session_id = None
    g.current_user = None
    return redirect_home()


@app.post("/api/register")
def api_register():
    payload = request.get_json(silent=True) or {}
    username = normalize_username(payload.get("username", ""))
    if not USERNAME_RE.fullmatch(username):
        return json_error("invalid_username", 400)

    password = generate_random_password()
    now = seconds_now()
    with transaction(app.config["DATABASE_PATH"]) as conn:
        existing = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        if existing is not None:
            return json_error("username_taken", 409)
        conn.execute(
            """
            INSERT INTO users (id, username, password_hash, is_admin, created_at, updated_at)
            VALUES (?, ?, ?, 0, ?, ?)
            """,
            (uuid.uuid4().hex, username, generate_password_hash(password), now, now),
        )

    return attach_cookies(jsonify({"username": username, "password": password}))


@app.post("/api/login")
def api_login():
    payload = request.get_json(silent=True) or {}
    username = normalize_username(payload.get("username", ""))
    password = payload.get("password", "")
    if not username:
        return json_error("missing_username", 400)
    if not password:
        return json_error("missing_password", 400)

    row = query_one(
        app.config["DATABASE_PATH"],
        "SELECT id, username, password_hash, is_admin FROM users WHERE username = ?",
        (username,),
    )
    if row is None or not check_password_hash(row["password_hash"], password):
        return json_error("invalid_credentials", 401)

    g.player_session_id = create_login_session(row["id"])
    g.current_user = {
        "id": row["id"],
        "username": row["username"],
        "is_admin": bool(row["is_admin"]),
    }
    return attach_cookies(
        jsonify(
            {
                "ok": True,
                "username": row["username"],
                "isAdmin": bool(row["is_admin"]),
            }
        )
    )


@app.get("/api/history")
def api_history():
    if (response := require_login_response()):
        return response
    rows = session_history_rows(g.current_user["id"])
    payload = [
        {
            "id": row["id"],
            "locale": row["locale"],
            "target": row["target"],
            "status": row["status"],
            "url": build_chat_path(row["id"]),
            "createdAt": row["created_at"],
            "updatedAt": row["updated_at"],
        }
        for row in rows
    ]
    return attach_cookies(jsonify({"items": payload}))


@app.post("/api/chats")
def api_create_chat():
    if (response := require_login_response()):
        return response
    limited = limit_or_429("create_chat")
    if limited:
        return limited

    payload = request.get_json(silent=True) or {}
    prompt_source = (payload.get("prompt") or "").strip()
    locale = payload.get("locale") if payload.get("locale") in ALLOWED_LOCALES else g.locale
    if not prompt_source:
        return json_error("missing_prompt", 400)
    if len(prompt_source) > 4000:
        return json_error("prompt_too_long", 400)

    chat_id = uuid.uuid4().hex
    now = seconds_now()
    prompt_html = sanitize_html(prompt_source)
    with transaction(app.config["DATABASE_PATH"]) as conn:
        conn.execute(
            """
            INSERT INTO chats (
                id, session_id, locale, prompt_source, prompt_html,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (chat_id, g.player_session_id, locale, prompt_source, prompt_html, now, now),
        )
    return attach_cookies(jsonify({"id": chat_id, "url": build_chat_path(chat_id)}))


@app.post("/api/dispatch")
def api_dispatch_chat():
    if (response := require_login_response()):
        return response
    limited = limit_or_429("dispatch_chat")
    if limited:
        return limited

    payload = request.get_json(silent=True) or {}
    target = payload.get("target")
    path = (payload.get("url") or "").strip()
    if not path.startswith("/chat/"):
        return json_error("invalid_url", 400)

    chat_id = path.split("?", 1)[0].split("#", 1)[0][len("/chat/"):]
    row = query_one(
        app.config["DATABASE_PATH"],
        """
        SELECT c.id, c.status, ps.user_id AS owner_user_id
        FROM chats c
        JOIN player_sessions ps ON ps.id = c.session_id
        WHERE c.id = ?
        """,
        (chat_id,),
    )
    if row is None:
        return json_error("not_found", 404)
    if row["owner_user_id"] != g.current_user["id"] and not g.current_user["is_admin"]:
        return json_error("forbidden", 403)
    if row["status"] != "draft":
        return json_error("already_dispatched", 400)
    if target not in {"human", "bot"}:
        return json_error("invalid_target", 400)

    now = seconds_now()
    next_status = "queued" if target == "human" else "bot_pending"
    with transaction(app.config["DATABASE_PATH"]) as conn:
        conn.execute(
            """
            UPDATE chats
            SET target = ?,
                full_url = ?,
                status = ?,
                dispatched_at = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (target, path, next_status, now, now, chat_id),
        )
        if target == "human":
            conn.execute(
                """
                INSERT INTO queue_items (
                    chat_id, status, created_at, updated_at
                )
                VALUES (?, 'queued', ?, ?)
                """,
                (chat_id, now, now),
            )

    position = bot_queue_position(chat_id) if target == "bot" else queue_position(chat_id)
    return attach_cookies(jsonify({
        "id": chat_id,
        "status": next_status,
        "url": path,
        "queuePosition": position,
    }))


def position_for(row) -> int | None:
    if row["target"] == "bot":
        return bot_queue_position(row["id"])
    return queue_position(row["id"])


@app.get("/api/chat")
def api_chat():
    chat_id = request.args.get("id", "")
    if not chat_id:
        return json_error("missing_id", 400)
    row = chat_row(chat_id)
    if row is None:
        return json_error("not_found", 404)

    payload = {
        "id": row["id"],
        "prompt": row["prompt_source"] or "",
        "answer": row["answer_source"] or "",
        "status": row["status"],
        "target": row["target"],
        "answerAuthor": row["answer_author"] or "",
        "queuePosition": position_for(row),
        "claimUntil": row["claim_until"],
    }
    return attach_cookies(jsonify(payload))


@app.get("/api/dashboard/queue")
def api_dashboard_queue():
    if (response := require_admin_response()):
        return response
    queued = query_all(
        app.config["DATABASE_PATH"],
        """
        SELECT c.id, c.locale, c.prompt_html, c.full_url, q.status, q.claimed_by, q.claim_until, q.created_at
        FROM queue_items q
        JOIN chats c ON c.id = q.chat_id
        WHERE q.status IN ('queued', 'claimed')
        ORDER BY q.created_at ASC
        """
    )
    recent = query_all(
        app.config["DATABASE_PATH"],
        """
        SELECT id, locale, prompt_html, answer_html, answer_author, updated_at
        FROM chats
        WHERE status = 'answered'
        ORDER BY answered_at DESC, updated_at DESC
        LIMIT 20
        """
    )
    current = []
    queue = []
    for row in queued:
        item = {
            "id": row["id"],
            "locale": row["locale"],
            "promptHtml": row["prompt_html"],
            "url": row["full_url"] or build_chat_path(row["id"]),
            "claimedBy": row["claimed_by"] or "",
            "claimUntil": row["claim_until"],
            "createdAt": row["created_at"],
        }
        if row["status"] == "claimed":
            current.append(item)
        else:
            queue.append(item)
    history = [
        {
            "id": row["id"],
            "locale": row["locale"],
            "promptHtml": row["prompt_html"],
            "answerHtml": row["answer_html"],
            "answerAuthor": row["answer_author"],
            "updatedAt": row["updated_at"],
        }
        for row in recent
    ]
    return attach_cookies(jsonify({"queue": queue, "claimed": current, "history": history}))


@app.post("/api/dashboard/claim-next")
def api_dashboard_claim_next():
    if (response := require_admin_response()):
        return response
    claim = claim_next_human_chat(
        app.config["DATABASE_PATH"],
        claimed_by=g.current_user["username"],
        lease_seconds=HUMAN_CLAIM_SECONDS,
        now=seconds_now(),
    )
    if claim is None:
        return attach_cookies(jsonify({"claim": None}))
    return attach_cookies(
        jsonify(
            {
                "claim": {
                    "id": claim["id"],
                    "locale": claim["locale"],
                    "promptHtml": claim["prompt_html"],
                    "promptSource": claim["prompt_source"],
                    "url": claim["full_url"] or build_chat_path(claim["id"]),
                    "claimToken": claim["claim_token"],
                    "claimUntil": claim["claim_until"],
                }
            }
        )
    )


@app.post("/api/dashboard/heartbeat")
def api_dashboard_heartbeat():
    if (response := require_admin_response()):
        return response
    payload = request.get_json(silent=True) or {}
    chat_id = (payload.get("id") or "").strip()
    if not chat_id:
        return json_error("missing_id", 400)
    draft_source = (payload.get("draft") or "").strip()
    draft_html = sanitize_html(draft_source)
    claim_until = extend_claim(
        app.config["DATABASE_PATH"],
        chat_id=chat_id,
        claim_token=payload.get("claimToken", ""),
        lease_seconds=HUMAN_CLAIM_SECONDS,
        now=seconds_now(),
        draft_source=draft_source,
        draft_html=draft_html,
    )
    if claim_until is None:
        return json_error("claim_expired", 409)
    return attach_cookies(jsonify({"ok": True, "claimUntil": claim_until}))


@app.post("/api/dashboard/answer")
def api_dashboard_answer():
    if (response := require_admin_response()):
        return response
    payload = request.get_json(silent=True) or {}
    chat_id = (payload.get("id") or "").strip()
    if not chat_id:
        return json_error("missing_id", 400)
    answer_source = (payload.get("answer") or "").strip() or DEFAULT_HUMAN_ANSWER
    answer_html = sanitize_html(answer_source)
    ok = finalize_claim(
        app.config["DATABASE_PATH"],
        chat_id=chat_id,
        claim_token=payload.get("claimToken", ""),
        answer_source=answer_source,
        answer_html=answer_html,
        answer_author=g.current_user["username"],
        now=seconds_now(),
    )
    if not ok:
        return json_error("claim_expired", 409)
    return attach_cookies(jsonify({"ok": True}))


@app.post("/api/dashboard/release")
def api_dashboard_release():
    if (response := require_admin_response()):
        return response
    payload = request.get_json(silent=True) or {}
    chat_id = (payload.get("id") or "").strip()
    if not chat_id:
        return json_error("missing_id", 400)
    ok = release_claim(
        app.config["DATABASE_PATH"],
        chat_id=chat_id,
        claim_token=payload.get("claimToken", ""),
        now=seconds_now(),
    )
    if not ok:
        return json_error("claim_expired", 409)
    return attach_cookies(jsonify({"ok": True}))


@app.post("/api/internal/bot/jobs/claim")
def api_bot_claim():
    try:
        require_bot_token()
    except PermissionError:
        return jsonify({"error": "forbidden"}), 403
    row = claim_next_bot_job(app.config["DATABASE_PATH"], seconds_now())
    if row is None:
        return ("", 204)
    return jsonify(
        {
            "id": row["id"],
            "url": row["full_url"] or build_chat_path(row["id"]),
            "answer": DEFAULT_BOT_ANSWER,
        }
    )


@app.post("/api/internal/bot/jobs/<chat_id>/complete")
def api_bot_complete(chat_id: str):
    try:
        require_bot_token()
    except PermissionError:
        return jsonify({"error": "forbidden"}), 403
    payload = request.get_json(silent=True) or {}
    answer_source = (payload.get("answer") or "").strip() or DEFAULT_BOT_ANSWER
    answer_html = sanitize_html(answer_source)
    ok = complete_bot_job(
        app.config["DATABASE_PATH"],
        chat_id=chat_id,
        answer_source=answer_source,
        answer_html=answer_html,
        answer_author="experimental bot",
        now=seconds_now(),
    )
    if not ok:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"ok": True})


@app.post("/api/internal/bot/jobs/<chat_id>/fail")
def api_bot_fail(chat_id: str):
    try:
        require_bot_token()
    except PermissionError:
        return jsonify({"error": "forbidden"}), 403
    ok = fail_bot_job(app.config["DATABASE_PATH"], chat_id, seconds_now())
    if not ok:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"ok": True})


@app.get("/healthz")
def healthz():
    query_one(app.config["DATABASE_PATH"], "SELECT 1")
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
