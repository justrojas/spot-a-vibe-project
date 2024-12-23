import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, REDIRECT_URI

class SpotifyClient:
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope='user-read-recently-played user-top-read user-library-read'
        ))

    def get_recently_played(self, limit=50):
        return self.sp.current_user_recently_played(limit=limit)
