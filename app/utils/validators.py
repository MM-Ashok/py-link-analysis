import ipaddress
import socket
from urllib.parse import urlparse
from fastapi import HTTPException

ALLOWED_SCHEMES = {"http", "https"}

def validate_public_url(url: str) -> str:
    """Reject non-web schemes, credentials, localhost and private/reserved IP destinations."""
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES or not parsed.hostname:
        raise HTTPException(status_code=422, detail="Only valid http:// or https:// website URLs are accepted.")
    if parsed.username or parsed.password:
        raise HTTPException(status_code=422, detail="URLs containing credentials are not allowed.")
    host = parsed.hostname.rstrip(".").lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".localhost") or host.endswith(".local"):
        raise HTTPException(status_code=422, detail="Local and internal hostnames are not allowed.")
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(host, None)}
    except socket.gaierror:
        raise HTTPException(status_code=422, detail="The website hostname could not be resolved.")
    if not addresses:
        raise HTTPException(status_code=422, detail="The website hostname could not be resolved.")
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if not ip.is_global:
            raise HTTPException(status_code=422, detail="Private, loopback, link-local, and reserved IP addresses are not allowed.")
    return url
