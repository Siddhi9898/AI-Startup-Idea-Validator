CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
.stApp {
    background-color: #0B0E17;
    background-image: radial-gradient(circle at 15% 0%, rgba(124,58,237,0.08) 0%, transparent 35%),
                       radial-gradient(circle at 85% 100%, rgba(124,58,237,0.06) 0%, transparent 40%);
    color: #E7E9F0;
}
* {
    scrollbar-width: thin;
    scrollbar-color: #3D2E7A #0B0E17;
}
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: #0B0E17; }
::-webkit-scrollbar-thumb { background-color: #3D2E7A; border-radius: 8px; }
::-webkit-scrollbar-thumb:hover { background-color: #4C2A9E; }

.app-header {
    background: linear-gradient(120deg, #4C2A9E 0%, #7C3AED 55%, #9F6BFF 100%);
    padding: 32px 36px;
    border-radius: 16px;
    margin-bottom: 28px;
    box-shadow: 0 10px 30px rgba(124, 58, 237, 0.3);
    position: relative;
    overflow: hidden;
}
.app-header::after {
    content: "";
    position: absolute;
    top: -60%; right: -10%;
    width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(255,255,255,0.10) 0%, transparent 70%);
    border-radius: 50%;
}
.app-header h1 {
    color: #FFFFFF;
    font-size: 2rem;
    margin: 0;
    font-weight: 800;
    letter-spacing: -0.03em;
}
.app-header p {
    color: #EDE7FF;
    margin: 8px 0 0 0;
    font-size: 1rem;
    font-weight: 400;
}

/* Section headers (st.subheader) - a left accent bar + tighter,
   heavier type reads as a premium dashboard rather than default
   Streamlit styling. */
h2, h3 {
    font-weight: 700 !important;
    letter-spacing: -0.01em;
}
div[data-testid="stMarkdownContainer"] > h3 {
    border-left: 4px solid #7C3AED;
    padding-left: 12px;
    margin-top: 8px !important;
}

section[data-testid="stSidebar"] {
    background-color: #10131F;
    border-right: 1px solid #262B3D;
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
    transition: background-color 0.15s ease, color 0.15s ease;
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
    border-radius: 12px;
    padding: 14px 16px;
    transition: border-color 0.2s ease, transform 0.2s ease;
}
div[data-testid="stMetric"]:hover {
    border-color: #4C2A9E;
    transform: translateY(-2px);
}
div[data-testid="stMetricValue"] {
    color: #B79CFF;
    font-weight: 700;
}
div.stButton > button[kind="primary"] {
    background: linear-gradient(120deg, #7C3AED, #9F6BFF);
    border: none;
    color: white;
    font-weight: 600;
    border-radius: 10px;
    padding: 0.6em 1em;
    box-shadow: 0 4px 14px rgba(124,58,237,0.3);
    transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
}
div.stButton > button[kind="primary"]:hover {
    background: linear-gradient(120deg, #6D2FE0, #8F5BF5);
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(124,58,237,0.4);
}
div.stButton > button[kind="primary"]:disabled {
    background: #3B3550;
    color: #8A85A0;
    box-shadow: none;
    transform: none;
}
div.stButton > button[kind="secondary"] {
    background-color: #1B2032;
    border: 1px solid #2B3148;
    color: #E7E9F0;
    border-radius: 10px;
    transition: border-color 0.15s ease, color 0.15s ease;
}
div.stButton > button[kind="secondary"]:hover {
    border-color: #7C3AED;
    color: #C9B3FF;
}
div[data-testid="stDownloadButton"] button {
    background-color: #161B29;
    border: 1px solid #7C3AED;
    color: #C9B3FF;
    border-radius: 10px;
    font-weight: 600;
    transition: background-color 0.15s ease;
}
div[data-testid="stDownloadButton"] button:hover {
    background-color: #241A3D;
}

.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
    background-color: #161B29 !important;
    border: 1px solid #2B3148 !important;
    color: #E7E9F0 !important;
    border-radius: 8px !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.stTextInput input:focus, .stTextArea textarea:focus,
.stSelectbox div[data-baseweb="select"]:focus-within > div {
    border-color: #7C3AED !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.25) !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color: #6B7290 !important;
}
label, .stTextArea label, .stTextInput label, .stSelectbox label, .stRadio label {
    color: #C9CCE0 !important;
}
/* Dropdown option menus (selectbox popovers) */
ul[data-baseweb="menu"] {
    background-color: #161B29 !important;
    border: 1px solid #2B3148 !important;
}
li[data-baseweb="menu-item"]:hover {
    background-color: #241A3D !important;
}

/* Tabs */
button[data-baseweb="tab"] {
    color: #9CA3C4 !important;
    font-weight: 500;
    transition: color 0.15s ease;
}
button[data-baseweb="tab"] p {
    color: inherit !important;
}
button[data-baseweb="tab"]:hover {
    color: #C9B3FF !important;
}
button[aria-selected="true"] {
    color: #C9B3FF !important;
}
button[aria-selected="true"] p {
    color: #C9B3FF !important;
}
div[data-baseweb="tab-highlight"] {
    background-color: #7C3AED !important;
    height: 3px !important;
}
div[data-baseweb="tab-border"] {
    background-color: #262B3D !important;
}

/* Expanders */
details {
    background-color: #12162374;
    border: 1px solid #262B3D !important;
    border-radius: 10px !important;
    transition: border-color 0.15s ease;
}
details:hover {
    border-color: #3D2E7A !important;
}
summary {
    color: #E7E9F0 !important;
    font-weight: 500;
}

/* Alert boxes - colored left accent instead of plain grey border, so
   info/success/warning/error read at a glance rather than blending
   into each other. */
div[data-testid="stAlertContainer"] {
    border-radius: 10px;
    border: 1px solid #262B3D;
    border-left-width: 4px !important;
}
div[data-testid="stAlertContainer"][data-baseweb="notification"] { background-color: #161B29; }
div[data-baseweb="notification"][kind="info"] { border-left-color: #60A5FA !important; }
div[data-baseweb="notification"][kind="positive"] { border-left-color: #34D399 !important; }
div[data-baseweb="notification"][kind="warning"] { border-left-color: #FBBF24 !important; }
div[data-baseweb="notification"][kind="negative"] { border-left-color: #F87171 !important; }

/* JSON / code viewers */
div[data-testid="stJson"] {
    background-color: #10131F !important;
    border: 1px solid #262B3D;
    border-radius: 10px;
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
</style>
"""