from app.job_queue import JobQueue


def test_queue_claim_complete_and_counts_are_durable(tmp_path):
    path = str(tmp_path / "jobs.sqlite3")
    queue = JobQueue(path)
    job_id = queue.enqueue("company_refresh", "company-1")

    claimed = queue.claim()
    assert [row["id"] for row in claimed] == [job_id]
    assert queue.counts()["running"] == 1

    queue.complete(job_id)
    reopened = JobQueue(path)
    assert reopened.counts()["completed"] == 1


def test_queue_dead_letters_after_bounded_retries(tmp_path):
    queue = JobQueue(str(tmp_path / "jobs.sqlite3"))
    job_id = queue.enqueue("company_refresh", "company-1")
    for _ in range(3):
        row = queue.claim()[0]
        queue.fail(row["id"], "temporary failure")
    assert queue.counts()["dead_letter"] == 1
    assert job_id == row["id"]
