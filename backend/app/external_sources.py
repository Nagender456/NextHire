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


def _fetch(
    url: str,
    accept: str = "text/html",
    extra_headers: dict[str, str] | None = None,
) -> bytes:
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
    req_headers = {
        "Accept": accept,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) NextHire/1.0",
    }
    if extra_headers:
        req_headers.update(extra_headers)
    request = Request(
        url,
        headers=req_headers,
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
        if not languages and repo.get("language"):
            languages = [str(repo["language"])]
        description = str(repo.get("description") or "").strip()
        readme = str(repo.get("readme") or "").strip()
        candidates.append(
            {
                "source_id": f"{username}/{name}",
                "source_url": repo.get("html_url") or f"https://github.com/{username}/{name}",
                "entity_type": "projects",
                "data": {
                    "name": name,
                    "description": f"{description}\n\n{readme}".strip(),
                    "technologies": sorted(set(topics + languages)),
                    "url": str(repo.get("html_url") or f"https://github.com/{username}/{name}"),
                },
            }
        )
    return candidates


def _fetch_github_html(username: str) -> list[dict]:
    url = f"https://github.com/{username}?tab=repositories"
    try:
        html = _fetch(url, "text/html").decode("utf-8", errors="replace")
    except Exception as error:
        raise SourceFetchError("SOURCE_UNAVAILABLE") from error

    items = re.findall(r'<li class="col-12 d-flex[^"]*">(.*?)</li>', html, re.DOTALL)
    if not items:
        items = re.findall(r'<li[^>]*itemprop="owns"[^>]*>(.*?)</li>', html, re.DOTALL)

    payload = []
    for item in items:
        name_m = re.search(r'itemprop="name codeRepository"[^>]*>\s*([^\s<]+)', item)
        if not name_m:
            continue
        name = name_m.group(1).strip()
        desc_m = re.search(r'itemprop="description"[^>]*>\s*([^<]+)', item)
        desc = desc_m.group(1).strip() if desc_m else ""
        lang_m = re.search(r'itemprop="programmingLanguage"[^>]*>\s*([^<]+)', item)
        lang = lang_m.group(1).strip() if lang_m else ""
        topics = [
            t.strip()
            for t in re.findall(r'class="topic-tag[^"]*"[^>]*>\s*([^<]+)', item)
            if t.strip()
        ]
        payload.append(
            {
                "name": name,
                "description": desc,
                "language": lang,
                "topics": topics,
                "html_url": f"https://github.com/{username}/{name}",
            }
        )

    if not payload:
        # Check if user profile exists
        try:
            _fetch(f"https://github.com/{username}", "text/html")
            return []
        except Exception:
            raise SourceFetchError("SOURCE_UNAVAILABLE")

    return _github_candidates(payload, username)


def fetch_github(request: GitHubSourceRequest) -> list[dict]:
    import os

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    extra_headers = {"Authorization": f"Bearer {token}"} if token else None
    url = f"https://api.github.com/users/{request.username}/repos?per_page=100"
    try:
        if extra_headers:
            raw = _fetch(url, "application/vnd.github+json", extra_headers=extra_headers)
        else:
            raw = _fetch(url, "application/vnd.github+json")
        payload = json.loads(raw)
        if not isinstance(payload, list):
            raise SourceFetchError("SOURCE_INVALID_RESPONSE")

        for repo in payload[:20]:
            languages_url = repo.get("languages_url")
            if isinstance(languages_url, str):
                try:
                    if extra_headers:
                        lang_raw = _fetch(languages_url, "application/vnd.github+json", extra_headers=extra_headers)
                    else:
                        lang_raw = _fetch(languages_url, "application/vnd.github+json")
                    languages = json.loads(lang_raw)
                    if isinstance(languages, dict):
                        repo["languages"] = languages
                except Exception:
                    repo["languages"] = {}
            readme_url = repo.get("contents_url")
            if isinstance(readme_url, str):
                try:
                    if extra_headers:
                        readme_raw = _fetch(f"{readme_url}/README", "application/vnd.github+json", extra_headers=extra_headers)
                    else:
                        readme_raw = _fetch(f"{readme_url}/README", "application/vnd.github+json")
                    readme_payload = json.loads(readme_raw)
                    if isinstance(readme_payload, dict):
                        encoded = readme_payload.get("content", "")
                        if isinstance(encoded, str):
                            repo["readme"] = base64.b64decode(encoded).decode(
                                "utf-8", errors="replace"
                            )[:4000]
                except Exception:
                    repo["readme"] = ""
        return _github_candidates(payload, request.username)
    except Exception as exc:
        # If unauthenticated GitHub API is rate-limited (403) or fails, fallback to HTML scraping
        try:
            return _fetch_github_html(request.username)
        except Exception:
            raise SourceFetchError("SOURCE_UNAVAILABLE") from exc



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
