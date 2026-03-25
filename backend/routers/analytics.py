from datetime import date, timedelta
from collections import defaultdict
from fastapi import APIRouter, Depends, Query
from scipy.stats import pearsonr
from database import database
from security import get_current_user

router = APIRouter()


@router.get("/correlations")
async def correlations(days: int = Query(30, ge=7, le=365), user=Depends(get_current_user)):
    since = date.today() - timedelta(days=days)
    uid   = user["id"]

    health = await database.fetch_all(
        "SELECT date, type, value FROM health_metrics WHERE user_id=:uid AND date>=:since ORDER BY date",
        {"uid": uid, "since": since}
    )
    tasks_done = await database.fetch_all(
        """SELECT DATE(completed_at) AS day, COUNT(*) AS cnt
           FROM tasks WHERE user_id=:uid AND status='done' AND completed_at>=:since
           GROUP BY DATE(completed_at)""",
        {"uid": uid, "since": since}
    )

    by_date: dict = defaultdict(dict)
    for r in health:
        by_date[str(r["date"])][r["type"]] = float(r["value"])

    tasks_by_day = {str(r["day"]): int(r["cnt"]) for r in tasks_done}

    results = []

    def pearson_corr(pairs):
        if len(pairs) < 5:
            return None
        x, y = zip(*pairs)
        if len(set(x)) < 2 or len(set(y)) < 2:
            return None
        r, p = pearsonr(x, y)
        return {"r": round(r, 3), "p": round(p, 4), "n": len(pairs), "significant": p < 0.05}

    # Sen → ukończone zadania
    pairs = [(by_date[d]["sleep"], tasks_by_day.get(d, 0)) for d in by_date if "sleep" in by_date[d]]
    c = pearson_corr(pairs)
    if c:
        results.append({"label": "sen → produktywność", **c})

    # Kroki → ukończone zadania
    pairs = [(by_date[d]["steps"], tasks_by_day.get(d, 0)) for d in by_date if "steps" in by_date[d]]
    c = pearson_corr(pairs)
    if c:
        results.append({"label": "kroki → produktywność", **c})

    # Scatter: sen vs zadania (dla wykresu)
    scatter = [
        {"sleep": by_date[d]["sleep"], "tasks": tasks_by_day.get(d, 0)}
        for d in sorted(by_date) if "sleep" in by_date[d]
    ]

    return {"correlations": results, "scatter": scatter, "days": days}


@router.get("/weekly")
async def weekly(user=Depends(get_current_user)):
    uid         = user["id"]
    today       = date.today()
    week_start  = today - timedelta(days=today.weekday())
    prev_start  = week_start - timedelta(days=7)

    async def stats(start: date):
        end = start + timedelta(days=6)
        health = await database.fetch_all(
            "SELECT type, AVG(value) AS avg FROM health_metrics WHERE user_id=:uid AND date BETWEEN :s AND :e GROUP BY type",
            {"uid": uid, "s": start, "e": end}
        )
        done = await database.fetch_val(
            "SELECT COUNT(*) FROM tasks WHERE user_id=:uid AND status='done' AND DATE(completed_at) BETWEEN :s AND :e",
            {"uid": uid, "s": start, "e": end}
        )
        tracked = await database.fetch_val(
            """SELECT COALESCE(SUM(ts.duration_minutes),0)
               FROM task_sessions ts JOIN tasks t ON t.id=ts.task_id
               WHERE t.user_id=:uid AND DATE(ts.started_at) BETWEEN :s AND :e""",
            {"uid": uid, "s": start, "e": end}
        )
        return {
            "week_start": str(start),
            "health": {r["type"]: round(float(r["avg"]), 2) for r in health},
            "tasks_done": done or 0,
            "time_tracked_minutes": tracked or 0,
        }

    return {
        "current_week":  await stats(week_start),
        "previous_week": await stats(prev_start),
    }
