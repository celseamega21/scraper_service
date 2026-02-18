from fastapi import APIRouter
from app.schemas.task import TaskPayload
from app.services.task_runner import run_task

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

# run task scraping and send the result to core
@router.post("/run-task")
def execute(payload: TaskPayload):
    return run_task(payload)