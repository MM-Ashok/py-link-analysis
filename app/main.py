
import logging

from fastapi import FastAPI, HTTPException

from app.schemas import LinkAnalysisRequest, LinkAnalysisResponse
from app.services.analysis_service import analyze_website
from app.services.website_extractor import WebsiteFetchError
from app.services.llm_service import LLMError


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger = logging.getLogger(__name__)


app = FastAPI(
    title="AI-Powered Website Link Analysis API",
    description="Extracts a public website and generates business, competitor, SEO, service, and audience insights.",
    version="1.0.0",
)


@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}


@app.post("/link-analysis", response_model=LinkAnalysisResponse)
async def link_analysis(payload: LinkAnalysisRequest):

    try:
        logger.info("Starting website analysis: %s", payload.url)

        result = await analyze_website(str(payload.url))

        logger.info("Website analysis completed successfully.")

        return result

    except WebsiteFetchError as exc:
        logger.exception("Website extraction failed.")
        raise HTTPException(status_code=422, detail=str(exc))

    except LLMError as exc:
        logger.exception("LLM analysis failed.")
        raise HTTPException(
            status_code=502,
            detail=f"LLM analysis failed: {exc}"
        )

    except Exception:
        logger.exception("Unexpected error during website analysis.")

        raise HTTPException(
            status_code=500,
            detail="Unexpected server error. Check application logs."
        )
