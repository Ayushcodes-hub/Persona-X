from datetime import datetime, timezone
from typing import Optional

import httpx
from bs4 import BeautifulSoup
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from backend.app.models.source import Source
from backend.app.models.source_capture import SourceCapture
from backend.app.utils.security import is_safe_url


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SourceCaptureService:
    """Acquire and preserve versioned public web sources with SSRF protection."""

    USER_AGENT = "PERSONA-X Research Engine/1.0"
    TIMEOUT = httpx.Timeout(
        connect=10.0,
        read=30.0,
        write=10.0,
        pool=10.0,
    )

    HTML_CONTENT_TYPES = {
        "text/html",
        "application/xhtml+xml",
    }

    TEXT_CONTENT_TYPES = {
        "text/plain",
        "text/xml",
        "application/xml",
    }

    def extract_text(self, html: str) -> str:
        soup = BeautifulSoup(html, "lxml")

        for element in soup(
            ["script", "style", "noscript", "svg", "template"]
        ):
            element.decompose()

        text = soup.get_text(" ", strip=True)

        return " ".join(text.split())

    def content_hash(self, content: str) -> str:
        return __import__("hashlib").sha256(
            content.encode("utf-8")
        ).hexdigest()

    def _next_capture_version(self, db, source_id: int) -> int:
        previous = (
            db.query(SourceCapture)
            .filter(SourceCapture.source_id == source_id)
            .order_by(SourceCapture.capture_version.desc())
            .first()
        )

        return previous.capture_version + 1 if previous else 1

    def _content_type(self, response: httpx.Response) -> str:
        return (
            response.headers.get("content-type", "")
            .split(";", 1)[0]
            .strip()
            .lower()
        )

    @retry(
        retry=retry_if_exception_type(
            (
                httpx.ConnectError,
                httpx.ConnectTimeout,
                httpx.ReadTimeout,
                httpx.WriteTimeout,
                httpx.PoolTimeout,
            )
        ),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        reraise=True,
    )
    def _fetch(self, url: str) -> httpx.Response:
        return httpx.get(
            url,
            timeout=self.TIMEOUT,
            follow_redirects=True,
            headers={
                "User-Agent": self.USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,text/plain,application/xml;q=0.9,*/*;q=0.8",
            },
        )

    def capture(self, db, source: Source) -> SourceCapture:
        version = self._next_capture_version(db, source.id)

        try:
            with db.begin_nested():
                # SSRF Protection: verify destination URL
                if not is_safe_url(source.url):
                    raise RuntimeError(
                        f"Blocked potential SSRF or unsafe URL target: {source.url}"
                    )

                response = self._fetch(source.url)
                content_type = self._content_type(response)

                if response.status_code >= 400:
                    raise RuntimeError(
                        f"HTTP {response.status_code} returned by source."
                    )

                if content_type in self.HTML_CONTENT_TYPES:
                    extracted_text = self.extract_text(response.text)
                elif content_type in self.TEXT_CONTENT_TYPES:
                    extracted_text = " ".join(response.text.split())
                else:
                    raise RuntimeError(
                        f"Unsupported content type: {content_type or 'unknown'}"
                    )

                if not extracted_text:
                    raise RuntimeError(
                        "Source returned no extractable textual content."
                    )

                digest = self.content_hash(extracted_text)

                capture = SourceCapture(
                    source_id=source.id,
                    capture_version=version,
                    retrieved_at=utc_now(),
                    http_status=response.status_code,
                    content_type=content_type or None,
                    content_hash=digest,
                    extracted_text=extracted_text,
                    capture_status="captured",
                )

                db.add(capture)
                db.flush()
                return capture

        except Exception as exc:
            capture = SourceCapture(
                source_id=source.id,
                capture_version=version,
                retrieved_at=utc_now(),
                capture_status="failed",
                error_message=str(exc),
            )

            db.add(capture)
            db.flush()
            return capture