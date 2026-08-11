"""Legal Retrieval Assistant query screen."""

import os
import sys

import streamlit as st


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
for _folder in ("retrieval", "generation"):
    _path = os.path.join(PROJECT_ROOT, _folder)
    if _path not in sys.path:
        sys.path.insert(0, _path)


st.set_page_config(page_title="Legal Retrieval Assistant", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700&family=Source+Serif+4:ital,wght@0,600;0,700;1,400&display=swap');

    :root {
        --mist: #E4E0E1;
        --sand: #D6C0B3;
        --tan: #AB886D;
        --brown: #493628;
        --canvas: #F1EEE9;
        --paper: #FDFBF8;
        --muted: #806C5D;
        --line: rgba(73, 54, 40, .18);
    }
    * { box-sizing: border-box; }
    html, body, [class*="css"] { font-family: Inter, sans-serif; }
    .stApp { background: var(--canvas); }
    #MainMenu, header[data-testid="stHeader"], footer { visibility: hidden; }
    .block-container {
        max-width: 100% !important;
        padding: 0 !important;
    }
    section[data-testid="stSidebar"] {
        width: 290px !important;
        min-width: 290px !important;
        top: 68px !important;
        height: calc(100vh - 68px) !important;
        background: var(--brown) !important;
        border-right: 1px solid rgba(214, 192, 179, .18);
    }
    section[data-testid="stSidebar"] > div { background: var(--brown) !important; }
    section[data-testid="stSidebar"] .block-container { height: 100%; padding: 0 !important; }
    [data-testid="stSidebarCollapseButton"] { display: none; }

    .topbar {
        position: fixed; z-index: 1000; top: 0; left: 0; right: 0; height: 68px;
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 28px; background: #F8F6F2; border-bottom: 1px solid var(--line);
    }
    .brand { display: flex; align-items: center; gap: 10px; color: var(--brown); }
    .brand-mark { font-size: 19px; line-height: 1; color: var(--tan); }
    .brand-name { font: 700 19px/1 'Source Serif 4', Georgia, serif; letter-spacing: -.02em; }
    .topbar-right { display: flex; align-items: center; gap: 14px; }
    .system-status {
        color: #8A5B4B; background: #F2E7E0; border: 1px solid #D6C0B3; border-radius: 999px;
        padding: 7px 11px; font: 600 10px/1 'IBM Plex Mono', monospace; letter-spacing: .06em;
    }
    .avatar { width: 32px; height: 32px; display: grid; place-items: center; border-radius: 50%; background: var(--brown); color: var(--mist); font-size: 15px; }

    .sidebar-layout { height: 100%; display: grid; grid-template-rows: minmax(0, 1fr) 1px minmax(0, 1fr); }
    .sidebar-pane { min-height: 0; overflow-y: auto; padding: 30px 22px 24px; scrollbar-color: rgba(214,192,179,.45) transparent; }
    .knowledge-pane { display: flex; flex-direction: column; }
    .sidebar-pane::-webkit-scrollbar, .document-list::-webkit-scrollbar, .history-list::-webkit-scrollbar { width: 5px; }
    .sidebar-pane::-webkit-scrollbar-thumb, .document-list::-webkit-scrollbar-thumb, .history-list::-webkit-scrollbar-thumb { background: rgba(214,192,179,.45); border-radius: 99px; }
    .sidebar-divider { background: rgba(214,192,179,.28); margin: 0 22px; }
    .sidebar-title { margin: 0 0 28px; color: #F5F0E9; font: 700 22px/1.1 'Source Serif 4', Georgia, serif; }
    .sidebar-label { color: var(--tan); font: 600 10px/1 'IBM Plex Mono', monospace; letter-spacing: .13em; }
    .dropzone { margin-top: 10px; min-height: 126px; display: grid; place-items: center; border: 1px dashed rgba(214,192,179,.64); border-radius: 8px; background: rgba(228,224,225,.07); }
    .upload-pill { display: inline-block; padding: 10px 22px; border-radius: 999px; background: var(--tan); color: var(--brown); font: 700 13px/1 Inter, sans-serif; }
    .sidebar-rule { border: 0; height: 1px; background: rgba(214,192,179,.28); margin: 24px 0; }
    .document-list { max-height: 112px; overflow-y: auto; margin-top: 12px; padding-right: 5px; }
    .empty-docs { margin: 22px 14px; text-align: center; color: rgba(228,224,225,.74); font: italic 14px/1.5 'Source Serif 4', Georgia, serif; }
    .build-button { display: block; width: 100%; margin-top: auto; padding: 13px 14px; background: var(--tan); border-radius: 7px; color: var(--brown); text-align: center; font: 700 11px/1.38 Inter, sans-serif; letter-spacing: .025em; }
    .history-heading { margin: 0 0 17px; color: #F5F0E9; font: 700 22px/1.1 'Source Serif 4', Georgia, serif; }
    .history-list { max-height: 220px; overflow-y: auto; margin-top: 12px; padding-right: 5px; }
    .history-item { padding: 0 0 13px; margin-bottom: 13px; border-bottom: 1px solid rgba(214,192,179,.18); }
    .history-item:last-child { margin-bottom: 0; }
    .history-query { margin-bottom: 8px; color: rgba(228,224,225,.9); font: 500 12px/1.46 Inter, sans-serif; }
    .trust-tag { display: inline-flex; align-items: center; border: 1px solid rgba(214,192,179,.48); border-radius: 4px; padding: 4px 6px; color: var(--sand); font: 600 9px/1 'IBM Plex Mono', monospace; letter-spacing: .04em; }
    .trust-tag.unverified { color: var(--tan); border-color: rgba(171,136,109,.6); }
    .trust-tag.insufficient { color: rgba(228,224,225,.6); border-color: rgba(228,224,225,.25); }

    .main-shell { min-height: calc(100vh - 68px); padding: 68px 28px 56px; }
    .query-page { max-width: 890px; margin: 0 auto; padding-top: 83px; }
    .eyebrow { text-align: center; color: var(--tan); font: 600 11px/1 'IBM Plex Mono', monospace; letter-spacing: .13em; }
    .query-page h1 { margin: 13px 0 13px; color: var(--brown); text-align: center; font: 700 45px/1.08 'Source Serif 4', Georgia, serif; letter-spacing: -.035em; }
    .intro { max-width: 635px; margin: 0 auto 34px; text-align: center; color: var(--muted); font-size: 15px; line-height: 1.65; }
    .query-card { background: var(--paper); border: 1px solid var(--line); border-radius: 11px; overflow: hidden; box-shadow: 0 2px 8px rgba(73,54,40,.035); }
    .card-top, .card-bottom { display: flex; align-items: center; justify-content: space-between; gap: 18px; padding: 16px 18px; }
    .card-top { border-bottom: 1px solid var(--line); }
    .mode-control { display: flex; align-items: center; gap: 5px; }
    .mode { padding: 8px 11px; border: 1px solid rgba(73,54,40,.25); border-radius: 5px; color: var(--muted); background: transparent; font: 600 10px/1 'IBM Plex Mono', monospace; letter-spacing: .07em; }
    .mode.active { color: var(--paper); background: var(--brown); border-color: var(--brown); }
    .options, .nlp { color: var(--muted); font: 600 10px/1 'IBM Plex Mono', monospace; letter-spacing: .07em; white-space: nowrap; }
    .question-space { min-height: 166px; padding: 25px 20px; color: #9C938C; font: italic 16px/1.55 'Source Serif 4', Georgia, serif; }
    .card-bottom { border-top: 1px solid var(--line); }
    .actions { display: flex; align-items: center; gap: 17px; }
    .ambiguity { color: var(--brown); font: 600 10px/1 'IBM Plex Mono', monospace; text-decoration: underline; text-underline-offset: 3px; letter-spacing: .05em; white-space: nowrap; }
    .retrieve { display: inline-block; border-radius: 5px; padding: 11px 15px; color: var(--paper); background: var(--brown); font: 700 11px/1 Inter, sans-serif; letter-spacing: .055em; white-space: nowrap; }
    [data-testid="stForm"] { max-width: 890px; margin: 0 auto; background: var(--paper); border: 1px solid var(--line); border-radius: 11px; overflow: hidden; box-shadow: 0 2px 8px rgba(73,54,40,.035); }
    [data-testid="stForm"] form { border: 0 !important; padding: 0 !important; }
    [data-testid="stForm"] [data-testid="stTextArea"] { padding: 0 18px; }
    [data-testid="stForm"] textarea { min-height: 150px !important; border: 0 !important; background: transparent !important; box-shadow: none !important; color: var(--brown) !important; font: italic 16px/1.55 'Source Serif 4', Georgia, serif !important; resize: none; }
    [data-testid="stForm"] textarea::placeholder { color: #9C938C !important; opacity: 1; }
    .form-top { display: flex; align-items: center; justify-content: space-between; gap: 18px; padding: 16px 18px; border-bottom: 1px solid var(--line); }
    .form-bottom { display: flex; align-items: center; justify-content: space-between; gap: 18px; padding: 12px 18px 16px; border-top: 1px solid var(--line); }
    .progress-stepper { max-width: 890px; margin: 22px auto 0; padding: 18px 20px; border: 1px solid var(--line); border-radius: 9px; background: rgba(253,251,248,.65); }
    .progress-track { display: grid; grid-template-columns: 1fr 1fr 1fr; }
    .step { position: relative; display: flex; align-items: center; gap: 8px; color: var(--muted); font: 600 10px/1 'IBM Plex Mono', monospace; letter-spacing: .07em; }
    .step:not(:last-child)::after { content: ''; position: absolute; top: 9px; left: 78px; right: 13px; height: 1px; background: var(--sand); }
    .step.complete:not(:last-child)::after { background: var(--tan); }
    .step-dot { position: relative; z-index: 1; display: grid; place-items: center; width: 19px; height: 19px; border-radius: 50%; color: var(--muted); background: var(--paper); border: 1px solid var(--sand); font-size: 11px; }
    .step.active { color: var(--brown); }
    .step.active .step-dot { background: var(--brown); border-color: var(--brown); color: var(--paper); }
    .step.complete { color: var(--brown); }
    .step.complete .step-dot { background: var(--tan); border-color: var(--tan); color: var(--brown); font-weight: 700; }
    .step-status { margin: 14px 0 0 27px; color: var(--muted); font: 500 12px/1.4 Inter, sans-serif; }
    .result-card { max-width: 890px; margin: 22px auto 0; padding: 20px; background: var(--paper); border: 1px solid var(--line); border-radius: 9px; color: var(--brown); line-height: 1.6; }
    @media (max-width: 800px) {
        section[data-testid="stSidebar"] { width: 250px !important; min-width: 250px !important; }
        .query-page h1 { font-size: 38px; }
    }
    </style>
    <div class="topbar">
      <div class="brand"><span class="brand-mark">⚖</span><span class="brand-name">Legal Retrieval Assistant</span></div>
      <div class="topbar-right"><span class="system-status">● SYSTEM STATUS: OFFLINE</span><span class="avatar">♙</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-layout">
          <section class="sidebar-pane knowledge-pane">
            <div class="sidebar-title">Knowledge Base</div>
            <div class="sidebar-label">UPLOAD CASES</div>
            <div class="dropzone"><span class="upload-pill">&uarr;&nbsp; Upload</span></div>
            <hr class="sidebar-rule">
            <div class="sidebar-label">DOCUMENTS</div>
            <div class="document-list">
              <div class="empty-docs">No case PDFs uploaded yet.</div>
            </div>
            <div class="build-button">&uarr; BUILD / UPDATE<br>KNOWLEDGE BASE</div>
          </section>
          <div class="sidebar-divider"></div>
          <section class="sidebar-pane history-pane">
            <div class="history-heading">History</div>
            <div class="sidebar-label">PAST QUERIES</div>
            <div class="history-list">
              <article class="history-item"><div class="history-query">Statute of limitations for medical malpractice in New York</div><span class="trust-tag">&sect; VERIFIED</span></article>
              <article class="history-item"><div class="history-query">Exceptions to the hearsay rule for business records</div><span class="trust-tag">&sect; VERIFIED</span></article>
              <article class="history-item"><div class="history-query">Recent Supreme Court rulings on Chevron deference</div><span class="trust-tag unverified">&sect; UNVERIFIED</span></article>
              <article class="history-item"><div class="history-query">Delaware veil-piercing standard and undercapitalization</div><span class="trust-tag insufficient">&sect; INSUFFICIENT</span></article>
              <article class="history-item"><div class="history-query">Elements required to establish promissory estoppel</div><span class="trust-tag">&sect; VERIFIED</span></article>
            </div>
          </section>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <main class="main-shell"><section class="query-page">
      <div class="eyebrow">§ QUERY ENGINE V.4</div>
      <h1>Ask a Legal Question</h1>
      <p class="intro">Enter your query, cite specific statutes, or describe a fact pattern. The system will retrieve relevant case law and synthesize a memorandum.</p>
      <section class="query-card">
        <div class="card-top">
          <div class="mode-control"><span class="mode active">FAST</span><span class="mode">DEEP THINKING</span><span class="mode">AUTO</span></div>
          <span class="options">⚙ OPTIONS</span>
        </div>
        <div class="question-space">E.g., What is the standard for piercing the corporate veil in Delaware regarding undercapitalization?</div>
        <div class="card-bottom"><span class="nlp">◈ NLP ACTIVE</span><div class="actions"><span class="ambiguity">TEST AMBIGUITY</span><span class="retrieve">RETRIEVE →</span></div></div>
      </section>
      <section class="suggestions">
        <article class="suggestion"><span class="suggestion-label">RECENT QUERY</span><div class="suggestion-text">Statute of limitations for medical malpractice in New...</div></article>
        <article class="suggestion"><span class="suggestion-label">SUGGESTED</span><div class="suggestion-text">Exceptions to the hearsay rule for business records in feder...</div></article>
        <article class="suggestion"><span class="suggestion-label">TRENDING</span><div class="suggestion-text">Recent Supreme Court rulings on Chevron deference...</div></article>
      </section>
    </section></main>
    """,
    unsafe_allow_html=True,
)
