import json
import pandas as pd
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import seaborn as sns
import matplotlib.pyplot as plt

class SpotifyAnalyzer:
    def __init__(self, client_id, client_secret, redirect_uri):
        """Initialize with Spotify API credentials"""
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope="playlist-modify-public playlist-modify-private user-library-read"
        ))
        
    def load_historical_data(self, json_file_path):
        """Load and process historical Spotify data from JSON file"""
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        return pd.DataFrame(data)
    
    def analyze_top_artists(self, df):
        """Analyze and return top artists from the dataset"""
        return df['artist'].value_counts().head(10)
    
    def create_playlist_from_data(self, playlist_name, track_uris):
        """Create a new playlist based on analyzed data"""
        user_id = self.sp.current_user()['id']
        playlist = self.sp.user_playlist_create(user_id, playlist_name)
        self.sp.playlist_add_items(playlist['id'], track_uris)
        return playlist['id']
    
    def visualize_listening_history(self, df):
        """Create visualizations for listening history"""
        plt.figure(figsize=(12, 6))
        sns.countplot(data=df, y='artist', order=df['artist'].value_counts().index[:10])
        plt.title('Top 10 Most Listened Artists')
        plt.tight_layout()
        plt.show()
