"""
Visualization utilities for notebooks and Streamlit.

Common plotting functions for data exploration.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional, List

# Set style
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)


def plot_top_genres(
    df: pd.DataFrame,
    top_n: int = 10,
    time_range: Optional[str] = None,
    figsize: tuple = (10, 6)
) -> plt.Figure:
    """
    Plot top genres bar chart.
    
    Args:
        df: Artists DataFrame
        top_n: Number of top genres to show
        time_range: Filter by time range (optional)
        figsize: Figure size
    
    Returns:
        Matplotlib figure
    """
    df_filtered = df.copy()
    if time_range:
        df_filtered = df_filtered[df_filtered["time_range"] == time_range]
    
    # Explode genres
    genres_list = []
    for genres_str in df_filtered["genres"].dropna():
        if genres_str:
            genres_list.extend([g.strip() for g in genres_str.split(",")])
    
    genre_counts = pd.Series(genres_list).value_counts().head(top_n)
    
    fig, ax = plt.subplots(figsize=figsize)
    genre_counts.plot(kind="barh", ax=ax, color="steelblue")
    ax.set_xlabel("Count")
    ax.set_ylabel("Genre")
    ax.set_title(f"Top {top_n} Genres")
    ax.invert_yaxis()
    plt.tight_layout()
    
    return fig


def plot_top_artists(
    df: pd.DataFrame,
    top_n: int = 10,
    time_range: Optional[str] = None,
    figsize: tuple = (10, 6)
) -> plt.Figure:
    """
    Plot top artists bar chart.
    
    Args:
        df: Artists DataFrame
        top_n: Number of top artists to show
        time_range: Filter by time range (optional)
        figsize: Figure size
    
    Returns:
        Matplotlib figure
    """
    df_filtered = df.copy()
    if time_range:
        df_filtered = df_filtered[df_filtered["time_range"] == time_range]
    
    artist_counts = df_filtered["artist_name"].value_counts().head(top_n)
    
    fig, ax = plt.subplots(figsize=figsize)
    artist_counts.plot(kind="barh", ax=ax, color="coral")
    ax.set_xlabel("Count")
    ax.set_ylabel("Artist")
    ax.set_title(f"Top {top_n} Artists")
    ax.invert_yaxis()
    plt.tight_layout()
    
    return fig


def plot_feature_distribution(
    df: pd.DataFrame,
    feature: str,
    figsize: tuple = (10, 6)
) -> plt.Figure:
    """
    Plot histogram of audio feature distribution.
    
    Args:
        df: Tracks DataFrame
        feature: Feature column name
        figsize: Figure size
    
    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    df[feature].dropna().hist(bins=30, ax=ax, edgecolor="black", alpha=0.7)
    ax.set_xlabel(feature.capitalize())
    ax.set_ylabel("Frequency")
    ax.set_title(f"Distribution of {feature.capitalize()}")
    plt.tight_layout()
    
    return fig


def plot_energy_valence_scatter(
    df: pd.DataFrame,
    color_by: Optional[str] = None,
    figsize: tuple = (10, 8)
) -> plt.Figure:
    """
    Plot energy vs valence scatter plot.
    
    Args:
        df: Tracks DataFrame
        color_by: Column to color by (e.g., 'cluster', 'time_range')
        figsize: Figure size
    
    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    if color_by and color_by in df.columns:
        for value in df[color_by].unique():
            mask = df[color_by] == value
            ax.scatter(
                df.loc[mask, "valence"],
                df.loc[mask, "energy"],
                label=str(value),
                alpha=0.6,
                s=50
            )
        ax.legend()
    else:
        ax.scatter(df["valence"], df["energy"], alpha=0.6, s=50)
    
    ax.set_xlabel("Valence (Positivity)")
    ax.set_ylabel("Energy")
    ax.set_title("Energy vs Valence")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    return fig


def plot_tempo_danceability_scatter(
    df: pd.DataFrame,
    color_by: Optional[str] = None,
    figsize: tuple = (10, 8)
) -> plt.Figure:
    """
    Plot tempo vs danceability scatter plot.
    
    Args:
        df: Tracks DataFrame
        color_by: Column to color by
        figsize: Figure size
    
    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    if color_by and color_by in df.columns:
        for value in df[color_by].unique():
            mask = df[color_by] == value
            ax.scatter(
                df.loc[mask, "danceability"],
                df.loc[mask, "tempo"],
                label=str(value),
                alpha=0.6,
                s=50
            )
        ax.legend()
    else:
        ax.scatter(df["danceability"], df["tempo"], alpha=0.6, s=50)
    
    ax.set_xlabel("Danceability")
    ax.set_ylabel("Tempo (BPM)")
    ax.set_title("Tempo vs Danceability")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    return fig


def plot_cluster_radar(
    df: pd.DataFrame,
    figsize: tuple = (10, 8)
) -> plt.Figure:
    """
    Plot radar chart showing mean features per cluster.
    
    Args:
        df: Tracks DataFrame with cluster assignments
        figsize: Figure size
    
    Returns:
        Matplotlib figure
    """
    feature_cols = ["danceability", "energy", "valence", "acousticness", "tempo"]
    
    # Normalize tempo to 0-1 scale for visualization
    df_normalized = df.copy()
    if "tempo" in df_normalized.columns:
        df_normalized["tempo_normalized"] = (
            (df_normalized["tempo"] - df_normalized["tempo"].min()) /
            (df_normalized["tempo"].max() - df_normalized["tempo"].min())
        )
        feature_cols_plot = ["danceability", "energy", "valence", "acousticness", "tempo_normalized"]
    else:
        feature_cols_plot = [f for f in feature_cols if f in df_normalized.columns]
    
    cluster_means = df_normalized.groupby(["cluster", "mood_label"])[feature_cols_plot].mean()
    
    # Create radar chart using plotly
    fig = go.Figure()
    
    for cluster_id in cluster_means.index.get_level_values(0).unique():
        cluster_data = cluster_means.loc[cluster_id]
        mood_label = cluster_data.index[0] if isinstance(cluster_data.index, pd.Index) else cluster_means.index.get_level_values(1)[0]
        
        # Get values
        values = cluster_data.values.tolist()
        # Close the radar chart
        values = values + [values[0]]
        
        # Feature names
        features = feature_cols_plot + [feature_cols_plot[0]]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=features,
            fill='toself',
            name=f"Cluster {cluster_id}: {mood_label}"
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        title="Cluster Feature Profiles (Radar Chart)"
    )
    
    return fig


def plot_time_heatmap(
    df: pd.DataFrame,
    figsize: tuple = (12, 6)
) -> plt.Figure:
    """
    Plot heatmap of plays by day of week vs hour of day.
    
    Args:
        df: Recently played DataFrame
        figsize: Figure size
    
    Returns:
        Matplotlib figure
    """
    if df.empty or "hour" not in df.columns or "day_of_week_num" not in df.columns:
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, "No recently played data available", 
                ha="center", va="center", fontsize=14)
        return fig
    
    # Create pivot table
    heatmap_data = df.groupby(["day_of_week_num", "hour"]).size().reset_index(name="count")
    pivot = heatmap_data.pivot(index="day_of_week_num", columns="hour", values="count").fillna(0)
    
    # Map day numbers to names
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot.index = [day_names[i] for i in pivot.index]
    
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlOrRd", ax=ax, cbar_kws={"label": "Play Count"})
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Day of Week")
    ax.set_title("Listening Activity Heatmap (Day of Week vs Hour)")
    plt.tight_layout()
    
    return fig


