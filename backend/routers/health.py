from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from database import database
from security import get_current_user
from models.schemas import SyncIn

router = APIRouter()


@router.post("/sync")
async def sync(data: SyncIn, user=Depends(get_current_user)):
    """Wywoływany przez Apple Shortcuts."""
    saved = []
    for m in data.metrics:
        await database.execute(
            """INSERT INTO health_metrics (user_id, date, type, value, unit, meta)
               VALUES (:uid, :date, :type, :value, :unit, :meta)
               ON CONFLICT (user_id, date, type)
               DO UPDATE SET value=EXCLUDED.value, unit=EXCLUDED.unit, meta=EXCLUDED.meta""",
            {"uid": user["id"], "date": data.date, "type": m.type,
             "value": m.value, "unit": m.unit, "meta": str(m.meta or {})}
        )
        saved.append(m.type)
    return {"saved": saved, "date": str(data.date)}


@router.get("/summary")
async def summary(user=Depends(get_current_user)):
    today    = date.today()
    week_ago = today - timedelta(days=7)

    today_rows = await database.fetch_all(
        "SELECT type, value, unit, meta FROM health_metrics WHERE user_id=:uid AND date=:d",
        {"uid": user["id"], "d": today}
    )
    week_rows = await database.fetch_all(
        """SELECT date, type, value FROM health_metrics
           WHERE user_id=:uid AND date>=:from ORDER BY date""",
        {"uid": user["id"], "from": week_ago}
    )
    return {
        "today": [dict(r) for r in today_rows],
        "week":  [dict(r) for r in week_rows],
    }


@router.get("/metrics")
async def metrics(
    type: Optional[str] = Query(None),
    days: int = Query(14, ge=1, le=365),
    user=Depends(get_current_user)
):
    since  = date.today() - timedelta(days=days)
    query  = "SELECT date, type, value, unit, meta FROM health_metrics WHERE user_id=:uid AND date>=:since"
    params: dict = {"uid": user["id"], "since": since}
    if type:
        query += " AND type=:type"
        params["type"] = type
    rows = await database.fetch_all(query + " ORDER BY date", params)
    return [dict(r) for r in rows]
