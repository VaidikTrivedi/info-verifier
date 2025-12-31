from fastapi import FastAPI, BackgroundTasks
from uuid import uuid4
from graph import app_graph

app = FastAPI()
job_store = {} # Replace with Redis in production

def run_verification_task(job_id: str, text: str):
    """Background worker function"""
    result = app_graph.invoke({"input_text": text}) # type: ignore
    job_store[job_id] = {
        "status": "COMPLETED",
        "result": result["final_report"].dict()
    }

@app.post("/verify")
async def verify_news(payload: dict, background_tasks: BackgroundTasks):
    """
    Input: {"text": "News article text..."}
    Output: {"job_id": "123-abc"}
    """
    job_id = str(uuid4())
    job_store[job_id] = {"status": "PROCESSING"}
    
    # Send to background worker
    background_tasks.add_task(run_verification_task, job_id, payload["text"])
    
    return {"job_id": job_id, "message": "Verification started. Poll /status/{job_id} for results."}

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    job = job_store.get(job_id)
    if not job:
        return {"error": "Job not found"}
    return job