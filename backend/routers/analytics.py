from datetime import date, timedelta
from collections import defaultdict
from fastapi import APIRouter, Depends, Query
from database import database
from security import get_current_user
import math

router = APIRouter()


def pearson(x, y):
    """Korelacja Pearsona bez scipy."""
    n = len(x)
    if n < 5:
        return None
    mx, my = sum(x)/n, sum(y)/n
    num  = sum((xi-mx)*(yi-my) for xi,yi in zip(x,y))
    den  = math.sqrt(sum((xi-mx)**2 for xi in x) * sum((yi-my)**2 for yi in y))
    if den == 0:
        return None
    r = num / den
    # Przybliżone p-value przez t-test
    if abs(r) == 1:
        p = 0.0
    else:
        t = r * math.sqrt(n-2) / math.sqrt(1-r**2)
        # Przybliżenie p dla dużych n
        p = 2 * (1 - min(0.9999, abs(t) / (abs(t) + n - 2)))
    return {"r": round(r, 3), "p": round(p, 4), "n": n, "significant": p < 0.05}


@router.get("/correlations")
async def correlations(days: int = Query(30, ge=7, le=365), user=Depends(get_current_user)):
    since = str(date.today() - timedelta(days=days))
    uid   = user["id"]

    health = await database.fetch_all(
        "SELECT date, type, value FROM health_metrics WHERE user_id=:uid AND date>=:since ORDER BY date",
        {"uid": uid, "since": since}
    )
    tasks_done = await database.fetch_all(
        """SELECT date(completed_at) AS day, COUNT(*) AS cnt
           FROM tasks WHERE user_id=:uid AND status='done' AND completed_at>=:since
           GROUP BY date(completed_at)""",
        {"uid": uid, "since": since}
    )

    by_date: dict = defaultdict(dict)
    for r in health:
        by_date[r["date"]][r["type"]] = float(r["value"])

    tasks_by_day = {r["day"]: int(r["cnt"]) for r in tasks_done}

    results = []

    def add_corr(label, pairs):
        if not pairs:
            return
        x, y = zip(*pairs)
        c = pearson(list(x), list(y))
        if c:
            results.append({"label": label, **c})

    add_corr(
        "sen → produktywność",
        [(by_date[d]["sleep"], tasks_by_day.get(d, 0)) for d in by_date if "sleep" in by_date[d]]
    )
    add_corr(
        "kroki → produktywność",
        [(by_date[d]["steps"], tasks_by_day.get(d, 0)) for d in by_date if "steps" in by_date[d]]
    )

    scatter = [
        {"sleep": by_date[d]["sleep"], "tasks": tasks_by_day.get(d, 0)}
        for d in sorted(by_date) if "sleep" in by_date[d]
    ]

    return {"correlations": results, "scatter": scatter, "days": days}


@router.get("/weekly")
async def weekly(user=Depends(get_current_user)):
    uid        = user["id"]
    today      = date.today()
    week_start = str(today - timedelta(days=today.weekday()))
    prev_start = str(today - timedelta(days=today.weekday() + 7))
    prev_end   = str(today - timedelta(days=today.weekday() + 1))
    week_end   = str(today)

    async def stats(start, end):
        health = await database.fetch_all(
            "SELECT type, AVG(value) AS avg FROM health_metrics WHERE user_id=:uid AND date BETWEEN :s AND :e GROUP BY type",
            {"uid": uid, "s": start, "e": end}
        )
        done = await database.fetch_val(
            "SELECT COUNT(*) FROM tasks WHERE user_id=:uid AND status='done' AND date(completed_at) BETWEEN :s AND :e",
            {"uid": uid, "s": start, "e": end}
        )
        tracked = await database.fetch_val(
            """SELECT COALESCE(SUM(ts.duration_minutes),0)
               FROM task_sessions ts JOIN tasks t ON t.id=ts.task_id
               WHERE t.user_id=:uid AND date(ts.started_at) BETWEEN :s AND :e""",
            {"uid": uid, "s": start, "e": end}
        )
        return {
            "week_start": start,
            "health": {r["type"]: round(float(r["avg"]), 2) for r in health},
            "tasks_done": done or 0,
            "time_tracked_minutes": tracked or 0,
        }

    return {
        "current_week":  await stats(week_start, week_end),
        "previous_week": await stats(prev_start, prev_end),
    }
