"""
Spotify Listening Insights - Streamlit Dashboard

Interactive dashboard for exploring Spotify listening data.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add src to path for visuals
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.visuals import plot_time_heatmap
import matplotlib.pyplot as plt

# Page config
st.set_page_config(
    page_title="Spotify Listening Insights",
    page_icon="🎵",
    layout="wide"
)

# Data paths
DATA_DIR = Path(__file__).parent.parent / "data" / "processed"
FEATURES_DIR = Path(__file__).parent.parent / "data" / "features"


@st.cache_data
def load_data():
    """Load processed datasets."""
    try:
        tracks_df = pd.read_csv(DATA_DIR / "tracks.csv")
        artists_df = pd.read_csv(DATA_DIR / "artists.csv")
        
        # Try to load recently played (optional)
        recently_played_df = pd.DataFrame()
        recently_played_path = DATA_DIR / "recently_played.csv"
        if recently_played_path.exists():
            recently_played_df = pd.read_csv(recently_played_path)
        
        # Try to load clustered data (optional)
        clustered_df = pd.DataFrame()
        clustered_path = FEATURES_DIR / "tracks_with_clusters.csv"
        if clustered_path.exists():
            clustered_df = pd.read_csv(clustered_path)
        
        return tracks_df, artists_df, recently_played_df, clustered_df
    except FileNotFoundError as e:
        st.error(f"Data files not found. Please run the data pipeline first.\n\nError: {e}")
        st.stop()


def main():
    """Main dashboard application."""
    st.title("🎵 Spotify Listening Insights")
    st.markdown("Explore your Spotify listening habits and discover your music personality!")
    
    # Load data
    tracks_df, artists_df, recently_played_df, clustered_df = load_data()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Choose a section",
        ["Overview", "Genre & Artist Insights", "Audio Feature Profile", "Mood Clusters", "Time Patterns"]
    )
    
    # Overview page
    if page == "Overview":
        st.header("Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            unique_tracks = tracks_df["track_id"].nunique()
            st.metric("Unique Tracks", unique_tracks)
        
        with col2:
            unique_artists = artists_df["artist_id"].nunique()
            st.metric("Unique Artists", unique_artists)
        
        with col3:
            # Count unique genres
            all_genres = []
            for genres_str in artists_df["genres"].dropna():
                if genres_str:
                    all_genres.extend([g.strip() for g in genres_str.split(",")])
            unique_genres = len(set(all_genres))
            st.metric("Unique Genres", unique_genres)
        
        with col4:
            if not clustered_df.empty:
                unique_moods = clustered_df["mood_label"].nunique()
                st.metric("Mood Clusters", unique_moods)
        
        st.markdown("---")
        
        st.subheader("About This Dashboard")
        st.markdown("""
        This dashboard provides insights into your Spotify listening behavior:
        - **Genre & Artist Insights**: Discover your top genres and artists
        - **Audio Feature Profile**: Understand your music preferences through audio features
        - **Mood Clusters**: See how your music is grouped by mood
        - **Time Patterns**: Explore when you listen to music (if recently played data is available)
        """)
    
    # Genre & Artist Insights
    elif page == "Genre & Artist Insights":
        st.header("Genre & Artist Insights")
        
        # Time range filter
        time_range = st.selectbox(
            "Select Time Range",
            ["All", "short_term", "medium_term", "long_term"],
            index=1
        )
        
        # Filter data
        artists_filtered = artists_df.copy()
        if time_range != "All":
            artists_filtered = artists_filtered[artists_filtered["time_range"] == time_range]
        
        # Top Genres
        st.subheader("Top Genres")
        
        # Explode genres
        genres_list = []
        for genres_str in artists_filtered["genres"].dropna():
            if genres_str:
                genres_list.extend([g.strip() for g in genres_str.split(",")])
        
        genre_counts = pd.Series(genres_list).value_counts().head(15)
        
        fig_genres = px.bar(
            x=genre_counts.values,
            y=genre_counts.index,
            orientation='h',
            labels={"x": "Count", "y": "Genre"},
            title="Top 15 Genres"
        )
        fig_genres.update_layout(height=500)
        st.plotly_chart(fig_genres, use_container_width=True)
        
        # Top Artists
        st.subheader("Top Artists")
        
        artist_counts = artists_filtered["artist_name"].value_counts().head(15)
        
        fig_artists = px.bar(
            x=artist_counts.values,
            y=artist_counts.index,
            orientation='h',
            labels={"x": "Count", "y": "Artist"},
            title="Top 15 Artists"
        )
        fig_artists.update_layout(height=500)
        st.plotly_chart(fig_artists, use_container_width=True)
    
    # Audio Feature Profile
    elif page == "Audio Feature Profile":
        st.header("Your Music Profile")
        
        # Time range filter
        time_range = st.selectbox(
            "Select Time Range",
            ["All", "short_term", "medium_term", "long_term"],
            index=1
        )
        
        # Filter tracks
        tracks_filtered = tracks_df.copy()
        if time_range != "All":
            tracks_filtered = tracks_filtered[tracks_filtered["time_range"] == time_range]
        
        # Calculate averages
        feature_cols = ["danceability", "energy", "valence", "acousticness", "tempo"]
        available_features = [f for f in feature_cols if f in tracks_filtered.columns]
        
        if available_features:
            avg_features = tracks_filtered[available_features].mean()
            
            # Normalize tempo for radar chart (0-1 scale)
            features_for_radar = avg_features.copy()
            if "tempo" in features_for_radar.index:
                # Normalize tempo (assuming range 60-180 BPM)
                tempo_min, tempo_max = 60, 180
                features_for_radar["tempo"] = (features_for_radar["tempo"] - tempo_min) / (tempo_max - tempo_min)
                features_for_radar["tempo"] = max(0, min(1, features_for_radar["tempo"]))
            
            # Radar chart
            st.subheader("Average Audio Features (Radar Chart)")
            
            fig_radar = go.Figure()
            
            # Prepare data for radar (close the loop)
            categories = list(features_for_radar.index)
            values = list(features_for_radar.values)
            categories.append(categories[0])
            values.append(values[0])
            
            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Your Profile'
            ))
            
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                showlegend=True,
                height=500
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
            
            # Feature distributions
            st.subheader("Feature Distributions")
            
            selected_feature = st.selectbox("Select Feature", available_features)
            
            fig_dist = px.histogram(
                tracks_filtered,
                x=selected_feature,
                nbins=30,
                title=f"Distribution of {selected_feature.capitalize()}"
            )
            st.plotly_chart(fig_dist, use_container_width=True)
            
            # Scatter plots
            col1, col2 = st.columns(2)
            
            with col1:
                fig_scatter1 = px.scatter(
                    tracks_filtered,
                    x="valence",
                    y="energy",
                    color="time_range" if "time_range" in tracks_filtered.columns else None,
                    title="Energy vs Valence",
                    labels={"valence": "Valence (Positivity)", "energy": "Energy"}
                )
                st.plotly_chart(fig_scatter1, use_container_width=True)
            
            with col2:
                if "tempo" in tracks_filtered.columns and "danceability" in tracks_filtered.columns:
                    fig_scatter2 = px.scatter(
                        tracks_filtered,
                        x="danceability",
                        y="tempo",
                        color="time_range" if "time_range" in tracks_filtered.columns else None,
                        title="Tempo vs Danceability",
                        labels={"danceability": "Danceability", "tempo": "Tempo (BPM)"}
                    )
                    st.plotly_chart(fig_scatter2, use_container_width=True)
    
    # Mood Clusters
    elif page == "Mood Clusters":
        st.header("Mood Clusters")
        
        if clustered_df.empty:
            st.warning("Clustered data not found. Please run the clustering notebook first (03_mood_clustering.ipynb).")
        else:
            # Cluster distribution
            st.subheader("Cluster Distribution")
            
            cluster_counts = clustered_df["mood_label"].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_pie = px.pie(
                    values=cluster_counts.values,
                    names=cluster_counts.index,
                    title="Mood Cluster Distribution"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                fig_bar = px.bar(
                    x=cluster_counts.index,
                    y=cluster_counts.values,
                    labels={"x": "Mood Cluster", "y": "Number of Tracks"},
                    title="Mood Cluster Counts"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Cluster features radar
            st.subheader("Cluster Feature Profiles")
            
            feature_cols = ["danceability", "energy", "valence", "acousticness", "tempo"]
            available_features = [f for f in feature_cols if f in clustered_df.columns]
            
            if available_features:
                # Normalize tempo
                clustered_normalized = clustered_df.copy()
                if "tempo" in clustered_normalized.columns:
                    tempo_min = clustered_normalized["tempo"].min()
                    tempo_max = clustered_normalized["tempo"].max()
                    clustered_normalized["tempo_normalized"] = (
                        (clustered_normalized["tempo"] - tempo_min) / (tempo_max - tempo_min)
                    )
                    available_features_plot = [f for f in available_features if f != "tempo"] + ["tempo_normalized"]
                else:
                    available_features_plot = available_features
                
                cluster_means = clustered_normalized.groupby(["cluster", "mood_label"])[available_features_plot].mean()
                
                fig_radar = go.Figure()
                
                for cluster_id in cluster_means.index.get_level_values(0).unique():
                    cluster_data = cluster_means.loc[cluster_id]
                    mood_label = cluster_means.index.get_level_values(1)[cluster_means.index.get_level_values(0) == cluster_id][0]
                    
                    values = cluster_data.values.tolist()
                    values = values + [values[0]]  # Close the loop
                    
                    features_plot = list(available_features_plot) + [available_features_plot[0]]
                    
                    fig_radar.add_trace(go.Scatterpolar(
                        r=values,
                        theta=features_plot,
                        fill='toself',
                        name=f"Cluster {cluster_id}: {mood_label}"
                    ))
                
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                    showlegend=True,
                    height=600
                )
                
                st.plotly_chart(fig_radar, use_container_width=True)
            
            # Explore tracks by cluster
            st.subheader("Explore Tracks by Cluster")
            
            selected_cluster = st.selectbox(
                "Select Mood Cluster",
                sorted(clustered_df["mood_label"].unique())
            )
            
            cluster_tracks = clustered_df[clustered_df["mood_label"] == selected_cluster]
            
            st.write(f"**{len(cluster_tracks)} tracks** in this cluster")
            
            # Display tracks
            display_cols = ["track_name", "primary_artist", "energy", "valence", "danceability"]
            available_display_cols = [c for c in display_cols if c in cluster_tracks.columns]
            
            st.dataframe(
                cluster_tracks[available_display_cols].head(20),
                use_container_width=True
            )
    
    # Time Patterns
    elif page == "Time Patterns":
        st.header("Time-of-Day Patterns")
        
        if recently_played_df.empty:
            st.warning("Recently played data not available. This section requires recently played tracks from the Spotify API.")
        else:
            # Heatmap
            st.subheader("Listening Activity Heatmap")
            
            if "hour" in recently_played_df.columns and "day_of_week_num" in recently_played_df.columns:
                heatmap_data = recently_played_df.groupby(["day_of_week_num", "hour"]).size().reset_index(name="count")
                pivot = heatmap_data.pivot(index="day_of_week_num", columns="hour", values="count").fillna(0)
                
                day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                pivot.index = [day_names[i] for i in pivot.index]
                
                fig_heatmap = px.imshow(
                    pivot,
                    labels=dict(x="Hour of Day", y="Day of Week", color="Play Count"),
                    title="Listening Activity by Day and Hour",
                    aspect="auto"
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)
            
            # Average features by time of day
            st.subheader("Average Features by Hour of Day")
            
            if "hour" in recently_played_df.columns:
                # Merge with tracks to get audio features
                if "track_id" in recently_played_df.columns:
                    merged = recently_played_df.merge(
                        tracks_df[["track_id", "energy", "valence", "danceability"]],
                        on="track_id",
                        how="left"
                    )
                    
                    hourly_features = merged.groupby("hour")[["energy", "valence", "danceability"]].mean()
                    
                    fig_hourly = px.line(
                        hourly_features,
                        title="Average Audio Features by Hour of Day",
                        labels={"value": "Feature Value", "index": "Hour of Day"}
                    )
                    st.plotly_chart(fig_hourly, use_container_width=True)


if __name__ == "__main__":
    main()


