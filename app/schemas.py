from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import List, Optional

class LinkAnalysisRequest(BaseModel):
    url: HttpUrl

class Competitor(BaseModel):
    name: str
    website: Optional[str] = None
    overview: str
    strengths: List[str] = Field(default_factory=list)
    weaknesses_or_gaps: List[str] = Field(default_factory=list)
    comparison_to_brand: str
    evidence_type: str = "AI-generated suggestion; verify independently"

class SearchQuery(BaseModel):
    query: str
    platforms: List[str]
    intent: str
    business_relevance: str
    target_audience: str

class SEOImprovements(BaseModel):
    primary_keyword: str
    secondary_keywords: List[str]
    long_tail_keywords: List[str]
    business_keywords: List[str]
    recommended_title: str
    title_primary_keyword: str
    meta_description: str
    supporting_content: List[str]

class Service(BaseModel):
    service_name: str
    description: str
    target_industry: str
    target_customer: str
    main_benefit: str
    source_type: str = "Found on website"

class Audience(BaseModel):
    segment: str
    business_type: str
    requirement: str
    needs_and_challenges: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)

class CompetitorAnalysis(BaseModel):
    brand_overview: str
    business_category: str
    main_products_services: List[str]
    competitors: List[Competitor]
    strengths: List[str]
    opportunities: List[str]

class TargetAudience(BaseModel):
    primary_audience: List[Audience]
    secondary_audience: List[Audience]
    industries: List[str]
    business_types: List[str]
    customer_needs: List[str]
    geographic_focus: List[str]
    recommended_marketing_segments: List[str]

class Analysis(BaseModel):
    competitor_analysis: CompetitorAnalysis
    target_search_queries: List[SearchQuery]
    seo_improvements: SEOImprovements
    top_services: List[Service]
    target_audience: TargetAudience

class Brand(BaseModel):
    name: str
    category: str
    summary: str

class LinkAnalysisResponse(BaseModel):
    success: bool = True
    website: str
    brand: Brand
    analysis: Analysis
    extraction: dict
    disclaimer: str = "AI-generated recommendations are hypotheses. Verify competitors, service claims, and SEO decisions before acting."
