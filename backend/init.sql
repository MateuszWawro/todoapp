CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    email         TEXT UNIQUE NOT NULL,
    username      TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    api_token     TEXT UNIQUE NOT NULL,
    created_at    TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS health_metrics (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users(id),
    date       TEXT NOT NULL,
    type       TEXT NOT NULL,
    value      REAL NOT NULL,
    unit       TEXT,
    meta       TEXT DEFAULT '{}',
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE (user_id, date, type)
);

CREATE TABLE IF NOT EXISTS tasks (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id           INTEGER NOT NULL REFERENCES users(id),
    title             TEXT NOT NULL,
    category          TEXT NOT NULL DEFAULT 'personal',
    status            TEXT NOT NULL DEFAULT 'todo',
    estimated_minutes INTEGER,
    created_at        TEXT DEFAULT (datetime('now')),
    started_at        TEXT,
    completed_at      TEXT
);

CREATE TABLE IF NOT EXISTS task_sessions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id          INTEGER NOT NULL REFERENCES tasks(id),
    started_at       TEXT NOT NULL DEFAULT (datetime('now')),
    ended_at         TEXT,
    duration_minutes INTEGER,
    notes            TEXT
);

CREATE INDEX IF NOT EXISTS idx_health_user_date ON health_metrics(user_id, date);
CREATE INDEX IF NOT EXISTS idx_tasks_user       ON tasks(user_id, status);
CREATE INDEX IF NOT EXISTS idx_sessions_task    ON task_sessions(task_id);
