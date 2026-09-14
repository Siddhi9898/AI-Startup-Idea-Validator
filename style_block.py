CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
.stApp {
    background:
        radial-gradient(circle at 73% 8%, rgba(106, 45, 205, .22), transparent 26rem),
        radial-gradient(circle at 30% 100%, rgba(27, 124, 204, .10), transparent 30rem),
        #070511;
    color: #E7E9F0;
}
.block-container { max-width: 1360px; padding-top: 2rem; }
.app-header {
    background: linear-gradient(105deg, rgba(53, 20, 100, .95), rgba(20, 12, 54, .82));
    border: 1px solid rgba(149, 83, 255, .38);
    padding: 25px 30px;
    border-radius: 18px;
    margin-bottom: 24px;
    box-shadow: 0 18px 44px rgba(0, 0, 0, .28), inset 0 1px rgba(255,255,255,.07);
}
.app-header h1 {
    color: #FFFFFF;
    font-size: 1.8rem;
    margin: 0;
    font-weight: 700;
    letter-spacing: -0.02em;
}
.app-header p {
    color: #E9E3FF;
    margin: 6px 0 0 0;
    font-size: 0.95rem;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d091b, #090712);
    border-right: 1px solid #302354;
}
section[data-testid="stSidebar"] * {
    color: #E7E9F0;
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
    background: linear-gradient(145deg, rgba(29, 20, 60, .93), rgba(14, 11, 34, .93));
    border: 1px solid rgba(137, 102, 216, .28) !important;
    border-radius: 16px;
}
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(37, 26, 76, .9), rgba(15, 13, 35, .95));
    border: 1px solid rgba(137, 102, 216, .32);
    border-radius: 14px;
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
div.stButton > button[kind="secondary"] {
    background-color: #1B2032;
    border: 1px solid #2B3148;
    color: #E7E9F0;
    border-radius: 10px;
}
div.stButton > button[kind="secondary"]:hover {
    border-color: #7C3AED;
    color: #C9B3FF;
}
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
    background-color: rgba(12, 9, 28, .78) !important;
    border: 1px solid #372959 !important;
    color: #E7E9F0 !important;
    border-radius: 8px !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color: #6B7290 !important;
}
.stTextInput input:focus, .stTextArea textarea:focus { border-color: #9866ff !important; box-shadow: 0 0 0 2px rgba(152,102,255,.16) !important; }
label, .stTextArea label, .stTextInput label, .stSelectbox label, .stRadio label {
    color: #C9CCE0 !important;
}
/* Tabs */
button[data-baseweb="tab"] {
    color: #9CA3C4 !important;
    font-weight: 500;
}
button[data-baseweb="tab"] p {
    color: inherit !important;
}
button[aria-selected="true"] {
    color: #C9B3FF !important;
}
button[aria-selected="true"] p {
    color: #C9B3FF !important;
}
div[data-baseweb="tab-highlight"] {
    background-color: #7C3AED !important;
}
div[data-baseweb="tab-border"] {
    background-color: #262B3D !important;
}
/* Expanders */
details {
    background-color: #12162374;
    border: 1px solid #262B3D !important;
    border-radius: 10px !important;
}
summary {
    color: #E7E9F0 !important;
}
/* Alert boxes */
div[data-testid="stAlertContainer"] {
    border-radius: 10px;
    border: 1px solid #262B3D;
}
/* Divider */
hr {
    border-color: #262B3D !important;
}
.status-log {
    background-color: #10131F;
    border: 1px solid #262B3D;
    border-radius: 10px;
    padding: 14px 18px;
    font-size: 0.9rem;
    color: #B9BEDA;
}
.app-footer {
    text-align: center;
    color: #5B6180;
    font-size: 0.8rem;
    margin-top: 40px;
    padding: 16px 0;
    border-top: 1px solid #1A1F30;
}
div[data-testid="stPopover"] > div > button { border: 1px solid rgba(202, 151, 255, .8) !important; }
div[data-testid="stTabs"] { background: rgba(14, 10, 32, .45); padding: .25rem .7rem 0; border-radius: 14px; }
</style>
"""
