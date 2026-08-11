"""Static visual baseline for the Legal Retrieval Assistant query screen."""

import streamlit as st


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
    section[data-testid="stSidebar"] .block-container { padding: 30px 22px 24px !important; }
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

    .sidebar-title { margin: 0 0 28px; color: #F5F0E9; font: 700 22px/1.1 'Source Serif 4', Georgia, serif; }
    .sidebar-label { color: var(--tan); font: 600 10px/1 'IBM Plex Mono', monospace; letter-spacing: .13em; }
    .dropzone { margin-top: 10px; min-height: 126px; display: grid; place-items: center; border: 1px dashed rgba(214,192,179,.64); border-radius: 8px; background: rgba(228,224,225,.07); }
    .upload-pill { display: inline-block; padding: 10px 22px; border-radius: 999px; background: var(--tan); color: var(--brown); font: 700 13px/1 Inter, sans-serif; }
    .sidebar-rule { border: 0; height: 1px; background: rgba(214,192,179,.28); margin: 24px 0; }
    .empty-docs { margin: 38px 14px 0; text-align: center; color: rgba(228,224,225,.74); font: italic 14px/1.5 'Source Serif 4', Georgia, serif; }
    .build-button { position: fixed; bottom: 24px; left: 22px; width: 246px; padding: 13px 14px; background: var(--tan); border-radius: 7px; color: var(--brown); text-align: center; font: 700 11px/1.38 Inter, sans-serif; letter-spacing: .025em; }

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
    .suggestions { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-top: 17px; }
    .suggestion { min-height: 106px; padding: 16px; border: 1px solid var(--line); border-radius: 8px; background: rgba(253,251,248,.58); }
    .suggestion-label { display: block; margin-bottom: 10px; color: var(--tan); font: 600 10px/1 'IBM Plex Mono', monospace; letter-spacing: .1em; }
    .suggestion-text { color: var(--brown); font: 500 13px/1.45 Inter, sans-serif; }
    @media (max-width: 800px) {
        section[data-testid="stSidebar"] { width: 250px !important; min-width: 250px !important; }
        .build-button { width: 206px; }
        .suggestions { grid-template-columns: 1fr; }
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
        <div class="sidebar-title">Knowledge Base</div>
        <div class="sidebar-label">UPLOAD CASES</div>
        <div class="dropzone"><span class="upload-pill">↑&nbsp; Upload</span></div>
        <hr class="sidebar-rule">
        <div class="sidebar-label">DOCUMENTS</div>
        <div class="empty-docs">No case PDFs uploaded yet.</div>
        <div class="build-button">↑ BUILD / UPDATE<br>KNOWLEDGE BASE</div>
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
