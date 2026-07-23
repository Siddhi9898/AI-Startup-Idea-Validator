from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()
client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_market(structured_idea: dict) -> dict:
    query = f"competitors and market size for {structured_idea['industry']} startups like {structured_idea['idea_name']}"
    results = client.search(query=query, max_results=5)
    return results