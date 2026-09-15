import sys
import os

# Allow imports from the parent folder (where extraction_agent.py and search_agent.py live)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from pydantic import BaseModel

from extraction_agent import extract_idea
from search_agent import search_market

app = FastAPI(title="AI Startup Idea Validator API")


class IdeaInput(BaseModel):
    idea_text: str


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/submit-idea")
def submit_idea(payload: IdeaInput):
    # Step 1: Run extraction agent
    extracted = extract_idea(payload.idea_text)

    # Step 2: Run search agent using the structured output from step 1
    search_results = search_market(extracted)

    return {
        "idea_text": payload.idea_text,
        "extracted": extracted,
        "search_results": search_results,
    }