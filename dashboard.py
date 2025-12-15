# dashboard.py

import streamlit as st
import sqlite3
import pandas as pd
import json
import difflib
import spacy
import os
import streamlit.components.v1 as components
from src.downloader import download_rule
from src.database_manager import get_latest_version, log_new_version

# --- Load NLP Model ---
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    pass 

# --- Configuration ---
st.set_page_config(page_title="Regulatory Harmony", layout="wide", page_icon="🌑")

# --- Styles ---
st.markdown("""
    <style>
    /* 1. THE CANVAS: Deep, dark midnight gradient */
    .stApp {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        background-attachment: fixed;
    }

    /* 2. THE GLASS CARDS (Metrics & Expanders) */
    div[data-testid="stMetric"], div[data-testid="stExpander"], div[data-testid="stMarkdownContainer"] > div {
        background-color: rgba(15, 32, 39, 0.7);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        # padding: 15px !important; /* Commented out to prevent padding issues on simple text */
    }
    
    div[data-testid="stMetricValue"] { color: #e0e0e0 !important; }
    div[data-testid="stMetricLabel"] { color: #a0a0a0 !important; }

    /* 3. THE SIDEBAR (Teal/Dark Glass) */
    section[data-testid="stSidebar"] {
        background-color: rgba(10, 25, 30, 0.85); 
        backdrop-filter: blur(30px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 10px 0 30px rgba(0,0,0,0.5);
    }
    
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        text-shadow: 0 0 10px rgba(255,255,255,0.2);
    }

    /* 4. TYPOGRAPHY */
    h1, h2, h3, p, label, .stMarkdown, li { color: #cfcfcf !important; }

    /* 5. GHOST BUTTONS */
    .stButton>button {
        width: 100%;
        border-radius: 50px;
        background: linear-gradient(90deg, rgba(255,255,255,0.05), rgba(255,255,255,0.1));
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: rgba(255, 255, 255, 0.2);
        border-color: #ffffff;
        box-shadow: 0 0 15px rgba(255,255,255,0.1);
        transform: translateY(-2px);
    }

    /* 6. TABS */
    .stTabs [data-baseweb="tab"] { color: #888; font-weight: 500; }
    .stTabs [aria-selected="true"] { 
        background-color: rgba(255,255,255, 0.1) !important; 
        color: #fff !important; 
        border-radius: 8px;
    }

    /* 7. INPUT FIELDS */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: rgba(0, 0, 0, 0.3) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- Helper Functions ---
def get_rules():
    try:
        with open('data/tracked_rules.json', 'r') as f: return json.load(f)
    except FileNotFoundError: return []

def get_history(rule_id):
    if not os.path.exists('data/regulations.db'): return pd.DataFrame()
    conn = sqlite3.connect('data/regulations.db')
    try:
        df = pd.read_sql_query("SELECT id, check_date, length(rule_text) as text_length, change_summary FROM rule_versions WHERE rule_id = ? ORDER BY check_date DESC", conn, params=(rule_id,))
    except Exception: df = pd.DataFrame()
    finally: conn.close()
    return df

def get_specific_version_text(version_id):
    conn = sqlite3.connect('data/regulations.db')
    cursor = conn.cursor()
    cursor.execute("SELECT rule_text FROM rule_versions WHERE id = ?", (version_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else ""

# --- CUSTOM DIFF ENGINE ---
def render_diff_html(old_text, new_text):
    a = old_text.splitlines()
    b = new_text.splitlines()
    matcher = difflib.SequenceMatcher(None, a, b)
    html = []
    html.append("""
    <style>
        .diff-row { display: flex; border-bottom: 1px solid #333; font-family: 'Helvetica Neue', sans-serif; font-size: 13px; }
        .diff-cell { flex: 1; padding: 5px 10px; word-wrap: break-word; white-space: pre-wrap; color: #ffffff; }
        .diff-num { width: 30px; color: #666; text-align: right; padding-right: 10px; border-right: 1px solid #333; user-select: none; }
        .added { background-color: rgba(15, 61, 27, 0.6); color: #84e897; } 
        .deleted { background-color: rgba(61, 20, 20, 0.6); color: #f28b8b; }
        .empty { background-color: transparent; }
    </style>
    <div style="background: rgba(0,0,0,0.2); border-radius: 8px; border: 1px solid #444; overflow: hidden;">
    """)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            for i, line in enumerate(a[i1:i2]):
                html.append(f'<div class="diff-row"><div class="diff-num">{i1+i+1}</div><div class="diff-cell">{line}</div><div class="diff-num">{j1+i+1}</div><div class="diff-cell">{line}</div></div>')
        elif tag == 'replace':
            old_chunk = a[i1:i2]
            new_chunk = b[j1:j2]
            max_len = max(len(old_chunk), len(new_chunk))
            old_chunk += [''] * (max_len - len(old_chunk))
            new_chunk += [''] * (max_len - len(new_chunk))
            for i in range(max_len):
                o_text, n_text = old_chunk[i], new_chunk[i]
                o_cls, n_cls = ("deleted" if o_text else "empty"), ("added" if n_text else "empty")
                html.append(f'<div class="diff-row"><div class="diff-num">{i1+i+1 if o_text else ""}</div><div class="diff-cell {o_cls}">{o_text}</div><div class="diff-num">{j1+i+1 if n_text else ""}</div><div class="diff-cell {n_cls}">{n_text}</div></div>')
        elif tag == 'delete':
            for i, line in enumerate(a[i1:i2]):
                html.append(f'<div class="diff-row"><div class="diff-num">{i1+i+1}</div><div class="diff-cell deleted">{line}</div><div class="diff-num"></div><div class="diff-cell empty"></div></div>')
        elif tag == 'insert':
            for i, line in enumerate(b[j1:j2]):
                html.append(f'<div class="diff-row"><div class="diff-num"></div><div class="diff-cell empty"></div><div class="diff-num">{j1+i+1}</div><div class="diff-cell added">{line}</div></div>')
    html.append("</div>")
    return "".join(html)

# --- DEMO DATA INJECTOR ---
def inject_demo_data(rule_id):
    common = """(a) Standards of Commercial Honor and Principles of Trade
A member, in the conduct of its business, shall observe high standards of commercial honor and just and equitable principles of trade.

(b) Prohibition Against Deceptive Practices
No member shall effect any transaction in, or induce the purchase or sale of, any security by means of any manipulative, deceptive or other fraudulent device or contrivance."""
    added = """
(c) New Requirement (Demo Update)
This section simulates a new regulatory requirement added by the SEC to demonstrate the redline capabilities. Because this text is NOT in the baseline, it will appear GREEN."""
    conn = sqlite3.connect('data/regulations.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS rule_versions (id INTEGER PRIMARY KEY AUTOINCREMENT, rule_id TEXT, check_date TEXT, rule_text TEXT, change_summary TEXT)''')
    c.execute("DELETE FROM rule_versions WHERE rule_id = ?", (rule_id,))
    c.execute("INSERT INTO rule_versions (rule_id, check_date, rule_text, change_summary) VALUES (?, datetime('now', '-1 day'), ?, ?)", (rule_id, common, "Historical Baseline (Demo)"))
    c.execute("INSERT INTO rule_versions (rule_id, check_date, rule_text, change_summary) VALUES (?, datetime('now'), ?, ?)", (rule_id, common + "\n" + added, "Live Audit (Demo)"))
    conn.commit()
    conn.close()
    return True

# --- APP LOGIC ---
st.sidebar.markdown("### ⚖️ Regulatory Harmony")
rules = get_rules()
if not rules: st.stop()

selected_rule_name = st.sidebar.selectbox("Select Rulebook", list({r['name']: r for r in rules}.keys()))
selected_rule = {r['name']: r for r in rules}[selected_rule_name]

if st.sidebar.button("Run Live Audit", type="primary"):
    with st.spinner("Scanning FINRA..."):
        latest = download_rule(selected_rule['url'])
        if not latest or len(latest) < 50 or "Error" in latest:
            st.error(f"Audit Failed: {latest}")
        else:
            baseline = get_latest_version(selected_rule['id'])
            if not baseline:
                log_new_version(selected_rule['id'], latest, "Initial Baseline")
                st.sidebar.success("Baseline Established")
            elif latest != baseline:
                log_new_version(selected_rule['id'], latest, "Audit: Change Detected")
                st.sidebar.warning("Change Logged")
            else:
                st.sidebar.success("Compliant")
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("##### 🛠️ Demo Tools")
if st.sidebar.button("⚠️ Load Test Data (Reset)"):
    inject_demo_data(selected_rule['id'])
    st.sidebar.success("System Reset: Demo Data Loaded.")
    st.rerun()

# --- MAIN DISPLAY ---
st.title(selected_rule_name)

# DATA FETCH
history_df = get_history(selected_rule['id'])

# TABS (Updated with "About")
tab_about, tab1, tab2, tab3 = st.tabs(["About", "Overview", "Redline Analysis", "Raw Text"])

# --- TAB 0: ABOUT ---
with tab_about:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Welcome to Regulatory Harmony")
        st.markdown("""
        **Regulatory Harmony** is an autonomous compliance monitoring engine designed to track, archive, and analyze changes in SEC and FINRA regulations.
        
        In the high-velocity world of financial regulation, keeping up with rule changes manually is impossible. This tool automates the vigilance, ensuring that legal teams and compliance officers never miss a critical amendment.
        """)
        
        st.markdown("#### 🚀 Key Capabilities")
        st.markdown("""
        * **Autonomous Surveillance:** Scrapes official regulatory bodies (FINRA/SEC) in real-time.
        * **Diff-Engine Analytics:** Uses NLP logic to compare the "DNA" of legal text, highlighting specific additions and deletions.
        * **Historical Archiving:** Maintains an immutable ledger of all rule versions over time.
        """)

    with col2:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1);">
            <h4 style="margin-top:0;">Quick Start</h4>
            <ol style="color: #ccc; padding-left: 20px;">
                <li style="margin-bottom: 10px;">Select a <b>Rulebook</b> from the sidebar.</li>
                <li style="margin-bottom: 10px;">Click <b>⚠️ Load Test Data</b> to see the simulation engine in action.</li>
                <li style="margin-bottom: 10px;">Go to the <b>Redline Analysis</b> tab to visualize the legal changes.</li>
            </ol>
            <hr style="border-color: rgba(255,255,255,0.1);">
            <div style="font-size: 12px; color: #888;">
                <strong>Tech Stack:</strong> Python, Streamlit, SQLite, BeautifulSoup, SpaCy
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 1: OVERVIEW ---
with tab1:
    if history_df.empty:
        st.info("System Ready. Please click '⚠️ Load Test Data' in the sidebar to initialize.")
    else:
        st.metric("Versions Archived", len(history_df))
        st.metric("Latest Update", pd.to_datetime(history_df['check_date'].iloc[0]).strftime('%b %d %H:%M'))
        st.line_chart(history_df.set_index('check_date')['text_length'])

# --- TAB 2: REDLINE ANALYSIS ---
with tab2:
    if history_df.empty:
        st.info("No data available.")
    elif len(history_df) < 2:
        st.warning("⚠️ Insufficient data for comparison.")
    else:
        col_a, col_b = st.columns(2)
        version_options = history_df.apply(lambda x: f"v.{x['id']} — {pd.to_datetime(x['check_date']).strftime('%b %d %H:%M')}", axis=1).tolist()
        version_map = {f"v.{row['id']} — {pd.to_datetime(row['check_date']).strftime('%b %d %H:%M')}": row['id'] for _, row in history_df.iterrows()}
        
        with col_a: ver_a_label = st.selectbox("Baseline Version", version_options, index=len(version_options)-1)
        with col_b: ver_b_label = st.selectbox("Comparison Version", version_options, index=0)
            
        id_a = version_map[ver_a_label]
        id_b = version_map[ver_b_label]
        text_a = get_specific_version_text(id_a)
        text_b = get_specific_version_text(id_b)
        
        # LEGEND
        st.markdown("""
        <div style="margin-bottom: 10px; padding: 8px; background: rgba(0,0,0,0.3); border-radius: 6px; display: flex; gap: 15px; font-family: sans-serif; font-size: 11px; color: #aaa; border: 1px solid #444; width: fit-content;">
            <span style="display:flex; align-items:center;"><span style="width:10px; height:10px; background:#0f3d1b; margin-right:5px; border:1px solid #84e897;"></span> Added</span>
            <span style="display:flex; align-items:center;"><span style="width:10px; height:10px; background:#3d1414; margin-right:5px; border:1px solid #f28b8b;"></span> Deleted</span>
        </div>
        """, unsafe_allow_html=True)

        if text_a == text_b:
            st.info("Versions are identical.")
        else:
            diff_html = render_diff_html(text_a, text_b)
            line_count = max(len(text_a.splitlines()), len(text_b.splitlines()))
            dynamic_height = min(max(300, line_count * 25 + 50), 800)
            components.html(diff_html, height=dynamic_height, scrolling=True)

# --- TAB 3: RAW TEXT ---
with tab3:
    if history_df.empty:
        st.info("No data available.")
    else:
        st.markdown("##### Current Legal Text")
        try: selected_text_view = get_specific_version_text(version_map[ver_b_label])
        except: selected_text_view = get_specific_version_text(history_df.iloc[0]['id'])
        st.code(selected_text_view, language="text")
