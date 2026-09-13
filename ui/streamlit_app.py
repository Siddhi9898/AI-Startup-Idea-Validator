"""
Streamlit UI - Tabs Navigation
Fixes: P1 (prominent download), P2 (quick summary), P3 (parallel
speed-up in orchestrator), P4 (full alphabetical location dropdowns
+ real GPS), P5/P10 (timeouts), P7/P8 (form-based follow-up),
P9 (dead link filtering), P11 (input validation), P12 (plausibility),
P13 (sensitive content), plus a working floating chat icon.
"""

import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from app.orchestrator import run_pipeline
from tools.input_validator import validate_idea_text, check_sensitive_content, check_plausibility
from tools.location_data import ALL_COUNTRIES, COUNTRY_STATES, STATE_CITIES, get_gps_location
from tools.timeout_utils import run_with_timeout, OperationTimedOut
from tools.pdf_generator import build_report_pdf
from db import database

st.set_page_config(page_title="AI Startup Idea Validator", layout="wide")

if "db_ready" not in st.session_state:
    st.session_state.db_ready = database.init_db()

if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

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
        p, span, div { color: #000000; }
        div[data-baseweb="select"] > div {
            background-color: #FFFFFF !important; color: #000000 !important;
            border: 1px solid #888888 !important;
        }
        div[data-baseweb="select"] span { color: #000000 !important; }
        .stButton > button, .stButton > button *,
        button[data-testid="stBaseButton-secondary"], button[data-testid="stBaseButton-secondary"] *,
        button[data-testid="stBaseButton-primary"], button[data-testid="stBaseButton-primary"] * {
            background-color: #1F2937 !important; color: #FFFFFF !important;
            border: 1px solid #1F2937 !important;
        }
        section[data-testid="stSidebar"] { background-color: #F5F5F5 !important; }
        section[data-testid="stSidebar"] * { color: #000000 !important; }
        div[data-testid="stRadio"] label p { color: #000000 !important; }
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
        p, span, div { color: #FAFAFA; }
        div[data-baseweb="select"] > div {
            background-color: #262730 !important; color: #FAFAFA !important;
            border: 1px solid #444444 !important;
        }
        div[data-baseweb="select"] span { color: #FAFAFA !important; }
        .stButton > button, .stButton > button *,
        button[data-testid="stBaseButton-secondary"], button[data-testid="stBaseButton-secondary"] *,
        button[data-testid="stBaseButton-primary"], button[data-testid="stBaseButton-primary"] * {
            background-color: #FAFAFA !important; color: #0E1117 !important;
            border: 1px solid #FAFAFA !important;
        }
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
    budget = st.selectbox("Expected Budget", BUDGET_RANGES)

with col_b:
    st.write("**Location**")
    use_gps = st.checkbox("Use my current location (GPS)")

    if use_gps:
        gps = get_gps_location()
        if gps:
            st.success(f"Detected: lat {gps['latitude']:.4f}, lon {gps['longitude']:.4f}")
            target_market = f"lat {gps['latitude']:.4f}, lon {gps['longitude']:.4f}"
            country = state_input = city_input = ""
        else:
            st.info("Waiting for browser location permission...")
            target_market = ""
            country = state_input = city_input = ""
    else:
        country = st.selectbox("Country (required)", ALL_COUNTRIES)

        if country in COUNTRY_STATES:
            state_input = st.selectbox("State", COUNTRY_STATES[country])
            state_input = "" if state_input in ("All States",) else state_input
        else:
            state_input = st.text_input("State (optional)", help="Full dropdown not available for this country yet - enter manually.")

        if state_input and state_input in STATE_CITIES:
            city_input = st.selectbox("City / Town", STATE_CITIES[state_input])
            city_input = "" if city_input in ("All Cities/Towns",) else city_input
        else:
            city_input = st.text_input("City / Town (optional)")

        location_parts = [p for p in [city_input.strip() if city_input else "", state_input.strip() if state_input else "", country if country != "All Countries" else ""] if p]
        target_market = ", ".join(location_parts)

    timeline = st.selectbox("Launch Timeline", TIMELINES)

validate_clicked = st.button("Validate Idea")

if validate_clicked:
    input_check = validate_idea_text(idea_text)
    sensitive_check = check_sensitive_content(idea_text) if input_check["is_valid"] else {"is_sensitive": False}
    plausibility_check = check_plausibility(idea_text) if input_check["is_valid"] else {"is_plausible": True}

    if not input_check["is_valid"]:
        st.session_state["result"] = {"invalid": True, "reason": input_check["reason"]}
    elif sensitive_check.get("is_sensitive"):
        st.session_state["result"] = {"invalid": True, "reason": sensitive_check["reason"]}
    elif not plausibility_check.get("is_plausible", True):
        st.session_state["result"] = {"invalid": True, "reason": plausibility_check["reason"]}
    else:
        try:
            with st.spinner("Running multi-agent validation pipeline..."):
                result = run_with_timeout(
                    run_pipeline, args=(idea_text, target_market), timeout_seconds=45.0
                )
            if not result.get("invalid"):
                meta = {
                    "budget": budget,
                    "timeline": timeline,
                    "submitted_at": datetime.now(),
                }
                result["_meta"] = {**meta, "submitted_at": meta["submitted_at"].strftime("%Y-%m-%d %H:%M")}
                # Persist to Postgres (fixes: history used to only live in
                # st.session_state and vanished on refresh/new session).
                # This call fails soft - a DB outage never blocks the
                # already-computed result from being shown.
                new_id = database.save_validation(result, meta)
                st.session_state["current_validation_id"] = new_id
                from agents.conversational_advisor import reset_advisor_memory
                reset_advisor_memory()
            st.session_state["result"] = result
        except OperationTimedOut as e:
            st.session_state["result"] = {"invalid": True, "reason": str(e)}

if "result" in st.session_state:
    result = st.session_state["result"]

    from tools.floating_chat_icon import render_floating_assistant
    render_floating_assistant(result)

    if result.get("invalid"):
        st.error(result.get("reason", "Please enter a valid input."))
    else:
        # P1 fix: prominent download button + quick summary shown
        # IMMEDIATELY, before any tabs - no scrolling required.
        st.divider()
        top_col1, top_col2 = st.columns([3, 1])
        with top_col1:
            st.subheader("Quick Summary")
            st.info(result.get("quick_summary", "Summary not available."))
        with top_col2:
            st.write("")
            st.write("")
            st.download_button(
                "Download Full Report (PDF)",
                data=build_report_pdf(result),
                file_name=f"{result.get('extracted', {}).get('idea_name', 'validation') or 'validation'}_report.pdf",
                mime="application/pdf",
                key="top_download_button",
            )
        st.divider()

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
                "Download Report (PDF)",
                data=build_report_pdf(result),
                file_name=f"{result.get('extracted', {}).get('idea_name', 'validation') or 'validation'}_report.pdf",
                mime="application/pdf",
                key="bottom_download_button",
            )

        with tabs[10]:
            st.subheader("Ask a Follow-up Question")
            st.caption("This advisor remembers earlier questions in this conversation.")

            from agents.conversational_advisor import _HISTORY_KEY
            if _HISTORY_KEY in st.session_state:
                for msg in st.session_state[_HISTORY_KEY]:
                    if msg["role"] == "user":
                        st.write(f"**You:** {msg['content']}")
                    elif msg["role"] == "assistant":
                        st.write(f"**Advisor:** {msg['content']}")

            with st.form(key="advisor_form", clear_on_submit=True):
                followup = st.text_input("Ask the Conversational Advisor about this report:")
                submitted = st.form_submit_button("Ask Advisor")

            if submitted and followup.strip():
                from agents.conversational_advisor import ask_advisor
                with st.spinner("Thinking..."):
                    ask_advisor(followup, result, st.session_state.get("current_validation_id"))
                st.rerun()
            elif submitted:
                st.warning("Please type a question first.")

        with tabs[11]:
            st.subheader("History")
            st.caption("Persisted in PostgreSQL - survives refreshes and new sessions.")
            if not st.session_state.get("db_ready"):
                st.warning(
                    "Could not connect to the PostgreSQL database, so history can't be "
                    "loaded or saved right now. Check your DB settings in `.env` "
                    "(PG_HOST / PG_PORT / PG_DB / PG_USER / PG_PASSWORD or DATABASE_URL)."
                )
            else:
                past_validations = database.list_validations()
                if not past_validations:
                    st.info("No validations saved yet.")
                else:
                    for row in past_validations:
                        score = row.get("viability_score")
                        score_label = f"{score}/100" if score is not None else "N/A"
                        submitted = row.get("submitted_at")
                        submitted_label = submitted.strftime("%Y-%m-%d %H:%M") if submitted else ""
                        with st.expander(f"{row['idea_name']} - Score: {score_label} - {submitted_label}"):
                            st.write(f"**Verdict:** {row.get('verdict', 'N/A')}")
                            st.write(f"**Budget:** {row.get('budget') or 'N/A'}")
                            st.write(f"**Timeline:** {row.get('timeline') or 'N/A'}")
                            st.write(f"**Location:** {row.get('target_market') or 'N/A'}")
                            if row.get("quick_summary"):
                                st.info(row["quick_summary"])

                            chat_summary = database.get_chat_summary(row["id"])
                            chat_messages = database.get_advisor_messages(row["id"])
                            if chat_summary or chat_messages:
                                with st.expander("Advisor Chat History", expanded=False):
                                    if chat_summary:
                                        st.caption("Summary of earlier conversation:")
                                        st.write(chat_summary)
                                    for msg in chat_messages:
                                        if msg["role"] == "user":
                                            st.write(f"**You:** {msg['content']}")
                                        else:
                                            st.write(f"**Advisor:** {msg['content']}")

                            past_full = database.get_validation(row["id"])
                            dl_col1, dl_col2 = st.columns(2)
                            with dl_col1:
                                if past_full:
                                    st.download_button(
                                        "Download PDF",
                                        data=build_report_pdf(past_full),
                                        file_name=f"{row['idea_name']}_report.pdf",
                                        mime="application/pdf",
                                        key=f"history_pdf_{row['id']}",
                                    )
                            with dl_col2:
                                if st.button("Delete", key=f"history_delete_{row['id']}"):
                                    database.delete_validation(row["id"])
                                    st.rerun()
