import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.models import Base, Source, SourceCapture
from backend.app.services.source_capture import SourceCaptureService


def create_test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(engine)

    return engine


def create_source(db, url):
    source = Source(
        url=url,
        title="Test Source",
        publisher="test.example",
        source_type="general_web",
        source_tier=4,
        reliability_score=0.5,
        is_verified=False,
    )

    db.add(source)
    db.commit()
    db.refresh(source)

    return source


def test_extract_text_removes_non_content_elements():
    service = SourceCaptureService()

    html = """
    <html>
        <head>
            <style>.hidden { display:none; }</style>
            <script>alert('test');</script>
        </head>
        <body>
            <h1>PERSONA-X Test</h1>
            <p>Public source content.</p>
            <noscript>Ignored content.</noscript>
        </body>
    </html>
    """

    text = service.extract_text(html)

    assert "PERSONA-X Test" in text
    assert "Public source content." in text
    assert "alert" not in text
    assert "Ignored content." not in text


def test_content_hash_is_deterministic():
    service = SourceCaptureService()

    first = service.content_hash("PERSONA-X")
    second = service.content_hash("PERSONA-X")

    assert first == second
    assert len(first) == 64


def test_successful_html_capture(monkeypatch):
    engine = create_test_db()
    db = Session(engine)

    source = create_source(
        db,
        "https://example.com/persona-x-test",
    )

    response = httpx.Response(
        200,
        headers={"content-type": "text/html; charset=utf-8"},
        text="""
            <html>
                <body>
                    <h1>PERSONA-X</h1>
                    <p>Verified public source text.</p>
                </body>
            </html>
        """,
        request=httpx.Request(
            "GET",
            source.url,
        ),
    )

    monkeypatch.setattr(
        "backend.app.services.source_capture.httpx.get",
        lambda *args, **kwargs: response,
    )

    service = SourceCaptureService()

    capture = service.capture(db, source)

    assert capture.capture_status == "captured"
    assert capture.capture_version == 1
    assert capture.http_status == 200
    assert capture.content_type == "text/html"
    assert "PERSONA-X" in capture.extracted_text
    assert "Verified public source text." in capture.extracted_text
    assert len(capture.content_hash) == 64

    db.close()
    engine.dispose()


def test_capture_versions_increment(monkeypatch):
    engine = create_test_db()
    db = Session(engine)

    source = create_source(
        db,
        "https://example.com/version-test",
    )

    def fake_get(*args, **kwargs):
        return httpx.Response(
            200,
            headers={"content-type": "text/plain"},
            text="Versioned source content.",
            request=httpx.Request(
                "GET",
                source.url,
            ),
        )

    monkeypatch.setattr(
        "backend.app.services.source_capture.httpx.get",
        fake_get,
    )

    service = SourceCaptureService()

    first = service.capture(db, source)
    second = service.capture(db, source)

    assert first.capture_version == 1
    assert second.capture_version == 2

    captures = (
        db.query(SourceCapture)
        .filter(SourceCapture.source_id == source.id)
        .order_by(SourceCapture.capture_version)
        .all()
    )

    assert len(captures) == 2

    db.close()
    engine.dispose()


def test_failed_capture_is_recorded(monkeypatch):
    engine = create_test_db()
    db = Session(engine)

    source = create_source(
        db,
        "https://example.com/failure-test",
    )

    def fake_get(*args, **kwargs):
        raise httpx.ConnectError("Connection failed")

    monkeypatch.setattr(
        "backend.app.services.source_capture.httpx.get",
        fake_get,
    )

    service = SourceCaptureService()

    capture = service.capture(db, source)

    assert capture.capture_status == "failed"
    assert capture.capture_version == 1
    assert capture.error_message is not None
    assert "Connection failed" in capture.error_message

    db.close()
    engine.dispose()


def test_unsupported_content_type_is_rejected(monkeypatch):
    engine = create_test_db()
    db = Session(engine)

    source = create_source(
        db,
        "https://example.com/binary-test",
    )

    response = httpx.Response(
        200,
        headers={"content-type": "application/octet-stream"},
        content=b"\x00\x01\x02",
        request=httpx.Request(
            "GET",
            source.url,
        ),
    )

    monkeypatch.setattr(
        "backend.app.services.source_capture.httpx.get",
        lambda *args, **kwargs: response,
    )

    service = SourceCaptureService()

    capture = service.capture(db, source)

    assert capture.capture_status == "failed"
    assert "Unsupported content type" in capture.error_message

    db.close()
    engine.dispose()