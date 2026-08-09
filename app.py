"""
Legal RAG — Streamlit UI.

Ties together Person A's ingestion/retrieval pipeline and Person B's
generation/verification/routing pipeline.

No fixtures — every call below hits the real functions from the other
modules. The knowledge base is built entirely from whatever the user
uploads through the sidebar; nothing is pre-populated.
"""

import os
import sys

import streamlit as st

# --- Make each module folder importable as flat modules. -------------------
# Person A's files use flat sibling imports internally (e.g. ingest.py does
# `from parser import chunk_pdf`, self_rag.py does
# `from stage1_case_retrieval import get_relevant_cases`), which only
# resolve if each folder is directly on sys.path — not if imported as
# "ingestion.ingest" from the project root. Adding each folder here lets
# every file's existing imports work exactly as written, no internal edits
# needed in Person A's files.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
for _folder in ("ingestion", "retrieval", "generation", "routing"):
    _folder_path = os.path.join(PROJECT_ROOT, _folder)
    if _folder_path not in sys.path:
        sys.path.insert(0, _folder_path)
# -----------------------------------------------------------------------------

from ingest import check_if_exists, ingest_new_case, replace_case
from stage1_case_retrieval import get_relevant_cases
from stage2_chunk_retrieval import get_relevant_chunks
from self_rag import get_graded_cases
from verifier import generate_verified_answer
from hyde import rewrite_query
from router import decide_mode, build_confidence_line, build_warning

CASES_FOLDER = "cases"

st.set_page_config(page_title="Legal RAG", layout="wide")

os.makedirs(CASES_FOLDER, exist_ok=True)

# --- session_state defaults ------------------------------------------------
if "pending_replace_filename" not in st.session_state:
    st.session_state.pending_replace_filename = None
if "selected_mode" not in st.session_state:
    st.session_state.selected_mode = None
if "stage1_results" not in st.session_state:
    st.session_state.stage1_results = None
if "warning_acknowledged" not in st.session_state:
    st.session_state.warning_acknowledged = False
if "pipeline_result" not in st.session_state:
    st.session_state.pipeline_result = None
if "result_mode" not in st.session_state:
    st.session_state.result_mode = None
if "result_question" not in st.session_state:
    st.session_state.result_question = None


def _list_uploaded_case_filenames():
    """Return sorted filenames currently sitting in the cases folder."""
    if not os.path.isdir(CASES_FOLDER):
        return []
    return sorted(
        f for f in os.listdir(CASES_FOLDER)
        if f.lower().endswith(".pdf")
    )


# ============================================================================
# Sidebar: upload + knowledge base (B5.1)
# ============================================================================

with st.sidebar:
    st.header("Knowledge Base")

    uploaded_files = st.file_uploader(
        "Upload case PDFs",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            save_path = os.path.join(CASES_FOLDER, uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.success(f"Saved {len(uploaded_files)} file(s) to '{CASES_FOLDER}/'.")

    st.subheader("Currently uploaded cases")
    case_filenames = _list_uploaded_case_filenames()
    if case_filenames:
        for filename in case_filenames:
            st.write(f"📄 {filename}")
    else:
        st.caption("No case PDFs uploaded yet.")

    st.divider()

    if st.button("Build/Update Knowledge Base", use_container_width=True):
        with st.spinner("Ingesting uploaded cases..."):
            for filename in case_filenames:
                filepath = os.path.join(CASES_FOLDER, filename)
                case_name = os.path.splitext(filename)[0]

                if check_if_exists(case_name):
                    # Don't replace silently — flag it and let the confirm
                    # dialog below (rendered outside this loop) handle it.
                    st.session_state.pending_replace_filename = filepath
                else:
                    ingest_new_case(filepath)
                    st.success(f"Ingested new case: {case_name}")

    # "This case already exists — replace it?" confirm dialog. Rendered
    # here (outside the button's if-block) so it persists across the
    # rerun that clicking a button inside Streamlit triggers, instead of
    # vanishing the instant the user clicks anything.
    if st.session_state.pending_replace_filename:
        pending_filepath = st.session_state.pending_replace_filename
        pending_case_name = os.path.splitext(os.path.basename(pending_filepath))[0]

        st.warning(f"'{pending_case_name}' already exists in the knowledge base.")
        confirm_col, cancel_col = st.columns(2)

        with confirm_col:
            if st.button("Replace it", use_container_width=True):
                with st.spinner(f"Replacing {pending_case_name}..."):
                    replace_case(pending_filepath)
                st.session_state.pending_replace_filename = None
                st.success(f"Replaced case: {pending_case_name}")
                st.rerun()

        with cancel_col:
            if st.button("Cancel", use_container_width=True):
                st.session_state.pending_replace_filename = None
                st.rerun()


# ============================================================================
# Step-based progress indicator (B5.3)
# ============================================================================

PROGRESS_STEPS = [
    "Searching for relevant cases...",
    "Reading through matched cases...",
    "Drafting answer...",
    "Verifying citations...",
]


def update_progress(step_index, steps):
    """
    Update a single, in-place progress bar + status line to reflect the
    given step, instead of a plain spinner that gives no sense of which
    stage the pipeline is actually in.
    """
    if step_index == 0 or "progress_placeholder" not in st.session_state:
        st.session_state.progress_placeholder = st.empty()

    placeholder = st.session_state.progress_placeholder
    fraction_complete = (step_index + 1) / len(steps)

    with placeholder.container():
        st.progress(fraction_complete)
        st.write(steps[step_index])


def clear_progress():
    """Clear the progress indicator once the pipeline finishes."""
    if "progress_placeholder" in st.session_state:
        st.session_state.progress_placeholder.empty()


# ============================================================================
# Pipeline orchestration — retrieval -> generation -> verification
# ============================================================================

def _set_result(answer, verified, mode, question):
    """Small helper so every exit path out of run_pipeline stores state
    the same way, instead of repeating the same four assignments."""
    st.session_state.pipeline_result = {"answer": answer, "verified": verified}
    st.session_state.result_mode = mode
    st.session_state.result_question = question


def run_pipeline(question, mode):
    """
    Run one end-to-end pass of the pipeline for a question and mode, and
    store the result in session_state for display further down the page.

    Args:
        question: the user's natural-language question.
        mode: "fast", "deep", or "auto". If "auto", the actual mode used
            is resolved via router.decide_mode based on Stage 1 results.
    """
    # A fresh run means any warning shown for a *previous* question no
    # longer applies — reset so a new ambiguous question is re-flagged
    # instead of staying silently acknowledged from an earlier question.
    st.session_state.warning_acknowledged = False

    update_progress(0, PROGRESS_STEPS)
    stage1_results = get_relevant_cases(question)
    st.session_state.stage1_results = stage1_results

    if not stage1_results:
        clear_progress()
        _set_result(
            "No matching cases were found. Make sure you've uploaded case "
            "PDFs and clicked 'Build/Update Knowledge Base' first.",
            False,
            mode if mode != "auto" else "fast",
            question,
        )
        return

    resolved_mode = decide_mode(stage1_results) if mode == "auto" else mode

    update_progress(1, PROGRESS_STEPS)
    if resolved_mode == "fast":
        top_case = stage1_results[0]["case_name"]
        chunks = get_relevant_chunks(question, [top_case])
    else:
        graded = get_graded_cases(question)
        if graded["insufficient_cases"]:
            chunks = []
        else:
            chunks = [c for case in graded["cases"] for c in case["chunks"]]

    if not chunks:
        clear_progress()
        _set_result(
            "No verified answer could be found in the uploaded documents "
            "for this question.",
            False,
            resolved_mode,
            question,
        )
        return

    update_progress(2, PROGRESS_STEPS)
    update_progress(3, PROGRESS_STEPS)
    result = generate_verified_answer(question, chunks)

    clear_progress()
    _set_result(result["answer"], result["verified"], resolved_mode, question)


# ============================================================================
# Main area: question input + mode selection (B5.2)
# ============================================================================

st.title("Legal RAG")

question = st.text_input(
    "Ask a question about your uploaded cases",
    key="question_input",
)

st.write("**Choose a mode:**")

fast_col, deep_col, auto_col = st.columns(3)

with fast_col:
    if st.button("⚡ Fast", use_container_width=True):
        st.session_state.selected_mode = "fast"
        if question:
            run_pipeline(question, "fast")
    st.caption("Quick answer from the single most relevant case.")

with deep_col:
    if st.button("🔎 Deep Thinking", use_container_width=True):
        st.session_state.selected_mode = "deep"
        if question:
            run_pipeline(question, "deep")
    st.caption("Searches and compares multiple cases — takes longer.")

with auto_col:
    if st.button("🤖 Auto", use_container_width=True):
        st.session_state.selected_mode = "auto"
        if question:
            run_pipeline(question, "auto")
    st.caption("Lets the system decide based on the question.")

if st.session_state.selected_mode and not question:
    st.caption("Type a question above, then choose a mode to run it.")


# ============================================================================
# Ambiguity warning: display + "Continue anyway" (B5.4)
# ============================================================================

if st.session_state.result_mode == "fast" and st.session_state.stage1_results:
    warning = build_warning(st.session_state.stage1_results)

    if warning and not st.session_state.warning_acknowledged:
        st.warning(warning["message"])

        with st.expander("Explain why"):
            st.write(warning["explain_why"])

        # "Continue anyway" never blocks Fast mode — the answer below has
        # already been generated regardless of this warning. This button
        # only dismisses the banner; it does not gate or delay output.
        if st.button("Continue anyway"):
            st.session_state.warning_acknowledged = True
            st.rerun()


# ============================================================================
# Answer display, confidence line, and "Not satisfied?" regenerate (B5.5)
# ============================================================================

if st.session_state.pipeline_result:
    st.subheader("Answer")
    st.write(st.session_state.pipeline_result["answer"])

    if not st.session_state.pipeline_result["verified"]:
        st.caption("⚠️ No verified answer was found — showing fallback text above.")

    if st.session_state.result_mode == "fast" and st.session_state.stage1_results:
        st.caption(build_confidence_line(st.session_state.stage1_results))

    if st.button("Not satisfied?"):
        if st.session_state.result_mode == "fast":
            # Original mode was Fast -> escalate to Deep Thinking on the
            # same, unmodified question.
            run_pipeline(st.session_state.result_question, "deep")
            st.rerun()
        else:
            # Original mode was Deep Thinking -> re-run the same mode,
            # but with a rewritten query.
            rewritten_question = rewrite_query(st.session_state.result_question)
            run_pipeline(rewritten_question, "deep")
            st.rerun()
