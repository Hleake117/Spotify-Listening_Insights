"""
Spotify OAuth authentication module.

Handles Authorization Code Flow for Spotify Web API.
Supports both script-based and notebook-friendly authentication.
"""

import os
import json
import time
import webbrowser
from urllib.parse import urlencode, parse_qs, urlparse
from typing import Optional, Dict, Tuple
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Spotify OAuth endpoints
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

# Required scopes
SCOPES = [
    "user-top-read",
    "user-read-recently-played",
    "user-library-read"
]

# Token storage path
TOKEN_FILE = "data/token.json"


def get_client_credentials() -> Tuple[str, str, str]:
    """
    Load Spotify client credentials from environment variables.
    
    Returns:
        Tuple of (client_id, client_secret, redirect_uri)
    
    Raises:
        ValueError: If required environment variables are missing
    """
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")
    
    if not client_id or not client_secret:
        raise ValueError(
            "Missing Spotify credentials. Please set SPOTIFY_CLIENT_ID and "
            "SPOTIFY_CLIENT_SECRET in your .env file or environment variables."
        )
    
    return client_id, client_secret, redirect_uri


def build_auth_url(state: Optional[str] = None) -> str:
    """
    Build the Spotify authorization URL.
    
    Args:
        state: Optional state parameter for security (not used in MVP)
    
    Returns:
        Authorization URL string
    """
    client_id, _, redirect_uri = get_client_credentials()
    
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": " ".join(SCOPES),
        "show_dialog": "false"
    }
    
    if state:
        params["state"] = state
    
    return f"{SPOTIFY_AUTH_URL}?{urlencode(params)}"


def exchange_code_for_token(auth_code: str) -> Dict:
    """
    Exchange authorization code for access and refresh tokens.
    
    Args:
        auth_code: Authorization code from redirect URL
    
    Returns:
        Dictionary containing tokens and metadata
    """
    client_id, client_secret, redirect_uri = get_client_credentials()
    
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": redirect_uri
    }
    
    response = requests.post(
        SPOTIFY_TOKEN_URL,
        data=data,
        auth=(client_id, client_secret),
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    response.raise_for_status()
    token_data = response.json()
    
    # Add timestamp for expiration tracking
    token_data["expires_at"] = time.time() + token_data.get("expires_in", 3600)
    
    return token_data


def extract_code_from_url(redirect_url: str) -> str:
    """
    Extract authorization code from redirect URL.
    
    Args:
        redirect_url: Full redirect URL from Spotify
    
    Returns:
        Authorization code string
    
    Raises:
        ValueError: If code not found in URL
    """
    parsed = urlparse(redirect_url)
    query_params = parse_qs(parsed.query)
    
    if "code" not in query_params:
        if "error" in query_params:
            error = query_params["error"][0]
            raise ValueError(f"Authorization failed: {error}")
        raise ValueError("No authorization code found in redirect URL")
    
    return query_params["code"][0]


def save_tokens(token_data: Dict, filepath: str = TOKEN_FILE) -> None:
    """
    Save tokens to JSON file.
    
    Args:
        token_data: Token dictionary from Spotify
        filepath: Path to save tokens
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, "w") as f:
        json.dump(token_data, f, indent=2)


def load_tokens(filepath: str = TOKEN_FILE) -> Optional[Dict]:
    """
    Load tokens from JSON file.
    
    Args:
        filepath: Path to token file
    
    Returns:
        Token dictionary or None if file doesn't exist
    """
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def is_token_expired(token_data: Dict) -> bool:
    """
    Check if access token is expired.
    
    Args:
        token_data: Token dictionary
    
    Returns:
        True if expired or expires within 60 seconds
    """
    expires_at = token_data.get("expires_at", 0)
    return time.time() >= (expires_at - 60)  # Refresh 60s before expiry


def refresh_access_token(refresh_token: str) -> Dict:
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_token: Refresh token from stored credentials
    
    Returns:
        Updated token dictionary
    """
    client_id, client_secret, _ = get_client_credentials()
    
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    response = requests.post(
        SPOTIFY_TOKEN_URL,
        data=data,
        auth=(client_id, client_secret),
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    response.raise_for_status()
    token_data = response.json()
    
    # Preserve refresh token if not returned
    if "refresh_token" not in token_data:
        token_data["refresh_token"] = refresh_token
    
    # Update expiration
    token_data["expires_at"] = time.time() + token_data.get("expires_in", 3600)
    
    return token_data


def get_valid_token() -> str:
    """
    Get a valid access token, refreshing if necessary.
    
    Returns:
        Valid access token string
    
    Raises:
        ValueError: If no tokens available or refresh fails
    """
    token_data = load_tokens()
    
    if not token_data:
        raise ValueError(
            "No tokens found. Please run authenticate() first to obtain tokens."
        )
    
    # Check if token needs refresh
    if is_token_expired(token_data):
        if "refresh_token" not in token_data:
            raise ValueError("Token expired and no refresh token available.")
        
        try:
            token_data = refresh_access_token(token_data["refresh_token"])
            save_tokens(token_data)
        except requests.RequestException as e:
            raise ValueError(f"Failed to refresh token: {e}")
    
    return token_data["access_token"]


def authenticate(interactive: bool = True) -> Dict:
    """
    Complete OAuth flow to obtain tokens.
    
    Two modes:
    1. Interactive (default): Opens browser, user authorizes, extracts code
    2. Non-interactive: Prints URL, waits for user to paste redirect URL
    
    Args:
        interactive: If True, opens browser. If False, prints URL for manual copy.
    
    Returns:
        Token dictionary
    """
    auth_url = build_auth_url()
    
    if interactive:
        print("Opening browser for Spotify authorization...")
        webbrowser.open(auth_url)
        print("\nAfter authorizing, paste the full redirect URL here:")
    else:
        print("\nPlease visit this URL to authorize:")
        print(auth_url)
        print("\nAfter authorizing, paste the full redirect URL here:")
    
    redirect_url = input("Redirect URL: ").strip()
    
    try:
        auth_code = extract_code_from_url(redirect_url)
        token_data = exchange_code_for_token(auth_code)
        save_tokens(token_data)
        print("\n✓ Authentication successful! Tokens saved.")
        return token_data
    except Exception as e:
        print(f"\n✗ Authentication failed: {e}")
        raise


