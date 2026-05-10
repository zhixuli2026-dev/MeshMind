import json
from uuid import UUID

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from meshmind.db.engine import AsyncSessionFactory

router = APIRouter(prefix="/workspaces/{workspace_id}/sse", tags=["sse"])


# In-memory task registry (shared with async task manager)
_task_registry: dict[str, dict] = {}


def register_task(task_id: str):
    _task_registry[task_id] = {"status": "pending", "progress": 0}


def update_task(task_id: str, **kwargs):
    if task_id in _task_registry:
        _task_registry[task_id].update(kwargs)


@router.get("/task/{task_id}")
async def task_sse(workspace_id: str, task_id: str):
    async def event_stream():
        import asyncio
        while True:
            task = _task_registry.get(task_id)
            if task is None:
                yield {"event": "task_error", "data": json.dumps({"message": "Task not found"})}
                break

            status = task.get("status")
            if status == "done":
                yield {"event": "task_complete", "data": json.dumps({
                    "status": "done",
                    "created_nodes": task.get("created_nodes", []),
                    "updated_nodes": task.get("updated_nodes", []),
                    "conflicts": task.get("conflicts", []),
                })}
                break
            elif status == "error":
                yield {"event": "task_error", "data": json.dumps({"message": task.get("error", "")})}
                break
            else:
                yield {"event": "task_progress", "data": json.dumps({
                    "status": status, "progress": task.get("progress", 0),
                })}

            await asyncio.sleep(1)

    return EventSourceResponse(event_stream())
