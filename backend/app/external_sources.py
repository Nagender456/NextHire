from __future__ import annotations

import json
import re
import base64
import ipaddress
import socket
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from app.models import (
    GitHubSourceRequest,
    LinkedInSourceRequest,
    PortfolioSourceRequest,
)

MAX_RESPONSE_BYTES = 1_000_000
FETCH_TIMEOUT_SECONDS = 5


class SourceFetchError(ValueError):
    pass


def _fetch(url: str, accept: str = "text/html") -> bytes:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise SourceFetchError("SOURCE_URL_INVALID")
    hostname = parsed.hostname
    if hostname is None:
        raise SourceFetchError("SOURCE_URL_INVALID")
    try:
        addresses = {
            info[4][0]
            for info in socket.getaddrinfo(
                hostname, parsed.port, type=socket.SOCK_STREAM
            )
        }
    except socket.gaierror as error:
        raise SourceFetchError("SOURCE_UNAVAILABLE") from error
    if any(
        ipaddress.ip_address(address).is_private
        or ipaddress.ip_address(address).is_loopback
        or ipaddress.ip_address(address).is_link_local
        for address in addresses
    ):
        raise SourceFetchError("SOURCE_URL_BLOCKED")
    request = Request(
        url,
        headers={"Accept": accept, "User-Agent": "NextHire/1.0"},
    )
    try:
        with urlopen(request, timeout=FETCH_TIMEOUT_SECONDS) as response:
            content = response.read(MAX_RESPONSE_BYTES + 1)
    except (HTTPError, URLError, TimeoutError) as error:
        raise SourceFetchError("SOURCE_UNAVAILABLE") from error
    if len(content) > MAX_RESPONSE_BYTES:
        raise SourceFetchError("SOURCE_TOO_LARGE")
    return content


def _github_candidates(payload: list[dict[str, object]], username: str) -> list[dict]:
    candidates = []
    for repo in payload:
        name = str(repo.get("name") or "").strip()
        if not name:
            continue
        topics = [str(topic) for topic in repo.get("topics", []) or []]
        language_data = repo.get("languages", {})
        languages = (
            [str(language) for language in language_data]
            if isinstance(language_data, dict)
            else []
        )
        description = str(repo.get("description") or "").strip()
        readme = str(repo.get("readme") or "").strip()
        candidates.append(
            {
                "source_id": f"{username}/{name}",
                "source_url": repo.get("html_url"),
                "entity_type": "projects",
                "data": {
                    "name": name,
                    "description": f"{description}\n\n{readme}".strip(),
                    "technologies": sorted(set(topics + languages)),
                    "url": str(repo.get("html_url") or ""),
                },
            }
        )
    return candidates


def fetch_github(request: GitHubSourceRequest) -> list[dict]:
    url = f"https://api.github.com/users/{request.username}/repos?per_page=100"
    try:
        payload = json.loads(_fetch(url, "application/vnd.github+json"))
    except json.JSONDecodeError as error:
        raise SourceFetchError("SOURCE_INVALID_RESPONSE") from error
    if not isinstance(payload, list):
        raise SourceFetchError("SOURCE_INVALID_RESPONSE")
    for repo in payload[:20]:
        languages_url = repo.get("languages_url")
        if isinstance(languages_url, str):
            try:
                languages = json.loads(
                    _fetch(languages_url, "application/vnd.github+json")
                )
                if isinstance(languages, dict):
                    repo["languages"] = languages
            except (SourceFetchError, json.JSONDecodeError):
                repo["languages"] = {}
        readme_url = repo.get("contents_url")
        if isinstance(readme_url, str):
            try:
                readme_payload = json.loads(
                    _fetch(f"{readme_url}/README", "application/vnd.github+json")
                )
                if isinstance(readme_payload, dict):
                    encoded = readme_payload.get("content", "")
                    if isinstance(encoded, str):
                        repo["readme"] = base64.b64decode(encoded).decode(
                            "utf-8", errors="replace"
                        )[:4000]
            except (SourceFetchError, json.JSONDecodeError, ValueError):
                repo["readme"] = ""
    return _github_candidates(payload, request.username)


class _ReadableTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._ignored = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript", "svg"}:
            self._ignored += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg"} and self._ignored:
            self._ignored -= 1

    def handle_data(self, data: str) -> None:
        if not self._ignored:
            text = re.sub(r"\s+", " ", data).strip()
            if text:
                self.parts.append(text)


def fetch_portfolio(request: PortfolioSourceRequest) -> list[dict]:
    url = str(request.url)
    parser = _ReadableTextParser()
    parser.feed(_fetch(url).decode("utf-8", errors="replace"))
    text = " ".join(parser.parts).strip()
    if not text:
        raise SourceFetchError("SOURCE_NO_READABLE_CONTENT")
    return [
        {
            "source_id": url,
            "source_url": url,
            "entity_type": "projects",
            "data": {
                "name": "Portfolio profile",
                "description": text[:2000],
                "url": url,
            },
        }
    ]


def parse_linkedin(request: LinkedInSourceRequest) -> list[dict]:
    text = re.sub(r"\s+", " ", request.profile_text).strip()
    return [
        {
            "source_id": "provided-profile",
            "source_url": None,
            "entity_type": "experience",
            "data": {
                "company": "LinkedIn profile",
                "title": "Provided career profile",
                "description": text[:2000],
            },
        }
    ]
