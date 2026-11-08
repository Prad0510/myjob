# Compare KMeans vs HDBSCAN clustering for job matching
"""Utility to evaluate which clustering method (K‑Means or HDBSCAN) produces
more coherent job clusters for the candidate‑matching pipeline.

The script:
1. Loads all active job embeddings from the database.
2. Runs **both** clustering algorithms on the same embedding matrix.
3. Computes clustering quality metrics (Silhouette score, number of clusters,
   noise proportion for HDBSCAN).
4. For a given candidate resume (the one stored in `data/processed/`
   `candidate_profile.json`), assigns the candidate to the nearest cluster for
   each method and reports the top‑N matches and their average similarity.
5. Prints a short summary so you can decide which method to keep.

Usage (from the project root)::
    python -m src.jobs.compare_clustering

You can tweak the environment variables `NUM_CLUSTERS` and `MIN_CLUSTER_SIZE`
to experiment with different hyper‑parameters.
"""

from src.resume.candidate_profile import CandidateProfile
import os
import json
import logging
from pathlib import Path
from typing import Tuple
import numpy as np
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_distances
from src.utils.logger import get_logger
from src.database.connection import get_connection, close_pool
from src.resume.resume_parser import build_candidate_profile
from src.embeddings import embed_text
from src.jobs.clustering import cluster_jobs, assign_candidate_to_cluster

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def load_job_embeddings(conn) -> Tuple[np.ndarray, list]:
    """Load active jobs and compute embeddings on‑the‑fly.

    The original schema does not store a pre‑computed ``embedding`` column, so we
    generate embeddings from the textual fields (title, description, skills) at
    runtime. This keeps the comparison script usable without altering the DB
    schema.
    """
    with conn.cursor() as cur:
        # Grab the fields that best represent a job for semantic similarity.
        cur.execute(
            """
            SELECT id, title, description, skills
            FROM jobs
            WHERE status = 'active';
            """
        )
        rows = cur.fetchall()
    ids = [row[0] for row in rows]
    # Combine the textual parts into a single string per job.
    texts = []
    for _, title, description, skills in rows:
        parts = []
        if title:
            parts.append(title)
        if description:
            parts.append(description)
        if skills:
            # ``skills`` is a PostgreSQL array; psycopg2 returns a Python list.
            parts.append(", ".join(skills))
        texts.append(" ".join(parts))
    # Use the embedding helper to produce a (n_jobs, dim) array.
    embeddings = embed_text(texts)  # returns np.ndarray
    return embeddings, ids

def evaluate_candidate(candidate_emb: np.ndarray, job_embs: np.ndarray, labels: np.ndarray, centroids: np.ndarray, top_n: int = 5) -> Tuple[list, float]:
    """Assign candidate to a cluster, score jobs in that cluster, and return top‑N matches.

    Returns a list of (job_id, similarity) and the mean similarity of those matches.
    """
    # Choose cluster
    cluster_idx = assign_candidate_to_cluster(candidate_emb, centroids)
    if cluster_idx == -1:
        mask = np.full(labels.shape, True)
    else:
        mask = labels == cluster_idx
    filtered_embs = job_embs[mask]
    filtered_ids = np.where(mask)[0]  # indices into the original id list
    if filtered_embs.size == 0:
        # fallback to all jobs
        filtered_embs = job_embs
        filtered_ids = np.arange(job_embs.shape[0])
    # Score
    cand_norm = candidate_emb / np.linalg.norm(candidate_emb)
    job_norms = filtered_embs / np.linalg.norm(filtered_embs, axis=1, keepdims=True)
    sims = np.dot(job_norms, cand_norm)
    top_k = min(top_n, sims.shape[0])
    top_idx = np.argpartition(-sims, range(top_k))[:top_k]
    top_ids = filtered_ids[top_idx]
    top_scores = sims[top_idx]
    matches = [(int(top_ids[i]), float(top_scores[i])) for i in range(top_k)]
    avg_score = float(top_scores.mean()) if top_k > 0 else 0.0
    return matches, avg_score

def _load_candidate_profile() -> CandidateProfile:
    """Load the candidate profile JSON and rebuild the CandidateProfile object.
    The JSON file created by `main.py` contains the parsed fields. We can
    reconstruct the original resume text by concatenating the sections,
    which is enough for the existing `build_candidate_profile` implementation.
    """
    json_path = Path("data/processed/candidate_profile.json")
    if not json_path.is_file():
        logger.error("Candidate profile JSON not found at %s", json_path)
        raise FileNotFoundError(json_path)
    data = json.loads(json_path.read_text(encoding="utf-8"))
    # Re‑assemble a plain‑text representation (the parser only needs the raw text)
    # Use fields that were stored: name, skills, education, experience, etc.
    parts = [
        data.get("name", ""),
        "Skills: " + ", ".join(data.get("skills", [])),
        "Education: " + "; ".join(
            f"{edu.get('degree','')} at {edu.get('institution','')}"
            for edu in data.get("education", [])
        ),
        "Experience: " + "; ".join(
            f"{exp.get('role','')} at {exp.get('organization','')}"
            for exp in data.get("experience", [])
        ),
    ]
    resume_text = "\n".join(filter(None, parts))
    # Now call the original parser to get a CandidateProfile object
    return build_candidate_profile(resume_text)
# ---------------------------------------------------------------------------
# Main routine
# ---------------------------------------------------------------------------

def main():
    conn = get_connection()
    try:
        # Load data
        job_embs, job_ids = load_job_embeddings(conn)
        if job_embs.shape[0] == 0:
            logger.error("No active jobs found in the database.")
            return
        # Candidate profile & embedding
        candidate = _load_candidate_profile()
        # Build a richer text representation for the candidate
        # Include name, skills, experience roles, and education degrees.
        candidate_text_parts = []
        if candidate.name:
            candidate_text_parts.append(candidate.name)
        if candidate.skills:
            candidate_text_parts.append(' '.join(candidate.skills))
        if getattr(candidate, 'experience', None):
            candidate_text_parts.extend([exp.role for exp in candidate.experience if exp.role])
        if getattr(candidate, 'education', None):
            candidate_text_parts.extend([edu.degree for edu in candidate.education if edu.degree])
        candidate_text = ' '.join(candidate_text_parts)
        if not candidate_text.strip():
            logger.warning('Candidate text is empty – using placeholder')
            candidate_text = 'placeholder'
        cand_emb = embed_text(candidate_text)  # np.ndarray
        # -------------------------------------------------------------------
        # 1️⃣ K‑Means
        os.environ["CLUSTER_METHOD"] = "kmeans"
        k_labels, k_centroids = cluster_jobs(job_embs)
        k_silhouette = silhouette_score(job_embs, k_labels) if len(set(k_labels)) > 1 else -1
        k_matches, k_avg = evaluate_candidate(cand_emb, job_embs, k_labels, k_centroids)
        # -------------------------------------------------------------------
        # 2️⃣ HDBSCAN
        os.environ["CLUSTER_METHOD"] = "hdbscan"
        h_labels, h_centroids = cluster_jobs(job_embs)
        # HDBSCAN can produce noise label -1; we filter those out for the score.
        valid_mask = h_labels != -1
        if valid_mask.sum() > 1:
            h_silhouette = silhouette_score(job_embs[valid_mask], h_labels[valid_mask])
        else:
            h_silhouette = -1
        h_noise_frac = (h_labels == -1).mean()
        h_matches, h_avg = evaluate_candidate(cand_emb, job_embs, h_labels, h_centroids)
        # -------------------------------------------------------------------
        # Report
        print("=== Clustering Comparison ===")
        print("K‑Means:")
        print(f"  #clusters   : {len(set(k_labels))}")
        print(f"  Silhouette  : {k_silhouette:.4f}")
        print(f"  Top-{len(k_matches)} matches avg similarity: {k_avg:.4f}")
        print("  Matches (job_id, score):")
        for jid, sc in k_matches:
            print(f"    {jid}: {sc:.4f}")
        print("\nHDBSCAN:")
        print(f"  #clusters   : {len(set(h_labels)) - (1 if -1 in h_labels else 0)} (noise={h_noise_frac:.2%})")
        print(f"  Silhouette  : {h_silhouette:.4f}")
        print(f"  Top-{len(h_matches)} matches avg similarity: {h_avg:.4f}")
        print("  Matches (job_id, score):")
        for jid, sc in h_matches:
            print(f"    {jid}: {sc:.4f}")
        # Simple recommendation based on silhouette & avg similarity
        if h_silhouette > k_silhouette and h_avg > k_avg:
            print("\nRecommendation: HDBSCAN appears to give tighter clusters and higher relevance.")
        else:
            print("\nRecommendation: K‑Means looks better for this data (or at least not worse).")
    finally:
        close_pool()

if __name__ == "__main__":
    main()

