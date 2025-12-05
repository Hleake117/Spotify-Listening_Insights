# 🎵 Spotify Listening Insights

A data analytics project that analyzes your Spotify listening behavior using the Spotify Web API. Discover your music personality, explore mood clusters, and visualize your listening patterns through an interactive Streamlit dashboard.

## What It Does

Spotify Listening Insights helps you understand your music preferences by:

- **Analyzing your top tracks and artists** across different time periods (short-term, medium-term, long-term)
- **Extracting audio features** (danceability, energy, valence, tempo, etc.) from your favorite songs
- **Identifying mood clusters** using machine learning (KMeans clustering) to group your music by emotional characteristics
- **Visualizing patterns** through interactive charts and dashboards
- **Exploring time-based insights** (when you listen to music, if recently played data is available)

## Tech Stack

- **Python 3.8+**
- **Spotify Web API** (via `spotipy` library)
- **pandas** - Data manipulation and analysis
- **numpy** - Numerical computations
- **matplotlib & seaborn** - Static visualizations
- **plotly** - Interactive visualizations
- **scikit-learn** - Machine learning (KMeans clustering)
- **streamlit** - Interactive dashboard
- **python-dotenv** - Environment variable management
- **jupyter** - Notebooks for analysis

## Project Structure

```
Spotify Listening Insights/
├── data/
│   ├── raw/              # Raw API responses (JSON/CSV)
│   ├── processed/        # Cleaned datasets (tracks.csv, artists.csv)
│   └── features/         # Clustered data (tracks_with_clusters.csv)
├── notebooks/
│   ├── 01_fetch_and_preprocess.ipynb    # Data pipeline
│   ├── 02_exploratory_analysis.ipynb    # EDA
│   └── 03_mood_clustering.ipynb         # Clustering analysis
├── src/
│   ├── auth.py           # Spotify OAuth authentication
│   ├── api_client.py     # Spotify API wrapper
│   ├── fetch_data.py     # Data fetching orchestration
│   ├── preprocess.py     # Data cleaning and merging
│   ├── features.py       # Feature engineering and clustering
│   └── visuals.py        # Plotting utilities
├── streamlit_app/
│   └── app.py            # Streamlit dashboard
├── requirements.txt
└── README.md
```

## Setup

### 1. Create a Spotify Developer App

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create an App"
4. Fill in app details (name, description)
5. Once created, note your **Client ID** and **Client Secret**
6. Click "Edit Settings" and add a redirect URI:
   - `http://localhost:8888/callback` (for local development)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```

**Important**: The `.env` file is already in `.gitignore` to keep your credentials safe.

### 4. Run the Data Pipeline

#### Option A: Using Jupyter Notebooks (Recommended)

1. Start Jupyter:
   ```bash
   jupyter notebook
   ```

2. Open `notebooks/01_fetch_and_preprocess.ipynb`
3. Run the cells to:
   - Authenticate with Spotify (first time only)
   - Fetch your top tracks, artists, and audio features
   - Preprocess and save cleaned data

4. Run `notebooks/02_exploratory_analysis.ipynb` for EDA

5. Run `notebooks/03_mood_clustering.ipynb` to perform clustering

#### Option B: Using Python Scripts

```bash
# Authenticate (first time only)
python -c "from src.auth import authenticate; authenticate()"

# Fetch data
python -m src.fetch_data

# Preprocess data
python -m src.preprocess

# Perform clustering
python -m src.features
```

### 5. Launch the Streamlit Dashboard

```bash
streamlit run streamlit_app/app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## Usage

### Dashboard Sections

1. **Overview**: Key statistics about your listening data
2. **Genre & Artist Insights**: Top genres and artists with time range filters
3. **Audio Feature Profile**: Radar charts and distributions of audio features
4. **Mood Clusters**: Explore your music grouped by mood (requires clustering to be run first)
5. **Time Patterns**: Listening activity heatmaps and time-based patterns (requires recently played data)

### Data Pipeline

The project follows a reproducible data pipeline:

1. **Fetch** → Get data from Spotify API, save to `data/raw/`
2. **Preprocess** → Clean and merge data, save to `data/processed/`
3. **Analyze** → Perform EDA and clustering, save to `data/features/`
4. **Visualize** → Explore results in Streamlit dashboard

## Types of Insights

- **Genre Analysis**: Discover your most-listened genres
- **Artist Preferences**: See your top artists across different time periods
- **Audio Feature Profile**: Understand your music taste through technical features
- **Mood Clusters**: Identify emotional patterns in your music (e.g., "High-Energy Hype", "Chill / Acoustic", "Melancholy / Low Energy")
- **Time Patterns**: Explore when you listen to music (if recently played data is available)

## Future Improvements

- **Automatic Syncing**: Schedule periodic data updates
- **Playlist Generation**: Create playlists based on mood clusters
- **Multi-User Mode**: Compare profiles with friends
- **Advanced Analytics**: Trend analysis, genre evolution over time
- **Export Features**: Export insights as PDF reports
- **Production Deployment**: Deploy dashboard with full OAuth flow

## Notes

- This is an MVP focused on personal use and local development
- All data is stored locally (not in a database)
- Authentication tokens are stored in `data/token.json` (already in `.gitignore`)
- The dashboard reads from processed data files, not live API calls

## License

This project is for personal/portfolio use. Make sure to comply with Spotify's API Terms of Service.

## Credits

Built with the [Spotify Web API](https://developer.spotify.com/documentation/web-api).




