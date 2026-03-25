from datetime import date
from typing import Optional, List
from pydantic import BaseModel, EmailStr


# ── Auth ──────────────────────────────────────────────────────────────────────
class RegisterIn(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    username: str
    password: str


# ── Health ────────────────────────────────────────────────────────────────────
class MetricIn(BaseModel):
    type: str                          # sleep | steps | workout | heart_rate
    value: float
    unit: Optional[str] = None
    meta: Optional[dict] = {}

class SyncIn(BaseModel):
    date: date
    metrics: List[MetricIn]


# ── Tasks ─────────────────────────────────────────────────────────────────────
class TaskIn(BaseModel):
    title: str
    category: str = "personal"         # personal | work | health
    estimated_minutes: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None       # todo | in_progress | done
    estimated_minutes: Optional[int] = None

class SessionIn(BaseModel):
    action: str                        # start | stop
    notes: Optional[str] = None
