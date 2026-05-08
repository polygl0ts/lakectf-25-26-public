PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 0,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS player_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    created_at INTEGER NOT NULL,
    last_seen_at INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS chats (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    locale TEXT NOT NULL,
    prompt_source TEXT NOT NULL,
    prompt_html TEXT NOT NULL,
    full_url TEXT,
    target TEXT,
    status TEXT NOT NULL DEFAULT 'draft',
    answer_source TEXT,
    answer_html TEXT,
    answer_author TEXT,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    dispatched_at INTEGER,
    answered_at INTEGER,
    FOREIGN KEY (session_id) REFERENCES player_sessions(id)
);

CREATE TABLE IF NOT EXISTS queue_items (
    chat_id TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'queued',
    claimed_by TEXT,
    claim_token TEXT,
    claim_until INTEGER,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS drafts (
    chat_id TEXT PRIMARY KEY,
    content_source TEXT NOT NULL DEFAULT '',
    content_html TEXT NOT NULL DEFAULT '',
    updated_at INTEGER NOT NULL,
    FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rate_limits (
    ip TEXT NOT NULL,
    action TEXT NOT NULL,
    window_start INTEGER NOT NULL,
    count INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (ip, action, window_start)
);

CREATE INDEX IF NOT EXISTS idx_chats_session_created
ON chats (session_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_player_sessions_user
ON player_sessions (user_id);

CREATE INDEX IF NOT EXISTS idx_users_username
ON users (username);

CREATE INDEX IF NOT EXISTS idx_chats_target_status
ON chats (target, status, dispatched_at);

CREATE INDEX IF NOT EXISTS idx_queue_status_created
ON queue_items (status, created_at);
