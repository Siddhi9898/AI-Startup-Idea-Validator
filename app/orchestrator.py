"""
Orchestrator Agent (parallelized for speed)
------------------------------------------------
Runs independent agents concurrently using threads instead of
strictly sequentially, to cut total pipeline time. Dependencies
that must stay sequential (e.g. SWOT needs Market Analysis +
Competitor data) are preserved.
"""

from concurrent.futures import ThreadPoolExecutor

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


def run_pipeline(idea_text: str, target_market: str = None) -> dict:
    state = SharedState(idea_text)

    # Step 1: Idea Extraction (includes feasibility/ethics check)
    state.extracted = extract_idea(state.idea_text)

    if state.extracted.get("invalid"):
        return {
            "invalid": True,
            "reason": state.extracted.get("reason", "Please enter a valid startup idea."),
        }

    if target_market:
        state.extracted["location"] = target_market

    # Step 2: Web Search Agent
    state.search_results = search_market(state.extracted)

    if state.search_results.get("error"):
        return {
            "invalid": True,
            "reason": state.search_results["error"],
        }

    # Step 3 + 4: Market Analysis and Competitor Agent run in PARALLEL
    # (both only depend on extracted + search_results)
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_market = executor.submit(analyze_market, state.extracted, state.search_results)
        future_competitors = executor.submit(analyze_competitors, state.extracted, state.search_results)
        state.market_analysis = future_market.result()
        state.competitors = future_competitors.result()

    # Step 5: SWOT & Risk Agent (needs both market_analysis and competitors)
    state.swot = analyze_swot(state.extracted, state.market_analysis, state.competitors)

    # Step 6 + 7: MVP and GTM Strategy run in PARALLEL
    # (MVP needs SWOT, GTM only needs market_analysis - independent of each other)
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_mvp = executor.submit(recommend_mvp, state.extracted, state.swot)
        future_gtm = executor.submit(generate_gtm_strategy, state.extracted, state.market_analysis)
        state.mvp = future_mvp.result()
        state.gtm = future_gtm.result()

    # Step 8: Viability Score (fast, no AI call - just math)
    state.viability = calculate_viability_score(
        extracted=state.extracted,
        search_results=state.search_results,
        market_analysis=state.market_analysis,
        swot=state.swot,
    )

    # Step 9: Insight Agent - all 4 calls run in PARALLEL (all independent)
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_blind_spots = executor.submit(find_blind_spots, state.extracted)
        future_summary = executor.submit(generate_honest_summary, state.extracted, state.search_results, state.viability)
        future_pitch = executor.submit(generate_elevator_pitch, state.extracted)
        future_funding = executor.submit(suggest_funding_paths, state.extracted, state.viability)

        state.blind_spots = future_blind_spots.result()["blind_spots"]
        state.honest_summary = future_summary.result()["honest_summary"]
        state.elevator_pitch = future_pitch.result()
        state.funding_suggestions = future_funding.result()["funding_suggestions"]

    # Step 10: Report Agent (fast, no AI call)
    state.report = generate_report(state.to_dict())

    result = state.to_dict()
    result["invalid"] = False
    return result
