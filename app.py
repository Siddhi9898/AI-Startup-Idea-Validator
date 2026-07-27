import streamlit as st
from orchestrator_agent import run_pipeline

st.set_page_config(page_title="AI Startup Idea Validator", layout="centered")
st.title(" AI Startup Idea Validator")
st.caption("Multi-Agent Startup Validation Platform — Live Demo")

idea_text = st.text_area("Describe your startup idea (2-3 lines):", height=100)

if st.button("Validate Idea"):
    if idea_text.strip() == "":
        st.warning("Please enter an idea first.")
    else:
        with st.spinner("Running multi-agent validation pipeline..."):
            result = run_pipeline(idea_text)

        # --- Structured Idea Output ---
        st.subheader(" Structured Idea Output")
        st.json(result["extracted"])

        # --- Live Market & Competitor Data ---
        st.subheader(" Live Market & Competitor Data")
        for r in result["search_results"]["results"]:
            st.markdown(f"**[{r['title']}]({r['url']})**")
            st.write(r["content"][:200] + "...")
            st.divider()

        # --- Viability Score ---
        st.subheader(" Viability Score")
        viability = result["viability_score"]
        st.metric(label="Overall Score", value=f"{viability['overall_score']}/100")
        st.write(f"**Verdict:** {viability['verdict']}")
        with st.expander("See score breakdown"):
            breakdown = viability["breakdown"]
            st.write(f"- Idea Clarity: {breakdown['idea_clarity']}/10")
            st.write(f"- Competition Density: {breakdown['competition_density']}/10")
            st.write(f"- Market Analysis: {breakdown['market_analysis']}/10")
            st.write(f"- SWOT/Risk: {breakdown['swot_risk']}/10")

        # --- Honest Summary ---
        st.subheader(" Honest Mentor Take")
        st.info(result["honest_summary"])

        # --- Blind Spots ---
        st.subheader(" What You Might Be Missing")
        for question in result["blind_spots"]:
            st.warning(question)

        # --- Elevator Pitch ---
        st.subheader(" Elevator Pitch")
        pitch = result["elevator_pitch"]
        st.write(f"**Pitch:** {pitch.get('elevator_pitch', '')}")
        st.write(f"**Tagline:** _{pitch.get('tagline', '')}_")

        # --- Funding Suggestions ---
        st.subheader(" Suggested Funding Paths")
        for suggestion in result["funding_suggestions"]:
            st.write(f"**{suggestion.get('funding_type')}** — {suggestion.get('reason')}")