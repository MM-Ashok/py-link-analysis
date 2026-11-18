import hashlib
import time
from app.config import settings
from app.services.website_extractor import extract_website
from app.services.llm_service import analyze_with_llm
from app.schemas import LinkAnalysisResponse

_CACHE = {}

async def analyze_website(url: str) -> dict:
    key = hashlib.sha256(url.encode()).hexdigest()
    cached = _CACHE.get(key)
    if cached and time.time() - cached["time"] < settings.cache_ttl_seconds:
        return cached["data"]
    extracted = await extract_website(url)
    llm_result = await analyze_with_llm(extracted)
    brand = llm_result["brand"]
    result = {
        "success": True,
        "website": extracted["final_url"],
        "brand": brand,
        "analysis": llm_result["analysis"],
        "extraction": {
            "page_title": extracted["title"],
            "meta_description": extracted["meta_description"],
            "headings_found": len(extracted["headings"]),
            "content_characters_analyzed": extracted["content_chars"],
            "http_status": extracted["http_status"],
            "canonical": extracted["canonical"],
        },
        "disclaimer": "AI-generated recommendations are hypotheses. Competitor suggestions are not live-verified; verify competitor claims, service claims, and SEO decisions before acting."
    }
    # Validate the generated payload before caching/returning.
    validated = LinkAnalysisResponse.model_validate(result).model_dump()
    _CACHE[key] = {"time": time.time(), "data": validated}
    return validated
