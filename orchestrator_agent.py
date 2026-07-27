"""
Agent Orchestrator
-------------------
Formalizes the orchestration layer shown in the architecture diagram:
Understand Idea -> Create Plan -> Invoke Agents -> Monitor/Pass Context -> Aggregate Results.

For Milestone 1, this coordinates the agents that exist today:
Idea Extraction, Web Search, Viability Score, and the Insight Agent
(blind spots, honest summary, elevator pitch, funding suggestions).

As more agents (Market Analysis, Competitor Analysis, SWOT, MVP,
GTM, Report Generation, Conversational Advisor) are built, they get
added into run_pipeline() as additional steps, following this same
shared-state pattern.
"""

from extraction_agent import extract_idea
from search_agent import search_market
from viability_score import calculate_viability_score
from insight_agent import (
    find_blind_spots,
    generate_honest_summary,
    generate_elevator_pitch,
    suggest_funding_paths,
)


class SharedState:
    """
    Represents the 'Shared State / Memory Store' from the architecture
    diagram. Holds all intermediate and final data as agents run,
    so each agent can read what previous agents produced.
    """

    def __init__(self, idea_text: str):
        self.idea_text = idea_text
        self.extracted: dict = {}
        self.search_results: dict = {}
        self.viability: dict = {}
        self.blind_spots: list = []
        self.honest_summary: str = ""
        self.elevator_pitch: dict = {}
        self.funding_suggestions: list = []

    def to_dict(self) -> dict:
        return {
            "idea_text": self.idea_text,
            "extracted": self.extracted,
            "search_results": self.search_results,
            "viability_score": self.viability,
            "blind_spots": self.blind_spots,
            "honest_summary": self.honest_summary,
            "elevator_pitch": self.elevator_pitch,
            "funding_suggestions": self.funding_suggestions,
        }


def run_pipeline(idea_text: str) -> dict:
    """
    Runs the full Milestone 1 agent pipeline in sequence, passing
    shared state between agents, and returns the aggregated result.
    """
    state = SharedState(idea_text)

    # Step 1: Understand the idea (Idea Extraction Agent)
    state.extracted = extract_idea(state.idea_text)

    # Step 2: Web Search Agent
    state.search_results = search_market(state.extracted)

    # Step 3: Viability Score
    state.viability = calculate_viability_score(
        extracted=state.extracted,
        search_results=state.search_results,
    )

    # Step 4: Insight Agent (blind spots, honest summary, pitch, funding)
    state.blind_spots = find_blind_spots(state.extracted)["blind_spots"]
    state.honest_summary = generate_honest_summary(
        state.extracted, state.search_results, state.viability
    )["honest_summary"]
    state.elevator_pitch = generate_elevator_pitch(state.extracted)
    state.funding_suggestions = suggest_funding_paths(
        state.extracted, state.viability
    )["funding_suggestions"]

    # Step 5: Aggregate results (Shared State -> final output)
    return state.to_dict()
