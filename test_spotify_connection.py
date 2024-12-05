from src.spotify_client import SpotifyClient

def test_spotify_connection():
    try:
        # Create client instance
        client = SpotifyClient()
        
        # Try to get current user info
        user = client.get_current_user()
        
        print("✅ Connection successful!")
        print(f"Connected as: {user['display_name']}")
        
        # Print all available user info for debugging
        print("\nAvailable user data:")
        for key in user:
            print(f"- {key}: {user[key]}")
        
    except Exception as e:
        print("❌ Connection failed!")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_spotify_connection()
