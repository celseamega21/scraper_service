from app.clients.core_client import send_callback

def send_success_callback(task_id, data):
    send_callback({
        "task_id": task_id,
        "status": "SUCCESS",
        **data
    })
    print(f"Result scraping: {data}")

def send_failed_callback(task_id, error):
    send_callback({
        "task_id": task_id,
        "status": "FAILED",
        "error_code": error
    })