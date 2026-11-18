# AI-Powered Website Link Analysis API

FastAPI application that fetches a public website, extracts visible content, and uses an LLM to produce structured business, competitor, search-query, SEO, service, and target-audience insights.

## Features

- `POST /link-analysis` accepts `{ "url": "https://example.com" }`.
- Extracts page title, meta description, headings, canonical URL, and visible text.
- Supports OpenAI (default), Google Gemini, or Anthropic through environment variables.
- Validates LLM output against Pydantic response models.
- Includes basic in-memory URL-result caching.
- Blocks localhost/private/reserved IP targets and re-checks redirect destinations to reduce SSRF risk.
- Returns no invented search volumes or ranking data.
- Labels competitor candidates and inferred services as AI-generated suggestions.

## Requirements

- Python 3.10+
- An API key from one supported LLM provider
- Internet access from the machine running the API

## Run locally (Windows PowerShell)

```powershell
# 1. Extract the ZIP and open the project folder
cd ai-link-analysis

# 2. Create a virtual environment
py -m venv .venv

# 3. Activate it
.venv\Scripts\Activate.ps1

# If PowerShell blocks activation, run this once for the current terminal:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 4. Install packages
python -m pip install --upgrade pip
pip install -r requirements.txt

# 5. Create your local environment file
Copy-Item .env.example .env

# 6. Open .env and replace OPENAI_API_KEY=replace_me with your real key
notepad .env

# 7. Start the API on port 4000
python -m uvicorn app.main:app --host 0.0.0.0 --port 4000 --reload
```

## Run locally (macOS / Linux)

```bash
cd ai-link-analysis
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set OPENAI_API_KEY
python -m uvicorn app.main:app --host 0.0.0.0 --port 4000 --reload
```

Open API docs at **http://localhost:4000/docs**.

## Test the endpoint

In Swagger UI (`/docs`), open `POST /link-analysis`, click **Try it out**, and send:

```json
{
  "url": "https://example.com"
}
```

Or use curl:

```bash
curl -X POST "http://localhost:4000/link-analysis" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

Example response shape (actual values depend on the submitted website and model):

```json
{
  "success": true,
  "website": "https://example.com/",
  "brand": {
    "name": "Example",
    "category": "Business category identified from the page",
    "summary": "Summary grounded in the extracted website content."
  },
  "analysis": {
    "competitor_analysis": {
      "brand_overview": "Overview based on the page.",
      "business_category": "Business category",
      "main_products_services": ["Service identified from page"],
      "competitors": [],
      "strengths": [],
      "opportunities": []
    },
    "target_search_queries": [],
    "seo_improvements": {
      "primary_keyword": "Relevant keyword",
      "secondary_keywords": [],
      "long_tail_keywords": [],
      "business_keywords": [],
      "recommended_title": "Recommended title",
      "title_primary_keyword": "Relevant keyword",
      "meta_description": "Suggested description.",
      "supporting_content": []
    },
    "top_services": [],
    "target_audience": {
      "primary_audience": [],
      "secondary_audience": [],
      "industries": [],
      "business_types": [],
      "customer_needs": [],
      "geographic_focus": [],
      "recommended_marketing_segments": []
    }
  },
  "extraction": {},
  "disclaimer": "AI-generated recommendations are hypotheses."
}
```

## Choose another provider

### Google Gemini

Set in `.env`:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-2.5-flash
```

### Anthropic

Set in `.env`:

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key
ANTHROPIC_MODEL=claude-3-5-haiku-latest
```

Restart Uvicorn after changing `.env`. Keep only your own API key in `.env`; never commit it.

## Run tests

```bash
pytest -q
```

The tests cover the health endpoint and basic invalid/local URL rejection. Live LLM integration requires a configured provider key.

## Project structure

```text
ai-link-analysis/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── services/
│   │   ├── website_extractor.py
│   │   ├── llm_service.py
│   │   ├── analysis_service.py
│   │   └── competitor_service.py
│   └── utils/
│       └── validators.py
├── tests/
│   └── test_link_analysis.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## LLM selection research (reference snapshot: 18 Nov 2026)

**Implementation default:** OpenAI `gpt-6.1-sol` as a quality-oriented default for the single-call structured analysis. If minimizing cost is the primary objective, benchmark Claude Haiku 5.5 and Gemini 2.5 Flash against the same test set; their current published token rates are lower. The code makes provider/model configurable. This is a reasoned starting choice, not a claim that it wins every benchmark.

Before submission, re-check live provider pricing and model availability because prices and model names can change. Official pricing pages:
- OpenAI: https://openai.com/api/pricing/
- Google Gemini: https://ai.google.dev/gemini-api/docs/pricing
- Anthropic: https://www.anthropic.com/pricing#api

### Comparison approach

| Provider / model candidate | Strength for this task | Cost/speed interpretation | Structured output |
|---|---|---|---|
| OpenAI GPT-6.1-sol | Strong general-purpose reasoning and schema-constrained JSON candidate | Published standard rates: $1 / 1M input and $5 / 1M output tokens | JSON Schema response format |
| Google Gemini 2.5 Flash | Fast, high-throughput model with a 1M-token context window | Published standard rates: $0.30 / 1M input and $2.50 / 1M output tokens | JSON MIME / response schema |
| Anthropic Claude Haiku 5.5 | Model positioned for high-volume, latency-sensitive extraction/classification | Published rates up to 100K context: $0.10 / 1M input and $0.50 / 1M output tokens | Request JSON and validate response in application |

### Token and cost estimate

For a typical small-business homepage after cleaning:
Planning example (5,000 input tokens + 2,500 output tokens; standard, non-cached rates):
- OpenAI GPT-6.1-sol: approximately **$0.0175** per analysis.
- Gemini 2.5 Flash: approximately **$0.00775** per analysis.
- Claude Haiku 5.5 (up to 100K input context): approximately **$0.00175** per analysis.

Estimated usage range for this application: 4,000–6,000 input tokens and 1,800–3,000 output tokens. These are planning assumptions, not measured token counts. Actual cost depends on page length, output length, provider billing rules, caching, and model version. Prices above are a snapshot checked on 18 Nov 2026; confirm before submission:
- OpenAI pricing: https://developers.openai.com/api/docs/pricing
- Gemini pricing: https://ai.google.dev/gemini-api/docs/pricing
- Anthropic pricing: https://platform.claude.com/docs/en/about-claude/pricing

For a fair report, run 10–20 representative URLs per candidate, record API usage metadata, latency, JSON validation rate, and have a human score relevance/grounding. Report median and p95 latency rather than calling an estimate a benchmark.

### Recommendation

Start with GPT-6.1-sol when answer quality and structured analysis are the priority; test Gemini 2.5 Flash and Claude Haiku 5.5 as lower-cost challengers. Use the same URL set, extracted text, prompt, and output schema for each provider. Choose the winner from observed quality, p95 latency, and cost per valid analysis—not model reputation alone. Keep a fallback provider configured operationally, but do not silently switch providers because that can change cost and data handling.

### Cost optimization

1. Remove scripts, styles, navigation, footer, and duplicate whitespace before sending text.
2. Cap HTML bytes and extracted text size (configurable in `.env`).
3. Cache analysis results for repeat requests; this starter uses a process-local cache.
4. Use one well-designed LLM call for the five sections rather than five separate calls.
5. Keep output concise and request only the required fields.
6. Log token usage and latency in a production deployment.
7. Consider Redis/shared cache and a search API for competitor verification at production scale.

## Important limitations and production hardening

- This starter fetches the submitted page only. It does not crawl the entire domain, execute JavaScript, or bypass bot protection/login walls.
- Competitor suggestions are AI-generated candidates, not live-verified competitor research. To meet a stricter research standard, integrate a reputable search API and cite the pages used to validate competitors.
- Social platforms are treated as query destinations, not keyword-volume data sources. No search volume or ranking is fabricated.
- Basic SSRF protections are included. For production, use an outbound proxy/firewall that blocks private networks, revalidate DNS at connection time, add rate limits, request-size limits, authentication, structured logging, and a persistent cache.
- In-memory caching is per worker and resets on restart.
- Some sites may block automated requests or render content client-side; those cases may return limited content or a clear fetch error.
- Do not commit `.env`, API keys, or private data.

## Deployment

Deploy on a Python host such as Render, Railway, Fly.io, or a VPS. Configure the environment variables in the hosting dashboard, install from `requirements.txt`, and use this start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

If the platform requires a fixed port, configure `PORT=4000`. After deployment, test `/health`, `/docs`, and `POST /link-analysis`. A public URL cannot be created from this local ZIP alone; you must create the hosting account/service and add your secret API key.

## GitHub submission checklist

1. Create a public repository named `ai-link-analysis`.
2. Upload the extracted project files (not your `.env`).
3. Add your deployed base URL to the README after deployment.
4. Include screenshots of `/docs` and a successful API response.
5. Verify `git status` does not show `.env` before pushing.
