"""
agents/competitor_agent.py
------------------------------
Agent: Competitor Research Agent

Refactored to match the reference project's architecture exactly:
- Class-based agent with dependency injection (llm, search tools)
- Runs multiple targeted search queries (not one broad query)
- LLM output forced through a validated Pydantic schema
  (CompetitorResearch), with automatic retry on invalid output
- Deterministic relevance filtering applied to search results
  BEFORE they reach the LLM, so irrelevant results (e.g. momos
  results for a panipuri idea) never get passed to the model at all -
  this preserves our earlier fix while adopting the reference's
  structural pattern.

Responsibilities
----------------
- Find direct and indirect competitors
- Analyse strengths / weaknesses per competitor
- Identify market gaps and differentiation opportunities

Tools  : DuckDuckGoTool (multi-query search), LLMTool (structured output)
Input  : extracted idea + search context
Output : CompetitorResearch (validated Pydantic model)
"""

from __future__ import annotations
import json
import logging

from models import CompetitorResearch
from tools.llm_tool import LLMTool
from tools.duckduckgo_tool import DuckDuckGoTool
from tools.validators import filter_relevant_results_with_fallback

logger = logging.getLogger("agents.competitor_agent")


COMPETITOR_SYSTEM_PROMPT = """You are a competitive research analyst.

Given a startup idea and web search context, identify direct and
indirect competitors, assess competitive intensity, and identify a
market gap.

IMPORTANT: Base your answer ONLY on the search context provided. If
the search context does not contain relevant information about real
competitors, say so honestly in market_gap rather than inventing
company names. Do not use any information not present in the search
context or the idea description.

Return ONLY valid JSON matching this schema:
{
  "direct_competitors": [{"name": "...", "strength": "...", "weakness": "...", "source_url": "..."}],
  "indirect_competitors": [{"name": "...", "strength": "...", "weakness": "...", "source_url": "..."}],
  "market_gap": "...",
  "competitive_intensity": "low" | "medium" | "high" | "unknown"
}
"""


class CompetitorResearchAgent:
    NAME = "CompetitorResearch"

    def __init__(self, llm: LLMTool, search: DuckDuckGoTool):
        self._llm = llm
        self._search = search

    def run(self, extracted: dict) -> CompetitorResearch:
        logger.info("[%s] Agent started", self.NAME)

        if not extracted:
            raise ValueError("CompetitorResearchAgent requires extracted idea data")

        industry = extracted.get("industry", "")
        idea_name = extracted.get("idea_name", "")
        target_customer = extracted.get("target_customer", "")

        # Multiple targeted queries, matching the reference project's
        # pattern - broader coverage than a single search
        queries = [
            f"{industry} startups competitors",
            f"best apps for {target_customer} {industry}",
            f"{idea_name} alternatives",
            f"{industry} market players",
        ]

        logger.info("[%s] Running %d searches", self.NAME, len(queries))
        search_responses = self._search.multi_search(queries)

        # Deterministic relevance filtering BEFORE building LLM
        # context - this is what prevents irrelevant results (the
        # panipuri/momos problem) from ever reaching the model
        all_hits = []
        for sr in search_responses:
            for hit in sr.hits:
                all_hits.append({"title": hit.get("title", ""), "content": hit.get("snippet", ""), "url": hit.get("url", "")})
        relevant_hits = filter_relevant_results_with_fallback(extracted, all_hits, min_relevance=0.20, min_results=6)

        if not relevant_hits:
            logger.info("[%s] No relevant search results found after filtering", self.NAME)
            return CompetitorResearch(
                market_gap="No relevant competitor data was found in search results for this specific idea.",
                competitive_intensity="unknown",
            )

        search_context = "\n".join(
            f"- {h['title']}: {h['content'][:300]} ({h['url']})" for h in relevant_hits[:10]
        )

        user_prompt = (
            f"Startup Idea: {idea_name}\n"
            f"Industry: {industry}\n"
            f"Target Customer: {target_customer}\n\n"
            f"Web Search Results (already filtered for relevance):\n{search_context}\n\n"
            "Based ONLY on the above, produce the competitor research JSON."
        )

        result: CompetitorResearch = self._llm.call_structured(
            COMPETITOR_SYSTEM_PROMPT,
            user_prompt,
            CompetitorResearch,
        )

        logger.info(
            "[%s] Agent completed - direct=%d | indirect=%d | intensity=%s",
            self.NAME,
            len(result.direct_competitors),
            len(result.indirect_competitors),
            result.competitive_intensity,
        )
        return result


# ---------------------------------------------------------------------
# Adapter function - keeps the SAME call signature the rest of our
# pipeline (orchestrator.py) already uses: analyze_competitors(extracted,
# search_results) -> dict. This means only THIS file changes; nothing
# else in the orchestrator or Streamlit UI needs to be touched.
# ---------------------------------------------------------------------
from app.config import GROQ_API_KEY, MODEL_NAME

_llm_tool = LLMTool(api_key=GROQ_API_KEY, model_name=MODEL_NAME)
_search_tool = DuckDuckGoTool()
_agent = CompetitorResearchAgent(llm=_llm_tool, search=_search_tool)


def analyze_competitors(extracted: dict, search_results: dict) -> dict:
    result = _agent.run(extracted)
    return {
        "competitors": [
            {"name": c.name, "strength": c.strength, "weakness": c.weakness, "url": c.source_url}
            for c in (result.direct_competitors + result.indirect_competitors)
        ],
        "market_gap": result.market_gap,
        "competitive_intensity": result.competitive_intensity,
    }
