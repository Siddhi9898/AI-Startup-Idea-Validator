# AI Startup Idea Validator

A Multi-Agent AI platform that validates startup ideas using Large Language Models (LLMs) and live market intelligence.

---

## Project Overview

AI Startup Idea Validator is a Multi-Agent AI platform designed to help entrepreneurs, innovators, and startups evaluate business ideas before investing time and resources into development.

The platform combines Large Language Models (LLMs) with live web search to extract structured business information, analyze the market and competitors, assess risk, recommend an MVP, generate a go-to-market strategy, and produce mentor-style guidance for the founder.

The project follows a Multi-Agent AI Architecture, coordinated by a central Orchestrator Agent that manages task planning, agent coordination, and shared context across the full validation pipeline.

---

## Features

- AI-powered Startup Idea Processing
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
- Interactive Streamlit Dashboard
- Secure API Key Management using `.env`

---

## How It Works

The system follows this flow, matching our architecture diagram:

1. **User** submits a startup idea through the Streamlit UI.
2. **Orchestrator Agent** interprets the request, creates an execution plan, and invokes each agent in sequence, monitoring and passing context between them.
3. **Agent Pipeline** runs in order:
   - Web Search Agent — searches DuckDuckGo for competitors, market trends, and related articles
   - Market Analysis Agent — estimates TAM/SAM/SOM, growth trend, and customer segments
   - Competitor Analysis Agent — identifies competitors, strengths/weaknesses, and market gaps
   - SWOT and Risk Analysis Agent — produces a SWOT analysis and a risk score
   - MVP Feature Recommendation Agent — prioritizes a feature roadmap
   - Go-To-Market Strategy Agent — recommends positioning, channels, and pricing
   - Report Generation Agent — compiles everything into a structured validation report
   - Conversational Advisor Agent — answers follow-up questions about the generated report
4. **Shared State** accumulates each agent's output so later agents and the final report can use earlier results.
5. **Final Output** — a validation report (currently Markdown, with PDF/DOC/HTML planned) is displayed in the Streamlit dashboard and available to download.

This mirrors our reference architecture diagram (see System Architecture below), which represents both what is built today and the target end-state we are building toward.

---

## Implemented Agents

### Idea Extraction (within Orchestrator)

Extracts structured information from the user's startup idea: idea name, industry, business model, problem statement, solution, and target customers.

### Web Search Agent

Searches the web using DuckDuckGo (no API key required) to find competitors, market trends, and related articles.

### Market Analysis Agent

Estimates market opportunity (TAM/SAM/SOM), growth trend, and customer segments based on the idea and search context.

### Competitor Agent

Analyzes competitors found by the Web Search Agent, comparing strengths and weaknesses, and identifies market gaps.

### SWOT and Risk Agent

Produces a SWOT analysis (strengths, weaknesses, opportunities, threats) and a risk score used in the Viability Score.

### MVP Recommendation Agent

Recommends a prioritized MVP feature set with an estimated development timeline.

### Go-To-Market Strategy Agent

Generates a positioning statement, marketing channels, pricing strategy, and launch checklist.

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

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Core development |
| Streamlit | Frontend and UI |
| Groq API | LLM provider for all agents |
| DuckDuckGo Search | Live web search (no API key required) |
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
│   └── duckduckgo_tool.py      
├── state/
│   └── memory.py              
├── ui/
│   └── streamlit_app.py        
├── web_search_agent/
│   ├── query_planner.py        
│   └── cleaner.py             
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

## Current Project Status

This project follows a 4-milestone plan (see `docs/project_statement.md` for the full official brief). Based on that plan, the team is currently ahead of schedule: work originally scoped for Milestones 1 through 3 is already implemented.

### Milestone 1 (Idea Submission + Web Search Agent) — Complete

- Startup Idea Submission interface (Streamlit)
- Structured idea extraction using an LLM (Idea Extraction, within the Orchestrator)
- Web Search Agent integrated using DuckDuckGo (in place of Tavily, per team decision)

### Milestone 2 (Market Analysis + Competitor Agent + Orchestration) — Complete

- Market Opportunity and Customer Segmentation Analysis Agent
- Competitor Discovery and Comparison Agent
- Orchestrator Agent with sequential pipeline execution and Shared State context passing
- Validated across multiple sample startup ideas

### Milestone 3 (SWOT + MVP + GTM + Conversational Advisor) — Complete

- SWOT and Risk Analysis Agent
- MVP Feature Recommendation Agent
- Go-To-Market Strategy generation
- Conversational Advisor Agent for follow-up questions

### Milestone 4 (Report Generation + Testing + Documentation) — In Progress

- Report Generation Agent — implemented, currently Markdown output only
- End-to-end testing across all agents — done informally via command-line and Streamlit runs; no formal test suite yet
- PDF, DOC, and HTML report export — not yet implemented
- Technical documentation — this README and the accompanying project explanation document

### Additional differentiator features (beyond the official brief)

- Viability Score module (0-100 score combining idea clarity, competition, market, and risk signals)
- Insight Layer: Blind Spot Finder, Honest Summary, Elevator Pitch Generator, Funding Suggestions

### Not yet started (future work, beyond current milestones)

- LangChain-based orchestration (currently a custom Python orchestrator)
- PostgreSQL integration
- Vector database and file storage
- Docker deployment
- Formal automated test suite

---

## License

This project is developed for educational, research, and demonstration purposes as part of the Infosys Springboard Virtual Internship.
