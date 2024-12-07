from src.spotify_client import SpotifyClient
from src.analyzer import MusicAnalyzer
import json
from pathlib import Path

def analyze_historical_data():
    analyzer = MusicAnalyzer()
    all_data = []
    
    # Load and combine all JSON files
    mydata_path = Path.home() / 'Downloads' / 'MyData'
    print(f"Reading files from: {mydata_path}")
    
    # List all JSON files
    json_files = list(mydata_path.glob('*.json'))
    print(f"\nFound {len(json_files)} JSON files:")
    for file in json_files:
        print(f"- {file.name}")
    
    # Process each file
    for json_file in json_files:
        print(f"\nProcessing {json_file.name}...")
        with open(json_file, 'r') as file:
            file_data = json.load(file)
            all_data.extend(file_data)
            print(f"Added {len(file_data)} entries")
    
    print(f"\nTotal entries collected: {len(all_data)}")
    
    # Process all data
    df = analyzer.process_historical_data(all_data)
    
    if len(df) > 0:
        # Basic listening patterns
        patterns = analyzer.analyze_listening_patterns(df)
        
        print("\n📊 Complete Listening History Analysis")
        print("--------------------------------")
        print(f"Total Tracks Analyzed: {patterns['total_tracks']}")
        print(f"Unique Tracks: {patterns['unique_tracks']}")
        print(f"Unique Artists: {patterns['unique_artists']}")
        print(f"Total Listening Hours: {patterns['listening_hours']:.2f}")
        
        print("\n🎵 Top Artists Overall:")
        for artist, count in patterns['top_artists'].items():
            print(f"- {artist}: {count} plays")
        
        # Year-by-Year Analysis
        print("\n📅 Year-by-Year Analysis")
        print("----------------------")
        yearly_stats = analyzer.analyze_by_year(df)
        for year, stats in yearly_stats.items():
            print(f"\n{year}:")
            print(f"Total Tracks: {stats['total_tracks']}")
            print(f"Unique Tracks: {stats['unique_tracks']}")
            print(f"Listening Hours: {stats['listening_hours']:.2f}")
            print("\nTop Artists:")
            for artist, count in list(stats['top_artists'].items())[:5]:
                print(f"- {artist}: {count} plays")

        # Time Patterns
        time_patterns = analyzer.analyze_time_patterns(df)
        if time_patterns:
            print("\n⏰ Listening Patterns by Time of Day:")
            for period, count in time_patterns.items():
                print(f"{period}: {count} tracks")

        # ASCII Visualizations
        print("\nGenerating ASCII Visualizations...")
        analyzer.create_ascii_graphs(df)
        
        # Create PNG visualizations
        print("\n📊 Creating Visualizations...")
        analyzer.create_visualizations(df)
        print("Saved visualizations:")
        print("- listening_heatmap.png (Activity by Hour and Year)")
        print("- top_artists_by_year.png (Artist Trends)")
        print("- monthly_patterns.png (Monthly Listening Patterns)")

        # In the genre analysis section of test_historical.py:
        print("\n🎸 Analyzing Genre Trends...")
        client = SpotifyClient()
        genre_trends = analyzer.analyze_genre_trends(df, client, top_n=100)  # Processing top 100 artists

        print("\n📊 Genre Analysis by Year")
        print("------------------------")
        for year in sorted(genre_trends.keys()):
            print(f"\n{year} Top Genres:")
            for genre, count in list(genre_trends[year].items())[:5]:
                bar_length = int((count / max(genre_trends[year].values())) * 20)
                print(f"- {genre:<20} {'█' * bar_length} ({count} plays)")

if __name__ == "__main__":
    analyze_historical_data()
