"""
Data preprocessing module.

Cleans and merges raw Spotify data into structured datasets.
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Data directories
RAW_DATA_DIR = Path("data/raw")
PROCESSED_DATA_DIR = Path("data/processed")
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_raw_json(filename: str) -> List[Dict]:
    """Load raw JSON file."""
    filepath = RAW_DATA_DIR / filename
    if not filepath.exists():
        return []
    
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_track_info(track: Dict) -> Dict:
    """
    Extract relevant fields from Spotify track object.
    
    Args:
        track: Raw track dictionary from API
    
    Returns:
        Flattened track dictionary
    """
    artists = track.get("artists", [])
    artist_names = [a["name"] for a in artists]
    artist_ids = [a["id"] for a in artists]
    album = track.get("album", {})
    
    return {
        "track_id": track.get("id"),
        "track_name": track.get("name"),
        "artist_names": ", ".join(artist_names),
        "artist_ids": ", ".join(artist_ids),
        "primary_artist": artist_names[0] if artist_names else None,
        "album_name": album.get("name"),
        "album_id": album.get("id"),
        "popularity": track.get("popularity"),
        "duration_ms": track.get("duration_ms"),
        "explicit": track.get("explicit", False),
        "preview_url": track.get("preview_url"),
        "external_url": track.get("external_urls", {}).get("spotify"),
    }


def merge_tracks_with_features(
    tracks_data: Dict[str, List[Dict]],
    audio_features: List[Dict]
) -> pd.DataFrame:
    """
    Merge track data with audio features.
    
    Note: Audio features may be empty if the endpoint is unavailable
    (Spotify deprecated /audio-features for new apps in Nov 2024).
    
    Args:
        tracks_data: Dictionary mapping time_range to list of tracks
        audio_features: List of audio feature dictionaries
    
    Returns:
        Combined DataFrame with tracks and features
    """
    # Create features lookup (may be empty if audio features unavailable)
    features_dict = {}
    if audio_features:
        features_dict = {f["id"]: f for f in audio_features if f and f.get("id")}
    else:
        print("  ⚠ No audio features available - tracks will have null audio feature values")
    
    all_tracks = []
    
    for time_range, tracks in tracks_data.items():
        for track in tracks:
            track_info = extract_track_info(track)
            track_info["time_range"] = time_range
            
            # Merge audio features
            track_id = track_info["track_id"]
            if track_id in features_dict:
                features = features_dict[track_id]
                track_info.update({
                    "danceability": features.get("danceability"),
                    "energy": features.get("energy"),
                    "key": features.get("key"),
                    "loudness": features.get("loudness"),
                    "mode": features.get("mode"),
                    "speechiness": features.get("speechiness"),
                    "acousticness": features.get("acousticness"),
                    "instrumentalness": features.get("instrumentalness"),
                    "liveness": features.get("liveness"),
                    "valence": features.get("valence"),
                    "tempo": features.get("tempo"),
                    "duration_ms_feature": features.get("duration_ms"),
                    "time_signature": features.get("time_signature"),
                })
            
            all_tracks.append(track_info)
    
    df = pd.DataFrame(all_tracks)
    return df


def process_artists(artists_data: Dict[str, List[Dict]]) -> pd.DataFrame:
    """
    Process artist data into structured format.
    
    Args:
        artists_data: Dictionary mapping time_range to list of artists
    
    Returns:
        DataFrame with artist information
    """
    all_artists = []
    
    for time_range, artists in artists_data.items():
        for artist in artists:
            artist_info = {
                "artist_id": artist.get("id"),
                "artist_name": artist.get("name"),
                "genres": ", ".join(artist.get("genres", [])),
                "popularity": artist.get("popularity"),
                "followers": artist.get("followers", {}).get("total", 0),
                "external_url": artist.get("external_urls", {}).get("spotify"),
                "time_range": time_range,
            }
            all_artists.append(artist_info)
    
    df = pd.DataFrame(all_artists)
    return df


def process_recently_played(recently_played: List[Dict]) -> pd.DataFrame:
    """
    Process recently played tracks with timestamp parsing.
    
    Args:
        recently_played: List of recently played track dictionaries
    
    Returns:
        DataFrame with timestamp and time-based features
    """
    if not recently_played:
        return pd.DataFrame()
    
    processed = []
    
    for item in recently_played:
        track = item.get("track", {})
        played_at = item.get("played_at")
        
        if not played_at:
            continue
        
        # Parse timestamp
        try:
            dt = datetime.fromisoformat(played_at.replace("Z", "+00:00"))
        except:
            continue
        
        artists = track.get("artists", [])
        artist_names = [a["name"] for a in artists]
        
        processed.append({
            "track_id": track.get("id"),
            "track_name": track.get("name"),
            "artist_names": ", ".join(artist_names),
            "played_at": played_at,
            "date": dt.date(),
            "hour": dt.hour,
            "day_of_week": dt.strftime("%A"),
            "day_of_week_num": dt.weekday(),
        })
    
    df = pd.DataFrame(processed)
    return df


def preprocess_all_data() -> Dict[str, pd.DataFrame]:
    """
    Load raw data and create processed datasets.
    
    Returns:
        Dictionary mapping dataset name to DataFrame
    """
    print("=" * 60)
    print("Starting data preprocessing...")
    print("=" * 60)
    
    # Load raw data
    print("Loading raw data...")
    
    tracks_data = {}
    for time_range in ["short_term", "medium_term", "long_term"]:
        tracks = load_raw_json(f"top_tracks_{time_range}.json")
        if tracks:
            tracks_data[time_range] = tracks
    
    artists_data = {}
    for time_range in ["short_term", "medium_term", "long_term"]:
        artists = load_raw_json(f"top_artists_{time_range}.json")
        if artists:
            artists_data[time_range] = artists
    
    audio_features = load_raw_json("audio_features.json")
    recently_played = load_raw_json("recently_played.json")
    
    # Process tracks
    print("Processing tracks...")
    tracks_df = merge_tracks_with_features(tracks_data, audio_features)
    tracks_path = PROCESSED_DATA_DIR / "tracks.csv"
    tracks_df.to_csv(tracks_path, index=False)
    print(f"  ✓ Saved {len(tracks_df)} tracks to {tracks_path}")
    
    # Process artists
    print("Processing artists...")
    artists_df = process_artists(artists_data)
    artists_path = PROCESSED_DATA_DIR / "artists.csv"
    artists_df.to_csv(artists_path, index=False)
    print(f"  ✓ Saved {len(artists_df)} artist records to {artists_path}")
    
    # Process recently played
    recently_played_df = pd.DataFrame()
    if recently_played:
        print("Processing recently played...")
        recently_played_df = process_recently_played(recently_played)
        if not recently_played_df.empty:
            recently_played_path = PROCESSED_DATA_DIR / "recently_played.csv"
            recently_played_df.to_csv(recently_played_path, index=False)
            print(f"  ✓ Saved {len(recently_played_df)} recently played records to {recently_played_path}")
    
    print("=" * 60)
    print("✓ Preprocessing complete!")
    print("=" * 60)
    
    return {
        "tracks": tracks_df,
        "artists": artists_df,
        "recently_played": recently_played_df
    }


if __name__ == "__main__":
    preprocess_all_data()


