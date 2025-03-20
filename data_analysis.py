import pandas as pd
import os
import json
import glob
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import time

from qbstyles import mpl_style
mpl_style(dark=True)



def load_spotify_data_csv(filename):
    return pd.read_csv(filename)

def generate_basic_stats(df):
    """
    Generate basic statistics from the Spotify data
    
    Parameters:
    df (pandas.DataFrame): Preprocessed Spotify data
    
    Returns:
    dict: Dictionary of basic statistics
    """
    print("\nGenerating basic statistics...")
    start_time = time.time()
    
    stats = {}
    
    # Total listening time
    print("  - Calculating total listening time")
    total_minutes = df['minutes_played'].sum()
    stats['total_hours'] = total_minutes / 60
    
    # Number of unique tracks, artists, and albums
    print("  - Counting unique tracks, artists, and albums")
    stats['unique_tracks'] = df['track_name'].nunique()
    stats['unique_artists'] = df['artist_name'].nunique()
    stats['unique_albums'] = df['album_name'].nunique()
    
    # Content type distribution
    print("  - Analyzing content type distribution")
    stats['content_type_counts'] = df['content_type'].value_counts().to_dict()
    
    # Date range
    print("  - Determining date range")
    stats['date_range'] = (df['ts'].min(), df['ts'].max())
    
    # Platform usage
    print("  - Analyzing platform usage")
    stats['platform_usage'] = df['platform'].value_counts().head(5).to_dict()
    
    # Skip rate
    print("  - Calculating skip and shuffle rates")
    stats['skip_rate'] = df['skipped'].mean() * 100  # as percentage
    
    # Shuffle rate
    stats['shuffle_rate'] = df['shuffle'].mean() * 100  # as percentage
    
    elapsed_time = time.time() - start_time
    print(f"Statistics generation completed in {elapsed_time:.2f} seconds")
    
    return stats

def top_10_artists_all_time(df):
    print("  - Generating top 10 artists chart")
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    top_artists = df.groupby('artist_name')['minutes_played'].sum().sort_values(ascending=False).head(10)
    sns.barplot(x=top_artists.values, y=top_artists.index)
    plt.title('Top 10 Artists by Listening Time')
    plt.xlabel('Minutes Played')
    plt.ylabel('Artist')
    plt.tight_layout()
    plt.savefig('top_10_artists.png')
    print("    ✓ Saved top_10_artists.png")

def listening_time_by_hour(df):
    print("  - Generating hourly listening chart")
    
    hourly_listening = df.groupby(['year', 'hour'])['minutes_played'].sum().unstack(level=0)

    fig, ax = plt.subplots(figsize=(12, 6))
    hourly_listening.plot(kind='bar', stacked=True, ax=ax)
    
    plt.title('Listening Time by Hour of Day')
    plt.xlabel('Hour of Day')
    plt.ylabel('Minutes Played')
    plt.xticks(range(24))
    plt.tight_layout()
    plt.savefig('listening_by_hour.png')
    print("    ✓ Saved listening_by_hour.png")
    #hourly_listening.to_csv('listening_by_hour.csv')

def listening_time_by_day(df):
    print("  - Generating weekly listening chart")
    plt.figure(figsize=(12, 6))
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly_listening = df.groupby('day_of_week')['minutes_played'].sum()
    sns.barplot(x=weekly_listening.index, y=weekly_listening.values)
    plt.xticks(range(7), day_names)
    plt.title('Listening Time by Day of Week')
    plt.xlabel('Day of Week')
    plt.ylabel('Minutes Played')
    plt.tight_layout()
    plt.savefig('listening_by_day.png')
    print("    ✓ Saved listening_by_day.png")

def most_played_albums(df):
    print("  - Generating most played albums chart")
    plt.figure(figsize=(12, 6))
    top_albums = df.groupby('album_name')['minutes_played'].sum().sort_values(ascending=False).head(10)
    sns.barplot(x=top_albums.values, y=top_albums.index)
    plt.title('Top 10 Albums by Listening Time')
    plt.xlabel('Minutes Played')
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig('top_albums.png')
    print("    ✓ Saved top_albums.png")

def analyze_yearly_trends(df):
    """
    Analyze trends by year
    """
    print("\nAnalyzing yearly trends...")
    
    # Group by year and get stats
    yearly_stats = {}
    
    for year in sorted(df['year'].unique()):
        print(f"  - Processing data for {year}")
        year_data = df[df['year'] == year]
        
        # Top 5 artists by year
        top_artists = year_data.groupby('artist_name')['minutes_played'].sum().sort_values(ascending=False).head(5)
        
        # Top 5 tracks by year
        top_tracks = year_data.groupby('track_name')['minutes_played'].sum().sort_values(ascending=False).head(5)
        
        # Listening time by month for this year
        monthly_listening = year_data.groupby('month')['minutes_played'].sum()
        
        # Total listening time for the year
        total_time = year_data['minutes_played'].sum()
        
        print(top_artists)
        print(top_tracks)
        
        print(f"Time per month: {monthly_listening}")
        print(f"Year time: {total_time}")

        yearly_stats[year] = {
            'top_artists': top_artists.to_dict(),
            'top_tracks': top_tracks.to_dict(),
            'monthly_listening': monthly_listening.to_dict(),
            'total_hours': total_time / 60
        }
    
    # Create year-over-year comparison chart
    years = sorted(yearly_stats.keys())
    hours_per_year = [yearly_stats[year]['total_hours'] for year in years]
    
    plt.figure(figsize=(12, 6))
    sns.barplot(x=years, y=hours_per_year)
    plt.title('Listening Hours by Year')
    plt.xlabel('Year')
    plt.ylabel('Hours')
    plt.tight_layout()
    plt.savefig('yearly_listening_comparison.png')
    print("    ✓ Saved yearly_listening_comparison.png")
    
    return yearly_stats

def analyze_skip_behavior(df):
    """
    Analyze skipping behavior to find insights
    """
    print("\nAnalyzing skip behavior...")
    
    # Filter to tracks that were played more than once
    track_counts = df['track_name'].value_counts()
    repeated_tracks = track_counts[track_counts > 1].index
    repeat_df = df[df['track_name'].isin(repeated_tracks)]
    
    # Calculate skip rates per track
    track_skip_rates = repeat_df.groupby('track_name')['skipped'].mean() * 100
    
    # Most skipped tracks (that were played at least 5 times)
    frequently_played = df['track_name'].value_counts()[df['track_name'].value_counts() >= 5].index
    frequent_tracks_df = df[df['track_name'].isin(frequently_played)]
    frequent_skip_rates = frequent_tracks_df.groupby('track_name').agg({
        'skipped': ['mean', 'count']
    })
    frequent_skip_rates.columns = ['skip_rate', 'play_count']
    frequent_skip_rates['skip_rate'] = frequent_skip_rates['skip_rate'] * 100
    most_skipped = frequent_skip_rates.sort_values('skip_rate', ascending=False).head(10)
    
    # Visualize most skipped tracks
    plt.figure(figsize=(12, 8))
    ax = sns.barplot(x=most_skipped['skip_rate'].values, y=most_skipped.index)
    plt.title('Most Frequently Skipped Tracks (Played at least 5 times)')
    plt.xlabel('Skip Rate (%)')
    plt.tight_layout()
    plt.savefig('most_skipped_tracks.png')
    print("    ✓ Saved most_skipped_tracks.png")
    
    # Calculate skip rates by time of day
    hourly_skip_rates = df.groupby('hour')['skipped'].mean() * 100
    
    plt.figure(figsize=(12, 6))
    sns.lineplot(x=hourly_skip_rates.index, y=hourly_skip_rates.values, marker='o')
    plt.title('Skip Rates by Hour of Day')
    plt.xlabel('Hour')
    plt.ylabel('Skip Rate (%)')
    plt.xticks(range(24))
    plt.tight_layout()
    plt.savefig('hourly_skip_rates.png')
    print("    ✓ Saved hourly_skip_rates.png")
    
    return most_skipped.to_dict()

def discover_listening_sessions(df):
    """
    Identify listening sessions and analyze them
    """
    print("\nIdentifying listening sessions...")
    
    # Sort by timestamp
    df_sorted = df.sort_values('ts')
    
    # Define a session as continuous listening with gaps less than 20 minutes
    SESSION_GAP_MINUTES = 20
    
    # Calculate time difference between consecutive tracks
    df_sorted['next_ts'] = df_sorted['ts'].shift(-1)
    df_sorted['time_diff'] = (df_sorted['next_ts'] - df_sorted['ts']).dt.total_seconds() / 60
    
    # Mark new sessions (where time gap > SESSION_GAP_MINUTES)
    df_sorted['new_session'] = (df_sorted['time_diff'] > SESSION_GAP_MINUTES) | (df_sorted['time_diff'].isna())
    df_sorted['session_id'] = df_sorted['new_session'].cumsum()
    
    # Analyze sessions
    sessions = df_sorted.groupby('session_id').agg({
        'ts': 'min',
        'track_name': 'count',
        'minutes_played': 'sum',
        'time_diff': 'sum'
    })
    
    sessions.columns = ['start_time', 'tracks_played', 'duration_minutes', 'gaps_minutes']
    sessions['total_session_minutes'] = sessions['duration_minutes'] + sessions['gaps_minutes']
    
    # Add day of week and hour info
    sessions['day_of_week'] = sessions['start_time'].dt.dayofweek
    sessions['hour'] = sessions['start_time'].dt.hour
    sessions['month'] = sessions['start_time'].dt.month
    sessions['year'] = sessions['start_time'].dt.year
    
    # Session insights
    avg_session_length = sessions['duration_minutes'].mean()
    avg_tracks_per_session = sessions['tracks_played'].mean()
    longest_session = sessions.sort_values('duration_minutes', ascending=False).iloc[0]
    
    # Visualize session lengths
    plt.figure(figsize=(12, 6))
    sns.histplot(sessions['duration_minutes'], bins=30)
    plt.axvline(avg_session_length, color='r', linestyle='--', label=f'Average ({avg_session_length:.1f} min)')
    plt.title('Distribution of Listening Session Lengths')
    plt.xlabel('Session Duration (minutes)')
    plt.ylabel('Count')
    plt.legend()
    plt.tight_layout()
    plt.savefig('session_length_distribution.png')
    print("    ✓ Saved session_length_distribution.png")
    
    # Visualize sessions by hour of day
    hourly_sessions = sessions.groupby('hour').size()
    plt.figure(figsize=(12, 6))
    sns.barplot(x=hourly_sessions.index, y=hourly_sessions.values)
    plt.title('Number of Listening Sessions by Hour of Day')
    plt.xlabel('Hour')
    plt.ylabel('Number of Sessions')
    plt.xticks(range(24))
    plt.tight_layout()
    plt.savefig('sessions_by_hour.png')
    print("    ✓ Saved sessions_by_hour.png")
    
    session_stats = {
        'total_sessions': len(sessions),
        'avg_session_length': avg_session_length,
        'avg_tracks_per_session': avg_tracks_per_session,
        'longest_session_minutes': longest_session['duration_minutes'],
        'longest_session_tracks': longest_session['tracks_played'],
        'longest_session_date': longest_session['start_time']
    }
    
    return session_stats, sessions

def analyze_binge_listening(df):
    """
    Analyze binge listening patterns - consecutive plays of the same artist
    """
    print("\nAnalyzing binge listening patterns...")
    
    # Sort by timestamp
    df_sorted = df.sort_values('ts').copy()
    
    # Add next artist column
    df_sorted['next_artist'] = df_sorted['artist_name'].shift(-1)
    
    # Mark when artist changes
    df_sorted['artist_change'] = df_sorted['artist_name'] != df_sorted['next_artist']
    
    # Create binge groups
    df_sorted['binge_group'] = df_sorted['artist_change'].cumsum()
    
    # Count consecutive plays of the same artist
    binge_counts = df_sorted.groupby('binge_group').agg({
        'artist_name': ['first', 'count'],
        'minutes_played': 'sum',
        'ts': 'min'
    })

    binge_counts.columns = ['artist', 'consecutive_plays', 'duration_minutes', 'start_time']
    
    # Find longest binges
    longest_binges = binge_counts.sort_values('consecutive_plays', ascending=False).head(10)
    # Visualize top binge artists
    top_binge_artists = binge_counts[binge_counts['consecutive_plays'] >= 3].groupby('artist').size().sort_values(ascending=False).head(10)
    
    plt.figure(figsize=(12, 6))
    sns.barplot(x=top_binge_artists.values, y=top_binge_artists.index)
    plt.title('Artists Most Frequently Listened to in Binges (3+ Consecutive Tracks)')
    plt.xlabel('Number of Binges')
    plt.tight_layout()
    
    plt.savefig('top_binge_artists.png')
    print("    ✓ Saved top_binge_artists.png")
    
    # Distribution of binge lengths
    plt.figure(figsize=(12, 6))
    sns.histplot(binge_counts[binge_counts['consecutive_plays'] > 1]['consecutive_plays'], bins=20)
    plt.title('Distribution of Artist Binge Lengths')
    plt.xlabel('Consecutive Tracks')
    plt.ylabel('Frequency')
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig('binge_length_distribution.png')
    print("    ✓ Saved binge_length_distribution.png")

def top_tracks_all_time_by_listen_time(df):
    top_tracks = df.groupby('track_name')['minutes_played'].sum().sort_values(ascending=False).head(10)
    plt.figure(figsize=(12, 6))
    sns.barplot(x=top_tracks.values, y=top_tracks.index)
    plt.title('Top 10 Tracks by Listening Time')
    plt.xlabel('Minutes')
    plt.ylabel('Track')
    plt.tight_layout()
    plt.savefig('top_10_tracks.png')
    print("    ✓ Saved top_10_tracks.png")

def top_tracks_all_time_by_play_count(df):
    top_tracks = df['track_name'].value_counts().head(10)
    plt.figure(figsize=(12, 6))
    sns.barplot(x=top_tracks.values, y=top_tracks.index)
    plt.title('Top 10 Tracks by Play Count')
    plt.xlabel('Play Count')
    plt.ylabel('Track')
    plt.tight_layout()
    plt.savefig('top_10_tracks_play_count.png')
    print("    ✓ Saved top_10_tracks_play_count.png")

def count_ips(df):
    c = df['ip_addr'].nunique()
    print(f"Unique IP ADDRs: {c}")

if __name__ == "__main__":
    print("=" * 50)
    print("SPOTIFY DATA ANALYSIS")
    print("=" * 50)

    # Start timing
    overall_start_time = time.time()
    
    # Load data
    df_clean = load_spotify_data_csv('spotify_data_combined.csv')

    # Generate basic statistics
    #stats = generate_basic_stats(df_clean)
    
    # Print basic statistics
    #print("\nBASIC STATISTICS:")
    #print("-" * 50)
    #print(f"Total listening time: {stats['total_hours']:.2f} hours")
    #print(f"Unique tracks: {stats['unique_tracks']}")
    #print(f"Unique artists: {stats['unique_artists']}")
    #print(f"Unique albums: {stats['unique_albums']}")
    #print(f"Date range: {stats['date_range'][0]} to {stats['date_range'][1]}")
    #print(f"Skip rate: {stats['skip_rate']:.2f}%")
    #print(f"Shuffle rate: {stats['shuffle_rate']:.2f}%")
    
   
    
    # Top 5 platforms
    #print("\nTop 5 Platforms:")
    #for platform, usage_count in list(stats['platform_usage'].items())[:5]:
    #    print(f"  - {platform}: {usage_count}")

    #top_tracks_all_time_by_listen_time(df_clean)
    #top_10_artists_all_time(df_clean)
    #most_played_albums(df_clean)
    #listening_time_by_day(df_clean)
    #listening_time_by_hour(df_clean)

    #analyze_yearly_trends(df_clean)
    #analyze_skip_behavior(df_clean)
    #discover_listening_sessions(df_clean)
    #analyze_listening_moods(df_clean)
    #analyze_binge_listening(df_clean)

    #top_tracks_all_time_by_play_count(df_clean)
    #top_tracks_all_time_by_listen_time(df_clean)

    count_ips(df_clean)

    # Calculate overall execution time
    overall_elapsed_time = time.time() - overall_start_time
    print(f"\nTotal execution time: {overall_elapsed_time:.2f} seconds")
    print("=" * 50)
