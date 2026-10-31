from time import time
from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from app.auth import github_login_url
from app.auth_store import auth_store
from app.main import app
from app.security import generate_token


@pytest.fixture(autouse=True)
def isolate_auth_store():
    fields = (
        "users",
        "sessions",
        "session_expires_at",
        "revoked_sessions",
        "reset_tokens",
        "oauth_states",
        "github_accounts",
        "github_tokens",
        "profiles",
        "career_entities",
        "documents",
        "document_contents",
        "extracted_entities",
        "external_candidates",
        "recommendation_feedback",
        "resume_versions",
        "notifications",
        "privacy_settings",
    )
    snapshots = {field: deepcopy(getattr(auth_store, field)) for field in fields}
    for field in fields:
        value = getattr(auth_store, field)
        value.clear()
    yield
    for field, snapshot in snapshots.items():
        value = getattr(auth_store, field)
        value.clear()
        value.update(snapshot)


def test_logout_revokes_server_side_session() -> None:
    client = TestClient(app)
    email = f"logout-{generate_token()}@example.com"
    assert (
        client.post(
            "/api/v1/auth/signup",
            json={
                "email": email,
                "display_name": "Logout",
                "password": "a secure password",
            },
        ).status_code
        == 201
    )
    token = client.cookies.get("nexthire_session")
    assert token in auth_store.sessions

    assert client.post("/api/v1/auth/logout").status_code == 204
    assert token not in auth_store.sessions
    assert client.get("/api/v1/auth/me").status_code == 401


def test_expired_session_is_rejected() -> None:
    client = TestClient(app)
    email = f"expired-{generate_token()}@example.com"
    assert (
        client.post(
            "/api/v1/auth/signup",
            json={
                "email": email,
                "display_name": "Expired",
                "password": "a secure password",
            },
        ).status_code
        == 201
    )
    token = client.cookies.get("nexthire_session")
    auth_store.session_expires_at[token] = time() - 1
    assert client.get("/api/v1/auth/me").status_code == 401


def test_github_login_requires_configuration_and_uses_read_only_scope(
    monkeypatch,
) -> None:
    from app.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("GITHUB_CLIENT_ID", "client-id")
    monkeypatch.setenv("GITHUB_CLIENT_SECRET", "client-secret")
    settings = get_settings()
    monkeypatch.setattr(settings, "github_client_id", "client-id")
    url = github_login_url()
    assert "scope=read%3Auser+user%3Aemail" in url
    assert "state=" in url
    state = next(iter(auth_store.oauth_states))
    assert auth_store.oauth_states[state] > time()
    get_settings.cache_clear()


def test_password_reset_revokes_existing_sessions() -> None:
    client = TestClient(app)
    email = f"reset-{generate_token()}@example.com"
    assert (
        client.post(
            "/api/v1/auth/signup",
            json={"email": email, "display_name": "Reset", "password": "old password"},
        ).status_code
        == 201
    )
    token = client.cookies.get("nexthire_session")
    reset = client.post("/api/v1/auth/password-reset/request", json={"email": email})
    assert reset.status_code == 200
    reset_token = next(iter(auth_store.reset_tokens))
    assert (
        client.post(
            "/api/v1/auth/password-reset/confirm",
            json={"token": reset_token, "password": "new password"},
        ).status_code
        == 200
    )
    assert token not in auth_store.sessions
