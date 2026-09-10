"""
Orchestrator Agent
--------------------
Coordinates the full validation pipeline.

Speed improvement (fixes P3): Market Analysis and Competitor Agent
both only depend on `extracted` + `search_results` - neither depends
on the other's output. Running them concurrently (instead of one
after another) cuts real wall-clock time, since these are the two
slowest deep-search steps. SWOT still waits for both to finish since
it genuinely needs both as input.
"""

import concurrent.futures

from state.memory import SharedState
from tools.validators import validate_extracted_idea, validate_search_results

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
from agents.summary_agent import generate_quick_summary


def run_pipeline(idea_text: str, target_market: str = "") -> dict:
    state = SharedState(idea_text)

    state.extracted = extract_idea(state.idea_text)
    if target_market:
        state.extracted["location"] = target_market
    check = validate_extracted_idea(state.extracted)
    state.log_step("idea_extraction", check["is_valid"], str(check.get("missing_fields", "")))

    state.search_results = search_market(state.extracted, target_market)
    check = validate_search_results(state.search_results.get("results", []))
    state.log_step("web_search", check["is_valid"], check.get("reason", ""))

    # Speed fix (P3): run Market Analysis and Competitor Agent
    # concurrently - neither depends on the other, so this cuts
    # real wall-clock time instead of running them one after another.
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        market_future = executor.submit(analyze_market, state.extracted, state.search_results)
        competitor_future = executor.submit(analyze_competitors, state.extracted, state.search_results)
        state.market_analysis = market_future.result()
        state.competitors = competitor_future.result()
    state.log_step("market_analysis", True, "")
    state.log_step("competitor_analysis", True, "")

    state.swot = analyze_swot(state.extracted, state.market_analysis, state.competitors)
    state.log_step("swot_risk", True, "")

    state.mvp = recommend_mvp(state.extracted, state.swot)
    state.log_step("mvp_recommendation", True, "")

    state.gtm = generate_gtm_strategy(state.extracted, state.market_analysis)
    state.log_step("gtm_strategy", True, "")

    state.viability = calculate_viability_score(
        extracted=state.extracted,
        search_results=state.search_results,
        market_analysis=state.market_analysis,
        swot=state.swot,
    )
    state.log_step("viability_score", True, "")

    state.blind_spots = find_blind_spots(state.extracted)["blind_spots"]
    state.honest_summary = generate_honest_summary(
        state.extracted, state.search_results, state.viability
    )["honest_summary"]
    state.elevator_pitch = generate_elevator_pitch(state.extracted)
    state.funding_suggestions = suggest_funding_paths(
        state.extracted, state.viability
    )["funding_suggestions"]
    state.log_step("insight_layer", True, "")

    state.report = generate_report(state.to_dict())
    state.log_step("report_generation", True, "")

    # Quick Summary (fixes P2) - one short paragraph condensing
    # everything, so the user doesn't have to read every agent's
    # full output to get the gist.
    state.quick_summary = generate_quick_summary(state.to_dict())
    state.log_step("quick_summary", True, "")

    return state.to_dict()
