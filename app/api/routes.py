from fastapi import APIRouter
from schemas.task import TaskPayload
from services.orchestrator import process_task
from fastapi import BackgroundTasks

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

# run task scraping and send the result to core
@router.post("/run-task")
def execute(payload: TaskPayload, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_task, payload)
    return {"status": "accepted"}