"""
Spotify Web API client wrapper.

Handles API calls with automatic token management, pagination, and basic retry logic.
"""

import time
from typing import List, Dict, Optional
import spotipy
from spotipy.exceptions import SpotifyException

from .auth import get_valid_token, get_client_credentials


class SpotifyAPIClient:
    """
    Wrapper around spotipy client with custom token management.
    """
    
    def __init__(self):
        """Initialize client with token management."""
        self._access_token = None
        self._spotipy_client = None
    
    def _get_client(self):
        """Get or create spotipy client with valid token."""
        if self._spotipy_client is None or self._access_token != get_valid_token():
            self._access_token = get_valid_token()
            client_id, client_secret, redirect_uri = get_client_credentials()
            
            # Create OAuth manager (we'll use token directly)
            self._spotipy_client = spotipy.Spotify(auth=self._access_token)
        
        return self._spotipy_client
    
    def _retry_request(self, func, max_retries: int = 3, delay: float = 1.0):
        """
        Retry API request with exponential backoff.
        
        Args:
            func: Function to retry (should be API call)
            max_retries: Maximum number of retry attempts
            delay: Initial delay in seconds
        
        Returns:
            Result from function
        
        Raises:
            SpotifyException: If all retries fail
        """
        for attempt in range(max_retries):
            try:
                return func()
            except SpotifyException as e:
                if e.http_status == 429:  # Rate limited
                    retry_after = int(e.headers.get("Retry-After", delay))
                    if attempt < max_retries - 1:
                        print(f"Rate limited. Waiting {retry_after} seconds...")
                        time.sleep(retry_after)
                        continue
                elif e.http_status >= 500:  # Server error
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)
                        print(f"Server error. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                raise
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = delay * (2 ** attempt)
                    print(f"Error: {e}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise
        
        raise Exception("Max retries exceeded")
    
    def get_top_tracks(
        self, 
        time_range: str = "medium_term", 
        limit: int = 50
    ) -> List[Dict]:
        """
        Get user's top tracks.
        
        Args:
            time_range: 'short_term', 'medium_term', or 'long_term'
            limit: Number of tracks (max 50 per request)
        
        Returns:
            List of track dictionaries
        """
        client = self._get_client()
        
        def _fetch():
            results = client.current_user_top_tracks(
                time_range=time_range,
                limit=limit
            )
            tracks = results.get("items", [])
            
            # Handle pagination
            while results.get("next"):
                results = client.next(results)
                tracks.extend(results.get("items", []))
            
            return tracks
        
        return self._retry_request(_fetch)
    
    def get_top_artists(
        self, 
        time_range: str = "medium_term", 
        limit: int = 50
    ) -> List[Dict]:
        """
        Get user's top artists.
        
        Args:
            time_range: 'short_term', 'medium_term', or 'long_term'
            limit: Number of artists (max 50 per request)
        
        Returns:
            List of artist dictionaries
        """
        client = self._get_client()
        
        def _fetch():
            results = client.current_user_top_artists(
                time_range=time_range,
                limit=limit
            )
            artists = results.get("items", [])
            
            # Handle pagination
            while results.get("next"):
                results = client.next(results)
                artists.extend(results.get("items", []))
            
            return artists
        
        return self._retry_request(_fetch)
    
    def get_audio_features_for_tracks(self, track_ids: List[str]) -> List[Dict]:
        """
        Get audio features for multiple tracks.
        
        Args:
            track_ids: List of Spotify track IDs
        
        Returns:
            List of audio feature dictionaries
        """
        client = self._get_client()
        
        # Try smaller batches due to potential API restrictions
        # Use batches of 20 to avoid URL length and rate limit issues
        all_features = []
        
        for i in range(0, len(track_ids), 20):
            batch = track_ids[i:i + 20]
            
            def _fetch_batch():
                try:
                    return client.audio_features(batch)
                except Exception as e:
                    # If batch fails, try individual requests
                    print(f"  Batch failed, trying individual requests for {len(batch)} tracks...")
                    individual_features = []
                    for track_id in batch:
                        try:
                            time.sleep(0.1)  # Small delay between requests
                            feat = client.audio_features([track_id])
                            if feat and feat[0]:
                                individual_features.append(feat[0])
                        except:
                            pass
                    return individual_features
            
            features = self._retry_request(_fetch_batch)
            # Filter out None values (invalid track IDs)
            all_features.extend([f for f in features if f is not None])
            
            # Small delay between batches to avoid rate limiting
            if i + 20 < len(track_ids):
                time.sleep(0.2)
        
        return all_features
    
    def get_recently_played(self, limit: int = 50) -> List[Dict]:
        """
        Get user's recently played tracks.
        
        Args:
            limit: Number of tracks (max 50 per request)
        
        Returns:
            List of recently played track dictionaries with 'played_at' timestamp
        """
        client = self._get_client()
        
        def _fetch():
            results = client.current_user_recently_played(limit=limit)
            return results.get("items", [])
        
        return self._retry_request(_fetch)
    
    def get_track_info(self, track_id: str) -> Dict:
        """
        Get detailed track information.
        
        Args:
            track_id: Spotify track ID
        
        Returns:
            Track dictionary with full details
        """
        client = self._get_client()
        
        def _fetch():
            return client.track(track_id)
        
        return self._retry_request(_fetch)

