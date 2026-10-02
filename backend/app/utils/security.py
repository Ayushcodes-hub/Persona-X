import ipaddress
import re
import socket
from urllib.parse import urlparse


BLOCKED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]


def is_safe_url(url: str) -> bool:
    """
    Validate that a URL is safe to retrieve and does not target internal / loopback / SSRF targets.
    """
    if not url or not isinstance(url, str):
        return False

    url = url.strip()
    try:
        parsed = urlparse(url)
    except Exception:
        return False

    if parsed.scheme.lower() not in {"http", "https"}:
        return False

    hostname = parsed.hostname
    if not hostname:
        return False

    # Block localhost by name
    if hostname.lower() in {"localhost", "127.0.0.1", "::1", "0.0.0.0"}:
        return False

    # Block AWS / GCP / Azure metadata hostnames
    if "metadata.google.internal" in hostname.lower() or "169.254" in hostname:
        return False

    try:
        # Resolve hostname to IP addresses
        addr_info = socket.getaddrinfo(hostname, None)
        for _, _, _, _, sockaddr in addr_info:
            ip_str = sockaddr[0]
            ip_obj = ipaddress.ip_address(ip_str)

            for blocked in BLOCKED_NETWORKS:
                if ip_obj in blocked:
                    return False
    except socket.gaierror:
        # If hostname does not resolve, it's not a reachable web target
        return False
    except Exception:
        return False

    return True


def sanitize_search_query(query: str) -> str:
    """
    Clean and sanitize user research query strings.
    """
    if not query:
        return ""
    # Strip dangerous characters, normalize whitespace
    cleaned = re.sub(r"[\x00-\x1f\x7f]", "", query)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:300]
