"""
theme.py
Premium visual theme for the Legal RAG application.
Warm cream / tan / brown palette; serif headings; monospace accents.
Call inject_theme() once at the very top of app.py, then use the
render_* helpers wherever the matching UI element appears.
"""

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Inter:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

/* ─── Palette tokens ─────────────────────────────────────────── */
:root {
    --cream:  #E4E0E1;
    --cream2: #EDE9EA;
    --tan:    #D6C0B3;
    --tan2:   #C9AE9E;
    --brown:  #AB886D;
    --dark:   #493628;
    --dark2:  #342219;
    --white:  #FDFBFA;
    --ink:    #2E1C0F;
    --muted:  #7A6558;
    --border: rgba(73,54,40,0.18);
    --shadow-sm: 0 1px 3px rgba(73,54,40,0.10), 0 1px 2px rgba(73,54,40,0.06);
    --shadow-md: 0 4px 12px rgba(73,54,40,0.12), 0 2px 4px rgba(73,54,40,0.08);
    --shadow-lg: 0 8px 24px rgba(73,54,40,0.14), 0 4px 8px rgba(73,54,40,0.08);
    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 14px;
}

/* ─── Base reset ─────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', system-ui, sans-serif;
    color: var(--dark);
    -webkit-font-smoothing: antialiased;
}
.stApp {
    background-color: var(--cream);
}
/* Remove default streamlit padding on top of main content */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 860px !important;
}

/* ─── Headings ───────────────────────────────────────────────── */
h1 {
    font-family: 'Source Serif 4', Georgia, serif !important;
    font-weight: 700 !important;
    font-size: 2rem !important;
    color: var(--ink) !important;
    letter-spacing: -0.02em;
    line-height: 1.15;
    margin-bottom: 0.1rem !important;
}
h2 {
    font-family: 'Source Serif 4', Georgia, serif !important;
    font-weight: 600 !important;
    font-size: 1.25rem !important;
    color: var(--dark) !important;
    letter-spacing: -0.01em;
}
h3 {
    font-family: 'Source Serif 4', Georgia, serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    color: var(--dark) !important;
}

/* ─── Sidebar ────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background-color: var(--dark);
    border-right: 1px solid var(--dark2);
}
section[data-testid="stSidebar"] * {
    color: var(--cream) !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.70rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.10em;
    color: var(--tan) !important;
    margin-top: 1.4rem !important;
    margin-bottom: 0.5rem !important;
}
/* File uploader zone */
section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background-color: rgba(214,192,179,0.10) !important;
    border: 1.5px dashed rgba(214,192,179,0.35) !important;
    border-radius: var(--radius-md) !important;
    padding: 0.75rem !important;
}
/* Divider in sidebar */
section[data-testid="stSidebar"] hr {
    border-color: rgba(214,192,179,0.20) !important;
    margin: 1rem 0 !important;
}
/* Success/info in sidebar */
section[data-testid="stSidebar"] [data-testid="stNotification"] {
    background-color: rgba(214,192,179,0.12) !important;
    border: 1px solid rgba(214,192,179,0.25) !important;
    border-radius: var(--radius-sm) !important;
}
/* Captions */
section[data-testid="stSidebar"] small,
section[data-testid="stSidebar"] .caption {
    color: var(--tan) !important;
    opacity: 0.75;
}
section[data-testid="stSidebar"] p {
    font-size: 0.85rem !important;
    color: rgba(228,224,225,0.80) !important;
    line-height: 1.5;
}

/* ─── Primary buttons ────────────────────────────────────────── */
.stButton > button {
    background-color: var(--dark);
    color: var(--cream);
    border: 1.5px solid var(--dark);
    border-radius: var(--radius-sm);
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    font-size: 0.875rem;
    padding: 0.55rem 1.25rem;
    letter-spacing: 0.01em;
    transition: all 0.18s ease;
    box-shadow: var(--shadow-sm);
    cursor: pointer;
}
.stButton > button:hover {
    background-color: var(--dark2);
    border-color: var(--dark2);
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
}
.stButton > button:active {
    transform: translateY(0);
    box-shadow: var(--shadow-sm);
}
/* Sidebar buttons get their own style on dark bg */
section[data-testid="stSidebar"] .stButton > button {
    background-color: var(--brown);
    color: var(--white);
    border: none;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 0.65rem 1rem;
    border-radius: var(--radius-sm);
    width: 100%;
    box-shadow: 0 2px 6px rgba(0,0,0,0.25);
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background-color: var(--tan2);
    color: var(--dark);
}

/* ─── Text input ─────────────────────────────────────────────── */
.stTextInput > div > div > input {
    background-color: var(--white);
    border: 1.5px solid var(--border);
    border-radius: var(--radius-md);
    color: var(--ink);
    font-size: 1rem;
    padding: 0.8rem 1rem;
    transition: border-color 0.18s ease, box-shadow 0.18s ease;
    box-shadow: var(--shadow-sm);
}
.stTextInput > div > div > input:focus {
    border-color: var(--brown);
    box-shadow: 0 0 0 3px rgba(171,136,109,0.15), var(--shadow-sm);
    outline: none;
}
.stTextInput > div > div > input::placeholder {
    color: var(--muted);
    font-style: italic;
}
/* Label above input */
.stTextInput label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted) !important;
    margin-bottom: 0.35rem !important;
}

/* ─── Progress bar ───────────────────────────────────────────── */
.stProgress > div > div > div > div {
    background-color: var(--brown) !important;
}

/* ─── Expander ───────────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    background-color: var(--white) !important;
}

/* ─── Spinner ────────────────────────────────────────────────── */
[data-testid="stSpinner"] > div {
    border-top-color: var(--brown) !important;
}

/* ═══════════════════════════════════════════════════════════════
   CUSTOM COMPONENTS
═══════════════════════════════════════════════════════════════ */

/* ─── App header bar ─────────────────────────────────────────── */
.app-header {
    display: flex;
    align-items: baseline;
    gap: 0.75rem;
    margin-bottom: 0.25rem;
}
.app-header-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--brown);
    background: rgba(171,136,109,0.12);
    border: 1px solid rgba(171,136,109,0.30);
    border-radius: 4px;
    padding: 0.15rem 0.5rem;
    vertical-align: middle;
    position: relative;
    top: -2px;
}
.app-header-title {
    font-family: 'Source Serif 4', Georgia, serif;
    font-weight: 700;
    font-size: 2.0rem;
    color: var(--ink);
    letter-spacing: -0.025em;
    line-height: 1.1;
}
.app-header-subtitle {
    font-size: 0.875rem;
    color: var(--muted);
    margin-top: 0.15rem;
    margin-bottom: 1.4rem;
    font-weight: 400;
    line-height: 1.5;
}

/* ─── Query card ─────────────────────────────────────────────── */
.query-card {
    background: var(--white);
    border: 1.5px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.4rem 1.5rem 1.25rem;
    box-shadow: var(--shadow-md);
    margin-bottom: 1.25rem;
}
.query-card-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.10em;
    color: var(--brown);
    margin-bottom: 0.6rem;
}

/* ─── Section divider label ──────────────────────────────────── */
.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.10em;
    color: var(--muted);
    margin-bottom: 0.65rem;
    margin-top: 0.1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.section-label::after {
    content: "";
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ─── Mode tabs (folder-tab visual) ──────────────────────────── */
.mode-tabs {
    display: flex;
    gap: 0;
    margin-bottom: -1px;
    position: relative;
    z-index: 1;
}
.mode-tab {
    flex: 1;
    padding: 0.65rem 0.75rem;
    text-align: center;
    background-color: var(--cream2);
    border: 1px solid var(--border);
    border-bottom: none;
    border-radius: var(--radius-sm) var(--radius-sm) 0 0;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--muted);
    font-weight: 500;
    cursor: default;
    transition: background 0.15s;
    margin-right: 3px;
}
.mode-tab:last-child { margin-right: 0; }
.mode-tab.active {
    background-color: var(--white);
    color: var(--dark);
    font-weight: 700;
    border-color: var(--border);
    border-bottom: 2px solid var(--white);
}
.mode-panel {
    background-color: var(--white);
    border: 1px solid var(--border);
    border-radius: 0 0 var(--radius-md) var(--radius-md);
    padding: 1rem 1.25rem 0.5rem;
}

/* ─── Mode button grid (below the tabs) ─────────────────────── */
.mode-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
    padding: 0;
    margin: 0;
}
.mode-card {
    background: var(--white);
    border: 1.5px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1rem;
    position: relative;
    overflow: hidden;
    transition: box-shadow 0.18s ease, border-color 0.18s ease, transform 0.15s ease;
}
.mode-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--tan);
    border-radius: var(--radius-md) var(--radius-md) 0 0;
}
.mode-card.active {
    border-color: var(--brown);
    box-shadow: var(--shadow-md);
}
.mode-card.active::before { background: var(--brown); }
.mode-card-icon {
    font-size: 1.25rem;
    margin-bottom: 0.35rem;
    display: block;
}
.mode-card-title {
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 700;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--dark);
    margin-bottom: 0.25rem;
}
.mode-card-desc {
    font-size: 0.78rem;
    color: var(--muted);
    line-height: 1.45;
}

/* ─── Citation stamps ────────────────────────────────────────── */
.citations-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin: 0.6rem 0 0.25rem;
}
.citation-stamp {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.70rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--dark);
    background-color: var(--cream2);
    border: 1.5px solid var(--dark);
    outline: 1.5px solid var(--brown);
    outline-offset: 2px;
    border-radius: 4px;
    padding: 0.25rem 0.55rem;
    white-space: nowrap;
    transition: background 0.15s, transform 0.12s;
}
.citation-stamp:hover {
    background-color: var(--tan);
    transform: translateY(-1px);
}
.citation-stamp::before {
    content: "\00a7";
    font-weight: 700;
    color: var(--brown);
    font-size: 0.75rem;
}

/* ─── Warning / advisory box ─────────────────────────────────── */
.warning-box {
    display: flex;
    align-items: flex-start;
    gap: 0.65rem;
    background: rgba(214,192,179,0.30);
    border: 1px solid var(--tan2);
    border-left: 4px solid var(--brown);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    padding: 0.85rem 1.1rem;
    margin: 0.75rem 0;
    font-size: 0.875rem;
    color: var(--dark);
    line-height: 1.5;
}
.warning-box::before {
    content: "⚠";
    font-size: 1rem;
    color: var(--brown);
    flex-shrink: 0;
    margin-top: 0.05rem;
}

/* ─── Progress steps ─────────────────────────────────────────── */
.progress-steps {
    display: flex;
    align-items: center;
    gap: 0;
    margin: 1rem 0 0.75rem;
    padding: 1rem 1.25rem;
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
}
.progress-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.35rem;
    flex: 1;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--tan2);
    text-align: center;
    position: relative;
}
.progress-step .dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--tan);
    border: 2px solid var(--tan2);
    transition: all 0.25s ease;
    z-index: 1;
}
.progress-step.done .dot {
    background: var(--dark);
    border-color: var(--dark);
    box-shadow: 0 0 0 3px rgba(73,54,40,0.15);
}
.progress-step.active .dot {
    background: var(--brown);
    border-color: var(--brown);
    box-shadow: 0 0 0 4px rgba(171,136,109,0.25);
    animation: pulse 1.4s infinite;
}
.progress-step.done { color: var(--dark); font-weight: 600; }
.progress-step.active { color: var(--brown); font-weight: 700; }
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 3px rgba(171,136,109,0.25); }
    50%       { box-shadow: 0 0 0 6px rgba(171,136,109,0.12); }
}
.progress-line {
    flex: 1 0 20px;
    height: 2px;
    background: linear-gradient(to right, var(--tan2), var(--tan));
    margin: 0;
    position: relative;
    top: -8px;
}
.progress-line.done {
    background: var(--dark);
}

/* ─── Answer card ────────────────────────────────────────────── */
.answer-card {
    background: var(--white);
    border: 1.5px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem 1.75rem;
    margin-top: 1.25rem;
    box-shadow: var(--shadow-lg);
    position: relative;
}
.answer-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(to right, var(--brown), var(--tan));
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}
.answer-card-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.10em;
    color: var(--brown);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.answer-card-header::after {
    content: "";
    flex: 1;
    height: 1px;
    background: var(--border);
}
.answer-verified-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.64rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    background: rgba(73,54,40,0.08);
    border: 1px solid rgba(73,54,40,0.18);
    color: var(--dark);
}
.answer-text {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.0rem;
    color: var(--ink);
    line-height: 1.75;
    margin: 0;
}
.answer-footer {
    margin-top: 1.1rem;
    padding-top: 0.9rem;
    border-top: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    flex-wrap: wrap;
}
.confidence-line {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.70rem;
    color: var(--muted);
    letter-spacing: 0.03em;
}

/* ─── Sidebar: document item ─────────────────────────────────── */
.doc-item {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    padding: 0.5rem 0.6rem;
    border-radius: var(--radius-sm);
    background: rgba(214,192,179,0.10);
    border: 1px solid rgba(214,192,179,0.18);
    margin-bottom: 0.4rem;
    font-size: 0.80rem;
    color: rgba(228,224,225,0.90);
    font-family: 'Inter', sans-serif;
    word-break: break-word;
}
.doc-item-icon {
    font-size: 0.9rem;
    flex-shrink: 0;
    opacity: 0.85;
}

/* ─── Sidebar: stat pill ─────────────────────────────────────── */
.stat-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    font-weight: 600;
    padding: 0.25rem 0.6rem;
    border-radius: 20px;
    background: rgba(171,136,109,0.20);
    border: 1px solid rgba(171,136,109,0.35);
    color: var(--tan);
    margin-bottom: 0.6rem;
}

/* ─── Empty state in sidebar ─────────────────────────────────── */
.empty-state {
    text-align: center;
    padding: 1.2rem 0.75rem;
    opacity: 0.55;
    font-size: 0.82rem;
    color: var(--tan);
    font-style: italic;
}

/* ─── Streamlit caption tweak ────────────────────────────────── */
.stCaption, small {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.70rem !important;
    color: var(--muted) !important;
    letter-spacing: 0.02em;
}

/* ─── Success / info messages ────────────────────────────────── */
[data-testid="stNotification"] {
    border-radius: var(--radius-sm) !important;
    font-size: 0.85rem !important;
}

/* ─── Hide Streamlit branding / toolbar clutter ──────────────── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
</style>
"""


# ─── Inject ──────────────────────────────────────────────────────────────────

def inject_theme():
    """Call once near the very top of app.py, before any other st. calls."""
    st.markdown(CSS, unsafe_allow_html=True)


# ─── Render helpers ──────────────────────────────────────────────────────────

def render_app_header():
    """Renders the branded application header with eyebrow tag + subtitle."""
    st.markdown(
        """
        <div class="app-header">
            <span class="app-header-eyebrow">AI · Legal Research</span>
            <span class="app-header-title">Legal RAG</span>
        </div>
        <p class="app-header-subtitle">
            Upload case PDFs, build your knowledge base, and ask natural-language
            questions — grounded answers, fully cited.
        </p>
        """,
        unsafe_allow_html=True,
    )


def render_section_label(label: str):
    """Small all-caps monospace label with a trailing rule — use as a section divider."""
    st.markdown(
        f'<div class="section-label">{label}</div>',
        unsafe_allow_html=True,
    )


def render_doc_item(filename: str):
    """A styled document row for the sidebar knowledge-base list."""
    st.markdown(
        f'<div class="doc-item"><span class="doc-item-icon">📄</span>{filename}</div>',
        unsafe_allow_html=True,
    )


def render_stat_pill(count: int, label: str):
    """A small pill badge showing a count — e.g. '3 cases indexed'."""
    st.markdown(
        f'<div class="stat-pill">◈ {count} {label}</div>',
        unsafe_allow_html=True,
    )


def render_citation_stamp(case_name: str, page_number):
    """Returns HTML for one citation badge."""
    return f'<span class="citation-stamp">{case_name}, p.{page_number}</span>'


def render_citations(chunks):
    """Renders a row of stamped citation badges from a list of {case_name, page_number} dicts."""
    if not chunks:
        return
    html = '<div class="citations-row">'
    html += "".join(render_citation_stamp(c["case_name"], c["page_number"]) for c in chunks)
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_mode_tabs(selected_mode: str):
    """
    Visual folder-tab row indicating the active mode.
    selected_mode: one of 'fast', 'deep', 'auto'.
    Pair with real st.button() calls beneath for click handling — visual only.
    """
    modes = [
        ("fast",  "⚡", "Fast"),
        ("deep",  "🔎", "Deep Thinking"),
        ("auto",  "🤖", "Auto"),
    ]
    tabs_html = '<div class="mode-tabs">'
    for key, icon, label in modes:
        active = "active" if key == selected_mode else ""
        tabs_html += f'<div class="mode-tab {active}">{icon} {label}</div>'
    tabs_html += '</div><div class="mode-panel"></div>'
    st.markdown(tabs_html, unsafe_allow_html=True)


def render_warning_box(message: str):
    """Advisory warning rendered as a styled left-bordered tan box."""
    st.markdown(
        f'<div class="warning-box">{message}</div>',
        unsafe_allow_html=True,
    )


def render_progress_steps(step_labels: list, current_index: int):
    """
    Renders a horizontal step-track progress indicator.
    step_labels: list of stage name strings.
    current_index: 0-based index of the currently active step.
    """
    html = '<div class="progress-steps">'
    for i, label in enumerate(step_labels):
        if i < current_index:
            state = "done"
        elif i == current_index:
            state = "active"
        else:
            state = ""
        html += (
            f'<div class="progress-step {state}">'
            f'<span class="dot"></span>'
            f'{label}'
            f'</div>'
        )
        if i < len(step_labels) - 1:
            line_class = "done" if i < current_index else ""
            html += f'<div class="progress-line {line_class}"></div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_answer_card(answer_text: str, verified: bool, confidence_line: str = "", citations_html: str = ""):
    """
    Renders the full answer in an elevated card with header, body text,
    optional citation row, and confidence/verified footer line.
    """
    verified_badge = (
        '<span class="answer-verified-badge">✓ Verified</span>'
        if verified
        else '<span class="answer-verified-badge" style="opacity:0.55">⚠ Unverified</span>'
    )
    footer_parts = []
    if confidence_line:
        footer_parts.append(f'<span class="confidence-line">{confidence_line}</span>')

    footer_html = (
        f'<div class="answer-footer">{" ".join(footer_parts)}{verified_badge}</div>'
        if footer_parts or verified
        else ""
    )

    citations_block = f'<div class="citations-row">{citations_html}</div>' if citations_html else ""

    st.markdown(
        f"""
        <div class="answer-card">
            <div class="answer-card-header">Answer</div>
            <p class="answer-text">{answer_text}</p>
            {citations_block}
            {footer_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
