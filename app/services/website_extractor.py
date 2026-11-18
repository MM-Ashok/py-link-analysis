import ipaddress
import socket
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup
from app.config import settings
from app.utils.validators import validate_public_url

class WebsiteFetchError(Exception):
    pass

def _assert_public_host(url: str):
    parsed = urlparse(url)
    host = parsed.hostname
    if not host:
        raise WebsiteFetchError("Invalid website hostname.")
    try:
        records = socket.getaddrinfo(host, None)
    except socket.gaierror:
        raise WebsiteFetchError("Website hostname could not be resolved.")
    for record in records:
        if not ipaddress.ip_address(record[4][0]).is_global:
            raise WebsiteFetchError("Website resolves to a private or reserved IP address.")

async def extract_website(url: str) -> dict:
    try:
        validate_public_url(url)
        headers = {"User-Agent": "Mozilla/5.0 (compatible; LinkAnalysisBot/1.0; +https://example.org/bot)"}
        timeout = httpx.Timeout(settings.request_timeout)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=False, headers=headers) as client:
            current = url
            response = None
            # Manually follow a small number of redirects and re-check every destination.
            for _ in range(4):
                _assert_public_host(current)
                response = await client.get(current)
                if response.status_code in (301, 302, 303, 307, 308):
                    location = response.headers.get("location")
                    if not location:
                        raise WebsiteFetchError("Website returned an invalid redirect.")
                    current = urljoin(current, location)
                    validate_public_url(current)
                    continue
                break
            if response is None:
                raise WebsiteFetchError("Could not retrieve the website.")
            if response.status_code >= 400:
                raise WebsiteFetchError(f"Website returned HTTP {response.status_code}.")
            content_type = response.headers.get("content-type", "").lower()
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                raise WebsiteFetchError("The URL did not return an HTML page.")
            if len(response.content) > settings.max_html_bytes:
                raise WebsiteFetchError("Website HTML is larger than the configured size limit.")
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "noscript", "svg", "iframe", "nav", "footer"]):
                tag.decompose()
            title = soup.title.get_text(" ", strip=True) if soup.title else ""
            description_tag = soup.find("meta", attrs={"name": "description"})
            description = description_tag.get("content", "").strip() if description_tag else ""
            headings = [h.get_text(" ", strip=True) for h in soup.find_all(["h1", "h2", "h3"]) if h.get_text(strip=True)]
            text = " ".join(soup.stripped_strings)
            text = " ".join(text.split())[:settings.max_text_chars]
            canonical_tag = soup.find("link", rel="canonical")
            canonical = canonical_tag.get("href") if canonical_tag else None
            return {
                "final_url": str(response.url),
                "title": title,
                "meta_description": description,
                "headings": headings[:60],
                "content": text,
                "canonical": canonical,
                "http_status": response.status_code,
                "content_chars": len(text),
            }
    except WebsiteFetchError:
        raise
    except httpx.TimeoutException:
        raise WebsiteFetchError("Website request timed out.")
    except httpx.RequestError:
        raise WebsiteFetchError("Could not connect to the website.")
    except Exception as exc:
        raise WebsiteFetchError(f"Website extraction failed: {type(exc).__name__}.")
