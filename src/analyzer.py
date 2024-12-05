import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import time
import pytz


class MusicAnalyzer:
    def __init__(self, data_dir='data', timezone='America/New_York'):
        self.data_dir = Path(data_dir)
        self.local_timezone = pytz.timezone(timezone)
    
    def process_recently_played(self, recent_tracks):
        """Process recently played tracks into a DataFrame with timezone debugging"""
        tracks_data = []
        
        # Print first track timing for debugging
        first_track = recent_tracks['items'][0]
        raw_time = first_track['played_at']
        print("\nTimezone Debugging:")
        print(f"Raw timestamp from Spotify: {raw_time}")
        
        utc_time = datetime.strptime(raw_time, '%Y-%m-%dT%H:%M:%S.%fZ')
        utc_time = utc_time.replace(tzinfo=pytz.UTC)
        print(f"UTC time: {utc_time}")
        
        local_time = utc_time.astimezone(self.local_timezone)
        print(f"Local time (Pacific): {local_time}")
        print(f"Current local timezone: {self.local_timezone}")
        
        for item in recent_tracks['items']:
            utc_time = datetime.strptime(item['played_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
            utc_time = utc_time.replace(tzinfo=pytz.UTC)
            local_time = utc_time.astimezone(self.local_timezone)
            
            track_data = {
                'track_name': item['track']['name'],
                'artist_name': item['track']['artists'][0]['name'],
                'played_at': local_time,
                'album_name': item['track']['album']['name'],
                'duration_ms': item['track']['duration_ms'],
                'popularity': item['track']['popularity']
            }
            tracks_data.append(track_data)
        
        df = pd.DataFrame(tracks_data)
        # Print first few timestamps after conversion
        print("\nFirst few converted timestamps:")
        print(df['played_at'].head())
        
        return df
    
    def analyze_listening_patterns(self, df):
        """Analyze listening patterns from DataFrame"""
        patterns = {
            'top_artists': df['artist_name'].value_counts().head(10).to_dict(),
            'total_tracks': len(df),
            'unique_tracks': df['track_name'].nunique(),
            'unique_artists': df['artist_name'].nunique(),
            'listening_hours': df['duration_ms'].sum() / (1000 * 60 * 60),  # Convert ms to hours
        }
        
        if 'played_at' in df.columns:
            df['hour'] = df['played_at'].dt.hour
            patterns['peak_hours'] = df['hour'].value_counts().sort_index().to_dict()
            
        return patterns

    def analyze_genres(self, df, spotify_client):
        """Analyze genre distribution"""
        genre_counts = {}
        total_artists = len(df['artist_name'].unique())
        print(f"\nAnalyzing genres for {total_artists} artists...")
        
        for i, artist_name in enumerate(df['artist_name'].unique()):
            try:
                print(f"Processing {i+1}/{total_artists}: {artist_name}")
                results = spotify_client.sp.search(artist_name, type='artist', limit=1)
                if results['artists']['items']:
                    artist_id = results['artists']['items'][0]['id']
                    genres = spotify_client.get_artist_genres(artist_id)
                    for genre in genres:
                        genre_counts[genre] = genre_counts.get(genre, 0) + 1
                # Add a small delay to avoid rate limiting
                time.sleep(0.1)
            except Exception as e:
                print(f"Error processing {artist_name}: {str(e)}")
                continue
                
        return dict(sorted(genre_counts.items(), key=lambda x: x[1], reverse=True))

    def analyze_time_patterns(self, df):
        """Analyze listening patterns by time of day"""
        if 'played_at' not in df.columns:
            return None
            
        df['hour'] = df['played_at'].dt.hour
        
        time_periods = {
            'Morning (6AM-12PM)': df[(df['hour'] >= 6) & (df['hour'] < 12)].shape[0],
            'Afternoon (12PM-5PM)': df[(df['hour'] >= 12) & (df['hour'] < 17)].shape[0],
            'Evening (5PM-10PM)': df[(df['hour'] >= 17) & (df['hour'] < 22)].shape[0],
            'Night (10PM-6AM)': df[(df['hour'] >= 22) | (df['hour'] < 6)].shape[0]
        }
        return time_periods
