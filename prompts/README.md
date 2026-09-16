# AI Startup Idea Validator

A Multi-Agent AI platform that validates startup ideas using Large Language Models (LLMs) and live market intelligence — now with accounts, persistent history, and a polished, presentation-ready UI.

---

## Project Overview

AI Startup Idea Validator helps entrepreneurs, innovators, and startups evaluate business ideas before investing time and resources into development.

The platform combines Large Language Models (LLMs) with live, location-aware web search to extract structured business information, analyze the market and competitors, assess risk, recommend an MVP, generate a go-to-market strategy, and produce mentor-style guidance for the founder — then lets the founder keep asking the AI advisor follow-up questions about their own report.

The project follows a Multi-Agent AI Architecture, coordinated by a central Orchestrator Agent that manages task planning, agent coordination, and shared context across the full validation pipeline. Each research-oriented agent performs its own targeted deep search rather than relying on a single shared search result.

---

## Features

### Core validation pipeline
- AI-powered Startup Idea Processing with structured extraction (idea name, industry, business model, problem, solution, target customer)
- Location Agent — detects or lets the user select a target market, so every downstream agent reasons with regional context
- Deep Search — Web Search, Market Analysis, Competitor, SWOT & Risk, MVP Recommendation, and GTM Strategy agents each run their own targeted DuckDuckGo search (no API key required), with deterministic relevance filtering and a fallback so a run is never left with near-zero usable results
- Market Analysis (TAM/SAM/SOM estimates, growth trend, customer segments)
- Competitor Analysis with market gap identification
- SWOT and Risk Analysis
- MVP Feature Recommendation with a prioritized MoSCoW roadmap
- Go-To-Market Strategy generation
- Viability Score (0-100) combining idea clarity, competition, market, and risk signals
- Blind Spot Finder, Honest Summary, Elevator Pitch Generator, and Funding Suggestions
- Suggestions to Improve — concrete, actionable next steps shown right under the Quick Summary
- Agent Scores tab — bar and radar charts comparing every agent's contribution on a common /100 scale, read directly from the same numbers shown elsewhere (never a separate calculation)

### Accounts, history, and the AI advisor
- Registration and Login, with a required security question (e.g. "What was the name of your first pet?") chosen at signup — this is the only password-reset path, verified by a case/whitespace-insensitive, bcrypt-hashed answer check
- Per-user History, persisted in PostgreSQL, visible only to the account that created it — enforced at the database layer, not just hidden in the UI
- Offline-resilient history — every successful history fetch is also cached to a small local file, so your history is still viewable if Postgres is temporarily unreachable or the app restarts before you're back online
- Anonymous use is still supported: you can validate an idea and download its PDF (including the advisor chat) without ever logging in — you just won't have a saved History
- Conversational Advisor with real multi-turn memory, reachable two ways: a dedicated "Advisor Chat" tab, and a floating chat icon fixed in the corner with animated blinking eyes so it's reachable from every tab
- Only questions actually related to your idea are saved to your persisted chat history — off-topic questions are still answered live but never stored, and older turns are automatically summarized once a conversation grows long, so history stays useful instead of unbounded

### Presentation and usability
- A single, deliberately designed dark/violet theme (no light-mode toggle) with a gradient header, accent-bordered section headers, color-coded alert boxes, hover states, and a custom scrollbar
- A walking progress companion that crosses the input box left-to-right while validation runs, so you can see how long it's taken instead of staring at a bare spinner — the character is selectable from the sidebar
- Cancellable validation — a Stop button lets you abandon a run and immediately edit your idea, rather than waiting for the in-flight run to fully unwind
- Ctrl+Enter submits your idea directly
- Multi-language input — write your idea in any language; it's silently normalized to English before the (English-tuned) pipeline runs, so the output is always in clear English
- Downloadable PDF Validation Reports, including a "Q & A" section with your advisor conversation, and sanitized text so LLM-added symbols/emoji never render as unreadable dark glyph boxes
- Standalone CLI pipeline (`pipeline.py`) for running validations outside Streamlit

---

## How It Works

1. **User** submits a startup idea (in any language) and a target market through the Streamlit UI, or via `pipeline.py` from the command line.
2. **Orchestrator Agent** interprets the request, creates an execution plan, and invokes each agent in sequence, monitoring and passing context between them — checking a cancellation flag between steps so a Stop request takes effect quickly instead of waiting for the whole run.
3. **Agent Pipeline** runs in order:
   - Idea Extraction Agent — extracts idea details and location
   - Web Search Agent — location-aware deep search on DuckDuckGo
   - Market Analysis Agent and Competitor Agent — run concurrently, each with their own deep search
   - SWOT and Risk Analysis Agent
   - MVP Feature Recommendation Agent
   - Go-To-Market Strategy Agent
   - Viability Score Agent
   - Insight Agent — blind spots, honest summary, elevator pitch, funding suggestions
   - Suggestion Agent — concrete improvement suggestions
   - Report Generation Agent — compiles everything into a structured Markdown report
   - Summary Agent — condenses everything into one quick, readable briefing
   - Conversational Advisor Agent — answers follow-up questions, on demand, with real conversation memory
4. **Shared State** accumulates each agent's output, including the extracted location, so later agents, the final report, and the PDF export all read from the same single source of truth.
5. **Final Output** — a validation report shown as formatted Markdown in the dashboard, and downloadable as a polished PDF with a Q & A section for the advisor conversation. If you're logged in, the whole result is saved to your personal History automatically.

---

## Deep Search and Location Agent

**Location Agent** — Idea Extraction identifies (or the user directly selects) a target market. This location is stored in Shared State and passed into every downstream agent's search query, so analysis reflects the actual region the founder is targeting instead of generic global assumptions.

**Deep Search** — Instead of one shared search reused by every agent, the Web Search Agent and the Competitor Agent each build several angled queries specific to their exact question, then apply a deterministic relevance filter with a fallback floor — so a handful of near-miss results don't leave an agent with almost nothing to reason over, without ever inventing information that wasn't actually retrieved.

Idea Extraction, Viability Score, Insight Agent, Suggestion Agent, Report Agent, Summary Agent, and Conversational Advisor do not perform their own searches — they reason over what the search-driven agents have already found.

---

## Implemented Agents

Every agent's exact role, inputs/outputs, and (where applicable) LLM prompt template is documented in [`prompts/`](./prompts/) — one Markdown file per agent, plus an index describing the pipeline order. Summary below:

| Agent | File | What it does |
|---|---|---|
| Idea Extraction | `agents/idea_extraction_agent.py` | Structures the raw idea into name, problem, solution, target customer, industry, business model |
| Web Search | `agents/web_search_agent.py` | Multi-query deep search with relevance + dead-link filtering |
| Market Analysis | `agents/market_analysis_agent.py` | TAM/SAM/SOM, growth trend, customer segments |
| Competitor | `agents/competitor_agent.py` | Direct/indirect competitors, competitive intensity, market gap |
| SWOT & Risk | `agents/swot_risk_agent.py` | Rule-based SWOT + a 0-10 risk score |
| MVP Recommendation | `agents/mvp_recommendation_agent.py` | MoSCoW-prioritized feature roadmap |
| GTM Strategy | `agents/gtm_strategy_agent.py` | Positioning, channels, pricing, launch checklist |
| Viability Score | `agents/viability_score_agent.py` | Deterministic 0-100 score combining every signal above |
| Insight Agent | `agents/insight_agent.py` | Blind spots, honest summary, elevator pitch, funding suggestions |
| Suggestion Agent | `agents/suggestion_agent.py` | Actionable suggestions to improve the idea |
| Report Agent | `agents/report_agent.py` | Compiles the full Markdown report |
| Summary Agent | `agents/summary_agent.py` | One quick, readable briefing |
| Conversational Advisor | `agents/conversational_advisor.py` | Multi-turn Q&A about the report, with relevance-filtered persistence |

---

## Setup

1. Copy `.env` and set your API keys: `GROQ_API_KEY` (required), and optionally `TAVILY_API_KEY`.
2. Set your PostgreSQL connection - either a single `DATABASE_URL`, or the individual `PG_HOST` / `PG_PORT` / `PG_DB` / `PG_USER` / `PG_PASSWORD` variables. The app creates every table it needs automatically on first run (`db/database.py:init_db()`); accounts, history, and chat persistence all degrade gracefully (the validator still works) if the database isn't reachable.
3. `pip install -r requirements.txt`
4. Run the dashboard:
   ```bash
   streamlit run ui/streamlit_app.py
   ```
   On Windows, you can also just double-click **`run_app.bat`** - it creates/uses an isolated `.venv`, installs dependencies, and launches the app in one step.
5. Or run a single validation from the CLI, no browser needed:
   ```bash
   python pipeline.py "A marketplace app for renting power tools" \
       --location "Hyderabad, India" \
       --budget "Bootstrap (very small budget)" \
       --timeline "3 Months" \
       --pdf-out validation_report.pdf
   ```

---

## Planned / Future Work

- Migrate orchestration to LangChain (currently a custom Python orchestrator)
- Vector database and file storage for semantic search across past validations
- Additional report export formats: DOC, HTML (Markdown + PDF supported today)
- True offline-first support (a PWA/service-worker rewrite) - today's offline history cache covers "Postgres is unreachable," not "no internet at all"
- Docker-based deployment
- Extend deep search with additional refinement rounds

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Core development |
| Streamlit | Frontend and UI |
| Groq API | LLM provider for all agents |
| DuckDuckGo Search | Live, location-aware deep search (no API key required) |
| PostgreSQL | Accounts, per-user idea history, and advisor chat persistence |
| bcrypt | Password and security-answer hashing |
| ReportLab | PDF report generation |
| Plotly | Agent score bar/radar charts |
| LangChain (planned) | Agent orchestration |
| Docker (planned) | Deployment |
| Git and GitHub | Version control |

---

## Project Structure

```text
AI-Startup-Idea-Validator/
|
├── app/
│   ├── config.py                 (env/secrets loading, model config)
│   └── orchestrator.py           (pipeline sequencing + cancellation)
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
│   ├── suggestion_agent.py
│   ├── report_agent.py
│   ├── summary_agent.py
│   └── conversational_advisor.py
├── tools/
│   ├── duckduckgo_tool.py        (search backend)
│   ├── validators.py             (relevance filtering with fallback)
│   ├── link_validator.py         (dead-link filtering)
│   ├── input_validator.py        (idea-text sanity checks)
│   ├── timeout_utils.py
│   ├── llm_tool.py
│   ├── location_data.py
│   ├── auth.py                   (register/login/security-question reset)
│   ├── pdf_generator.py          (PDF export, incl. Q & A section)
│   ├── mascot.py                 (walking progress companion)
│   ├── score_charts.py           (Agent Scores bar/radar charts)
│   ├── translator.py             (silent input -> English normalization)
│   ├── chat_ui.py                (shared chat-bubble rendering)
│   └── floating_chat_icon.py     (corner advisor widget)
├── db/
│   └── database.py               (PostgreSQL: users, validated_ideas, advisor_messages)
├── prompts/
│   ├── README.md                 (agent prompt/role documentation index)
│   └── <one .md per agent>
├── state/
│   └── memory.py                 (SharedState)
├── ui/
│   └── streamlit_app.py
├── web_search_agent/
│   ├── query_planner.py
│   └── cleaner.py
├── .streamlit/
│   └── config.toml
├── style_block.py                (professional theme CSS)
├── pipeline.py                   (standalone CLI entry point)
├── run_app.bat                   (Windows one-click launcher)
├── models.py
├── requirements.txt
├── README.md
├── .gitignore
└── screenshots/
```

Note: API keys and DB credentials are stored locally in a `.env` file, which is excluded from GitHub via `.gitignore`.

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
TAVILY_API_KEY=your_tavily_api_key

DATABASE_URL=postgresql://user:password@host:5432/dbname
# ...or the individual PG_HOST / PG_PORT / PG_DB / PG_USER / PG_PASSWORD variables
```

### 6. Run the Application

```bash
streamlit run ui/streamlit_app.py
```

Windows users can instead just double-click `run_app.bat`, which sets up its own virtual environment and dependencies automatically.

---

## Sample Startup Idea

An AI-powered platform that matches freelance nurses with hospitals facing temporary staffing shortages. The platform intelligently recommends qualified healthcare professionals based on skills, certifications, experience, location, and availability while managing scheduling, contracts, payments, and performance tracking.

---

## System Architecture

![Architecture](screenshots/Architecture.png)

This diagram represents both what is implemented today and the target end-state architecture we are building toward. See "Planned / Future Work" above for what remains.

---

## Screenshots

### Login, Registration, and Forgot Password

![Login and registration and forgot password](<screenshots/Login and registration and forgot password.png>)

### Home / UI

![UI](<screenshots/UI .png>)

### Entering an Idea

![After logging in, entering the data and giving relevant information](<screenshots/After logging in, Entering the data and giving relavent information.png>)

### Output — Quick Summary and Suggestions

![Output with quick summary and suggestions](<screenshots/Output with quick summary and suggestions.png>)

### Web Search Agent

![Web search agent](<screenshots/Web search agent.png>)

### Market Analysis

![Market Analysis](<screenshots/Market Analysis.png>)

### Competitor Analysis

![Competitor Analysis](<screenshots/Competitor Analysis.png>)

### SWOT & Risk Analysis

![Swot & Risk Analysis](<screenshots/Swot & Risk Analysis.png>)

### MVP Recommendation

![MVP recomendation](<screenshots/MVP recomendation.png>)

### Go-To-Market Strategy

![GTM Stratergy](<screenshots/GTM Stratergy.png>)

### Viability Score

![Viability Score](<screenshots/Viability Score.png>)

### Agent Scores and Graphs

![Agent Scores and Graphs](<screenshots/Agent Scores and Graphs.png>)

### Insights (Honest Mentor Take)

![Insights (Honest Mentor Take)](<screenshots/Insights(Honest Mentor Take).png>)

### Advisor Chat

![Advisor Chat](<screenshots/Advisor Chat.png>)

### Report with Downloaded PDF

![Report with downloaded pdf](<screenshots/Report with downloaded pdf.png>)

### History

![History](<screenshots/History .png>)

---

## Team

Project: AI Startup Idea Validator

Developed as part of the Infosys Springboard Virtual Internship.

- Maheswari Sravya
- Niharika Pamugari
- Siddhi Bhingare
- Kasula Pavan Kumar Reddy

---

## License

This project is developed for educational, research, and demonstration purposes as part of the Infosys Springboard Virtual Internship.