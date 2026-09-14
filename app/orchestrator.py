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
<<<<<<< Updated upstream
=======

Cooperative cancellation: a validation can take a while, and the
founder may want to stop and fix their input rather than wait for a
run that's already headed in the wrong direction. Python can't
safely force-kill a thread mid-network-call, so instead every step
boundary checks `cancel_event` (a threading.Event set from the UI's
"Stop" button) and raises PipelineCancelled if it's been set - this
means a cancellation takes effect at the NEXT step boundary rather
than instantly, but every step here is only a few seconds, so in
practice this is a fast, clean stop rather than a true kill -9.

progress_callback(step_name): optional hook the UI can pass in to
know which step just finished, purely for showing "now running: X"
- has no effect on the pipeline's actual behavior.
>>>>>>> Stashed changes
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
from agents.suggestion_agent import generate_improvement_suggestions
from agents.report_agent import generate_report
from agents.summary_agent import generate_quick_summary


<<<<<<< Updated upstream
def run_pipeline(idea_text: str, target_market: str = "") -> dict:
=======
class PipelineCancelled(Exception):
    """Raised when the UI's Stop button set the cancel_event between
    pipeline steps. Callers should treat this as a clean, expected
    stop - not an error - and let the founder edit their input."""
    pass


def _check_cancelled(cancel_event):
    if cancel_event is not None and cancel_event.is_set():
        raise PipelineCancelled("Validation stopped by user.")


def run_pipeline(idea_text: str, target_market: str = "", cancel_event=None, progress_callback=None) -> dict:
    def _tick(step_name):
        _check_cancelled(cancel_event)
        if progress_callback:
            try:
                progress_callback(step_name)
            except Exception:
                pass  # progress reporting must never break the pipeline itself

>>>>>>> Stashed changes
    state = SharedState(idea_text)

    state.extracted = extract_idea(state.idea_text)
    if target_market:
        state.extracted["location"] = target_market
    check = validate_extracted_idea(state.extracted)
    state.log_step("idea_extraction", check["is_valid"], str(check.get("missing_fields", "")))
<<<<<<< Updated upstream
=======
    _tick("Idea Extraction")
>>>>>>> Stashed changes

    state.search_results = search_market(state.extracted, target_market)
    check = validate_search_results(state.search_results.get("results", []))
    state.log_step("web_search", check["is_valid"], check.get("reason", ""))
<<<<<<< Updated upstream
=======
    _tick("Web Search")
>>>>>>> Stashed changes

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
<<<<<<< Updated upstream

    state.swot = analyze_swot(state.extracted, state.market_analysis, state.competitors)
    state.log_step("swot_risk", True, "")

    state.mvp = recommend_mvp(state.extracted, state.swot)
    state.log_step("mvp_recommendation", True, "")

    state.gtm = generate_gtm_strategy(state.extracted, state.market_analysis)
    state.log_step("gtm_strategy", True, "")
=======
    _tick("Market & Competitor Analysis")

    state.swot = analyze_swot(state.extracted, state.market_analysis, state.competitors)
    state.log_step("swot_risk", True, "")
    _tick("SWOT & Risk Analysis")

    state.mvp = recommend_mvp(state.extracted, state.swot)
    state.log_step("mvp_recommendation", True, "")
    _tick("MVP Recommendation")

    state.gtm = generate_gtm_strategy(state.extracted, state.market_analysis)
    state.log_step("gtm_strategy", True, "")
    _tick("Go-To-Market Strategy")
>>>>>>> Stashed changes

    state.viability = calculate_viability_score(
        extracted=state.extracted,
        search_results=state.search_results,
        market_analysis=state.market_analysis,
        swot=state.swot,
    )
    state.log_step("viability_score", True, "")
<<<<<<< Updated upstream
=======
    _tick("Viability Scoring")
>>>>>>> Stashed changes

    state.blind_spots = find_blind_spots(state.extracted)["blind_spots"]
    state.honest_summary = generate_honest_summary(
        state.extracted, state.search_results, state.viability
    )["honest_summary"]
    state.elevator_pitch = generate_elevator_pitch(state.extracted)
    state.funding_suggestions = suggest_funding_paths(
        state.extracted, state.viability
    )["funding_suggestions"]
    state.log_step("insight_layer", True, "")
<<<<<<< Updated upstream

    state.report = generate_report(state.to_dict())
    state.log_step("report_generation", True, "")
=======
    _tick("Mentor Insights")

    state.improvement_suggestions = generate_improvement_suggestions(state.to_dict())
    state.log_step("improvement_suggestions", True, "")
    _tick("Improvement Suggestions")

    state.report = generate_report(state.to_dict())
    state.log_step("report_generation", True, "")
    _tick("Report Generation")
>>>>>>> Stashed changes

    # Quick Summary (fixes P2) - one short paragraph condensing
    # everything, so the user doesn't have to read every agent's
    # full output to get the gist.
    state.quick_summary = generate_quick_summary(state.to_dict())
    state.log_step("quick_summary", True, "")
<<<<<<< Updated upstream
=======
    _tick("Quick Summary")
>>>>>>> Stashed changes

    return state.to_dict()
