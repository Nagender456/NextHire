from app.config import Settings
from app.job_ingestion import CrawlError, JobIngestionStore
from app.metrics import Metrics
from app.models import CompanyCreate


def test_metrics_registry_exposes_prometheus_without_external_services():
    registry = Metrics()
    registry.increment("requests_total")
    registry.increment("responses_200", 2)

    output = registry.prometheus()

    assert "nexthire_requests_total 1" in output
    assert "nexthire_responses_200 2" in output


def test_failed_ingestion_creates_an_alert(monkeypatch):
    store = JobIngestionStore()
    company = store.add_company(
        CompanyCreate(
            name="Example",
            website="https://example.com",
            career_page_url="https://example.com/careers",
        ),
        verified=True,
    )
    monkeypatch.setattr(
        "app.job_ingestion.GenericCareerAdapter.discover_jobs",
        lambda _self, _company: (_ for _ in ()).throw(
            CrawlError("CAREER_SOURCE_UNAVAILABLE")
        ),
    )

    result = store.refresh(company.id)

    assert result.status == "failed"
    assert store.alerts[0]["code"] == "INGESTION_FAILED"
    assert store.alerts[0]["company_id"] == company.id


def test_managed_service_settings_are_environment_driven(monkeypatch):
    monkeypatch.setenv("REPOSITORY_BACKEND", "mongo")
    monkeypatch.setenv("MONGODB_URL", "mongodb://managed.example/nexthire")
    monkeypatch.setenv("SESSION_SECRET", "test-secret")
    settings = Settings()

    assert settings.repository_backend == "mongo"
    assert settings.mongodb_url == "mongodb://managed.example/nexthire"
