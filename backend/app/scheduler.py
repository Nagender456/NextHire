"""Background scraper scheduler that crawls career pages periodically (default: every 12 hours)."""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from app.admin_store import admin_store
from app.job_ingestion import ingestion_store

logger = logging.getLogger("nexthire.scraper_scheduler")


class ScraperScheduler:
    def __init__(self, interval_seconds: int = 12 * 3600) -> None:
        self.interval_seconds = interval_seconds
        self.is_running = False
        self.last_run_at: datetime | None = None
        self.next_run_at: datetime | None = None
        self.total_runs = 0
        self.last_result: dict[str, Any] = {}
        self._task: asyncio.Task | None = None

    async def run_once(self) -> dict[str, Any]:
        """Execute a crawl of all active, verified companies."""
        started_at = datetime.now(UTC)
        self.last_run_at = started_at
        logger.info("Starting scheduled Naukri job scraping for companies (every 12h)...")

        target_companies = [
            c for c in ingestion_store.companies.values()
            if c.active
        ]

        results = []
        for company in target_companies:
            try:
                result = await asyncio.to_thread(ingestion_store.refresh, company.id)
                results.append({
                    "company_id": company.id,
                    "company_name": company.name,
                    "status": result.status,
                    "jobs_found": result.jobs_found,
                    "jobs_added": result.jobs_added,
                    "jobs_updated": result.jobs_updated,
                    "jobs_closed": result.jobs_closed,
                    "error_code": result.error_code,
                })
            except Exception as exc:
                logger.error("Error scraping company %s: %s", company.name, exc)
                results.append({
                    "company_id": company.id,
                    "company_name": company.name,
                    "status": "failed",
                    "jobs_found": 0,
                    "jobs_added": 0,
                    "jobs_updated": 0,
                    "jobs_closed": 0,
                    "error_code": str(exc),
                })

        admin_store.activity("periodic_scrape_12h")
        self.total_runs += 1
        completed_at = datetime.now(UTC)
        self.next_run_at = completed_at + timedelta(seconds=self.interval_seconds)
        self.last_result = {
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
            "companies_crawled": len(target_companies),
            "results": results,
        }
        logger.info(
            "Scheduled scrape completed. Crawled %d companies. Next run at %s",
            len(target_companies),
            self.next_run_at.isoformat(),
        )
        return self.last_result

    async def _loop(self) -> None:
        self.next_run_at = datetime.now(UTC) + timedelta(seconds=self.interval_seconds)
        while self.is_running:
            try:
                await asyncio.sleep(self.interval_seconds)
                if not self.is_running:
                    break
                await self.run_once()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Unexpected error in scraper scheduler loop: %s", e)
                await asyncio.sleep(60)

    def start(self) -> None:
        if self.is_running:
            return
        self.is_running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("Scraper scheduler started with %s-second interval (12h)", self.interval_seconds)

    def stop(self) -> None:
        self.is_running = False
        if self._task and not self._task.done():
            self._task.cancel()
        logger.info("Scraper scheduler stopped")

    def get_status(self) -> dict[str, Any]:
        return {
            "enabled": self.is_running,
            "interval_hours": round(self.interval_seconds / 3600, 1),
            "interval_seconds": self.interval_seconds,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "next_run_at": self.next_run_at.isoformat() if self.next_run_at else None,
            "total_runs": self.total_runs,
            "active_companies": len([c for c in ingestion_store.companies.values() if c.active and c.career_page_url]),
            "last_result": self.last_result,
        }


scraper_scheduler = ScraperScheduler(interval_seconds=12 * 3600)
