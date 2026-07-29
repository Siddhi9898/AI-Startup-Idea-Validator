"""
Shared State / Memory
-----------------------
Centralized state object passed between agents during the
validation pipeline, as described in docs/architecture.md.
"""


class SharedState:
    def __init__(self, idea_text: str):
        self.idea_text = idea_text
        self.extracted: dict = {}
        self.search_results: dict = {}
        self.market_analysis: dict = {}
        self.competitors: dict = {}
        self.swot: dict = {}
        self.mvp: dict = {}
        self.gtm: dict = {}
        self.viability: dict = {}
        self.blind_spots: list = []
        self.honest_summary: str = ""
        self.elevator_pitch: dict = {}
        self.funding_suggestions: list = []
        self.report: str = ""

    def to_dict(self) -> dict:
        return {
            "idea_text": self.idea_text,
            "extracted": self.extracted,
            "search_results": self.search_results,
            "market_analysis": self.market_analysis,
            "competitors": self.competitors,
            "swot": self.swot,
            "mvp": self.mvp,
            "gtm": self.gtm,
            "viability_score": self.viability,
            "blind_spots": self.blind_spots,
            "honest_summary": self.honest_summary,
            "elevator_pitch": self.elevator_pitch,
            "funding_suggestions": self.funding_suggestions,
            "report": self.report,
        }
