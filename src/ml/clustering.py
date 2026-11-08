import json

import hdbscan
import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

import umap.umap_ as umap


INPUT_FILE = "data/processed/technical_job_feature_matrix.csv"

OUTPUT_CLUSTERS = "data/processed/technical_job_clusters.csv"
OUTPUT_UMAP = "data/processed/technical_job_umap.csv"
OUTPUT_SUMMARY = "data/processed/technical_cluster_summary.json"


def load_features():

    df = pd.read_csv(INPUT_FILE)

    metadata_columns = {
        "id",
        "title",
        "company",
        "location",
        "description",
        "application_url",
        "technical_title",
        "technical_skill_evidence",
        "is_technical",
    }

    feature_columns = [
        column
        for column in df.columns
        if column not in metadata_columns
    ]

    X = df[feature_columns].fillna(0)

    return df, X, feature_columns


def remove_rare_features(X, min_jobs=2):

    feature_frequency = (
        (X > 0).sum(axis=0)
    )

    selected_features = feature_frequency[
        feature_frequency >= min_jobs
    ].index

    return X[selected_features]


def apply_feature_weighting(X):

    X = X.copy()

    for column in X.columns:

        if column.startswith("role__"):
            X[column] *= 1.5

        elif column.startswith("seniority__"):
            X[column] *= 0.6

        elif column.startswith("title_skill__"):
            X[column] *= 1.0

        elif column.startswith("skill__"):
            X[column] *= 1.0

        elif column.startswith("domain__"):
            X[column] *= 1.5

        elif column == "technical_skill_count":
            X[column] *= 0.5

        elif column == "technical_skill_density":
            X[column] *= 0.5

        elif column == "technical_domain_count":
            X[column] *= 1.0

    return X


def run_pca(X):

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    # With only 30 observations, avoid requesting
    # an unnecessarily large number of components.
    max_components = min(
        X_scaled.shape[0] - 1,
        X_scaled.shape[1]
    )

    pca_full = PCA(
        n_components=max_components
    )

    X_pca_full = pca_full.fit_transform(
        X_scaled
    )

    cumulative_variance = np.cumsum(
        pca_full.explained_variance_ratio_
    )

    n_components = (
        np.argmax(
            cumulative_variance >= 0.90
        ) + 1
    )

    pca = PCA(
        n_components=n_components
    )

    X_pca = pca.fit_transform(
        X_scaled
    )

    print("\nPCA")
    print("-" * 30)
    print(
        f"Original dimensions: {X.shape[1]}"
    )
    print(
        f"PCA dimensions: {n_components}"
    )
    print(
        f"Explained variance: "
        f"{pca.explained_variance_ratio_.sum():.2%}"
    )

    return X_pca


def run_kmeans(X):

    print("\nK-Means silhouette analysis")
    print("-" * 30)

    results = {}

    # Small dataset: test a sensible range.
    for k in range(2, 7):

        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=20,
        )

        labels = model.fit_predict(X)

        score = silhouette_score(
            X,
            labels
        )

        results[k] = score

        print(
            f"k={k}: silhouette={score:.4f}"
        )

    best_k = max(
        results,
        key=results.get
    )

    print(
        f"\nSelected K={best_k} "
        f"with silhouette={results[best_k]:.4f}"
    )

    model = KMeans(
        n_clusters=best_k,
        random_state=42,
        n_init=20,
    )

    labels = model.fit_predict(X)

    return labels, results


def run_hdbscan(X):

    print("\nHDBSCAN")
    print("-" * 30)

    # Smaller values are appropriate for
    # a 30-job technical dataset.
    model = hdbscan.HDBSCAN(
        min_cluster_size=4,
        min_samples=2,
        cluster_selection_method="eom",
    )

    labels = model.fit_predict(X)

    unique_labels = sorted(
        set(labels)
    )

    noise_count = int(
        np.sum(labels == -1)
    )

    print(
        f"Noise: {noise_count} jobs"
    )

    for label in unique_labels:

        if label == -1:
            continue

        count = int(
            np.sum(labels == label)
        )

        print(
            f"Cluster {label}: "
            f"{count} jobs"
        )

    return labels


def run_umap(X):

    reducer = umap.UMAP(
        n_neighbors=min(10, len(X) - 1),
        min_dist=0.2,
        n_components=2,
        metric="euclidean",
        random_state=42,
    )

    embedding = reducer.fit_transform(X)

    return embedding


def profile_clusters(
    df,
    labels,
    feature_matrix,
):

    df = df.copy()

    df["cluster"] = labels

    summaries = {}

    for cluster in sorted(
        set(labels)
    ):

        cluster_df = df[
            df["cluster"] == cluster
        ]

        cluster_size = len(
            cluster_df
        )

        if cluster == -1:

            cluster_name = "noise"

        else:

            cluster_name = f"cluster_{cluster}"

        # Find dominant features
        feature_values = feature_matrix.loc[
            cluster_df.index
        ].mean()

        top_features = (
            feature_values
            .sort_values(
                ascending=False
            )
            .head(10)
        )

        examples = []

        for _, row in cluster_df.head(10).iterrows():

            examples.append(
                {
                    "job_id": int(row["id"]),
                    "title": row["title"],
                    "company": row["company"],
                }
            )

        summaries[cluster_name] = {
            "size": cluster_size,
            "percentage": round(
                cluster_size / len(df) * 100,
                2,
            ),
            "top_features": [
                {
                    "feature": feature,
                    "value": round(
                        float(value),
                        4,
                    ),
                }
                for feature, value
                in top_features.items()
            ],
            "example_jobs": examples,
        }

    return df, summaries


def main():

    print("=" * 60)
    print("TECHNICAL JOB CLUSTERING")
    print("=" * 60)

    # ---------------------------------------------------------
    # Load
    # ---------------------------------------------------------

    df, X, feature_columns = load_features()

    print(
        f"\nTechnical jobs: {len(df)}"
    )

    print(
        f"Total ML features: "
        f"{len(feature_columns)}"
    )

    # ---------------------------------------------------------
    # Remove rare features
    # ---------------------------------------------------------

    X = remove_rare_features(
        X,
        min_jobs=2,
    )

    print(
        f"Features after rare-feature filtering: "
        f"{X.shape[1]}"
    )

    # ---------------------------------------------------------
    # Feature weighting
    # ---------------------------------------------------------

    X = apply_feature_weighting(X)

    # ---------------------------------------------------------
    # PCA
    # ---------------------------------------------------------

    X_pca = run_pca(X)

    # ---------------------------------------------------------
    # K-Means
    # ---------------------------------------------------------

    kmeans_labels, kmeans_scores = run_kmeans(
        X_pca
    )

    # ---------------------------------------------------------
    # HDBSCAN
    # ---------------------------------------------------------

    hdbscan_labels = run_hdbscan(
        X_pca
    )

    # ---------------------------------------------------------
    # UMAP
    # ---------------------------------------------------------

    print("\nUMAP")
    print("-" * 30)

    embedding = run_umap(
        X_pca
    )

    print(
        "UMAP embedding generated successfully."
    )

    # ---------------------------------------------------------
    # Cluster profiling
    # ---------------------------------------------------------

    print("\nHDBSCAN cluster profiles")
    print("=" * 60)

    profiled_df, summaries = profile_clusters(
        df,
        hdbscan_labels,
        X,
    )

    for cluster_name, summary in summaries.items():

        print(
            f"\n{cluster_name.upper()}"
        )

        print(
            f"Size: {summary['size']} "
            f"({summary['percentage']}%)"
        )

        print("Top features:")

        for feature in summary[
            "top_features"
        ][:5]:

            print(
                f"  {feature['feature']}"
            )

        print("Examples:")

        for job in summary[
            "example_jobs"
        ][:5]:

            print(
                f"  {job['job_id']}: "
                f"{job['title']} "
                f"({job['company']})"
            )

    # ---------------------------------------------------------
    # Save cluster results
    # ---------------------------------------------------------

    profiled_df[
        [
            "id",
            "title",
            "company",
            "cluster",
        ]
    ].to_csv(
        OUTPUT_CLUSTERS,
        index=False,
    )

    # ---------------------------------------------------------
    # Save UMAP
    # ---------------------------------------------------------

    umap_df = pd.DataFrame(
        {
            "job_id": df["id"],
            "title": df["title"],
            "company": df["company"],
            "cluster": hdbscan_labels,
            "umap_x": embedding[:, 0],
            "umap_y": embedding[:, 1],
        }
    )

    umap_df.to_csv(
        OUTPUT_UMAP,
        index=False,
    )

    # ---------------------------------------------------------
    # Save summary
    # ---------------------------------------------------------

    output_summary = {
        "dataset_size": len(df),
        "feature_count": int(X.shape[1]),
        "kmeans": {
            "silhouette_scores": {
                str(k): round(
                    float(score),
                    4,
                )
                for k, score
                in kmeans_scores.items()
            }
        },
        "hdbscan": summaries,
    }

    with open(
        OUTPUT_SUMMARY,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            output_summary,
            file,
            indent=2,
        )

    print("\nSaved:")
    print(
        f"  {OUTPUT_CLUSTERS}"
    )
    print(
        f"  {OUTPUT_UMAP}"
    )
    print(
        f"  {OUTPUT_SUMMARY}"
    )

    print("\n" + "=" * 60)
    print("TECHNICAL CLUSTERING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()