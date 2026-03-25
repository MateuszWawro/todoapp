from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from database import database
from security import get_current_user
from models.schemas import TaskIn, TaskUpdate, SessionIn

router = APIRouter()


@router.get("")
async def list_tasks(
    status: Optional[str]   = Query(None),
    category: Optional[str] = Query(None),
    user=Depends(get_current_user)
):
    q = "SELECT * FROM tasks WHERE user_id=:uid"
    p: dict = {"uid": user["id"]}
    if status:   q += " AND status=:status";   p["status"] = status
    if category: q += " AND category=:cat";    p["cat"] = category
    rows = await database.fetch_all(q + " ORDER BY created_at DESC", p)
    return [dict(r) for r in rows]


@router.post("", status_code=201)
async def create_task(data: TaskIn, user=Depends(get_current_user)):
    task_id = await database.fetch_val(
        "INSERT INTO tasks (user_id,title,category,estimated_minutes) VALUES (:uid,:t,:c,:e) RETURNING id",
        {"uid": user["id"], "t": data.title, "c": data.category, "e": data.estimated_minutes}
    )
    return await _get(task_id, user["id"])


@router.patch("/{task_id}")
async def update_task(task_id: int, data: TaskUpdate, user=Depends(get_current_user)):
    task   = await _get(task_id, user["id"])
    fields, params = [], {"id": task_id, "uid": user["id"]}

    if data.title is not None:
        fields.append("title=:title"); params["title"] = data.title
    if data.category is not None:
        fields.append("category=:cat"); params["cat"] = data.category
    if data.estimated_minutes is not None:
        fields.append("estimated_minutes=:est"); params["est"] = data.estimated_minutes
    if data.status is not None:
        fields.append("status=:status"); params["status"] = data.status
        if data.status == "in_progress" and not task["started_at"]:
            fields.append("started_at=now()")
        if data.status == "done":
            fields.append("completed_at=now()")

    if fields:
        await database.execute(
            f"UPDATE tasks SET {', '.join(fields)} WHERE id=:id AND user_id=:uid", params
        )
    return await _get(task_id, user["id"])


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int, user=Depends(get_current_user)):
    await _get(task_id, user["id"])
    await database.execute(
        "DELETE FROM tasks WHERE id=:id AND user_id=:uid", {"id": task_id, "uid": user["id"]}
    )


@router.post("/{task_id}/sessions")
async def session(task_id: int, data: SessionIn, user=Depends(get_current_user)):
    await _get(task_id, user["id"])

    if data.action == "start":
        # zamknij inne otwarte sesje tego usera
        await database.execute(
            """UPDATE task_sessions SET
                 ended_at=now(),
                 duration_minutes=GREATEST(1, ROUND(EXTRACT(EPOCH FROM (now()-started_at))/60))
               WHERE task_id IN (SELECT id FROM tasks WHERE user_id=:uid) AND ended_at IS NULL""",
            {"uid": user["id"]}
        )
        sid = await database.fetch_val(
            "INSERT INTO task_sessions (task_id) VALUES (:tid) RETURNING id", {"tid": task_id}
        )
        await database.execute(
            "UPDATE tasks SET status='in_progress', started_at=COALESCE(started_at,now()) WHERE id=:id",
            {"id": task_id}
        )
        return {"session_id": sid, "started": True}

    if data.action == "stop":
        sess = await database.fetch_one(
            "SELECT id FROM task_sessions WHERE task_id=:tid AND ended_at IS NULL", {"tid": task_id}
        )
        if not sess:
            raise HTTPException(400, "Brak aktywnej sesji")
        await database.execute(
            """UPDATE task_sessions SET
                 ended_at=now(),
                 duration_minutes=GREATEST(1, ROUND(EXTRACT(EPOCH FROM (now()-started_at))/60)),
                 notes=:notes
               WHERE id=:id""",
            {"id": sess["id"], "notes": data.notes}
        )
        total = await database.fetch_val(
            "SELECT COALESCE(SUM(duration_minutes),0) FROM task_sessions WHERE task_id=:tid",
            {"tid": task_id}
        )
        return {"stopped": True, "total_minutes": int(total)}

    raise HTTPException(400, "action musi być 'start' lub 'stop'")


@router.get("/{task_id}/sessions")
async def get_sessions(task_id: int, user=Depends(get_current_user)):
    await _get(task_id, user["id"])
    rows = await database.fetch_all(
        "SELECT * FROM task_sessions WHERE task_id=:tid ORDER BY started_at DESC",
        {"tid": task_id}
    )
    return [dict(r) for r in rows]


async def _get(task_id: int, user_id: int):
    row = await database.fetch_one(
        "SELECT * FROM tasks WHERE id=:id AND user_id=:uid", {"id": task_id, "uid": user_id}
    )
    if not row:
        raise HTTPException(404, "Zadanie nie znalezione")
    return dict(row)
