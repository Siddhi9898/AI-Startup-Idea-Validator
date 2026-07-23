import streamlit as st
from extraction_agent import extract_idea
from search_agent import search_market

st.set_page_config(page_title="AI Startup Idea Validator", layout="centered")
st.title("🚀 AI Startup Idea Validator")
st.caption("Multi-Agent Startup Validation Platform — Live Demo")

idea_text = st.text_area("Describe your startup idea (2-3 lines):", height=100)

if st.button("Validate Idea"):
    if idea_text.strip() == "":
        st.warning("Please enter an idea first.")
    else:
        with st.spinner("🧠 Idea Processing Agent: extracting structured data..."):
            structured = extract_idea(idea_text)
        st.subheader("📋 Structured Idea Output")
        st.json(structured)

        with st.spinner("🌐 Web Search Agent: fetching live market & competitor data..."):
            market_data = search_market(structured)
        st.subheader("🌐 Live Market & Competitor Data")
        for r in market_data["results"]:
            st.markdown(f"**[{r['title']}]({r['url']})**")
            st.write(r["content"][:200] + "...")
            st.divider()