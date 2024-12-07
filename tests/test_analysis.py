from src.spotify_client import SpotifyClient
from src.analyzer import MusicAnalyzer

def test_listening_history():
    client = SpotifyClient()
    analyzer = MusicAnalyzer()
    
    # Get recent tracks
    recent_tracks = client.get_recently_played(limit=50)
    
    # Process into DataFrame
    df = analyzer.process_recently_played(recent_tracks)
    
    # Analyze patterns
    patterns = analyzer.analyze_listening_patterns(df)
    
    # Get genre analysis
    genres = analyzer.analyze_genres(df, client)
    
    # Print all results
    print("\n📊 Listening History Analysis")
    print("----------------------------")
    print(f"Total Tracks Analyzed: {patterns['total_tracks']}")
    print(f"Unique Tracks: {patterns['unique_tracks']}")
    print(f"Unique Artists: {patterns['unique_artists']}")
    print(f"Total Listening Hours: {patterns['listening_hours']:.2f}")
    
    print("\n🎵 Top Artists:")
    for artist, count in patterns['top_artists'].items():
        print(f"- {artist}: {count} plays")
    
    print("\n🎸 Top Genres:")
    # Only show top 10 genres
    for genre, count in list(genres.items())[:10]:
        print(f"- {genre}: {count} tracks")
    
    if 'peak_hours' in patterns:
        print("\n⏰ Listening by Hour:")
        for hour, count in patterns['peak_hours'].items():
            print(f"{hour:02d}:00 - {count} tracks")

if __name__ == "__main__":
    test_listening_history()
