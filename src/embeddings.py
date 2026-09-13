from sentence_transformers import SentenceTransformer


model = SentenceTransformer("all-mpnet-base-v2")


def create_embeddings(texts):
    embeddings = model.encode(texts)
    return embeddings