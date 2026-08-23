import sys, os
for d in ['retrieval', 'generation', 'routing', 'ingestion']: sys.path.insert(0, d)
from self_rag import get_graded_cases
from generate import generate_answer
from verifier import verify_answer, _check_has_content, _check_citations_deterministic

question = 'My client paid an advance to a government contractor for a supply contract, but before any work was done, the contract was cancelled. The contractor is refusing to refund the advance, pointing to a clause that lets them keep it if the deal falls through. Is there a similar case on whether that kind of forfeiture is valid without proof the government actually suffered a loss?'

graded = get_graded_cases(question)
print('=== GRADING ===')
print('insufficient_cases:', graded['insufficient_cases'])
for case in graded['cases']:
    print(f"  {case['case_name']}: {len(case['chunks'])} surviving chunks")
    for c in case['chunks']:
        print(f"    p.{c['page_number']}  score={c['relevance_score']:.3f}  {c['text'][:80]!r}")

chunks = [c for case in graded['cases'] for c in case['chunks']]

print('\n=== RAW GENERATED ANSWER (attempt 1) ===')
answer = generate_answer(question, chunks)
print(repr(answer))

print('\n=== DETERMINISTIC CONTENT CHECK ===')
print(_check_has_content(answer))

print('\n=== DETERMINISTIC CITATION CHECK ===')
print(_check_citations_deterministic(answer, chunks))

print('\n=== FULL VERIFY_ANSWER RESULT (includes LLM check if deterministic checks pass) ===')
result = verify_answer(answer, chunks)
print(result)

