from backend.app.utils.security import is_safe_url, sanitize_search_query


def test_ssrf_blocks_loopback():
    assert is_safe_url("http://127.0.0.1/admin") is False
    assert is_safe_url("http://localhost:8000/metrics") is False
    assert is_safe_url("http://[::1]/secret") is False


def test_ssrf_blocks_private_networks():
    assert is_safe_url("http://10.0.0.1/internal") is False
    assert is_safe_url("http://192.168.1.1/router") is False
    assert is_safe_url("http://172.16.0.5/api") is False


def test_ssrf_blocks_cloud_metadata():
    assert is_safe_url("http://169.254.169.254/latest/meta-data/") is False
    assert is_safe_url("http://metadata.google.internal/computeMetadata/v1/") is False


def test_ssrf_allows_public_https():
    # Public domains
    assert is_safe_url("https://en.wikipedia.org/wiki/Jasprit_Bumrah") is True
    assert is_safe_url("https://www.bbc.com/news") is True


def test_sanitize_query():
    raw = "  Jasprit \x00 Bumrah \t\n cricket  "
    cleaned = sanitize_search_query(raw)
    assert cleaned == "Jasprit Bumrah cricket"
