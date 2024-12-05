import seaborn as sns
import matplotlib.pyplot as plt

class MusicVisualizer:
    def __init__(self):
        self.style = 'darkgrid'
        sns.set_style(self.style)
    
    def plot_top_artists(self, df, limit=10):
        """Create a bar plot of top artists"""
        plt.figure(figsize=(12, 6))
        top_artists = df['artist'].value_counts().head(limit)
        sns.barplot(x=top_artists.values, y=top_artists.index)
        plt.title('Top Artists')
        plt.xlabel('Play Count')
        plt.tight_layout()
        return plt
