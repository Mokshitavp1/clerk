"""Legal Retrieval Assistant query screen."""

import html
import os
import sys

import streamlit as st
from theme import inject_query_interaction_theme


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
for _folder in ("retrieval", "generation", "routing", "ingestion"):
    _path = os.path.join(PROJECT_ROOT, _folder)
    if _path not in sys.path:
        sys.path.insert(0, _path)


st.set_page_config(page_title="Legal Retrieval Assistant", layout="wide")
inject_query_interaction_theme()

if "selected_mode" not in st.session_state:
    st.session_state.selected_mode = "Fast"
if "query_draft" not in st.session_state:
    st.session_state.query_draft = ""
if "pending_warning" not in st.session_state:
    st.session_state.pending_warning = None


def _choose_mode(mode):
    """Persist the native mode control and clear irrelevant Fast warnings."""
    st.session_state.selected_mode = mode
    if mode != "Fast":
        st.session_state.pending_warning = None


def _switch_to_deep_thinking():
    st.session_state.selected_mode = "Deep Thinking"
    st.session_state.pending_warning = None


def _continue_with_fast():
    warning = st.session_state.pending_warning
    if warning:
        st.session_state.run_after_warning = {
            "query": warning["query"],
            "cases": warning["cases"],
        }
    st.session_state.pending_warning = None


def _indexed_case_names():
    """Return the case names currently represented by the persisted index."""
    try:
        import chromadb
        from ingest import CASES_COLLECTION, CHROMA_PATH

        collection = chromadb.PersistentClient(path=CHROMA_PATH).get_collection(CASES_COLLECTION)
        return {metadata["case_name"] for metadata in collection.get().get("metadatas", [])}
    except Exception:
        return set()


def _build_uploaded_cases(uploaded_files):
    """Persist and index the selected PDFs only when the user requests it."""
    from ingest import replace_case

    os.makedirs(os.path.join(PROJECT_ROOT, "cases"), exist_ok=True)
    for uploaded_file in uploaded_files:
        filename = os.path.basename(uploaded_file.name)
        destination = os.path.join(PROJECT_ROOT, "cases", filename)
        with open(destination, "wb") as case_file:
            case_file.write(uploaded_file.getvalue())
        replace_case(destination)


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
        color: #4A6741; background: #EBF0E8; border: 1px solid #B8CCAF; border-radius: 999px;
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
    .knowledge-steps { margin: -17px 0 20px; color: rgba(228,224,225,.88); font: 500 11px/1.45 Inter, sans-serif; }
    .sidebar-label { color: var(--tan); font: 600 10px/1 'IBM Plex Mono', monospace; letter-spacing: .13em; }
    .dropzone { margin-top: 10px; min-height: 126px; display: grid; place-items: center; border: 1px dashed rgba(214,192,179,.64); border-radius: 8px; background: rgba(228,224,225,.07); }
    .upload-pill { display: inline-block; padding: 10px 22px; border-radius: 999px; background: var(--tan); color: var(--brown); font: 700 13px/1 Inter, sans-serif; }

    /* ── Sidebar file-uploader: restyle as dashed dropzone ───────────── */
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
        padding: 0 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
        border: 1.5px dashed rgba(214,192,179,.60) !important;
        border-radius: 8px !important;
        background: rgba(228,224,225,.06) !important;
        padding: 22px 14px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        gap: 10px !important;
        transition: border-color .18s, background .18s;
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"]:hover,
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"]:focus-within {
        border-color: rgba(171,136,109,.85) !important;
        background: rgba(228,224,225,.11) !important;
    }
    /* drag-over glow */
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"][aria-dropeffect] {
        border-color: var(--tan) !important;
        background: rgba(171,136,109,.12) !important;
    }
    /* hide the default "Drag and drop" text + limit line */
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] > div > span,
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] > div > small {
        display: none !important;
    }
    /* custom icon + label above the button */
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"]::before {
        content: '↑';
        display: block;
        font-size: 22px;
        line-height: 1;
        color: rgba(214,192,179,.70);
        text-align: center;
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"]::after {
        content: 'Drag & drop PDFs here';
        display: block;
        font: 500 11px/1.4 Inter, sans-serif;
        color: rgba(228,224,225,.52);
        text-align: center;
        margin-top: 4px;
    }
    /* style the Browse button to match the sidebar palette */
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
        background: var(--tan) !important;
        color: var(--brown) !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 8px 18px !important;
        font: 700 11px/1 Inter, sans-serif !important;
        letter-spacing: .04em !important;
        cursor: pointer !important;
        transition: opacity .15s;
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button:hover {
        opacity: .85 !important;
    }
    /* upload-dropzone file pills */
    section[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] {
        background: rgba(228,224,225,.08) !important;
        border: 1px solid rgba(214,192,179,.22) !important;
        border-radius: 5px !important;
        color: rgba(228,224,225,.88) !important;
        font-size: 11px !important;
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDeleteBtn"] button {
        color: rgba(214,192,179,.65) !important;
    }
    /* BUILD button — dimmed when nothing is uploaded */
    section[data-testid="stSidebar"] .stButton button:disabled {
        opacity: 0.38 !important;
        cursor: not-allowed !important;
        pointer-events: auto !important;  /* keep cursor visible even though click is blocked */
        filter: grayscale(18%);
    }
    .sidebar-rule { border: 0; height: 1px; background: rgba(214,192,179,.28); margin: 24px 0; }
    .document-list { max-height: 112px; overflow-y: auto; margin-top: 12px; padding-right: 5px; }
    .empty-docs { margin: 22px 14px; text-align: center; color: rgba(228,224,225,.90); font: italic 14px/1.5 'Source Serif 4', Georgia, serif; }
    .document-name { padding: 8px 0; border-bottom: 1px solid rgba(214,192,179,.18); color: rgba(228,224,225,.9); font-size: 12px; overflow-wrap: anywhere; }
    .sync-status { display: inline-block; margin: 12px 0 16px; padding: 5px 7px; border: 1px solid rgba(214,192,179,.38); border-radius: 4px; color: var(--sand); font: 600 9px/1 'IBM Plex Mono', monospace; letter-spacing: .04em; }
    .build-button { display: block; width: 100%; margin-top: auto; padding: 13px 14px; background: var(--tan); border-radius: 7px; color: var(--brown); text-align: center; font: 700 11px/1.38 Inter, sans-serif; letter-spacing: .025em; }
    .history-heading { margin: 0 0 17px; color: #F5F0E9; font: 700 22px/1.1 'Source Serif 4', Georgia, serif; }
    .history-list { max-height: 220px; overflow-y: auto; margin-top: 12px; padding-right: 5px; }
    .history-item { padding: 0 0 13px; margin-bottom: 13px; border-bottom: 1px solid rgba(214,192,179,.18); }
    .history-item:last-child { margin-bottom: 0; }
    .history-query { margin-bottom: 8px; color: rgba(228,224,225,.9); font: 500 12px/1.46 Inter, sans-serif; }
    .trust-tag { display: inline-flex; align-items: center; border: 1px solid rgba(214,192,179,.48); border-radius: 4px; padding: 4px 6px; color: var(--sand); font: 600 9px/1 'IBM Plex Mono', monospace; letter-spacing: .04em; }
    .trust-tag.unverified { color: var(--tan); border-color: rgba(171,136,109,.6); }
    .trust-tag.insufficient { color: rgba(228,224,225,.6); border-color: rgba(228,224,225,.25); }
    .trust-tag::before { content: ''; display: inline-block; width: 7px; height: 7px; border-radius: 50%; margin-right: 6px; background-color: #82b97c; }
    .trust-tag.unverified::before { background-color: #dfad56; }
    .trust-tag.insufficient::before { background-color: #9c9995; }

    .main-shell { padding: 68px 28px 0; }
    .query-page { max-width: 890px; margin: 0 auto; padding-top: 44px; }
    .eyebrow { text-align: center; color: var(--tan); font: 600 11px/1 'IBM Plex Mono', monospace; letter-spacing: .13em; }
    .query-page h1 { margin: 13px 0 13px; color: var(--brown); text-align: center; font: 700 45px/1.08 'Source Serif 4', Georgia, serif; letter-spacing: -.035em; }
    .intro { max-width: 635px; margin: 0 auto 24px; text-align: center; color: var(--muted); font-size: 15px; line-height: 1.65; }
    .query-card { background: var(--paper); border: 1px solid var(--line); border-radius: 11px; overflow: hidden; box-shadow: 0 2px 8px rgba(73,54,40,.035); }
    .card-top, .card-bottom { display: flex; align-items: center; justify-content: space-between; gap: 18px; padding: 16px 18px; }
    .card-top { border-bottom: 1px solid var(--line); }
    .mode-control { display: flex; align-items: center; gap: 5px; }
    .mode { padding: 8px 11px; border: 1px solid rgba(73,54,40,.25); border-radius: 5px; color: var(--muted); background: transparent; font: 600 10px/1 'IBM Plex Mono', monospace; letter-spacing: .07em; }
    .mode.active { color: var(--paper); background: var(--brown); border-color: var(--brown); }
    .btn-caption { margin-top: 5px; color: var(--muted); font: 500 10px/1.3 'IBM Plex Mono', monospace; letter-spacing: .04em; text-align: center; }
    .mode-caption { color: var(--muted); font: 500 10px/1.3 'IBM Plex Mono', monospace; letter-spacing: .04em; }
    .options, .nlp { color: var(--muted); font: 600 10px/1 'IBM Plex Mono', monospace; letter-spacing: .07em; white-space: nowrap; }
    .question-space { min-height: 166px; padding: 25px 20px; color: #9C938C; font: italic 16px/1.55 'Source Serif 4', Georgia, serif; }
    .card-bottom { border-top: 1px solid var(--line); }
    .actions { display: flex; align-items: center; gap: 17px; }
    .ambiguity { color: var(--brown); font: 600 10px/1 'IBM Plex Mono', monospace; text-decoration: underline; text-underline-offset: 3px; letter-spacing: .05em; white-space: nowrap; }
    .retrieve { display: inline-block; border-radius: 5px; padding: 11px 15px; color: var(--paper); background: var(--brown); font: 700 11px/1 Inter, sans-serif; letter-spacing: .055em; white-space: nowrap; }
    .mode-warning { max-width: 890px; margin: 0 auto 10px; padding: 15px 17px; border: 1px solid rgba(171,136,109,.55); border-left: 4px solid var(--tan); border-radius: 8px; background: #F7F1EB; color: var(--brown); }
    .warning-message { font: 600 14px/1.45 Inter, sans-serif; }
    .warning-explanation { margin-top: 10px; color: var(--muted); font-size: 13px; line-height: 1.5; }
    .warning-actions { max-width: 890px; margin: -2px auto 13px; }
    .warning-actions button { width: 100%; min-height: 38px; border-radius: 5px; font: 600 11px/1.2 Inter, sans-serif; }
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
    /* hide Streamlit's "Press Enter to submit" hint — query form only */
    .st-key-query-section [data-testid="InputInstructions"] { display: none !important; }
    @media (max-width: 800px) {
        section[data-testid="stSidebar"] { width: 250px !important; min-width: 250px !important; }
        .query-page h1 { font-size: 38px; }
    }
    </style>
    <div class="topbar">
      <div class="brand"><span class="brand-mark">⚖</span><span class="brand-name">Legal Retrieval Assistant</span></div>
      <div class="topbar-right"><span class="system-status">● LOCAL / PRIVATE</span><span class="avatar">♙</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    # ── Knowledge Base header ──────────────────────────────────────────
    st.markdown(
        """
        <div class="sidebar-title" style="padding: 30px 22px 0; margin-bottom: 6px;">Knowledge Base</div>
        <p class="knowledge-steps" style="padding: 0 22px; margin-bottom: 14px;">1. Upload PDFs &rarr; 2. Build/Update &rarr; 3. Ask questions</p>
        <div class="sidebar-label" style="padding: 0 22px;">UPLOAD CASES</div>
        """,
        unsafe_allow_html=True,
    )

    # ── Actual file uploader (right under the heading) ─────────────────
    uploaded_cases = st.file_uploader(
        "Upload case PDFs",
        type="pdf",
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="case-pdf-upload",
    )
    uploaded_names = {os.path.splitext(os.path.basename(case.name))[0] for case in uploaded_cases}
    indexed_names = _indexed_case_names()
    pending_names = uploaded_names - indexed_names

    # ── Documents list ─────────────────────────────────────────────────
    st.markdown('<div class="sidebar-label" style="padding: 0 22px; margin-top: 4px;">DOCUMENTS</div>', unsafe_allow_html=True)
    if uploaded_cases:
        st.markdown(
            '<div class="document-list" style="padding: 0 22px;">' + "".join(
                f'<div class="document-name">{html.escape(case.name)}</div>' for case in uploaded_cases
            ) + '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div class="empty-docs">No case PDFs uploaded yet.</div>', unsafe_allow_html=True)
    if pending_names:
        count = len(pending_names)
        noun = "document" if count == 1 else "documents"
        st.markdown(f'<div class="sync-status" style="margin: 8px 22px 0;">&#x25CF;&nbsp;{count} new {noun} not yet indexed</div>', unsafe_allow_html=True)

    # ── Build button ───────────────────────────────────────────────────
    if st.button(
        "BUILD / UPDATE KNOWLEDGE BASE",
        key="build-knowledge-base",
        use_container_width=True,
        disabled=not uploaded_cases,
    ):
        if not uploaded_cases:
            st.info("Upload one or more PDFs before rebuilding the knowledge base.")
        else:
            with st.spinner("Building knowledge base…"):
                _build_uploaded_cases(uploaded_cases)
            st.success("Knowledge base updated.")
            st.rerun()

    # ── Divider + History ──────────────────────────────────────────────
    st.markdown(
        """
        <div class="sidebar-divider" style="margin: 18px 0;"></div>
        <div style="padding: 0 22px 30px;">
          <div class="history-heading">History</div>
          <div class="sidebar-label">PAST QUERIES</div>
          <div class="history-list">
            <article class="history-item"><div class="history-query">Statute of limitations for medical malpractice in New York</div><span class="trust-tag">&sect; VERIFIED</span></article>
            <article class="history-item"><div class="history-query">Exceptions to the hearsay rule for business records</div><span class="trust-tag">&sect; VERIFIED</span></article>
            <article class="history-item"><div class="history-query">Recent Supreme Court rulings on Chevron deference</div><span class="trust-tag unverified">&sect; UNVERIFIED</span></article>
            <article class="history-item"><div class="history-query">Delaware veil-piercing standard and undercapitalization</div><span class="trust-tag insufficient">&sect; INSUFFICIENT</span></article>
            <article class="history-item"><div class="history-query">Elements required to establish promissory estoppel</div><span class="trust-tag">&sect; VERIFIED</span></article>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def _render_progress(slot, active_step, status):
    """Render the transient pipeline indicator with one current status line."""
    steps = ("RETRIEVE", "GRADE", "VERIFY")
    parts = []
    for index, label in enumerate(steps):
        state = "complete" if index < active_step else "active" if index == active_step else ""
        marker = "&#10003;" if index < active_step else str(index + 1)
        parts.append(f'<div class="step {state}"><span class="step-dot">{marker}</span>{label}</div>')
    slot.markdown(
        f'<section class="progress-stepper"><div class="progress-track">{"".join(parts)}</div><div class="step-status">{status}</div></section>',
        unsafe_allow_html=True,
    )


def _run_query(question, progress_slot, mode, shortlisted_cases=None):
    """Run the Retrieve → Grade → Verify contract and update its live status."""
    from stage1_case_retrieval import get_relevant_cases
    from stage2_chunk_retrieval import get_relevant_chunks
    from self_rag import get_graded_cases
    from verifier import generate_verified_answer
    from router import decide_mode

    _render_progress(progress_slot, 0, "Searching the knowledge base for relevant cases…")
    shortlisted_cases = shortlisted_cases if shortlisted_cases is not None else get_relevant_cases(question)
    resolved_mode = decide_mode(shortlisted_cases) if mode == "Auto" else mode.lower()
    case_names = (
        [shortlisted_cases[0]["case_name"]]
        if resolved_mode == "fast" and shortlisted_cases
        else [case["case_name"] for case in shortlisted_cases]
    )
    retrieved_chunks = get_relevant_chunks(question, case_names)

    _render_progress(
        progress_slot,
        1,
        f"Shortlisted {len(shortlisted_cases)} case{'s' if len(shortlisted_cases) != 1 else ''}; retrieved {len(retrieved_chunks)} relevant passages.",
    )

    def grade_status(signal):
        if signal["retrying"]:
            message = (
                f"{signal['dropped_chunks']} passages fell below the relevance floor; "
                "retrying with a wider shortlist."
            )
        else:
            message = (
                f"{signal['surviving']} of {signal['shortlisted']} cases cleared the relevance floor."
            )
        _render_progress(progress_slot, 1, message)

    if resolved_mode == "fast":
        _render_progress(progress_slot, 1, "Fast mode will use the highest-ranked case only.")
        chunks = retrieved_chunks
    else:
        graded = get_graded_cases(question, progress_callback=grade_status)
        if graded["insufficient_cases"]:
            progress_slot.empty()
            return {"answer": "No sufficient, relevant cases were found in the uploaded documents.", "verified": False}
        chunks = [chunk for case in graded["cases"] for chunk in case["chunks"]]
    _render_progress(progress_slot, 2, "Generating a grounded response and checking its citations…")

    def verify_status(signal):
        if signal["retrying"]:
            _render_progress(progress_slot, 2, "Verification flagged an issue; retrying once with the verifier feedback.")
        elif signal["verified"]:
            _render_progress(progress_slot, 2, "Verification passed cleanly.")
        else:
            _render_progress(progress_slot, 2, "Verification could not produce a fully grounded answer.")

    result = generate_verified_answer(question, chunks, progress_callback=verify_status)
    progress_slot.empty()
    return result


st.markdown(
    """
    <main class="main-shell"><section class="query-page">
      <div class="eyebrow">§ QUERY ENGINE V.4</div>
      <h1>Ask a Legal Question</h1>
      <p class="intro">Enter your query, cite specific statutes, or describe a fact pattern. The system will retrieve relevant case law and synthesize a memorandum.</p>
    </section></main>
    """,
    unsafe_allow_html=True,
)

mode_picker = st.container(key="query-section-mode-picker")
fast_col, deep_col, auto_col, _ = mode_picker.columns((1, 1.55, 1, 4.45))
with fast_col:
    st.button(
        "FAST",
        key="mode-fast",
        type="primary" if st.session_state.selected_mode == "Fast" else "secondary",
        help="Uses the single top-matched case for a quick answer.",
        on_click=_choose_mode,
        args=("Fast",),
    )
    st.markdown('<div class="btn-caption">Single top match</div>', unsafe_allow_html=True)
with deep_col:
    st.button(
        "DEEP THINKING",
        key="mode-deep",
        type="primary" if st.session_state.selected_mode == "Deep Thinking" else "secondary",
        help="Searches and compares multiple cases instead of relying on one match.",
        on_click=_choose_mode,
        args=("Deep Thinking",),
    )
    st.markdown('<div class="btn-caption">Compares multiple cases</div>', unsafe_allow_html=True)
with auto_col:
    st.button(
        "AUTO",
        key="mode-auto",
        type="primary" if st.session_state.selected_mode == "Auto" else "secondary",
        help="Chooses Fast when one case clearly dominates, or Deep Thinking when top matches are close.",
        on_click=_choose_mode,
        args=("Auto",),
    )
    st.markdown('<div class="btn-caption">Picks for you</div>', unsafe_allow_html=True)
mode_picker.markdown('<div class="mode-caption">Not sure? Auto picks for you.</div>', unsafe_allow_html=True)
selected_mode = st.session_state.selected_mode

pending_warning = st.session_state.pending_warning
if pending_warning:
    st.markdown(
        f'<section class="mode-warning"><div class="warning-message">{html.escape(pending_warning["message"])}</div>'
        f'<details><summary>Explain why</summary><div class="warning-explanation">{html.escape(pending_warning["explain_why"])}</div></details></section>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="warning-actions">', unsafe_allow_html=True)
    switch_col, continue_col = st.columns(2)
    with switch_col:
        st.button(
            "Switch to Deep Thinking",
            use_container_width=True,
            key="switch-mode",
            on_click=_switch_to_deep_thinking,
        )
    with continue_col:
        st.button(
            "Continue with Fast anyway",
            use_container_width=True,
            key="continue-mode",
            on_click=_continue_with_fast,
        )
    st.markdown('</div>', unsafe_allow_html=True)

query_section = st.container(key="query-section")
with query_section.form("legal-query", clear_on_submit=False):
    st.markdown(
        '<div class="form-top"><span class="options">&#9881; OPTIONS</span></div>',
        unsafe_allow_html=True,
    )
    question = st.text_area(
        "Legal question",
        key="query_draft",
        label_visibility="collapsed",
        placeholder="E.g., What is the standard for piercing the corporate veil in Delaware regarding undercapitalization?",
    )
    submitted = st.form_submit_button("RETRIEVE →", use_container_width=True)

progress_slot = st.empty()
run_request = st.session_state.pop("run_after_warning", None)
if submitted and question.strip():
    from router import build_warning
    from stage1_case_retrieval import get_relevant_cases

    shortlist = get_relevant_cases(question.strip())
    warning = build_warning(shortlist)
    # The warning contract describes a Fast-mode limitation. Auto already
    # resolves that choice itself, while Deep Thinking addresses it directly.
    if selected_mode == "Fast" and warning:
        st.session_state.pending_warning = {
            **warning,
            "query": question.strip(),
            "cases": shortlist,
        }
        st.rerun()
    run_request = {"query": question.strip(), "cases": shortlist}

if run_request:
    with st.spinner(""):
        st.session_state.last_query_result = _run_query(
            run_request["query"], progress_slot, selected_mode, run_request["cases"]
        )

if submitted and not question.strip():
    st.warning("Enter a legal question before retrieving cases.")

if "last_query_result" in st.session_state:
    result = st.session_state.last_query_result
    st.markdown(
        f'<div class="result-card">{html.escape(result["answer"])}</div>',
        unsafe_allow_html=True,
    )
