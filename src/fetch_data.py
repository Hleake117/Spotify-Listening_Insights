"""
Data fetching orchestration module.

Fetches data from Spotify API and saves raw data to disk.
"""

import os
import json
import pandas as pd
from typing import List, Dict
from pathlib import Path

from .api_client import SpotifyAPIClient


# Data directories
RAW_DATA_DIR = Path("data/raw")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


def fetch_top_tracks(time_ranges: List[str] = None) -> Dict[str, List[Dict]]:
    """
    Fetch top tracks for specified time ranges.
    
    Args:
        time_ranges: List of time ranges ('short_term', 'medium_term', 'long_term')
                    Defaults to all three
    
    Returns:
        Dictionary mapping time_range to list of tracks
    """
    if time_ranges is None:
        time_ranges = ["short_term", "medium_term", "long_term"]
    
    client = SpotifyAPIClient()
    all_tracks = {}
    
    for time_range in time_ranges:
        print(f"Fetching top tracks ({time_range})...")
        tracks = client.get_top_tracks(time_range=time_range, limit=50)
        all_tracks[time_range] = tracks
        
        # Save raw JSON
        json_path = RAW_DATA_DIR / f"top_tracks_{time_range}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(tracks, f, indent=2, ensure_ascii=False)
        
        # Also save as CSV for easy inspection
        df = pd.DataFrame(tracks)
        csv_path = RAW_DATA_DIR / f"top_tracks_{time_range}.csv"
        df.to_csv(csv_path, index=False)
        
        print(f"  ✓ Saved {len(tracks)} tracks to {json_path}")
    
    return all_tracks


def fetch_top_artists(time_ranges: List[str] = None) -> Dict[str, List[Dict]]:
    """
    Fetch top artists for specified time ranges.
    
    Args:
        time_ranges: List of time ranges ('short_term', 'medium_term', 'long_term')
                    Defaults to all three
    
    Returns:
        Dictionary mapping time_range to list of artists
    """
    if time_ranges is None:
        time_ranges = ["short_term", "medium_term", "long_term"]
    
    client = SpotifyAPIClient()
    all_artists = {}
    
    for time_range in time_ranges:
        print(f"Fetching top artists ({time_range})...")
        artists = client.get_top_artists(time_range=time_range, limit=50)
        all_artists[time_range] = artists
        
        # Save raw JSON
        json_path = RAW_DATA_DIR / f"top_artists_{time_range}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(artists, f, indent=2, ensure_ascii=False)
        
        # Also save as CSV
        df = pd.DataFrame(artists)
        csv_path = RAW_DATA_DIR / f"top_artists_{time_range}.csv"
        df.to_csv(csv_path, index=False)
        
        print(f"  ✓ Saved {len(artists)} artists to {json_path}")
    
    return all_artists


def fetch_audio_features(track_ids: List[str]) -> List[Dict]:
    """
    Fetch audio features for given track IDs.
    
    Args:
        track_ids: List of Spotify track IDs
    
    Returns:
        List of audio feature dictionaries
    """
    if not track_ids:
        print("No track IDs provided. Skipping audio features.")
        return []
    
    client = SpotifyAPIClient()
    
    print(f"Fetching audio features for {len(track_ids)} tracks...")
    features = client.get_audio_features_for_tracks(track_ids)
    
    # Save raw JSON
    json_path = RAW_DATA_DIR / "audio_features.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(features, f, indent=2, ensure_ascii=False)
    
    # Also save as CSV
    df = pd.DataFrame(features)
    csv_path = RAW_DATA_DIR / "audio_features.csv"
    df.to_csv(csv_path, index=False)
    
    print(f"  ✓ Saved {len(features)} audio features to {json_path}")
    
    return features


def fetch_recently_played(limit: int = 50) -> List[Dict]:
    """
    Fetch recently played tracks.
    
    Args:
        limit: Number of tracks to fetch (max 50)
    
    Returns:
        List of recently played track dictionaries
    """
    client = SpotifyAPIClient()
    
    print(f"Fetching {limit} recently played tracks...")
    recently_played = client.get_recently_played(limit=limit)
    
    # Save raw JSON
    json_path = RAW_DATA_DIR / "recently_played.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(recently_played, f, indent=2, ensure_ascii=False)
    
    # Also save as CSV
    df = pd.DataFrame(recently_played)
    csv_path = RAW_DATA_DIR / "recently_played.csv"
    df.to_csv(csv_path, index=False)
    
    print(f"  ✓ Saved {len(recently_played)} recently played tracks to {json_path}")
    
    return recently_played


def fetch_all_data(
    time_ranges: List[str] = None,
    include_recently_played: bool = True,
    recently_played_limit: int = 50
) -> Dict:
    """
    Orchestrate fetching all data from Spotify API.
    
    Args:
        time_ranges: List of time ranges to fetch (defaults to all three)
        include_recently_played: Whether to fetch recently played tracks
        recently_played_limit: Limit for recently played tracks
    
    Returns:
        Dictionary containing all fetched data
    """
    print("=" * 60)
    print("Starting Spotify data fetch...")
    print("=" * 60)
    
    # Fetch top tracks
    tracks_data = fetch_top_tracks(time_ranges)
    
    # Collect all unique track IDs
    all_track_ids = set()
    for tracks in tracks_data.values():
        for track in tracks:
            all_track_ids.add(track["id"])
    
    # Fetch audio features for all tracks
    # NOTE: Spotify deprecated /audio-features endpoint for new apps (Nov 2024)
    # This will likely fail with 403 for new applications
    print("\n⚠ Note: Audio features endpoint may be unavailable for new Spotify apps.")
    print("  Spotify deprecated this endpoint on Nov 27, 2024 for new applications.")
    print("  The pipeline will continue without audio features if this fails.\n")
    
    try:
        audio_features = fetch_audio_features(list(all_track_ids))
        if not audio_features:
            print("  ⚠ No audio features retrieved. Continuing without them.")
    except Exception as e:
        print(f"  ⚠ Could not fetch audio features: {type(e).__name__}")
        print("  Continuing without audio features. You can still analyze tracks and artists.")
        audio_features = []
    
    # Fetch top artists
    artists_data = fetch_top_artists(time_ranges)
    
    # Fetch recently played (optional)
    recently_played = None
    if include_recently_played:
        recently_played = fetch_recently_played(limit=recently_played_limit)
    
    print("=" * 60)
    print("✓ Data fetch complete!")
    print("=" * 60)
    
    return {
        "tracks": tracks_data,
        "artists": artists_data,
        "audio_features": audio_features,
        "recently_played": recently_played
    }


if __name__ == "__main__":
    # Script entry point for direct execution
    from .auth import authenticate, load_tokens
    
    # Check if tokens exist
    if not load_tokens():
        print("No tokens found. Starting authentication...")
        authenticate()
    
    # Fetch all data
    fetch_all_data()


