"""
Streamlit UI - Tabs Navigation (fixes remaining light-mode contrast
issues on tabs/radio labels, fixes $ rendering bug, makes Budget
currency-neutral)
"""

import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from app.orchestrator import run_pipeline

st.set_page_config(page_title="AI Startup Idea Validator", layout="wide")

if "theme" not in st.session_state:
    st.session_state.theme = "Dark"
if "history" not in st.session_state:
    st.session_state.history = []

theme_choice = st.sidebar.radio("Theme", ["Dark", "Light"], index=0 if st.session_state.theme == "Dark" else 1)
st.session_state.theme = theme_choice

if theme_choice == "Light":
    st.markdown(
        """
        <style>
        .stApp { background-color: #FFFFFF; color: #000000; }
        textarea, input, .stTextArea textarea, .stTextInput input {
            background-color: #FFFFFF !important; color: #000000 !important;
            border: 1px solid #888888 !important;
        }
        textarea::placeholder, input::placeholder { color: #666666 !important; opacity: 1 !important; }
        label, .stTextArea label, .stTextInput label, .stSelectbox label,
        p, span, div {
            color: #000000;
        }
        div[data-baseweb="select"] > div {
            background-color: #FFFFFF !important; color: #000000 !important;
            border: 1px solid #888888 !important;
        }
        div[data-baseweb="select"] span { color: #000000 !important; }
        .stButton > button {
            background-color: #1F2937 !important; color: #FFFFFF !important;
            border: 1px solid #1F2937 !important;
        }
        .stButton > button:hover { background-color: #374151 !important; color: #FFFFFF !important; }
        section[data-testid="stSidebar"] { background-color: #F5F5F5 !important; }
        section[data-testid="stSidebar"] * { color: #000000 !important; }

        /* Radio button options (Theme: Dark/Light) */
        div[data-testid="stRadio"] label p { color: #000000 !important; }
        div[data-testid="stRadio"] label div[data-baseweb="radio"] { color: #000000 !important; }

        /* Tab bar labels - these were invisible before */
        button[data-baseweb="tab"] { color: #000000 !important; }
        button[data-baseweb="tab"] p { color: #000000 !important; }
        button[aria-selected="true"] { color: #6D28D9 !important; }
        button[aria-selected="true"] p { color: #6D28D9 !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <style>
        .stApp { background-color: #0E1117; color: #FAFAFA; }
        textarea, input, .stTextArea textarea, .stTextInput input {
            background-color: #262730 !important; color: #FAFAFA !important;
            border: 1px solid #444444 !important;
        }
        textarea::placeholder, input::placeholder { color: #AAAAAA !important; opacity: 1 !important; }
        label, .stTextArea label, .stTextInput label, .stSelectbox label,
        p, span, div {
            color: #FAFAFA;
        }
        div[data-baseweb="select"] > div {
            background-color: #262730 !important; color: #FAFAFA !important;
            border: 1px solid #444444 !important;
        }
        div[data-baseweb="select"] span { color: #FAFAFA !important; }
        .stButton > button {
            background-color: #FAFAFA !important; color: #0E1117 !important;
            border: 1px solid #FAFAFA !important;
        }
        .stButton > button:hover { background-color: #DDDDDD !important; color: #0E1117 !important; }
        section[data-testid="stSidebar"] { background-color: #161A25 !important; }
        section[data-testid="stSidebar"] * { color: #FAFAFA !important; }

        div[data-testid="stRadio"] label p { color: #FAFAFA !important; }
        button[data-baseweb="tab"] { color: #FAFAFA !important; }
        button[data-baseweb="tab"] p { color: #FAFAFA !important; }
        button[aria-selected="true"] { color: #A78BFA !important; }
        button[aria-selected="true"] p { color: #A78BFA !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

st.title("AI Startup Idea Validator")
st.caption("Multi-Agent Startup Validation Platform")

COUNTRIES = [
    "India", "United States", "United Kingdom", "Canada", "Australia",
    "Germany", "France", "Singapore", "United Arab Emirates", "Japan",
    "Brazil", "South Africa", "Global", "Other",
]
# Currency-neutral budget brackets (avoids $ sign - both fixes the
# LaTeX rendering bug and makes sense for non-US founders too)
BUDGET_RANGES = [
    "Bootstrap (very small budget)",
    "Seed stage (small funding raised)",
    "Series A ready (significant funding raised)",
    "Not sure yet",
]
TIMELINES = ["1 Month", "3 Months", "6 Months", "12 Months"]

col_a, col_b = st.columns(2)
with col_a:
    idea_text = st.text_area(
        "Describe your startup idea (2-3 lines):",
        height=100,
        help="Write a real, coherent business idea.",
    )
    budget = st.selectbox(
        "Expected Budget",
        BUDGET_RANGES,
        help="How much funding you realistically have to build and launch this idea. Used to tailor MVP and go-to-market advice.",
    )
with col_b:
    country = st.selectbox("Target Market - Country (required)", COUNTRIES)
    state_input = st.text_input("State (optional)")
    city_input = st.text_input("City / Town (optional)")
    timeline = st.selectbox("Launch Timeline", TIMELINES)

location_parts = [p for p in [city_input.strip(), state_input.strip(), country] if p]
target_market = ", ".join(location_parts)

validate_clicked = st.button("Validate Idea")

if validate_clicked:
    if idea_text.strip() == "":
        st.warning("Please enter an idea first.")
    else:
        with st.spinner("Running multi-agent validation pipeline..."):
            result = run_pipeline(idea_text, target_market)

        if not result.get("invalid"):
            result["_meta"] = {
                "budget": budget,
                "timeline": timeline,
                "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            st.session_state.history.append(result)

        st.session_state["result"] = result

if "result" in st.session_state:
    result = st.session_state["result"]

    if result.get("invalid"):
        st.error(result.get("reason", "Please enter a valid input."))
    else:
        tabs = st.tabs([
            "Idea", "Web Search", "Market Analysis", "Competitors",
            "SWOT & Risk", "MVP", "GTM Strategy", "Viability Score",
            "Insights", "Report", "Advisor Chat", "History",
        ])

        with tabs[0]:
            st.subheader("Structured Idea Output")
            st.json(result["extracted"])

        with tabs[1]:
            st.subheader("Live Market & Competitor Data (Web Search Agent)")
            st.caption(f"Search query used: {result['search_results'].get('query', '')}")
            if not result["search_results"].get("results"):
                st.info("No live results found for this query.")
            for r in result["search_results"]["results"]:
                st.markdown(f"**[{r['title']}]({r['url']})**")
                st.write(r["content"][:200] + "...")
                st.divider()

        with tabs[2]:
            st.subheader("Market Analysis (Deep Search)")
            market = result["market_analysis"]
            st.write(f"**TAM:** {market.get('tam_estimate', '')}")
            st.write(f"**SAM:** {market.get('sam_estimate', '')}")
            st.write(f"**SOM:** {market.get('som_estimate', '')}")
            st.write(f"**Growth Trend:** {market.get('growth_trend', '')}")
            st.write(f"**Customer Segments:** {', '.join(market.get('customer_segments', []))}")
            with st.expander("Market-specific search sources used (deep search)"):
                for src in market.get("market_search_sources", []):
                    st.write(f"- [{src.get('title', '')}]({src.get('url', '')})")

        with tabs[3]:
            st.subheader("Competitor Analysis")
            for c in result["competitors"].get("competitors", []):
                st.write(f"**{c.get('name', '')}** — Strength: {c.get('strength', '')} | Weakness: {c.get('weakness', '')}")
            st.write(f"**Market Gap:** {result['competitors'].get('market_gap', '')}")

        with tabs[4]:
            st.subheader("SWOT & Risk Analysis")
            swot = result["swot"]
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Strengths:**")
                for s in swot.get("strengths", []):
                    st.write(f"- {s}")
                st.write("**Opportunities:**")
                for o in swot.get("opportunities", []):
                    st.write(f"- {o}")
            with col2:
                st.write("**Weaknesses:**")
                for w in swot.get("weaknesses", []):
                    st.write(f"- {w}")
                st.write("**Threats:**")
                for t in swot.get("threats", []):
                    st.write(f"- {t}")

        with tabs[5]:
            st.subheader("MVP Recommendation")
            for f in result["mvp"].get("mvp_features", []):
                st.write(f"**[{f.get('priority', '')}]** {f.get('feature', '')}")
            st.write(f"**Estimated Timeline:** {result['mvp'].get('estimated_timeline', '')}")

        with tabs[6]:
            st.subheader("Go-To-Market Strategy")
            gtm = result["gtm"]
            st.write(f"**Positioning:** {gtm.get('positioning_statement', '')}")
            st.write(f"**Channels:** {', '.join(gtm.get('marketing_channels', []))}")
            st.write(f"**Pricing:** {gtm.get('pricing_strategy', '')}")

        with tabs[7]:
            st.subheader("Viability Score")
            viability = result["viability_score"]
            st.metric(label="Overall Score", value=f"{viability['overall_score']}/100")
            st.write(f"**Verdict:** {viability['verdict']}")
            with st.expander("See score breakdown"):
                breakdown = viability["breakdown"]
                st.write(f"- Idea Clarity: {breakdown['idea_clarity']}/10")
                st.write(f"- Competition Density: {breakdown['competition_density']}/10")
                st.write(f"- Market Analysis: {breakdown['market_analysis']}/10")
                st.write(f"- SWOT/Risk: {breakdown['swot_risk']}/10")

        with tabs[8]:
            st.subheader("Honest Mentor Take")
            st.info(result["honest_summary"])
            st.subheader("What You Might Be Missing")
            for question in result["blind_spots"]:
                st.warning(question)
            st.subheader("Elevator Pitch")
            pitch = result["elevator_pitch"]
            st.write(f"**Pitch:** {pitch.get('elevator_pitch', '')}")
            st.write(f"**Tagline:** _{pitch.get('tagline', '')}_")
            st.subheader("Suggested Funding Paths")
            for suggestion in result["funding_suggestions"]:
                st.write(f"**{suggestion.get('funding_type')}** — {suggestion.get('reason')}")

        with tabs[9]:
            st.subheader("Full Validation Report")
            st.markdown(result["report"])
            st.download_button(
                "Download Report (Markdown)",
                data=result["report"],
                file_name="validation_report.md",
                mime="text/markdown",
            )

        with tabs[10]:
            st.subheader("Ask a Follow-up Question")
            followup = st.text_input(
                "Ask the Conversational Advisor about this report:",
                key="advisor_question",
            )
            if st.button("Ask Advisor"):
                if followup.strip():
                    from agents.conversational_advisor import ask_advisor
                    with st.spinner("Thinking..."):
                        answer = ask_advisor(followup, result)
                    st.session_state["advisor_answer"] = answer
                else:
                    st.warning("Please type a question first.")
            if "advisor_answer" in st.session_state:
                st.write(st.session_state["advisor_answer"])

        with tabs[11]:
            st.subheader("History")
            if not st.session_state.history:
                st.info("No validations yet this session.")
            else:
                for i, past in enumerate(reversed(st.session_state.history)):
                    meta = past.get("_meta", {})
                    idea_name = past.get("extracted", {}).get("idea_name", "Untitled Idea")
                    score = past.get("viability_score", {}).get("overall_score", "N/A")
                    with st.expander(f"{idea_name} - Score: {score}/100 - {meta.get('submitted_at', '')}"):
                        st.write(f"**Budget:** {meta.get('budget', 'N/A')}")
                        st.write(f"**Timeline:** {meta.get('timeline', 'N/A')}")
                        st.write(f"**Location:** {past.get('extracted', {}).get('location', 'N/A')}")
                        st.download_button(
                            "Download this report",
                            data=past.get("report", ""),
                            file_name=f"{idea_name}_report.md",
                            mime="text/markdown",
                            key=f"history_download_{i}",
                        )