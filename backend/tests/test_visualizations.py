from src.spotify_client import SpotifyClient
from src.analyzer import MusicAnalyzer
import json
from pathlib import Path

def test_visualizations():
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
    
    # Process all data
    df = analyzer.process_historical_data(all_data)
    
    if len(df) > 0:
        print("\nCreating visualizations...")
        analyzer.create_visualizations(df)
        print("\nVisualization files created:")
        for viz_file in Path('visualizations').glob('*.png'):
            print(f"- {viz_file}")
    else:
        print("No valid tracks found in the data")

if __name__ == "__main__":
    test_visualizations()
