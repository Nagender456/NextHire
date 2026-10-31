from fastapi import FastAPI
from datetime import UTC, datetime
import os

from app.job_queue import JobQueue

app = FastAPI(title="NextHire Worker", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "nexthire-worker"}


@app.post("/jobs/notifications")
async def notification_job() -> dict[str, str]:
    """Worker boundary for the scheduler to enqueue reminder delivery."""
    return {
        "status": "accepted",
        "job": "notifications",
        "queued_at": datetime.now(UTC).isoformat(),
    }


def process_queue_once(limit: int = 10) -> dict[str, int]:
    """Process durable refresh jobs; supervisors invoke this every few minutes."""
    queue = JobQueue(os.getenv("JOB_QUEUE_PATH", "nexthire-jobs.sqlite3"))
    completed = failed = 0
    for job in queue.claim(limit):
        try:
            if job["kind"] == "company_refresh":
                from app.job_ingestion import ingestion_store

                ingestion_store.refresh(job["payload"])
            queue.complete(job["id"])
            completed += 1
        except Exception as error:
            queue.fail(job["id"], str(error))
            failed += 1
    return {"completed": completed, "failed": failed}
