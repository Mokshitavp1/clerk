"""
theme.py
Custom visual theme for the legal RAG app: warm cream/tan/brown palette,
serif headings, monospace citation "stamps". Import and call inject_theme()
once at the top of app.py, then use the render_* helpers wherever the
matching UI element appears.
"""

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap');

:root {
    --cream: #E4E0E1;
    --tan: #D6C0B3;
    --brown: #AB886D;
    --dark: #493628;
}

/* base */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: var(--dark);
}
.stApp {
    background-color: var(--cream);
}

/* headings — serif, tightened tracking, no generic bold-black */
h1, h2, h3 {
    font-family: 'Source Serif 4', serif !important;
    color: var(--dark) !important;
    letter-spacing: -0.01em;
}
h1 {
    border-bottom: 2px solid var(--brown);
    padding-bottom: 0.4rem;
}

/* sidebar — case-file panel */
section[data-testid="stSidebar"] {
    background-color: var(--tan);
    border-right: 1px solid var(--brown);
}
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--dark) !important;
}

/* buttons */
.stButton > button {
    background-color: var(--dark);
    color: var(--cream);
    border: none;
    border-radius: 4px;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    padding: 0.5rem 1.2rem;
    transition: background-color 0.15s ease;
}
.stButton > button:hover {
    background-color: var(--brown);
    color: var(--dark);
}

/* text input */
.stTextInput > div > div > input {
    background-color: white;
    border: 1px solid var(--brown);
    border-radius: 4px;
    color: var(--dark);
}

/* mode selector — folder-tab styling, use with render_mode_tabs() markup */
.mode-tabs {
    display: flex;
    gap: 4px;
    margin-bottom: 0;
}
.mode-tab {
    flex: 1;
    padding: 0.7rem 1rem;
    text-align: center;
    background-color: var(--tan);
    border: 1px solid var(--brown);
    border-bottom: none;
    border-radius: 8px 8px 0 0;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--dark);
    opacity: 0.6;
}
.mode-tab.active {
    background-color: white;
    opacity: 1;
    font-weight: 600;
    border-bottom: 1px solid white;
    margin-bottom: -1px;
}
.mode-panel {
    background-color: white;
    border: 1px solid var(--brown);
    border-radius: 0 0 8px 8px;
    padding: 1rem 1.2rem;
    font-size: 0.9rem;
    color: var(--dark);
    opacity: 0.85;
}

/* citation stamp — the signature element */
.citation-stamp {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--dark);
    background-color: var(--cream);
    border: 1.5px solid var(--dark);
    outline: 1px solid var(--brown);
    outline-offset: 2px;
    border-radius: 3px;
    padding: 0.3rem 0.6rem;
    margin: 0.2rem 0.3rem 0.2rem 0;
}
.citation-stamp::before {
    content: "\\00a7"; /* section sign, reads as a legal mark */
    font-weight: 600;
}

/* advisory warning box */
.warning-box {
    background-color: var(--tan);
    border-left: 4px solid var(--brown);
    border-radius: 4px;
    padding: 0.8rem 1rem;
    margin: 0.6rem 0;
    font-size: 0.9rem;
    color: var(--dark);
}

/* progress steps */
.progress-steps {
    display: flex;
    align-items: center;
    margin: 1rem 0;
}
.progress-step {
    display: flex;
    align-items: center;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    color: var(--brown);
}
.progress-step.done { color: var(--dark); }
.progress-step.active { color: var(--dark); font-weight: 600; }
.progress-step .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: var(--brown);
    margin-right: 6px;
}
.progress-step.done .dot,
.progress-step.active .dot {
    background-color: var(--dark);
}
.progress-line {
    flex: 1;
    height: 1px;
    background-color: var(--brown);
    margin: 0 10px;
}
</style>
"""


def inject_theme():
    """Call once near the top of app.py, before any other st. calls."""
    st.markdown(CSS, unsafe_allow_html=True)


def render_citation_stamp(case_name, page_number):
    """Returns HTML for one citation badge. Use with st.markdown(..., unsafe_allow_html=True)."""
    return f'<span class="citation-stamp">{case_name}, p.{page_number}</span>'


def render_citations(chunks):
    """Renders a row of citation stamps from a list of {case_name, page_number} dicts."""
    html = "".join(render_citation_stamp(c["case_name"], c["page_number"]) for c in chunks)
    st.markdown(html, unsafe_allow_html=True)


def render_mode_tabs(selected_mode):
    """
    selected_mode: one of "fast", "deep", "auto"
    Renders the visual folder-tab row. Pair with actual st.button() calls
    beneath it for the real click handling — this is visual only.
    """
    modes = [
        ("fast", "⚡ Fast"),
        ("deep", "🔎 Deep Thinking"),
        ("auto", "🤖 Auto"),
    ]
    tabs_html = '<div class="mode-tabs">'
    for key, label in modes:
        active_class = "active" if key == selected_mode else ""
        tabs_html += f'<div class="mode-tab {active_class}">{label}</div>'
    tabs_html += "</div>"
    st.markdown(tabs_html, unsafe_allow_html=True)


def render_warning_box(message):
    """Advisory warning shown when Fast is selected on a likely multi-hop question."""
    st.markdown(f'<div class="warning-box">{message}</div>', unsafe_allow_html=True)


def render_progress_steps(step_labels, current_index):
    """
    step_labels: list of strings, e.g. ["Searching cases", "Reading matches", "Drafting", "Verifying"]
    current_index: index of the currently active step (0-based)
    """
    html = '<div class="progress-steps">'
    for i, label in enumerate(step_labels):
        if i < current_index:
            state = "done"
        elif i == current_index:
            state = "active"
        else:
            state = ""
        html += f'<div class="progress-step {state}"><span class="dot"></span>{label}</div>'
        if i < len(step_labels) - 1:
            html += '<div class="progress-line"></div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)
