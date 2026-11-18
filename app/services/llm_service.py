import traceback
import json
import asyncio
from app.config import settings

class LLMError(Exception):
    pass

SYSTEM_PROMPT = """You are a careful website business and SEO analyst. Use only the supplied website evidence for claims about the submitted brand and its services. You may suggest likely competitors, but label them as AI-generated suggestions and do not pretend you browsed competitor sites. Never invent search volumes, rankings, traffic, or measured performance. Return ONLY valid JSON matching the requested schema. If evidence is missing, say so or use a clearly qualified inference. Provide five search queries and five service entries; if fewer than five services are evidenced, mark extra ideas as 'Inferred recommendation'. Include all five platforms where suitable across the query list: Google, Facebook, Instagram, LinkedIn, X (Twitter)."""

JSON_SCHEMA = {
 "type":"object",
 "properties":{
  "brand":{"type":"object","properties":{"name":{"type":"string"},"category":{"type":"string"},"summary":{"type":"string"}},"required":["name","category","summary"],"additionalProperties":False},
  "analysis":{"type":"object","properties":{
   "competitor_analysis":{"type":"object","properties":{
    "brand_overview":{"type":"string"},"business_category":{"type":"string"},"main_products_services":{"type":"array","items":{"type":"string"}},
    "competitors":{"type":"array","items":{"type":"object","properties":{
     "name":{"type":"string"},"website":{
    "anyOf":[
        {"type":"string"},
        {"type":"null"}
    ]
},"overview":{"type":"string"},"strengths":{"type":"array","items":{"type":"string"}},
     "weaknesses_or_gaps":{"type":"array","items":{"type":"string"}},"comparison_to_brand":{"type":"string"},"evidence_type":{"type":"string"}
    },"required":["name","website","overview","strengths","weaknesses_or_gaps","comparison_to_brand","evidence_type"],"additionalProperties":False}},
    "strengths":{"type":"array","items":{"type":"string"}},"opportunities":{"type":"array","items":{"type":"string"}}
   },"required":["brand_overview","business_category","main_products_services","competitors","strengths","opportunities"],"additionalProperties":False},
   "target_search_queries":{"type":"array","items":{"type":"object","properties":{"query":{"type":"string"},"platforms":{"type":"array","items":{"type":"string"}},"intent":{"type":"string"},"business_relevance":{"type":"string"},"target_audience":{"type":"string"}},"required":["query","platforms","intent","business_relevance","target_audience"],"additionalProperties":False}},
   "seo_improvements":{"type":"object","properties":{"primary_keyword":{"type":"string"},"secondary_keywords":{"type":"array","items":{"type":"string"}},"long_tail_keywords":{"type":"array","items":{"type":"string"}},"business_keywords":{"type":"array","items":{"type":"string"}},"recommended_title":{"type":"string"},"title_primary_keyword":{"type":"string"},"meta_description":{"type":"string"},"supporting_content":{"type":"array","items":{"type":"string"}}},"required":["primary_keyword","secondary_keywords","long_tail_keywords","business_keywords","recommended_title","title_primary_keyword","meta_description","supporting_content"],"additionalProperties":False},
   "top_services":{"type":"array","items":{"type":"object","properties":{"service_name":{"type":"string"},"description":{"type":"string"},"target_industry":{"type":"string"},"target_customer":{"type":"string"},"main_benefit":{"type":"string"},"source_type":{"type":"string"}},"required":["service_name","description","target_industry","target_customer","main_benefit","source_type"],"additionalProperties":False}},
   "target_audience":{"type":"object","properties":{
    "primary_audience":{"type":"array","items":{"type":"object","properties":{"segment":{"type":"string"},"business_type":{"type":"string"},"requirement":{"type":"string"},"needs_and_challenges":{"type":"array","items":{"type":"string"}},"interests":{"type":"array","items":{"type":"string"}}},"required":["segment","business_type","requirement","needs_and_challenges","interests"],"additionalProperties":False}},
    "secondary_audience":{"type":"array","items":{"type":"object","properties":{"segment":{"type":"string"},"business_type":{"type":"string"},"requirement":{"type":"string"},"needs_and_challenges":{"type":"array","items":{"type":"string"}},"interests":{"type":"array","items":{"type":"string"}}},"required":["segment","business_type","requirement","needs_and_challenges","interests"],"additionalProperties":False}},
    "industries":{"type":"array","items":{"type":"string"}},"business_types":{"type":"array","items":{"type":"string"}},"customer_needs":{"type":"array","items":{"type":"string"}},"geographic_focus":{"type":"array","items":{"type":"string"}},"recommended_marketing_segments":{"type":"array","items":{"type":"string"}}
   },"required":["primary_audience","secondary_audience","industries","business_types","customer_needs","geographic_focus","recommended_marketing_segments"],"additionalProperties":False}
  },"required":["competitor_analysis","target_search_queries","seo_improvements","top_services","target_audience"],"additionalProperties":False}
 },
 "required":["brand","analysis"],"additionalProperties":False
}

def _prompt(website: dict) -> str:
    return f"""Analyze this website. Website URL: {website['final_url']}
Page title: {website['title']}
Meta description: {website['meta_description']}
Headings: {json.dumps(website['headings'], ensure_ascii=False)}
Extracted visible text:
{website['content']}

Return a JSON object with exactly these top-level keys:
brand: name, category, summary
analysis:
 competitor_analysis: brand_overview, business_category, main_products_services, competitors (aim for 3 credible likely competitors; qualify suggestions), strengths, opportunities
 target_search_queries: exactly 5 objects with query, platforms, intent, business_relevance, target_audience
 seo_improvements: primary_keyword, secondary_keywords, long_tail_keywords, business_keywords, recommended_title, title_primary_keyword, meta_description, supporting_content
 top_services: 5 objects with service_name, description, target_industry, target_customer, main_benefit, source_type
 target_audience: primary_audience, secondary_audience, industries, business_types, customer_needs, geographic_focus, recommended_marketing_segments

Use "Found on website" only for evidenced services; use "Inferred recommendation" for inferred services. Competitor weaknesses are hypotheses unless backed by evidence. Do not claim to have researched competitors live."""

async def _openai(prompt: str) -> dict:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt}],
        response_format={"type":"json_schema","json_schema":{"name":"website_analysis","strict":True,"schema":JSON_SCHEMA}},
        temperature=0.2,
    )
    return json.loads(response.choices[0].message.content)

# async def _gemini(prompt: str) -> dict:
#     from google import genai
#     from google.genai import types
#     client = genai.Client(api_key=settings.gemini_api_key)
#     response = await client.aio.models.generate_content(
#         model=settings.gemini_model,
#         contents=SYSTEM_PROMPT + "\n\n" + prompt,
#         config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=JSON_SCHEMA, temperature=0.2),
#     )
#     return json.loads(response.text)




async def _gemini(prompt: str) -> dict:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.gemini_api_key)

    retry_delays = [2, 5, 10]

    for attempt in range(4):
        try:
            response = await client.aio.models.generate_content(
                model=settings.gemini_model,
                contents=SYSTEM_PROMPT + "\n\n" + prompt,
               config=types.GenerateContentConfig(
    response_mime_type="application/json",
    response_json_schema=JSON_SCHEMA,
    max_output_tokens=8192,
),
            )

            if not response.text:
                raise LLMError("Gemini returned an empty response.")

            # Prefer Gemini's parsed structured response.
            if response.parsed is not None:
                if isinstance(response.parsed, dict):
                    return response.parsed

            # Fallback to JSON parsing.
            return json.loads(response.text)

        except Exception as exc:
            error_message = str(exc).upper()

            temporary_error = any(
                code in error_message
                for code in [
                    "503",
                    "429",
                    "UNAVAILABLE",
                    "RESOURCE_EXHAUSTED",
                    "HIGH DEMAND",
                ]
            )

            if not temporary_error or attempt == 3:
                raise

            wait_time = retry_delays[attempt]

            print(
                f"Gemini temporarily unavailable. "
                f"Retry {attempt + 1}/3 in {wait_time} seconds..."
            )

            await asyncio.sleep(wait_time)

    raise LLMError("Gemini failed after multiple retry attempts.")



async def _anthropic(prompt: str) -> dict:
    from anthropic import AsyncAnthropic
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    response = await client.messages.create(
        model=settings.anthropic_model, max_tokens=5000, temperature=0.2,
        system=SYSTEM_PROMPT + " Return the requested object as JSON only.",
        messages=[{"role":"user","content":prompt}],
    )
    text = "".join(block.text for block in response.content if getattr(block, "type", "") == "text")
    text = text.strip().removeprefix("```json").removesuffix("```").strip()
    return json.loads(text)

async def analyze_with_llm(website: dict) -> dict:
    provider = settings.llm_provider
    prompt = _prompt(website)
    try:
        if provider == "openai":
            if not settings.openai_api_key: raise LLMError("OPENAI_API_KEY is not configured.")
            return await _openai(prompt)
        if provider == "gemini":
            if not settings.gemini_api_key: raise LLMError("GEMINI_API_KEY is not configured.")
            return await _gemini(prompt)
        if provider == "anthropic":
            if not settings.anthropic_api_key: raise LLMError("ANTHROPIC_API_KEY is not configured.")
            return await _anthropic(prompt)
        raise LLMError("Unsupported LLM_PROVIDER. Choose openai, gemini, or anthropic.")
    except LLMError:
        raise
    
    except Exception as exc:
        traceback.print_exc()
        raise LLMError(
            f"{provider} error: {type(exc).__name__}: {str(exc)}"
        ) from exc
