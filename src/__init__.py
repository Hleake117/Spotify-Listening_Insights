"""
Spotify Listening Insights - Source Package
"""

from .auth import authenticate, get_valid_token
from .api_client import SpotifyAPIClient
from .fetch_data import fetch_all_data
from .preprocess import preprocess_all_data
from .features import perform_clustering
from .visuals import (
    plot_top_genres,
    plot_top_artists,
    plot_feature_distribution,
    plot_energy_valence_scatter,
    plot_tempo_danceability_scatter,
    plot_cluster_radar,
    plot_time_heatmap,
)

__all__ = [
    "authenticate",
    "get_valid_token",
    "SpotifyAPIClient",
    "fetch_all_data",
    "preprocess_all_data",
    "perform_clustering",
    "plot_top_genres",
    "plot_top_artists",
    "plot_feature_distribution",
    "plot_energy_valence_scatter",
    "plot_tempo_danceability_scatter",
    "plot_cluster_radar",
    "plot_time_heatmap",
]




