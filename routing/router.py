"""
Auto-mode routing: decides Fast vs Deep Thinking based on how confidently
Stage 1 retrieval picked a single dominant case.
"""


def decide_mode(stage1_results, threshold=0.1):
    """
    Decide whether Auto mode should run Fast or Deep Thinking, based on
    whether one case clearly dominates the Stage 1 shortlist.

    Args:
        stage1_results: list of {"case_name": str, "relevance_score": float}
            dicts, as returned by stage1_case_retrieval.get_relevant_cases,
            assumed to already be sorted by relevance_score descending.
        threshold: if the top two relevance_score values differ by this
            much or less, the result is considered ambiguous and routed
            to "deep". Matches the default used by
            stage1_case_retrieval.is_ambiguous for consistency.

    Returns:
        str: "fast" if the top result clearly dominates (or there's only
        one/zero results, since ambiguity requires at least two
        candidates to compare), "deep" if the top two scores are within
        threshold of each other.
    """
    if len(stage1_results) < 2:
        return "fast"

    top_score = stage1_results[0]["relevance_score"]
    second_score = stage1_results[1]["relevance_score"]

    if (top_score - second_score) <= threshold:
        return "deep"

    return "fast"


def build_confidence_line(stage1_results):
    """
    Build a short confidence line naming the top Stage 1 result, for
    display in Fast mode.

    This is shown regardless of whether the top result was ambiguous —
    it's a simple statement of what Fast mode actually matched against,
    not a judgment about confidence. The separate ambiguity warning (see
    build_warning) is what tells the user if that match might be shaky.

    Args:
        stage1_results: list of {"case_name": str, "relevance_score": float}
            dicts, as returned by stage1_case_retrieval.get_relevant_cases,
            assumed to already be sorted by relevance_score descending.

    Returns:
        str: e.g. "Matched primarily against Smith_v_Jones_2019". If
        stage1_results is empty, returns a line saying no case was
        matched, since there is no top result to name.
    """
    if not stage1_results:
        return "No matching case was found."

    top_case_name = stage1_results[0]["case_name"]
    return f"Matched primarily against {top_case_name}"


def build_warning(stage1_results):
    """
    Build an ambiguity warning if the top two Stage 1 results are close
    enough that a single-case (Fast mode) answer might miss relevant
    context from a competing case.

    Args:
        stage1_results: list of {"case_name": str, "relevance_score": float}
            dicts, as returned by stage1_case_retrieval.get_relevant_cases,
            assumed to already be sorted by relevance_score descending.

    Returns:
        None if decide_mode(stage1_results) is "fast" (top result clearly
        dominates, or fewer than 2 results). Otherwise a dict per
        CONTRACTS.md 3.5:
            {
                "message": str,       # short line for display
                "explain_why": str,   # longer explanation naming the
                                       # competing cases + scores, and
                                       # recommending Deep Thinking mode
            }
    """
    if decide_mode(stage1_results) == "fast":
        return None

    top_case = stage1_results[0]
    second_case = stage1_results[1]

    message = "This question may involve comparing multiple cases."
    explain_why = (
        f"The top two matches were close in relevance: "
        f"{top_case['case_name']} (score {top_case['relevance_score']:.2f}) and "
        f"{second_case['case_name']} (score {second_case['relevance_score']:.2f}). "
        f"Fast mode only looks at the single top-matched case, so it may miss "
        f"relevant context from {second_case['case_name']}. "
        f"Deep Thinking mode is recommended, since it searches and compares "
        f"across multiple cases instead of relying on just one."
    )

    return {"message": message, "explain_why": explain_why}


if __name__ == "__main__":
    clear = [
        {"case_name": "Smith_v_Jones_2019", "relevance_score": 0.87},
        {"case_name": "Doe_v_Acme_Corp_2021", "relevance_score": 0.41},
    ]
    ambiguous = [
        {"case_name": "Smith_v_Jones_2019", "relevance_score": 0.74},
        {"case_name": "Doe_v_Acme_Corp_2021", "relevance_score": 0.69},
    ]

    print("Clear top result ->", decide_mode(clear))
    print("Ambiguous top two ->", decide_mode(ambiguous))
    print("Confidence line (clear) ->", build_confidence_line(clear))
    print("Confidence line (ambiguous) ->", build_confidence_line(ambiguous))
    print("Confidence line (empty) ->", build_confidence_line([]))

    print("\nWarning (clear) ->", build_warning(clear))
    print("\nWarning (ambiguous) ->")
    warning = build_warning(ambiguous)
    print(" message:", warning["message"])
    print(" explain_why:", warning["explain_why"])
