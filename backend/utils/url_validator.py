import ipaddress
import socket
from urllib.parse import urlparse

ALLOWED_SCHEMES = {"http", "https"}
MAX_URL_LENGTH = 2048
BLOCKED_HOSTS = {"localhost", "metadata.google.internal", "metadata"}


class InvalidURLError(ValueError):
    pass


def validate_url(url: str) -> str:
    if not url or not url.strip():
        raise InvalidURLError("URL is empty")
    url = url.strip()
    if len(url) > MAX_URL_LENGTH:
        raise InvalidURLError(f"URL exceeds {MAX_URL_LENGTH} characters")

    parsed = urlparse(url)
    scheme = (parsed.scheme or "").lower()
    if scheme not in ALLOWED_SCHEMES:
        raise InvalidURLError(f"Only http/https allowed (got {scheme!r})")
    if not parsed.hostname:
        raise InvalidURLError("URL is missing hostname")

    host = parsed.hostname.lower()
    if host in BLOCKED_HOSTS:
        raise InvalidURLError(f"Host '{host}' is blocked")

    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as e:
        raise InvalidURLError(f"Could not resolve hostname: {host}") from e

    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            raise InvalidURLError(f"URL resolves to non-public address: {ip}")

    return url
