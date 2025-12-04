#!/usr/bin/env python3
"""
Quick authentication script for Spotify.
Run this in your terminal to authenticate.
"""

from src.auth import authenticate, load_tokens

if __name__ == "__main__":
    # Check if tokens already exist
    tokens = load_tokens()
    
    if tokens:
        print("✓ Tokens already exist!")
        print("If you need to re-authenticate, delete data/token.json first.")
    else:
        print("Starting Spotify authentication...")
        print("=" * 60)
        authenticate(interactive=True)
        print("=" * 60)
        print("✓ Authentication complete!")

