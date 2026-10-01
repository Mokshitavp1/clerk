import json
import statistics
import sys
import os

# Add internal modules to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'retrieval')))

from stage1_case_retrieval import get_relevant_cases
from stage2_chunk_retrieval import get_relevant_chunks

def calibrate():
    questions_file = "eval_questions.json"
    if not os.path.exists(questions_file):
        print(f"Error: {questions_file} not found. Please create it or run from the correct directory.")
        return

    with open(questions_file, "r") as f:
        questions = json.load(f)
        
    relevant_scores = []
    irrelevant_scores = []
    
    for q in questions:
        # Check if the question is a placeholder, skip if it is
        if q["expected_case"] == "TODO":
            continue
            
        query = q["question"]
        expected_case = q["expected_case"]
        expected_pages = q["expected_pages"]
        
        cases = get_relevant_cases(query, top_k=5)
        case_names = [c["case_name"] for c in cases]
        chunks = get_relevant_chunks(query, case_names, top_k=6)
        
        for chunk in chunks:
            if chunk["case_name"] == expected_case and chunk["page_number"] in expected_pages:
                relevant_scores.append(chunk["relevance_score"])
            else:
                irrelevant_scores.append(chunk["relevance_score"])
                
    if not relevant_scores:
        print("No relevant chunks found in the top-6 for any non-TODO question. Cannot calibrate.")
        return
        
    def print_stats(name, scores):
        if not scores:
            print(f"{name} (0 chunks): None")
            return
        scores = sorted(scores)
        print(f"{name} ({len(scores)} chunks):")
        print(f"  Min:    {min(scores):.4f}")
        print(f"  Median: {statistics.median(scores):.4f}")
        print(f"  Max:    {max(scores):.4f}")
        
    print("--- Score Distributions ---")
    print_stats("Relevant chunks", relevant_scores)
    print_stats("Irrelevant chunks", irrelevant_scores)
    
    # Calculate F1
    all_scores = sorted(list(set(relevant_scores + irrelevant_scores)))
    best_f1 = -1
    best_threshold = 0
    
    for threshold in all_scores:
        tp = sum(1 for s in relevant_scores if s >= threshold)
        fp = sum(1 for s in irrelevant_scores if s >= threshold)
        fn = sum(1 for s in relevant_scores if s < threshold)
        
        precision = tp / (tp + fp) if tp + fp > 0 else 0
        recall = tp / (tp + fn) if tp + fn > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0
        
        # In case of tie, prefer the higher threshold to drop more irrelevant chunks
        if f1 >= best_f1:
            best_f1 = f1
            best_threshold = threshold
            
    print("\n--- Calibration Results ---")
    print(f"Threshold for Max F1 ({best_f1:.4f}): {best_threshold:.4f}")
    
    recall_100_threshold = min(relevant_scores) if relevant_scores else 0
    print(f"Threshold for 100% Recall: {recall_100_threshold:.4f}")

if __name__ == "__main__":
    calibrate()
