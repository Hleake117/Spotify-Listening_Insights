# Audio Features Endpoint Limitation

## Important Notice

**Spotify deprecated the `/v1/audio-features` endpoint for new applications as of November 27, 2024.**

This means that applications created after this date will receive a `403 Forbidden` error when attempting to access audio features.

## Impact on This Project

The following features require audio features and **will not work** for new Spotify apps:

- Audio feature analysis (danceability, energy, valence, etc.)
- Mood clustering based on audio features
- Audio feature visualizations in the dashboard

## What Still Works

Even without audio features, you can still:

- ✅ Analyze your top tracks and artists
- ✅ Explore genre distributions
- ✅ View listening patterns (if recently played data is available)
- ✅ See track popularity and basic metadata

## Potential Solutions

1. **Request Access**: Contact Spotify Developer Support to request access to the audio features endpoint (may require justification)

2. **Use Alternative Data**: Some third-party services provide audio analysis, though they may have limitations

3. **Focus on Available Data**: The project is designed to work with or without audio features - you can still get valuable insights from your listening patterns

## Current Status

The code is designed to handle this gracefully:
- The pipeline will continue even if audio features fail to fetch
- Clustering will show a clear error message if attempted without audio features
- The dashboard will work but with limited functionality

## References

- [Spotify Community Discussion](https://community.spotify.com/t5/Spotify-for-Developers/Web-API-Get-Track-s-Audio-Features-403-error/td-p/6654507)

