from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from config.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, REDIRECT_URI


class SpotifyClient:
    def __init__(self):
        self.sp = Spotify(auth_manager=SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope="user-read-recently-played user-top-read playlist-read-private"
        ))
    
    def get_current_user(self):
        return self.sp.current_user()
    
    def get_recently_played(self, limit=50):
        """Get recently played tracks"""
        return self.sp.current_user_recently_played(limit=limit)
    
    def get_top_tracks(self, time_range='medium_term', limit=50):
        """Get user's top tracks
        time_range: short_term (4 weeks), medium_term (6 months), long_term (years)
        """
        return self.sp.current_user_top_tracks(time_range=time_range, limit=limit)
    
    def get_top_artists(self, time_range='medium_term', limit=50):
        """Get user's top artists"""
        return self.sp.current_user_top_artists(time_range=time_range, limit=limit)
    
    def get_artist_genres(self, artist_id):
        """Get genres for a specific artist"""
        artist = self.sp.artist(artist_id)
        return artist['genres']
