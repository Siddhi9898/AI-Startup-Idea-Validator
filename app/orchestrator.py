"""
Orchestrator Agent
--------------------
Central coordinator for the validation workflow, as described in
docs/architecture.md. Runs the full agent pipeline in sequence,
passing shared state between agents, and aggregates the final report.
"""

from state.memory import SharedState
from agents.idea_extraction_agent import extract_idea
from agents.web_search_agent import search_market
from agents.market_analysis_agent import analyze_market
from agents.competitor_agent import analyze_competitors
from agents.swot_risk_agent import analyze_swot
from agents.mvp_recommendation_agent import recommend_mvp
from agents.gtm_strategy_agent import generate_gtm_strategy
from agents.viability_score_agent import calculate_viability_score
from agents.insight_agent import (
    find_blind_spots,
    generate_honest_summary,
    generate_elevator_pitch,
    suggest_funding_paths,
)
from agents.report_agent import generate_report


def run_pipeline(idea_text: str) -> dict:
    state = SharedState(idea_text)

    # Step 1: Idea Extraction Agent
    state.extracted = extract_idea(state.idea_text)

    # Step 2: Web Search Agent
    state.search_results = search_market(state.extracted)

    # Step 3: Market Analysis Agent
    state.market_analysis = analyze_market(state.extracted, state.search_results)

    # Step 4: Competitor Agent
    state.competitors = analyze_competitors(state.extracted, state.search_results)

    # Step 5: SWOT & Risk Agent
    state.swot = analyze_swot(state.extracted, state.market_analysis, state.competitors)

    # Step 6: MVP Recommendation Agent
    state.mvp = recommend_mvp(state.extracted, state.swot)

    # Step 7: GTM Strategy Agent
    state.gtm = generate_gtm_strategy(state.extracted, state.market_analysis)

    # Step 8: Viability Score (now uses real market_analysis + swot signals)
    state.viability = calculate_viability_score(
        extracted=state.extracted,
        search_results=state.search_results,
        market_analysis=state.market_analysis,
        swot=state.swot,
    )

    # Step 9: Insight Agent (blind spots, honest summary, pitch, funding)
    state.blind_spots = find_blind_spots(state.extracted)["blind_spots"]
    state.honest_summary = generate_honest_summary(
        state.extracted, state.search_results, state.viability
    )["honest_summary"]
    state.elevator_pitch = generate_elevator_pitch(state.extracted)
    state.funding_suggestions = suggest_funding_paths(
        state.extracted, state.viability
    )["funding_suggestions"]

    # Step 10: Report Agent - compile everything
    state.report = generate_report(state.to_dict())

    return state.to_dict()
