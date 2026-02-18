from pydantic import BaseModel

class TaskPayload(BaseModel):
    task_id: int
    product_url: str