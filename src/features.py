"""
Feature engineering and clustering module.

Performs clustering on audio features to identify mood clusters.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple

# Data directories
PROCESSED_DATA_DIR = Path("data/processed")
FEATURES_DATA_DIR = Path("data/features")
FEATURES_DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_processed_tracks() -> pd.DataFrame:
    """Load processed tracks dataset."""
    filepath = PROCESSED_DATA_DIR / "tracks.csv"
    if not filepath.exists():
        raise FileNotFoundError(
            f"Processed tracks not found at {filepath}. "
            "Please run preprocessing first."
        )
    return pd.read_csv(filepath)


def prepare_feature_matrix(df: pd.DataFrame) -> Tuple[pd.DataFrame, np.ndarray, List[str], object]:
    """
    Prepare feature matrix for clustering.
    
    Args:
        df: Tracks DataFrame with audio features
    
    Returns:
        Tuple of (feature_names, feature_matrix)
    """
    # Select features for clustering
    feature_cols = [
        "danceability",
        "energy",
        "valence",
        "acousticness",
        "tempo",
    ]
    
    # Filter out rows with missing features
    df_clean = df.dropna(subset=feature_cols)
    
    if len(df_clean) == 0:
        raise ValueError("No tracks with complete audio features found.")
    
    # Extract feature matrix
    X = df_clean[feature_cols].values
    
    # Standardize features (tempo is on different scale)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    return df_clean, X_scaled, feature_cols, scaler


def assign_mood_labels(cluster_labels: np.ndarray, df: pd.DataFrame) -> List[str]:
    """
    Assign human-readable mood labels based on cluster characteristics.
    
    Args:
        cluster_labels: Array of cluster assignments
        df: DataFrame with features (same rows as cluster_labels)
    
    Returns:
        List of mood label strings
    """
    n_clusters = len(np.unique(cluster_labels))
    mood_labels = []
    
    # Calculate mean features per cluster
    cluster_means = {}
    for cluster_id in range(n_clusters):
        mask = cluster_labels == cluster_id
        cluster_data = df[mask]
        
        cluster_means[cluster_id] = {
            "energy": cluster_data["energy"].mean(),
            "valence": cluster_data["valence"].mean(),
            "danceability": cluster_data["danceability"].mean(),
            "acousticness": cluster_data["acousticness"].mean(),
        }
    
    # Assign labels based on characteristics
    for cluster_id in cluster_labels:
        means = cluster_means[cluster_id]
        
        if means["energy"] > 0.7 and means["valence"] > 0.6:
            label = "High-Energy Hype"
        elif means["energy"] < 0.4 and means["valence"] < 0.4:
            label = "Melancholy / Low Energy"
        elif means["acousticness"] > 0.5:
            label = "Chill / Acoustic"
        elif means["danceability"] > 0.7:
            label = "Dance Party"
        else:
            label = "Balanced / Mixed"
        
        mood_labels.append(label)
    
    return mood_labels


def perform_clustering(
    n_clusters: int = 4,
    random_state: int = 42
) -> pd.DataFrame:
    """
    Perform KMeans clustering on audio features.
    
    Args:
        n_clusters: Number of clusters (default 4)
        random_state: Random seed for reproducibility
    
    Returns:
        DataFrame with cluster assignments and mood labels
    
    Note: Requires audio features. If unavailable, clustering cannot be performed.
    """
    print("=" * 60)
    print("Starting mood clustering...")
    print("=" * 60)
    
    # Load data
    print("Loading processed tracks...")
    df = load_processed_tracks()
    
    # Check if audio features are available
    required_features = ["danceability", "energy", "valence", "acousticness", "tempo"]
    missing_features = [f for f in required_features if f not in df.columns or df[f].isna().all()]
    
    if missing_features:
        raise ValueError(
            f"Audio features are required for clustering but are missing: {missing_features}\n"
            "This is likely because Spotify's /audio-features endpoint is unavailable for new apps.\n"
            "Spotify deprecated this endpoint on Nov 27, 2024 for new applications.\n"
            "Clustering cannot be performed without audio features."
        )
    
    # Prepare features
    print("Preparing feature matrix...")
    df_clean, X_scaled, feature_cols, scaler = prepare_feature_matrix(df)
    
    print(f"  Using {len(df_clean)} tracks with complete features")
    print(f"  Features: {', '.join(feature_cols)}")
    
    # Perform clustering
    print(f"Performing KMeans clustering (k={n_clusters})...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    cluster_labels = kmeans.fit_predict(X_scaled)
    
    # Add cluster assignments
    df_clean = df_clean.copy()
    df_clean["cluster"] = cluster_labels
    
    # Assign mood labels
    print("Assigning mood labels...")
    mood_labels = assign_mood_labels(cluster_labels, df_clean)
    df_clean["mood_label"] = mood_labels
    
    # Analyze clusters
    print("\nCluster Analysis:")
    print("-" * 60)
    for cluster_id in range(n_clusters):
        cluster_data = df_clean[df_clean["cluster"] == cluster_id]
        # Get the mood label for this specific cluster
        mood_label = cluster_data['mood_label'].iloc[0] if len(cluster_data) > 0 else "Unknown"
        print(f"\nCluster {cluster_id} ({mood_label}):")
        print(f"  Size: {len(cluster_data)} tracks")
        print(f"  Mean Energy: {cluster_data['energy'].mean():.3f}")
        print(f"  Mean Valence: {cluster_data['valence'].mean():.3f}")
        print(f"  Mean Danceability: {cluster_data['danceability'].mean():.3f}")
        print(f"  Mean Acousticness: {cluster_data['acousticness'].mean():.3f}")
        
        # Show example tracks
        examples = cluster_data.head(3)
        print(f"  Example tracks:")
        for _, track in examples.iterrows():
            print(f"    - {track['track_name']} by {track['primary_artist']}")
    
    # Save clustered data
    output_path = FEATURES_DATA_DIR / "tracks_with_clusters.csv"
    df_clean.to_csv(output_path, index=False)
    print(f"\n✓ Saved clustered tracks to {output_path}")
    
    print("=" * 60)
    print("✓ Clustering complete!")
    print("=" * 60)
    
    return df_clean


def get_cluster_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate summary statistics per cluster.
    
    Args:
        df: DataFrame with cluster assignments
    
    Returns:
        Summary DataFrame with mean features per cluster
    """
    feature_cols = [
        "danceability",
        "energy",
        "valence",
        "acousticness",
        "tempo",
    ]
    
    summary = df.groupby(["cluster", "mood_label"])[feature_cols].mean()
    summary["count"] = df.groupby(["cluster", "mood_label"]).size()
    
    return summary.reset_index()


if __name__ == "__main__":
    perform_clustering(n_clusters=4)

