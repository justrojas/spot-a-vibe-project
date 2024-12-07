import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import time
import pytz
import matplotlib.pyplot as plt


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
        print(f"Local time (Eastern): {local_time}")
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
                'popularity': item['track']['popularity'],
                'ms_played': item['track']['duration_ms']
            }
            tracks_data.append(track_data)
        
        df = pd.DataFrame(tracks_data)
        print("\nFirst few converted timestamps:")
        print(df['played_at'].head())
        
        return df

    def process_historical_data(self, json_data):
        """Process historical Spotify data from JSON file"""
        tracks_data = []
        skipped = 0
        podcast = 0
        null_track = 0
        short_play = 0
        
        print("\nAnalyzing data sample:")
        print(f"First entry timestamp: {json_data[0]['ts']}")
        print(f"Last entry timestamp: {json_data[-1]['ts']}")
        
        for item in json_data:
            # Skip podcasts
            if item.get('episode_name'):
                podcast += 1
                continue
                
            # Process music tracks
            if (item.get('master_metadata_track_name') and 
                item.get('master_metadata_album_artist_name') and 
                item['ms_played'] > 0):
                
                track_data = {
                    'track_name': item['master_metadata_track_name'],
                    'artist_name': item['master_metadata_album_artist_name'],
                    'album_name': item['master_metadata_album_album_name'],
                    'played_at': datetime.strptime(item['ts'], '%Y-%m-%dT%H:%M:%SZ'),
                    'ms_played': item['ms_played'],
                    'platform': item['platform']
                }
                tracks_data.append(track_data)
            else:
                if item['ms_played'] == 0:
                    skipped += 1
                elif item['ms_played'] < 30000:
                    short_play += 1
                else:
                    null_track += 1
        
        print("\nProcessing Statistics:")
        print(f"Total entries: {len(json_data)}")
        print(f"Skipped (0ms): {skipped}")
        print(f"Podcasts: {podcast}")
        print(f"Null tracks: {null_track}")
        print(f"Short plays: {short_play}")
        print(f"Valid music tracks: {len(tracks_data)}")
        
        if len(tracks_data) > 0:
            print("\nSample of processed tracks:")
            for i, track in enumerate(tracks_data[:3]):
                print(f"{i+1}. {track['track_name']} by {track['artist_name']}")
        
        return pd.DataFrame(tracks_data)

    def analyze_listening_patterns(self, df):
        """Analyze listening patterns from DataFrame"""
        patterns = {
            'top_artists': df['artist_name'].value_counts().head(10).to_dict(),
            'total_tracks': len(df),
            'unique_tracks': df['track_name'].nunique(),
            'unique_artists': df['artist_name'].nunique(),
            'listening_hours': df['ms_played'].sum() / (1000 * 60 * 60),
        }
        
        if 'played_at' in df.columns:
            df['hour'] = df['played_at'].dt.hour
            patterns['peak_hours'] = df['hour'].value_counts().sort_index().to_dict()
            
        return patterns

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

    def analyze_by_year(self, df):
        """Analyze listening patterns by year"""
        # Add year column
        df['year'] = pd.to_datetime(df['played_at']).dt.year
        
        yearly_stats = {}
        for year in sorted(df['year'].unique()):
            year_df = df[df['year'] == year]
            yearly_stats[year] = {
                'total_tracks': len(year_df),
                'unique_tracks': year_df['track_name'].nunique(),
                'unique_artists': year_df['artist_name'].nunique(),
                'listening_hours': year_df['ms_played'].sum() / (1000 * 60 * 60),
                'top_artists': year_df['artist_name'].value_counts().head(5).to_dict(),
                'peak_hours': year_df['played_at'].dt.hour.value_counts().sort_index().to_dict()
            }
        
        return yearly_stats

    def create_visualizations(self, df):
        """Create various visualizations of listening data"""
        import matplotlib.pyplot as plt
        try:
            import seaborn as sns
            sns.set_theme()
        except ImportError:
            print("Seaborn not found, using default matplotlib style")
        
        # Create directory for visualizations if it doesn't exist
        Path('visualizations').mkdir(exist_ok=True)
        
        # 1. Listening Activity Heatmap
        print("Creating listening activity heatmap...")
        plt.figure(figsize=(15, 8))
        df['hour'] = df['played_at'].dt.hour
        df['year'] = df['played_at'].dt.year
        pivot_data = df.groupby(['year', 'hour']).size().unstack()
        try:
            sns.heatmap(pivot_data, cmap='YlOrRd')
        except NameError:
            plt.imshow(pivot_data, cmap='YlOrRd', aspect='auto')
            plt.colorbar()
        plt.title('Listening Activity by Hour and Year')
        plt.xlabel('Hour of Day')
        plt.ylabel('Year')
        plt.savefig('visualizations/listening_heatmap.png', bbox_inches='tight')
        plt.close()
        
        # 2. Top Artists Over Time
        print("Creating top artists visualization...")
        plt.figure(figsize=(15, 8))
        top_artists = df['artist_name'].value_counts().head(10).index
        artist_by_year = df[df['artist_name'].isin(top_artists)].groupby(['year', 'artist_name']).size().unstack()
        artist_by_year.plot(kind='bar', stacked=True)
        plt.title('Top Artists Listening Patterns Over Years')
        plt.xlabel('Year')
        plt.ylabel('Number of Plays')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig('visualizations/top_artists_by_year.png', bbox_inches='tight')
        plt.close()
        
        # 3. Monthly Listening Trends
        print("Creating monthly trends visualization...")
        plt.figure(figsize=(15, 6))
        df['month'] = df['played_at'].dt.month
        monthly_plays = df.groupby(['year', 'month']).size().unstack()
        try:
            sns.heatmap(monthly_plays, cmap='YlOrRd')
        except NameError:
            plt.imshow(monthly_plays, cmap='YlOrRd', aspect='auto')
            plt.colorbar()
        plt.title('Monthly Listening Patterns')
        plt.xlabel('Month')
        plt.ylabel('Year')
        plt.savefig('visualizations/monthly_patterns.png', bbox_inches='tight')
        plt.close()
        
        print("Successfully created visualizations in 'visualizations' directory!")

    def analyze_genre_trends(self, df, spotify_client, top_n=100):
        """Analyze how genre preferences change over time
        Args:
            df: DataFrame with listening history
            spotify_client: SpotifyClient instance
            top_n: Number of top artists to analyze (default: 100)
        """
        # Get only top N artists to analyze
        top_artists = df['artist_name'].value_counts().head(top_n).index
        artist_genres = {}
        
        print(f"\nAnalyzing genres for top {top_n} artists...")
        print(f"This represents {(len(top_artists)/df['artist_name'].nunique()*100):.1f}% of your unique artists")
        
        for i, artist in enumerate(top_artists):
            try:
                print(f"Processing {i+1}/{top_n}: {artist}")
                results = spotify_client.sp.search(artist, type='artist', limit=1)
                if results['artists']['items']:
                    artist_genres[artist] = results['artists']['items'][0]['genres']
                time.sleep(0.1)  # Rate limiting
            except Exception as e:
                print(f"Error processing {artist}: {str(e)}")
        
        # Add genres to dataframe but only for analyzed artists
        df['genres'] = df['artist_name'].map(lambda x: artist_genres.get(x, []))
        
        # Analyze genres by year
        genre_trends = {}
        for year in sorted(df['year'].unique()):
            year_df = df[df['year'] == year]
            genre_counts = {}
            for genres in year_df['genres']:
                for genre in genres:
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1
            # Only keep top 10 genres per year
            genre_trends[year] = dict(sorted(genre_counts.items(), 
                                           key=lambda x: x[1], 
                                           reverse=True)[:10])
        
        return genre_trends

    def create_ascii_graphs(self, df):
        """Create ASCII visualizations for terminal display"""
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
