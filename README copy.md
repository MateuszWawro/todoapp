# Life Dashboard

Personal health & productivity dashboard dla Mateusza i Agnieszki.

## Stack

| Warstwa | Technologia |
|---|---|
| Backend | FastAPI + PostgreSQL |
| Frontend | Vue.js 3 + Vite + Chart.js |
| Auth | JWT + Bearer Token (Shortcuts) |
| Deployment | Docker Compose |
| iOS sync | Apple Shortcuts → REST API |

## Struktura projektu

```
life-dashboard/
├── backend/
│   ├── routers/
│   │   ├── auth.py         # login, register, /me
│   │   ├── health.py       # /sync (Shortcuts), /summary, /metrics
│   │   ├── tasks.py        # CRUD zadań + sesje timera
│   │   └── analytics.py    # korelacje, raport tygodniowy
│   ├── models/
│   │   └── schemas.py      # Pydantic modele
│   ├── init.sql            # schemat bazy danych
│   ├── database.py         # połączenie z DB
│   ├── security.py         # JWT, bcrypt, get_current_user
│   ├── main.py             # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── LoginView.vue
│   │   │   ├── OverviewView.vue
│   │   │   ├── SleepView.vue
│   │   │   ├── TasksView.vue
│   │   │   ├── CorrelationsView.vue
│   │   │   └── ApiView.vue
│   │   ├── components/
│   │   │   ├── charts/
│   │   │   │   ├── ActivityChart.vue
│   │   │   │   ├── SleepChart.vue
│   │   │   │   └── ScatterChart.vue
│   │   │   └── ui/
│   │   │       ├── MetricCard.vue
│   │   │       ├── TaskItem.vue
│   │   │       └── CorrRow.vue
│   │   ├── stores/
│   │   │   ├── auth.js     # Pinia — user, token, login/logout
│   │   │   ├── health.js   # Pinia — dane zdrowotne
│   │   │   ├── tasks.js    # Pinia — zadania + timer
│   │   │   └── analytics.js
│   │   ├── composables/
│   │   │   └── useApi.js   # axios wrapper z auth headerem
│   │   ├── router/
│   │   │   └── index.js    # vue-router + auth guard
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── .env.example
├── .gitignore
└── docker-compose.yml
```

## Uruchomienie (dev)

```bash
cp .env.example .env
# edytuj .env — ustaw POSTGRES_PASSWORD i JWT_SECRET

docker compose up -d
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs

## Pierwsze uruchomienie — utwórz konta

```bash
# Mateusz
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"mateusz","email":"mateusz@local.pl","password":"twoje-haslo"}'

# Agnieszka
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"agnieszka","email":"agnieszka@local.pl","password":"jej-haslo"}'
```

Odpowiedź zawiera `api_token` — wklejasz go raz do Apple Shortcuts.

## Apple Shortcuts — sync

Shortcut wysyła codziennie o 23:30:

```
POST /api/health/sync
Authorization: Bearer <api_token>
Content-Type: application/json

{
  "date": "2026-03-25",
  "metrics": [
    {"type": "steps",   "value": 8432},
    {"type": "sleep",   "value": 7.5, "meta": {"bedtime": "23:15"}},
    {"type": "workout", "value": 45,  "meta": {"workout_type": "Running", "calories": 420}},
    {"type": "heart_rate", "value": 62}
  ]
}
```

## Fazy rozwoju

- [x] Faza 0 — PoC (HTML mockup)
- [ ] Faza 1 — Backend (FastAPI + PostgreSQL)
- [ ] Faza 2 — Frontend (Vue.js)
- [ ] Faza 3 — Shortcuts integration
- [ ] Faza 4 — Analytics & correlations
