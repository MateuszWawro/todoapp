import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import database
from routers import auth, health, tasks, analytics

app = FastAPI(title="Life Dashboard API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()
    # Utwórz tabele jeśli nie istnieją (SQLite)
    init_sql = os.path.join(os.path.dirname(__file__), "init.sql")
    with open(init_sql) as f:
        statements = [s.strip() for s in f.read().split(";") if s.strip()]
    for stmt in statements:
        await database.execute(stmt)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

app.include_router(auth.router,      prefix="/api/auth",      tags=["auth"])
app.include_router(health.router,    prefix="/api/health",    tags=["health"])
app.include_router(tasks.router,     prefix="/api/tasks",     tags=["tasks"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

@app.get("/api/ping")
async def ping():
    return {"status": "ok"}
