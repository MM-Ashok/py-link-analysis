"""Competitor notes.

Competitor discovery in this practical implementation is LLM-assisted from the
submitted brand context, not a live competitor-web research engine. Results are
explicitly labeled as suggestions. A production version should validate each
candidate using a search API, business directory, or manually curated dataset.
"""
def competitor_disclaimer() -> str:
    return "Competitors are AI-generated candidate suggestions, not verified live research."
