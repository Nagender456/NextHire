"""Small durable job queue used by ingestion and notification workers.

SQLite keeps the local deployment dependency-free while providing durable,
claimable jobs in production when the file is placed on a persistent volume.
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4


class JobQueue:
    def __init__(self, path: str = "nexthire-jobs.sqlite3") -> None:
        self.path = path
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY, kind TEXT NOT NULL, payload TEXT NOT NULL,
                    status TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
                    available_at TEXT NOT NULL, locked_at TEXT, last_error TEXT,
                    created_at TEXT NOT NULL
                )"""
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def enqueue(self, kind: str, payload: str, delay_seconds: int = 0) -> str:
        now = datetime.now(UTC)
        job_id = f"job-{uuid4().hex}"
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO jobs VALUES (?, ?, ?, 'queued', 0, ?, NULL, NULL, ?)",
                (
                    job_id,
                    kind,
                    payload,
                    (now + timedelta(seconds=delay_seconds)).isoformat(),
                    now.isoformat(),
                ),
            )
        return job_id

    def claim(self, limit: int = 10) -> list[sqlite3.Row]:
        now = datetime.now(UTC).isoformat()
        with self._connect() as connection:
            rows = connection.execute(
                """SELECT * FROM jobs
                   WHERE status = 'queued' AND available_at <= ?
                   ORDER BY created_at LIMIT ?""",
                (now, limit),
            ).fetchall()
            for row in rows:
                connection.execute(
                    "UPDATE jobs SET status='running', locked_at=?, attempts=attempts+1 WHERE id=?",
                    (now, row["id"]),
                )
        return rows

    def complete(self, job_id: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE jobs SET status='completed' WHERE id=?", (job_id,)
            )

    def fail(self, job_id: str, error: str, max_attempts: int = 3) -> None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT attempts FROM jobs WHERE id=?", (job_id,)
            ).fetchone()
            if not row:
                return
            status = "dead_letter" if row["attempts"] >= max_attempts else "queued"
            connection.execute(
                "UPDATE jobs SET status=?, last_error=?, available_at=? WHERE id=?",
                (status, error[:500], datetime.now(UTC).isoformat(), job_id),
            )

    def counts(self) -> dict[str, int]:
        with self._connect() as connection:
            return {
                row["status"]: row["count"]
                for row in connection.execute(
                    "SELECT status, COUNT(*) AS count FROM jobs GROUP BY status"
                )
            }
