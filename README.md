# AI Startup Idea Validator

A Multi-Agent AI platform that validates startup ideas using Large Language Models (LLMs) and live market intelligence.

---

## Project Overview

AI Startup Idea Validator is a Multi-Agent AI platform designed to help entrepreneurs, innovators, and startups evaluate business ideas before investing time and resources into development.

The platform combines Large Language Models (LLMs) with live, location-aware web search to extract structured business information, analyze the market and competitors, assess risk, recommend an MVP, generate a go-to-market strategy, and produce mentor-style guidance for the founder.

The project follows a Multi-Agent AI Architecture, coordinated by a central Orchestrator Agent that manages task planning, agent coordination, and shared context across the full validation pipeline. Each research-oriented agent performs its own targeted deep search rather than relying on a single shared search result.

---

## Features

- AI-powered Startup Idea Processing
- Location Agent — detects or lets the user select a target market (India, US, Europe, Southeast Asia, Global, etc.), so every downstream agent reasons with regional context
- Deep Search — Web Search, Market Analysis, Competitor, SWOT & Risk, MVP Recommendation, and GTM Strategy agents each run their own targeted DuckDuckGo search, automatically refining and re-searching if the first attempt returns too few relevant results
- Live Market Research using DuckDuckGo Search
- Structured Business Information Extraction
- Multi-Agent AI Architecture with a central Orchestrator Agent
- Market Analysis (TAM/SAM/SOM estimates, growth trend, customer segments)
- Competitor Analysis with market gap identification
- SWOT and Risk Analysis
- MVP Feature Recommendation with prioritized roadmap
- Go-To-Market Strategy generation
- Automated Validation Report compilation
- Conversational Advisor for follow-up questions
- Viability Score (0-100) combining idea clarity, competition, market, and risk signals
- Blind Spot Finder — surfaces what the founder has not addressed
- Honest Summary — a grounded, mentor-style closing assessment
- Elevator Pitch Generator — auto-generated one-liner and tagline
- Funding Suggestions — realistic funding paths with reasoning
- Interactive Streamlit Dashboard with sidebar navigation and live agent-status log
- Secure API Key Management using `.env`

---

## How It Works

The system follows this flow, matching our architecture diagram:

1. **User** submits a startup idea and selects a target market through the Streamlit UI.
2. **Orchestrator Agent** interprets the request, creates an execution plan, and invokes each agent in sequence, monitoring and passing context between them.
3. **Agent Pipeline** runs in order:
   - Idea Extraction Agent — extracts idea details and location (Location Agent)
   - Web Search Agent — location-aware deep search on DuckDuckGo for competitors, market trends, and related articles
   - Market Analysis Agent — deep search + estimates TAM/SAM/SOM, growth trend, and customer segments
   - Competitor Analysis Agent — deep search + identifies competitors, strengths/weaknesses, and market gaps
   - SWOT and Risk Analysis Agent — deep search + produces a SWOT analysis and a risk score
   - MVP Feature Recommendation Agent — deep search + prioritizes a feature roadmap
   - Go-To-Market Strategy Agent — deep search + recommends positioning, channels, and pricing
   - Report Generation Agent — compiles everything into a structured validation report
   - Conversational Advisor Agent — answers follow-up questions about the generated report
4. **Shared State** accumulates each agent's output, including the extracted location, so later agents and the final report can use earlier results.
5. **Final Output** — a validation report (currently Markdown, with PDF/DOC/HTML planned) is displayed in the Streamlit dashboard and available to download.

This mirrors our reference architecture diagram (see System Architecture below), which represents both what is built today and the target end-state we are building toward.

---

## Deep Search and Location Agent

Two additions strengthen how each agent researches the idea:

**Location Agent** — Idea Extraction now identifies (or the user directly selects) a target market. This location is stored in Shared State and passed into every downstream agent's search query, so analysis reflects the actual region the founder is targeting instead of generic global assumptions (e.g. "$10B TAM in India" instead of a vague global estimate).

**Deep Search** — Instead of one shared search reused by every agent, each research-oriented agent (Web Search, Market Analysis, Competitor, SWOT & Risk, MVP Recommendation, GTM Strategy) builds its own targeted query specific to its exact question. If the first search returns fewer than two relevant results, the agent automatically builds a refined, more specific query and searches a second time before reasoning over the combined results. This gives each agent research tailored to its own job, closer to how a real analyst team would divide the work, rather than every agent reasoning over the same shallow, generic search.

Idea Extraction, Viability Score, Insight Agent, Report Agent, and Conversational Advisor do not perform their own searches — they reason over what the other agents have already found.

---

## Implemented Agents

### Idea Extraction Agent 

Extracts structured information from the user's startup idea: idea name, industry, business model, problem statement, solution, target customers, and location/target market.

### Web Search Agent

Performs a location-aware deep search using DuckDuckGo (no API key required) to find competitors, market trends, and related articles.

### Market Analysis Agent

Runs its own deep search for market-size and growth data specific to the idea's industry and location, then estimates market opportunity (TAM/SAM/SOM), growth trend, and customer segments.

### Competitor Agent

Runs its own deep search for competitors specific to the idea, industry, and location, comparing strengths and weaknesses and identifying market gaps.

### SWOT and Risk Agent

Runs its own deep search for industry-specific risks and challenges, then produces a SWOT analysis (strengths, weaknesses, opportunities, threats) and a risk score used in the Viability Score.

### MVP Recommendation Agent

Runs its own deep search for comparable app features, then recommends a prioritized MVP feature set with an estimated development timeline.

### Go-To-Market Strategy Agent

Runs its own deep search for customer acquisition approaches, then generates a positioning statement, marketing channels, pricing strategy, and launch checklist.

### Report Generation Agent

Compiles all agent outputs into a single structured Markdown validation report, downloadable from the Streamlit dashboard.

### Conversational Advisor Agent

Answers founder follow-up questions about their validation report (e.g. "why is this competitor stronger?") without rerunning the full pipeline.

### Viability Score

Combines idea clarity, competition density, market analysis, and SWOT risk into a single 0-100 score with a plain-language verdict.

### Insight Layer

Generates the mentor-style layer of the report:

- Blind Spot Finder — identifies what the founder has not addressed
- Honest Summary — a short, realistic closing statement
- Elevator Pitch Generator — a punchy one-liner and tagline
- Funding Suggestions — realistic funding paths with reasoning

---

## Planned / Future Work

- Migrate orchestration to LangChain (currently a custom Python orchestrator)
- PostgreSQL for persistent storage of ideas, results, and reports
- Vector database and file storage for semantic search across past validations
- Additional report export formats: PDF, DOC, HTML (currently Markdown only)
- Richer shared state: user session state, conversation memory, execution logs
- Docker-based deployment
- Extend deep search with additional refinement rounds, currently limited to one retry per agent

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Core development |
| Streamlit | Frontend and UI |
| Groq API | LLM provider for all agents |
| DuckDuckGo Search | Live, location-aware deep search (no API key required) |
| PostgreSQL (planned) | Persistent storage |
| LangChain (planned) | Agent orchestration |
| Docker (planned) | Deployment |
| Git and GitHub | Version control |

---

## Project Structure

```text
ai-startup-validator-demo/
|
├── app/
│   ├── config.py               
│   └── orchestrator.py         
├── agents/
│   ├── idea_extraction_agent.py    
│   ├── web_search_agent.py         
│   ├── market_analysis_agent.py    
│   ├── competitor_agent.py         
│   ├── swot_risk_agent.py          
│   ├── mvp_recommendation_agent.py 
│   ├── gtm_strategy_agent.py       
│   ├── viability_score_agent.py
│   ├── insight_agent.py
│   ├── report_agent.py
│   └── conversational_advisor.py
├── tools/
│   ├── duckduckgo_tool.py      
│   └── deep_search.py          
├── state/
│   └── memory.py              
├── ui/
│   └── streamlit_app.py        
├── web_search_agent/
│   ├── query_planner.py        
│   └── cleaner.py             
├── .streamlit/
│   └── config.toml             
├── style_block.py               
├── requirements.txt
├── README.md
├── .gitignore
└── screenshots/
    ├── Home.png
    ├── dashboard.png
    ├── search-results.png
    └── Architecture.png
```

Note: API keys are stored locally in a `.env` file, which is excluded from GitHub using `.gitignore`.

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Siddhi9898/AI-Startup-Idea-Validator.git
cd AI-Startup-Idea-Validator
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

Linux / macOS:

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a file named `.env`:

```env
GROQ_API_KEY=your_groq_api_key
```

### 6. Run the Application

```bash
streamlit run ui/streamlit_app.py
```

---

## Sample Startup Idea

An AI-powered platform that matches freelance nurses with hospitals facing temporary staffing shortages. The platform intelligently recommends qualified healthcare professionals based on skills, certifications, experience, location, and availability while managing scheduling, contracts, payments, and performance tracking.

---

## System Architecture

![Architecture](screenshots/Architecture.png)

This diagram represents both what is implemented today and the target end-state architecture we are building toward. See "Planned / Future Work" above for what remains.

---

### Home Page

![Home Page](screenshots/Home.png)

### Structured Idea Dashboard

![Dashboard](screenshots/dashboard.png)

### Live Market and Competitor Search

![Search Results](screenshots/search-results.png)

---

## Team

Project: AI Startup Idea Validator

Developed as part of the Infosys Springboard Virtual Internship.

- Siddhi Bhingare
- Sravya Maheswari
- Niharika Pamugari
- Kasula Pavan Kumar Reddy

---

## License

This project is developed for educational, research, and demonstration purposes as part of the Infosys Springboard Virtual Internship.
