from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


model = SentenceTransformer("all-MiniLM-L6-v2")


def calculate_semantic_score(
    candidate_text: str,
    job_text: str
) -> float:

    candidate_embedding = model.encode([candidate_text])
    job_embedding = model.encode([job_text])

    similarity = cosine_similarity(
        candidate_embedding,
        job_embedding
    )[0][0]

    return round(float(similarity) * 100, 2)