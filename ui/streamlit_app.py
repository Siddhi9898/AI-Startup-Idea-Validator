"""
Streamlit UI
------------
Frontend entrypoint. Run with: streamlit run ui/streamlit_app.py
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from app.orchestrator import run_pipeline

st.set_page_config(page_title="AI Startup Idea Validator", layout="centered")
st.title("AI Startup Idea Validator")
st.caption("Multi-Agent Startup Validation Platform")

idea_text = st.text_area("Describe your startup idea (2-3 lines):", height=100)

if st.button("Validate Idea"):
    if idea_text.strip() == "":
        st.warning("Please enter an idea first.")
    else:
        with st.spinner("Running multi-agent validation pipeline..."):
            result = run_pipeline(idea_text)

        st.subheader("Structured Idea Output")
        st.json(result["extracted"])

        st.subheader("Live Market & Competitor Data")
        for r in result["search_results"]["results"]:
            st.markdown(f"**[{r['title']}]({r['url']})**")
            st.write(r["content"][:200] + "...")
            st.divider()

        st.subheader("Market Analysis")
        market = result["market_analysis"]
        st.write(f"**TAM:** {market.get('tam_estimate', '')}")
        st.write(f"**SAM:** {market.get('sam_estimate', '')}")
        st.write(f"**SOM:** {market.get('som_estimate', '')}")
        st.write(f"**Growth Trend:** {market.get('growth_trend', '')}")

        st.subheader("Competitor Analysis")
        for c in result["competitors"].get("competitors", []):
            st.write(f"**{c.get('name', '')}** — Strength: {c.get('strength', '')} | Weakness: {c.get('weakness', '')}")
        st.write(f"**Market Gap:** {result['competitors'].get('market_gap', '')}")

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

        st.subheader("MVP Recommendation")
        for f in result["mvp"].get("mvp_features", []):
            st.write(f"**[{f.get('priority', '')}]** {f.get('feature', '')}")
        st.write(f"**Estimated Timeline:** {result['mvp'].get('estimated_timeline', '')}")

        st.subheader("Go-To-Market Strategy")
        gtm = result["gtm"]
        st.write(f"**Positioning:** {gtm.get('positioning_statement', '')}")
        st.write(f"**Channels:** {', '.join(gtm.get('marketing_channels', []))}")
        st.write(f"**Pricing:** {gtm.get('pricing_strategy', '')}")

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

        st.subheader("Full Validation Report")
        with st.expander("View full compiled report"):
            st.markdown(result["report"])
        st.download_button(
            "Download Report (Markdown)",
            data=result["report"],
            file_name="validation_report.md",
            mime="text/markdown",
        )

        st.subheader("Ask a Follow-up Question")
        followup = st.text_input("Ask the Conversational Advisor about this report:")
        if st.button("Ask Advisor") and followup.strip():
            from agents.conversational_advisor import ask_advisor
            with st.spinner("Thinking..."):
                answer = ask_advisor(followup, result)
            st.write(answer)