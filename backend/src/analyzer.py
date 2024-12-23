import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import time
import pytz
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Union
import logging

class MusicAnalyzer:
    def __init__(self, data_dir: str = 'data', timezone: str = 'America/New_York'):
        """
        Initialize the MusicAnalyzer with improved error handling and logging.
        
        Args:
            data_dir (str): Directory for data storage
            timezone (str): Timezone for analysis (default: 'America/New_York')
        """
        self.data_dir = Path(data_dir)
        try:
            self.local_timezone = pytz.timezone(timezone)
        except pytz.exceptions.UnknownTimeZoneError:
            logging.error(f"Invalid timezone: {timezone}")
            raise ValueError(f"Invalid timezone: {timezone}")
            
        # Create data directory if it doesn't exist
        self.data_dir.mkdir(exist_ok=True)
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Required columns for different analyses
        self.required_columns = {
            'basic': ['track_name', 'artist_name', 'played_at'],
            'extended': ['track_name', 'artist_name', 'played_at', 'ms_played'],
        }

    def process_recently_played(self, recent_tracks: Dict) -> pd.DataFrame:
        """Process recently played tracks into a DataFrame with timezone information"""
        if not recent_tracks or 'items' not in recent_tracks:
            raise ValueError("Invalid recent_tracks data structure")
            
        tracks_data = []
        first_track = recent_tracks['items'][0]
        
        # Timezone debugging with error handling
        try:
            raw_time = first_track['played_at']
            self.logger.info("\nTimezone Analysis:")
            self.logger.info(f"Raw timestamp: {raw_time}")
            
            utc_time = datetime.strptime(raw_time, '%Y-%m-%dT%H:%M:%S.%fZ')
            utc_time = utc_time.replace(tzinfo=pytz.UTC)
            local_time = utc_time.astimezone(self.local_timezone)
            
            self.logger.info(f"UTC time: {utc_time}")
            self.logger.info(f"Local time: {local_time}")
            self.logger.info(f"Timezone: {self.local_timezone}")
        except (ValueError, KeyError) as e:
            self.logger.error(f"Error processing timestamps: {e}")
            raise
            
        # Process all tracks with error handling
        for item in recent_tracks['items']:
            try:
                utc_time = datetime.strptime(item['played_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
                utc_time = utc_time.replace(tzinfo=pytz.UTC)
                local_time = utc_time.astimezone(self.local_timezone)
                
                track_data = {
                    'track_name': item['track']['name'],
                    'artist_name': item['track']['artists'][0]['name'],
                    'played_at': local_time,
                    'album_name': item['track']['album']['name'],
                    'duration_ms': item['track']['duration_ms'],
                    'popularity': item['track']['popularity'],
                    'ms_played': item['track']['duration_ms']
                }
                tracks_data.append(track_data)
            except KeyError as e:
                self.logger.warning(f"Skipping track due to missing data: {e}")
                continue
                
        df = pd.DataFrame(tracks_data)
        return df

    def analyze_listening_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze listening patterns from DataFrame"""
        if df.empty:
            raise ValueError("DataFrame is empty")
        
        try:
            patterns = {
                'top_artists': df['artist_name'].value_counts().head(10).to_dict(),
                'total_tracks': len(df),
                'unique_tracks': df['track_name'].nunique(),
                'unique_artists': df['artist_name'].nunique(),
                'listening_hours': round(df['ms_played'].sum() / (1000 * 60 * 60), 2),
            }
            
            if 'played_at' in df.columns:
                df['hour'] = df['played_at'].dt.hour
                patterns['peak_hours'] = df['hour'].value_counts().sort_index().to_dict()
                
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error analyzing patterns: {e}")
            raise

    def analyze_genre_trends(self, df: pd.DataFrame, spotify_client, top_n: int = 10, 
                           rate_limit_delay: float = 0.5) -> Dict:
        """Analyze genre distribution for top artists"""
        if df.empty:
            raise ValueError("DataFrame is empty")
        
        top_artists = df['artist_name'].value_counts().head(top_n).index
        artist_genres = {}
        delay = rate_limit_delay
        
        self.logger.info(f"\nAnalyzing genres for top {top_n} artists...")
        self.logger.info(f"Coverage: {(len(top_artists)/df['artist_name'].nunique()*100):.1f}% of unique artists")
        
        for i, artist in enumerate(top_artists, 1):
            try:
                self.logger.info(f"Processing {i}/{top_n}: {artist}")
                results = spotify_client.sp.search(artist, type='artist', limit=1)
                
                if results['artists']['items']:
                    artist_genres[artist] = results['artists']['items'][0]['genres']
                    
                time.sleep(delay)
                
            except Exception as e:
                self.logger.warning(f"Error processing {artist}: {e}")
                delay *= 2  # Exponential backoff
                self.logger.info(f"Increased delay to {delay}s")
                continue
        
        # Process genre data
        all_genres = {}
        for artist, genres in artist_genres.items():
            artist_plays = df[df['artist_name'] == artist].shape[0]
            for genre in genres:
                all_genres[genre] = all_genres.get(genre, 0) + artist_plays
        
        return all_genres

    def create_ascii_graphs(self, df: pd.DataFrame) -> None:
        """Create ASCII visualizations for terminal display"""
        if df.empty:
            raise ValueError("Cannot create visualizations with empty DataFrame")
            
        # Top Artists ASCII Bar Chart
        print("\n📊 Top Artists (ASCII Graph)")
        print("=" * 50)
        top_artists = df['artist_name'].value_counts().head(10)
        max_plays = top_artists.max()
        max_name_length = max(len(name) for name in top_artists.index)
        
        for artist, plays in top_artists.items():
            bar_length = int((plays / max_plays) * 30)
            print(f"{artist:<{max_name_length}} | {'█' * bar_length} {plays}")

        # Listening by Hour ASCII Graph
        print("\n📈 Listening by Hour (ASCII Graph)")
        print("=" * 50)
        hourly = df['played_at'].dt.hour.value_counts().sort_index()
        max_plays_hour = hourly.max()
        
        for hour, count in hourly.items():
            bar_length = int((count / max_plays_hour) * 30)
            hour_label = f"{hour:02d}:00"
            print(f"{hour_label} | {'█' * bar_length} {count}")
