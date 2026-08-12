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
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Inter:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');

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
    --transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

/* ─── Base reset & Smooth Scroll ──────────────────────────────── */
html {
    scroll-behavior: smooth;
}
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
    padding-top: 1.5rem !important;
    padding-bottom: 4rem !important;
    max-width: 920px !important;
}

/* ─── Headings ───────────────────────────────────────────────── */
h1 {
    font-family: 'Source Serif 4', Georgia, serif !important;
    font-weight: 700 !important;
    font-size: 2.2rem !important;
    color: var(--ink) !important;
    letter-spacing: -0.02em;
    line-height: 1.15;
    margin-bottom: 0.1rem !important;
}
h2 {
    font-family: 'Source Serif 4', Georgia, serif !important;
    font-weight: 600 !important;
    font-size: 1.35rem !important;
    color: var(--dark) !important;
    letter-spacing: -0.01em;
    margin-top: 1.5rem !important;
}
h3 {
    font-family: 'Source Serif 4', Georgia, serif !important;
    font-weight: 600 !important;
    font-size: 1.1rem !important;
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
section[data-testid="stSidebar"] [data-testid="stFileUploader"],
.main-upload-zone {
    background-color: rgba(214,192,179,0.06) !important;
    border: 1.5px dashed rgba(214,192,179,0.30) !important;
    border-radius: var(--radius-md) !important;
    padding: 0.75rem !important;
    transition: var(--transition) !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"]:hover,
.main-upload-zone:hover {
    border-color: var(--brown) !important;
    background-color: rgba(214,192,179,0.12) !important;
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
    font-weight: 600;
    font-size: 0.875rem;
    padding: 0.55rem 1.25rem;
    letter-spacing: 0.01em;
    transition: var(--transition);
    box-shadow: var(--shadow-sm);
    cursor: pointer;
}
.stButton > button:hover {
    background-color: var(--dark2);
    border-color: var(--dark2);
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
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
    transition: var(--transition);
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background-color: var(--tan);
    color: var(--dark) !important;
    transform: translateY(-2px);
}

/* ─── Text input ─────────────────────────────────────────────── */
.stTextInput > div > div > input {
    background-color: var(--white);
    border: 1.5px solid var(--border);
    border-radius: var(--radius-md);
    color: var(--ink);
    font-size: 1rem;
    padding: 0.8rem 1rem;
    transition: var(--transition);
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
    box-shadow: var(--shadow-sm);
}

/* ─── Spinner ────────────────────────────────────────────────── */
[data-testid="stSpinner"] > div {
    border-top-color: var(--brown) !important;
}

/* ═══════════════════════════════════════════════════════════════
   CUSTOM COMPONENT LAYOUTS & INTERACTION STYLES
═══════════════════════════════════════════════════════════════ */

/* ─── Section Card layout ────────────────────────────────────── */
.section-card {
    background: var(--white);
    border: 1.5px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.8rem 2rem;
    box-shadow: var(--shadow-md);
    margin-bottom: 2rem;
    transition: var(--transition);
    position: relative;
    overflow: hidden;
}
.section-card:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
}

/* ─── Custom Page Animations ─────────────────────────────────── */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(24px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
.fade-in-up {
    animation: fadeInUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) both;
}
.delay-1 { animation-delay: 0.1s; }
.delay-2 { animation-delay: 0.2s; }
.delay-3 { animation-delay: 0.3s; }
.delay-4 { animation-delay: 0.4s; }

/* ─── Hero / Landing Experience ──────────────────────────────── */
.hero-container {
    padding: 2.5rem 0 1.5rem;
    margin-bottom: 1.5rem;
    text-align: center;
    position: relative;
}
.hero-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--brown);
    background: rgba(171,136,109,0.1);
    border: 1px solid rgba(171,136,109,0.25);
    border-radius: 20px;
    padding: 0.25rem 0.8rem;
    display: inline-block;
    margin-bottom: 0.8rem;
}
.hero-title {
    font-family: 'Source Serif 4', Georgia, serif !important;
    font-weight: 700 !important;
    font-size: 3.2rem !important;
    color: var(--ink) !important;
    letter-spacing: -0.03em;
    line-height: 1.1;
    margin-bottom: 0.8rem !important;
}
.hero-subtitle {
    font-size: 1.05rem;
    color: var(--muted);
    max-width: 620px;
    margin: 0 auto 1.8rem;
    line-height: 1.6;
}
.hero-motifs {
    display: flex;
    justify-content: center;
    gap: 0.8rem;
    flex-wrap: wrap;
}
.motif-badge {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--dark);
    background: var(--cream2);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 0.3rem 0.65rem;
    transition: var(--transition);
}
.motif-badge:hover {
    background: var(--tan);
    transform: translateY(-1px);
}

/* ─── Document Workspace manager cards ───────────────────────── */
.doc-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
    margin-bottom: 1rem;
}
.doc-card {
    background: var(--cream2);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    transition: var(--transition);
    cursor: default;
    position: relative;
    overflow: hidden;
}
.doc-card:hover {
    background: var(--white);
    border-color: var(--brown);
    box-shadow: var(--shadow-sm);
    transform: translateY(-2px);
}
.doc-card-icon {
    font-size: 1.5rem;
    flex-shrink: 0;
}
.doc-card-info {
    flex: 1;
    min-width: 0;
}
.doc-card-title {
    font-weight: 600;
    font-size: 0.85rem;
    color: var(--dark);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.doc-card-meta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    color: var(--muted);
    margin-top: 0.15rem;
}

/* ─── Animated Dashed Border for Upload card ─────────────────── */
.main-upload-zone {
    text-align: center;
    padding: 2.2rem 1.5rem !important;
    border: 2px dashed var(--tan2) !important;
    border-radius: var(--radius-lg) !important;
    cursor: pointer;
    background: var(--cream2);
}
.main-upload-icon {
    font-size: 2.2rem;
    margin-bottom: 0.6rem;
    display: inline-block;
    transition: var(--transition);
}
.main-upload-zone:hover .main-upload-icon {
    transform: translateY(-4px) scale(1.1);
}

/* ─── Question command center ────────────────────────────────── */
.command-center {
    background: var(--white);
    border: 2px solid var(--brown);
    border-radius: var(--radius-lg);
    padding: 1.6rem;
    box-shadow: var(--shadow-lg);
    position: relative;
}
.command-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--brown);
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.command-header::after {
    content: "";
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ─── Style question input within command center ─────────────── */
.question-input-anchor + div div[data-testid="stTextInput"] input {
    background-color: var(--cream2) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    padding: 1rem 1.2rem !important;
    font-size: 1.05rem !important;
    color: var(--ink) !important;
    transition: var(--transition) !important;
}
.question-input-anchor + div div[data-testid="stTextInput"] input:focus {
    background-color: var(--white) !important;
    border-color: var(--dark) !important;
    box-shadow: 0 0 0 4px rgba(73,54,40,0.10) !important;
}

/* ─── Section divider label ──────────────────────────────────── */
.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--brown);
    margin-bottom: 1rem;
    margin-top: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.section-label::after {
    content: "";
    flex: 1;
    height: 1.5px;
    background: var(--border);
}

/* ─── Mode tabs (folder-tab visual) ──────────────────────────── */
.mode-tabs {
    display: flex;
    gap: 4px;
    margin-bottom: -1.5px;
    position: relative;
    z-index: 1;
}
.mode-tab {
    flex: 1;
    padding: 0.75rem 1rem;
    text-align: center;
    background-color: var(--cream2);
    border: 1.5px solid var(--border);
    border-bottom: none;
    border-radius: var(--radius-md) var(--radius-md) 0 0;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    font-weight: 600;
    cursor: default;
    transition: var(--transition);
}
.mode-tab.active {
    background-color: var(--white);
    color: var(--ink);
    font-weight: 700;
    border-color: var(--border);
    border-bottom: 2px solid var(--white);
    box-shadow: 0 -2px 8px rgba(73,54,40,0.05);
}

/* ─── Dynamic Mode Selection buttons styling via Sibling selectors ─── */
.mode-anchor + div[data-testid="stHorizontalBlock"] {
    background-color: var(--white);
    border: 1.5px solid var(--border);
    border-top: none;
    border-radius: 0 0 var(--radius-lg) var(--radius-lg);
    padding: 1.8rem 1.6rem 1.2rem !important;
    box-shadow: var(--shadow-md);
    margin-bottom: 1.5rem;
}

/* Custom styled st.button inside horizontal columns to look like large mode cards */
.mode-anchor + div[data-testid="stHorizontalBlock"] div[data-testid="column"] button {
    width: 100% !important;
    height: 130px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    border-radius: var(--radius-md) !important;
    background-color: var(--cream2) !important;
    border: 1.5px solid var(--border) !important;
    color: var(--dark) !important;
    padding: 1.2rem !important;
    box-shadow: var(--shadow-sm) !important;
    transition: var(--transition) !important;
    position: relative;
    overflow: hidden;
}
.mode-anchor + div[data-testid="stHorizontalBlock"] div[data-testid="column"] button::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: var(--tan);
    transition: var(--transition);
}

/* Hover effects for mode buttons */
.mode-anchor + div[data-testid="stHorizontalBlock"] div[data-testid="column"] button:hover {
    transform: translateY(-5px) !important;
    background-color: var(--white) !important;
    border-color: var(--brown) !important;
    box-shadow: var(--shadow-lg) !important;
}
.mode-anchor + div[data-testid="stHorizontalBlock"] div[data-testid="column"] button:hover::before {
    background: var(--brown);
}

/* Selected states triggered by state classes on the anchor */
.mode-anchor.selected-fast + div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(1) button,
.mode-anchor.selected-deep + div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(2) button,
.mode-anchor.selected-auto + div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(3) button {
    background-color: var(--white) !important;
    border-color: var(--brown) !important;
    border-width: 2px !important;
    box-shadow: var(--shadow-lg) !important;
}
.mode-anchor.selected-fast + div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(1) button::before,
.mode-anchor.selected-deep + div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(2) button::before,
.mode-anchor.selected-auto + div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(3) button::before {
    background: var(--brown);
    height: 5px;
}

/* Move the st.caption description inside the cards using layout tweaks or keep standard caption styles */
.mode-anchor + div[data-testid="stHorizontalBlock"] div[data-testid="column"] small {
    display: block;
    text-align: center;
    margin-top: 0.6rem;
    font-size: 0.72rem !important;
    color: var(--muted) !important;
    line-height: 1.4;
}

/* ─── Citation stamps ────────────────────────────────────────── */
.citations-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin: 0.8rem 0 0.25rem;
}
.citation-stamp {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--dark);
    background-color: var(--cream2);
    border: 1.5px solid var(--dark);
    outline: 1.5px solid var(--brown);
    outline-offset: 2px;
    border-radius: 4px;
    padding: 0.25rem 0.55rem;
    white-space: nowrap;
    transition: var(--transition);
}
.citation-stamp:hover {
    background-color: var(--tan);
    transform: translateY(-2px);
    box-shadow: var(--shadow-sm);
}
.citation-stamp::before {
    content: "\\00a7";
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
    margin: 1.5rem 0;
    padding: 1.2rem 1.5rem;
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
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--tan2);
    text-align: center;
    position: relative;
}
.progress-step .dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--tan);
    border: 2.5px solid var(--tan2);
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
.progress-step.done { color: var(--dark); font-weight: 700; }
.progress-step.active { color: var(--brown); font-weight: 700; }

.progress-line {
    flex: 1 0 20px;
    height: 2.5px;
    background: linear-gradient(to right, var(--tan2), var(--tan));
    margin: 0;
    position: relative;
    top: -9px;
}
.progress-line.done {
    background: var(--dark);
}

/* ─── Answer card ────────────────────────────────────────────── */
.answer-card {
    background: var(--white);
    border: 1.5px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.8rem 2rem;
    margin-top: 1.5rem;
    box-shadow: var(--shadow-lg);
    position: relative;
}
.answer-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 5px;
    background: linear-gradient(to right, var(--brown), var(--tan));
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}
.answer-card-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--brown);
    margin-bottom: 0.85rem;
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
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 700;
    padding: 0.25rem 0.6rem;
    border-radius: 4px;
    background: rgba(73,54,40,0.08);
    border: 1px solid rgba(73,54,40,0.18);
    color: var(--dark);
}
.answer-text {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.05rem;
    color: var(--ink);
    line-height: 1.8;
    margin: 0;
}
.answer-footer {
    margin-top: 1.2rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    flex-wrap: wrap;
}
.confidence-line {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: var(--muted);
    letter-spacing: 0.03em;
}

/* ─── How It Works Visual Steps ──────────────────────────────── */
.works-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.2rem;
    margin-top: 1rem;
}
.works-step-card {
    background: var(--cream2);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1.25rem;
    transition: var(--transition);
    position: relative;
}
.works-step-card:hover {
    background: var(--white);
    border-color: var(--brown);
    box-shadow: var(--shadow-md);
    transform: translateY(-3px);
}
.works-step-num {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    color: rgba(171,136,109,0.35);
    position: absolute;
    top: 0.8rem;
    right: 1rem;
}
.works-step-icon {
    font-size: 1.6rem;
    margin-bottom: 0.6rem;
    display: block;
}
.works-step-title {
    font-family: 'Source Serif 4', Georgia, serif;
    font-weight: 700;
    font-size: 0.95rem;
    color: var(--ink);
    margin-bottom: 0.35rem;
}
.works-step-desc {
    font-size: 0.8rem;
    color: var(--muted);
    line-height: 1.5;
}

/* ─── System / Footer Status ─────────────────────────────────── */
.footer-status {
    border-top: 1.5px solid var(--border);
    padding-top: 1.5rem;
    margin-top: 3.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
}
.status-pill-indicator {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    font-weight: 700;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.pulse-dot {
    width: 7px;
    height: 7px;
    background-color: #4A7559;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 0 0 rgba(74, 117, 89, 0.4);
    animation: pulseGreen 2s infinite;
}
@keyframes pulseGreen {
    0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(74, 117, 89, 0.4); }
    50% { transform: scale(1.25); box-shadow: 0 0 0 5px rgba(74, 117, 89, 0); }
}
.footer-text {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    color: var(--muted);
}

/* Responsive layout adjustments */
@media (max-width: 768px) {
    .hero-title {
        font-size: 2.4rem !important;
    }
    .works-grid {
        grid-template-columns: 1fr;
    }
    .mode-anchor + div[data-testid="stHorizontalBlock"] {
        padding: 1rem !important;
    }
    .mode-anchor + div[data-testid="stHorizontalBlock"] div[data-testid="column"] button {
        height: 100px !important;
        margin-bottom: 0.5rem;
    }
}
</style>
"""


# ─── Inject ──────────────────────────────────────────────────────────────────

def inject_theme():
    """Call once near the very top of app.py, before any other st. calls."""
    st.markdown(CSS, unsafe_allow_html=True)


def inject_query_interaction_theme():
    """Small query-screen additions for native button tooltips and mode controls."""
    st.markdown(
        """
        <style>
        /* Streamlit renders a button's `help` text as an accessible hover tooltip. */
        [data-testid="stTooltipHoverTarget"] { cursor: help; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ─── Render helpers ──────────────────────────────────────────────────────────

def render_hero_section():
    """Renders a beautiful hero landing experience at the top of the main area."""
    st.markdown(
        """
        <div class="hero-container fade-in-up">
            <div class="hero-eyebrow">CLERK LEGAL AI</div>
            <h1 class="hero-title">Legal RAG Workspace</h1>
            <p class="hero-subtitle">
                Interactive document intelligence platform. Analyze, verify, and cross-reference multiple legal briefs and rulings with precision.
            </p>
            <div class="hero-motifs">
                <span class="motif-badge">⚡ grounded answers</span>
                <span class="motif-badge">🔎 verified citations</span>
                <span class="motif-badge">🤖 adaptive reasoning</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_app_header():
    """Fallback header."""
    pass


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


def render_document_workspace(case_filenames):
    """Renders a modern document manager panel in the main area."""
    if not case_filenames:
        st.markdown(
            """
            <div class="doc-grid">
                <div class="doc-card" style="justify-content: center; opacity: 0.65;">
                    <div class="empty-state">No cases uploaded in workspace database.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    html = '<div class="doc-grid">'
    for filename in case_filenames:
        # Mock file info metadata for premium aesthetic
        meta = "PDF Case Document"
        html += f"""
        <div class="doc-card">
            <span class="doc-card-icon">📄</span>
            <div class="doc-card-info">
                <div class="doc-card-title">{filename}</div>
                <div class="doc-card-meta">{meta}</div>
            </div>
        </div>
        """
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


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
    tabs_html += '</div>'
    # Renders the hidden mode anchor with class to trigger active button selection in CSS
    st.markdown(f'<div class="mode-anchor selected-{selected_mode}"></div>', unsafe_allow_html=True)
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


def render_how_it_works():
    """Renders Section 5 - How it works panel."""
    st.markdown(
        """
        <div class="works-grid">
            <div class="works-step-card">
                <span class="works-step-num">01</span>
                <span class="works-step-icon">📤</span>
                <div class="works-step-title">Upload Case PDFs</div>
                <div class="works-step-desc">Securely load legal briefs, transcripts, and rulings into Clerk's workspace databases.</div>
            </div>
            <div class="works-step-card">
                <span class="works-step-num">02</span>
                <span class="works-step-icon">🔎</span>
                <div class="works-step-title">Retrieve Context</div>
                <div class="works-step-desc">Cross-reference and extract semantically relevant matches across all indexed cases.</div>
            </div>
            <div class="works-step-card">
                <span class="works-step-num">03</span>
                <span class="works-step-icon">🖋</span>
                <div class="works-step-title">Grounded Answer</div>
                <div class="works-step-desc">Draft accurate responses complete with local citations and fact-verification tags.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer_status(count: int):
    """Renders Section 7 - Footer / System status bar."""
    st.markdown(
        f"""
        <div class="footer-status">
            <div class="status-pill-indicator">
                <span class="pulse-dot"></span> All Systems Operational
            </div>
            <div class="footer-text">
                ChromaDB Vector Store • {count} cases loaded • Legal RAG CLI v1.2
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
