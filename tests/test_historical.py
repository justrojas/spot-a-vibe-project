import sys
import os
import json
import pandas as pd
from datetime import datetime
import logging
from pathlib import Path

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.spotify_client import SpotifyClient
from src.analyzer import MusicAnalyzer

def test_historical_data():
    """Analyze historical Spotify listening data."""
    client = SpotifyClient()
    analyzer = MusicAnalyzer()
    
    print("\n🎵 SPOTIFY HISTORICAL ANALYSIS")
    print("=" * 50)
    
    # Load all JSON files from the history directory
    history_data = []
    history_dir = Path('data/history')
    
    print("\n📂 Loading Data Files")
    print("-" * 20)
    
    for json_file in history_dir.glob('*.json'):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                history_data.extend(data)
                print(f"Loaded {len(data)} entries from {json_file.name}")
        except Exception as e:
            print(f"Error loading {json_file.name}: {e}")
            continue
    
    if not history_data:
        print("No historical data found!")
        return
    
    # Convert to DataFrame and clean data
    df = pd.DataFrame(history_data)
    
    # Basic data cleanup
    df['ts'] = pd.to_datetime(df['ts'])
    df['year'] = df['ts'].dt.year
    df['month'] = df['ts'].dt.month
    df['hour'] = df['ts'].dt.hour
    
    # Remove podcasts and empty tracks
    music_df = df[
        df['master_metadata_track_name'].notna() & 
        (df['episode_name'].isna()) &
        (df['ms_played'] > 30000)  # Filter out skipped tracks (less than 30 seconds)
    ].copy()
    
    # Print overall statistics
    print("\n📊 OVERALL STATISTICS")
    print("-" * 20)
    total_hours = music_df['ms_played'].sum() / (1000 * 60 * 60)
    print(f"Total Listening Time: {total_hours:.1f} hours")
    print(f"Total Tracks Played: {len(music_df):,}")
    print(f"Date Range: {music_df['ts'].min():%Y-%m-%d} to {music_df['ts'].max():%Y-%m-%d}")
    
    # Yearly breakdown
    print("\n📅 YEARLY BREAKDOWN")
    print("-" * 20)
    yearly_stats = music_df.groupby('year').agg({
        'master_metadata_track_name': 'count',
        'master_metadata_album_artist_name': 'nunique',
        'ms_played': lambda x: round(x.sum() / (1000 * 60 * 60), 1)
    }).round(1)
    
    yearly_stats.columns = ['Tracks Played', 'Unique Artists', 'Hours Listened']
    print(yearly_stats.to_string())
    
    # Top artists by year
    print("\n🎤 TOP ARTISTS BY YEAR")
    print("-" * 20)
    for year in sorted(music_df['year'].unique()):
        year_df = music_df[music_df['year'] == year]
        top_artists = year_df['master_metadata_album_artist_name'].value_counts().head(5)
        
        print(f"\n{year}:")
        for artist, count in top_artists.items():
            print(f"  {artist:<30} {count:>5} plays")
    
    # Most played tracks
    print("\n💿 MOST PLAYED TRACKS OVERALL")
    print("-" * 20)
    top_tracks = music_df.groupby([
        'master_metadata_track_name', 
        'master_metadata_album_artist_name'
    ]).size().sort_values(ascending=False).head(10)
    
    for (track, artist), plays in top_tracks.items():
        print(f"{track:<40} - {artist:<25} {plays:>5} plays")
    
    # Listening patterns by hour
    print("\n⏰ PEAK LISTENING HOURS")
    print("-" * 20)
    hourly = music_df['hour'].value_counts().sort_index()
    max_plays = hourly.max()
    
    for hour, count in hourly.items():
        bar_length = int((count / max_plays) * 30)
        print(f"{hour:02d}:00 {('█' * bar_length):<30} {count:>5}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_historical_data()
