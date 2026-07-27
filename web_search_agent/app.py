import streamlit as st
import time

from web_search import search_web
from cleaner import clean_results

# ---------------- Page Settings ---------------- #
st.set_page_config(
    page_title="Web Search Agent",
    page_icon="🔎",
    layout="wide"
)

# ---------------- Sidebar ---------------- #
st.sidebar.title("🔎 Web Search Agent")

st.sidebar.write(
    "Search the web for relevant information using DuckDuckGo."
)

# ---------------- Main Page ---------------- #
st.title("🔎 Web Search Agent")
st.write("Search the web for startup ideas, competitors, and market information.")

query = st.text_input("Enter your search query:")

if st.button("Search"):

    if query.strip() == "":
        st.warning("Please enter a search query.")

    else:

        start = time.time()

        with st.spinner("Searching the web..."):

            results = search_web(query)
            cleaned_results = clean_results(results)

        end = time.time()

        st.success(f"Found {len(cleaned_results)} results")

        st.info(f"Search completed in {end-start:.2f} seconds")

        st.divider()

        for i, result in enumerate(cleaned_results, 1):

            with st.container():

                st.subheader(f"{i}. {result['title']}")

                st.write(result["description"])

                st.markdown(
                    f"🔗 [Visit Website]({result['link']})"
                )

                st.divider()