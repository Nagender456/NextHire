from app.job_ingestion import (
    ADAPTERS,
    GenericCareerAdapter,
    discover_career_url,
    ingestion_store,
    register_adapter,
)
from app.models import CompanyCreate


def test_refresh_reports_incremental_deltas_and_freshness(monkeypatch):
    ingestion_store.companies.clear()
    ingestion_store.jobs.clear()
    ingestion_store.crawls.clear()
    company = ingestion_store.add_company(
        CompanyCreate(
            name="Example",
            website="https://example.com",
            career_page_url="https://example.com/careers",
        ),
        verified=True,
    )
    monkeypatch.setattr(
        "app.job_ingestion._fetch",
        lambda _url: '<a href="/jobs/backend">Backend Engineer</a>',
    )
    first = ingestion_store.refresh(company.id)
    second = ingestion_store.refresh(company.id)
    assert (first.jobs_added, first.jobs_updated) == (1, 0)
    assert (second.jobs_added, second.jobs_updated) == (0, 0)
    assert ingestion_store.companies[company.id].last_sync_status == "succeeded"
    assert ingestion_store.companies[company.id].last_synced_at is not None


def test_official_career_url_discovery_stays_on_domain(monkeypatch):
    pages = {
        "https://example.com": '<a href="/about">About</a><a href="/careers">Careers</a>',
        "https://example.com/careers": "<h1>Jobs</h1>",
    }
    monkeypatch.setattr("app.job_ingestion._fetch", pages.__getitem__)
    assert discover_career_url("https://example.com") == "https://example.com/careers"


def test_company_specific_adapter_can_be_registered():
    class TestAdapter(GenericCareerAdapter):
        name = "test-provider"

        def discover_jobs(self, company):
            return []

    adapter = TestAdapter()
    register_adapter(adapter)
    assert "test-provider" in ADAPTERS
