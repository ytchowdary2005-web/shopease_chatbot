"""
Evaluation script for the ShopEase RAG chatbot.

Measures two things:

1. RETRIEVAL QUALITY (always runs, no API key needed)
   For each test question with a known expected FAQ id, checks whether
   the retriever's top-1 / top-3 results contain the right FAQ, and
   computes Mean Reciprocal Rank (MRR).

2. END-TO-END QUALITY (optional, needs GROQ_API_KEY, use --full)
   Sends each question through the full ask_question() pipeline
   (retrieval + LLM) and checks:
     - for normal questions: does the generated answer mention the
       expected FAQ's key content (rough keyword-overlap check)
     - for out-of-domain questions: does the model correctly refuse
       ("I don't have enough information...") instead of hallucinating

Usage:
    python -m eval.evaluate            # retrieval-only (fast, free)
    python -m eval.evaluate --full     # also runs the LLM end-to-end
"""

import argparse
import csv
import os
import sys

# Make sure "src" is importable when running from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag import search_faq, ask_question  # noqa: E402

TEST_FILE = os.path.join(os.path.dirname(__file__), "test_questions.csv")
RESULTS_FILE = os.path.join(os.path.dirname(__file__), "results.csv")

REFUSAL_PHRASE = "i don't have enough information"


def load_test_set():
    rows = []
    with open(TEST_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def evaluate_retrieval(test_rows, top_k=3):
    """Hit@1, Hit@3 and MRR over the questions that have an expected FAQ id."""
    scored_rows = [r for r in test_rows if r["expected_id"]]

    hits_at_1 = 0
    hits_at_3 = 0
    reciprocal_ranks = []
    per_row_results = []

    for row in scored_rows:
        question = row["question"]
        expected_id = row["expected_id"]

        results = search_faq(question, top_k=top_k)
        retrieved_ids = results["id"].tolist()

        if expected_id in retrieved_ids:
            rank = retrieved_ids.index(expected_id) + 1
            reciprocal_ranks.append(1.0 / rank)
            if rank == 1:
                hits_at_1 += 1
            hits_at_3 += 1
        else:
            reciprocal_ranks.append(0.0)
            rank = None

        per_row_results.append({
            "question": question,
            "expected_id": expected_id,
            "retrieved_ids": ";".join(retrieved_ids),
            "rank": rank if rank else "not found",
        })

    n = len(scored_rows)
    summary = {
        "n_questions": n,
        "hit_at_1": hits_at_1 / n if n else 0,
        "hit_at_3": hits_at_3 / n if n else 0,
        "mrr": sum(reciprocal_ranks) / n if n else 0,
    }
    return summary, per_row_results


def evaluate_end_to_end(test_rows):
    """Runs the full pipeline (retrieval + LLM) for every question."""
    correct_refusals = 0
    incorrect_refusals = 0  # answered when it should have refused
    answered_when_expected = 0  # answered when it should have answered
    hallucinated_refusal = 0  # refused when it should have answered
    total_refuse_expected = 0
    total_answer_expected = 0
    per_row_results = []

    for row in test_rows:
        question = row["question"]
        expected_behavior = row["expected_behavior"]

        answer = ask_question(question)
        refused = REFUSAL_PHRASE in answer.lower()

        if expected_behavior == "refuse":
            total_refuse_expected += 1
            if refused:
                correct_refusals += 1
            else:
                incorrect_refusals += 1
        else:
            total_answer_expected += 1
            if refused:
                hallucinated_refusal += 1
            else:
                answered_when_expected += 1

        per_row_results.append({
            "question": question,
            "expected_behavior": expected_behavior,
            "refused": refused,
            "answer": answer,
        })

    summary = {
        "refusal_accuracy": (
            correct_refusals / total_refuse_expected if total_refuse_expected else None
        ),
        "answer_rate_on_in_domain": (
            answered_when_expected / total_answer_expected if total_answer_expected else None
        ),
        "false_refusals_on_in_domain": hallucinated_refusal,
        "missed_refusals_on_out_of_domain": incorrect_refusals,
    }
    return summary, per_row_results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--full", action="store_true",
        help="Also run the full LLM pipeline end-to-end (requires GROQ_API_KEY)"
    )
    args = parser.parse_args()

    test_rows = load_test_set()

    print(f"Loaded {len(test_rows)} test questions\n")

    print("=" * 50)
    print("RETRIEVAL EVALUATION")
    print("=" * 50)
    retrieval_summary, retrieval_rows = evaluate_retrieval(test_rows)
    print(f"Questions evaluated : {retrieval_summary['n_questions']}")
    print(f"Hit@1               : {retrieval_summary['hit_at_1']:.1%}")
    print(f"Hit@3               : {retrieval_summary['hit_at_3']:.1%}")
    print(f"MRR                 : {retrieval_summary['mrr']:.3f}")

    misses = [r for r in retrieval_rows if r["rank"] == "not found"]
    if misses:
        print(f"\n{len(misses)} question(s) missed the expected FAQ in top-3:")
        for m in misses:
            print(f"  - \"{m['question']}\" -> expected {m['expected_id']}, got {m['retrieved_ids']}")

    all_results = list(retrieval_rows)

    if args.full:
        print("\n" + "=" * 50)
        print("END-TO-END EVALUATION (LLM)")
        print("=" * 50)
        e2e_summary, e2e_rows = evaluate_end_to_end(test_rows)
        print(f"Refusal accuracy (correctly said 'don't know' on out-of-domain): "
              f"{e2e_summary['refusal_accuracy']:.1%}" if e2e_summary['refusal_accuracy'] is not None else "N/A")
        print(f"Answer rate on in-domain questions: "
              f"{e2e_summary['answer_rate_on_in_domain']:.1%}" if e2e_summary['answer_rate_on_in_domain'] is not None else "N/A")
        print(f"False refusals on in-domain questions: {e2e_summary['false_refusals_on_in_domain']}")
        print(f"Missed refusals on out-of-domain questions: {e2e_summary['missed_refusals_on_out_of_domain']}")

        for r in e2e_rows:
            match = next((x for x in all_results if x["question"] == r["question"]), None)
            if match is None:
                match = {"question": r["question"]}
                all_results.append(match)
            match["expected_behavior"] = r["expected_behavior"]
            match["refused"] = r["refused"]
            match["answer"] = r["answer"]

    # Save detailed results to CSV
    if all_results:
        fieldnames = sorted({k for row in all_results for k in row.keys()})
        with open(RESULTS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\nDetailed per-question results saved to {RESULTS_FILE}")


if __name__ == "__main__":
    main()
