from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


model = SentenceTransformer("all-MiniLM-L6-v2")


def calculate_similarity(text1: str, text2: str) -> float:
    if not text1.strip() or not text2.strip():
        return 0.0

    embeddings = model.encode([text1, text2])

    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    return round(float(similarity) * 100, 2)


def calculate_semantic_components(
    candidate_skills: list[str],
    candidate_experience: str,
    candidate_projects: str,
    job_skills: list[str],
    job_description: str
) -> dict:

    candidate_skill_text = ", ".join(candidate_skills)
    job_skill_text = ", ".join(job_skills)

    skill_similarity = calculate_similarity(
        candidate_skill_text,
        job_skill_text
    )

    experience_similarity = calculate_similarity(
        candidate_experience,
        job_description
    )

    project_similarity = calculate_similarity(
        candidate_projects,
        job_description
    )

    semantic_score = (
        skill_similarity * 0.50
        + experience_similarity * 0.30
        + project_similarity * 0.20
    )

    return {
        "skill_similarity": skill_similarity,
        "experience_similarity": experience_similarity,
        "project_similarity": project_similarity,
        "semantic_score": round(semantic_score, 2)
    }