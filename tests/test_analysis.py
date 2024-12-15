import sys
import os
import pandas as pd
import logging
from datetime import datetime
from pathlib import Path

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.spotify_client import SpotifyClient
from src.analyzer import MusicAnalyzer

def test_listening_history():
    """Test the full listening history analysis workflow."""
    # Initialize with logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        client = SpotifyClient()
        analyzer = MusicAnalyzer()
        
        print("\n🎵 SPOTIFY LISTENING REPORT")
        print("=" * 40)
        
        # Get recent tracks and process data
        logger.info("Fetching recent tracks...")
        recent_tracks = client.get_recently_played(limit=50)
        
        logger.info("Processing tracks into DataFrame...")
        df = analyzer.process_recently_played(recent_tracks)
        
        logger.info("Analyzing listening patterns...")
        patterns = analyzer.analyze_listening_patterns(df)
        
        # Recent Activity Overview
        print("\n📊 RECENT ACTIVITY")
        print("-" * 20)
        print(f"Listening Time: {patterns.get('listening_hours', 0):.1f} hours")
        print(f"Tracks Played: {patterns.get('total_tracks', 'N/A')}")
        print(f"Unique Artists: {patterns.get('unique_artists', 'N/A')}")
        
        # Top Artists
        if 'top_artists' in patterns and patterns['top_artists']:
            print("\n🎤 TOP ARTISTS")
            print("-" * 20)
            for artist, count in list(patterns['top_artists'].items())[:5]:
                print(f"{artist:<25} {count} plays")
        
        # Recent Tracks
        print("\n💿 RECENTLY PLAYED")
        print("-" * 20)
        recent = df[['track_name', 'artist_name']].head(5)
        for _, row in recent.iterrows():
            print(f"{row['track_name']:<30} - {row['artist_name']}")
        
        # Peak Hours
        if 'peak_hours' in patterns and patterns['peak_hours']:
            print("\n⏰ PEAK LISTENING HOURS")
            print("-" * 20)
            peak_hours = patterns['peak_hours']
            max_plays = max(peak_hours.values())
            for hour, plays in sorted(peak_hours.items())[:5]:
                bar = "█" * int((plays/max_plays) * 15)
                print(f"{int(hour):02d}:00  {bar:<15} {plays} plays")
        
        # Genre Analysis
        try:
            logger.info("Analyzing genre trends...")
            genres = analyzer.analyze_genre_trends(df, client, top_n=10)
            
            if genres:
                print("\n🎸 TOP GENRES")
                print("-" * 20)
                sorted_genres = dict(sorted(genres.items(), key=lambda x: x[1], reverse=True)[:5])
                for genre, count in sorted_genres.items():
                    print(f"{genre:<25} {count} tracks")
        
        except Exception as e:
            logger.warning(f"Could not analyze genres: {e}")
        
        print("\n" + "=" * 40)
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        raise

if __name__ == "__main__":
    test_listening_history()
