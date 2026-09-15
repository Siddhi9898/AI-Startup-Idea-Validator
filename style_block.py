CUSTOM_CSS = """
<style>
.app-header {
    background: linear-gradient(120deg, #4C2A9E 0%, #7C3AED 55%, #9F6BFF 100%);
    padding: 28px 32px;
    border-radius: 14px;
    margin-bottom: 24px;
}
.app-header h1 {
    color: #FFFFFF;
    font-size: 1.8rem;
    margin: 0;
    font-weight: 700;
}
.app-header p {
    color: #E9E3FF;
    margin: 6px 0 0 0;
    font-size: 0.95rem;
}
section[data-testid="stSidebar"] {
    background-color: #10131F;
    border-right: 1px solid #262B3D;
}
section[data-testid="stSidebar"] .stButton button {
    background-color: transparent;
    color: #C9CCE0;
    border: none;
    text-align: left;
    padding: 8px 10px;
    border-radius: 8px;
    font-size: 0.92rem;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background-color: #1E2436;
    color: #FFFFFF;
}
section[data-testid="stSidebar"] .stButton button[kind="primary"] {
    background-color: #7C3AED !important;
    color: #FFFFFF !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #161B29;
    border: 1px solid #262B3D !important;
    border-radius: 12px;
}
div[data-testid="stMetric"] {
    background-color: #161B29;
    border: 1px solid #262B3D;
    border-radius: 10px;
    padding: 12px 14px;
}
div[data-testid="stMetricValue"] {
    color: #B79CFF;
}
div.stButton > button[kind="primary"] {
    background: linear-gradient(120deg, #7C3AED, #9F6BFF);
    border: none;
    color: white;
    font-weight: 600;
    border-radius: 10px;
    padding: 0.6em 1em;
}
div.stButton > button[kind="primary"]:hover {
    background: linear-gradient(120deg, #6D2FE0, #8F5BF5);
    color: white;
}
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
    background-color: #161B29 !important;
    border: 1px solid #2B3148 !important;
    color: #E7E9F0 !important;
    border-radius: 8px !important;
}
.status-log {
    background-color: #10131F;
    border: 1px solid #262B3D;
    border-radius: 10px;
    padding: 14px 18px;
    font-size: 0.9rem;
    color: #B9BEDA;
}
</style>
"""