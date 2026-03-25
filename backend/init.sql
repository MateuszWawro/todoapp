CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    email         TEXT UNIQUE NOT NULL,
    username      TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    api_token     TEXT UNIQUE NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS health_metrics (
    id         SERIAL PRIMARY KEY,
    user_id    INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date       DATE NOT NULL,
    type       TEXT NOT NULL,
    value      NUMERIC NOT NULL,
    unit       TEXT,
    meta       JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (user_id, date, type)
);

CREATE TABLE IF NOT EXISTS tasks (
    id                SERIAL PRIMARY KEY,
    user_id           INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title             TEXT NOT NULL,
    category          TEXT NOT NULL DEFAULT 'personal',
    status            TEXT NOT NULL DEFAULT 'todo',
    estimated_minutes INT,
    created_at        TIMESTAMPTZ DEFAULT now(),
    started_at        TIMESTAMPTZ,
    completed_at      TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS task_sessions (
    id               SERIAL PRIMARY KEY,
    task_id          INT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    started_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at         TIMESTAMPTZ,
    duration_minutes INT,
    notes            TEXT
);

CREATE INDEX IF NOT EXISTS idx_health_user_date ON health_metrics(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_user       ON tasks(user_id, status);
CREATE INDEX IF NOT EXISTS idx_sessions_task    ON task_sessions(task_id);
