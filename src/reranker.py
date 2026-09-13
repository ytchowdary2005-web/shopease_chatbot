from sentence_transformers import CrossEncoder

# Cross-encoders score a (question, candidate) pair directly, instead of
# comparing separately-computed embeddings. Slower per-pair, but much better
# at telling apart near-duplicate FAQs within the same category.
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def rerank(question, candidates_df, top_k=3):
    """
    Re-scores a small set of candidate FAQs (already retrieved by FAISS)
    against the question, and returns the best top_k re-ordered by the
    new scores.
    """
    pairs = [
        (question, row["question"])
        for _, row in candidates_df.iterrows()
    ]

    scores = reranker.predict(pairs)

    reranked = candidates_df.copy()
    reranked["rerank_score"] = scores
    reranked = reranked.sort_values("rerank_score", ascending=False)

    return reranked.head(top_k)