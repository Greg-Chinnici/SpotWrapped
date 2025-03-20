import time
import os
import pandas as pd
import json
import glob


def load_spotify_data(directory_path):
    """
    Load all Spotify JSON files from a directory into a single pandas DataFrame
    
    Parameters:
    directory_path (str): Path to the directory containing Spotify JSON files
    
    Returns:
    pandas.DataFrame: Combined DataFrame of all streaming history
    """
    print("Starting to load Spotify data files...")
    
    # Get all JSON files in the directory
    json_files = glob.glob(os.path.join(directory_path, "*.json"))
    
    print(f"Found {len(json_files)} JSON files")
    
    # Initialize an empty list to store data
    all_data = []
    
    # Process each JSON file
    for i, file_path in enumerate(json_files):
        print(f"Processing file {i+1}/{len(json_files)}: {os.path.basename(file_path)}")
        start_time = time.time()
        
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            file_records = len(data)
            all_data.extend(data)  # Combine all data from each file
        
        elapsed_time = time.time() - start_time
        print(f"  - Loaded {file_records} records in {elapsed_time:.2f} seconds")
    
    total_records = len(all_data)
    print(f"Completed loading {total_records} records in total")
    
    # Convert to DataFrame
    print("Converting to DataFrame...")
    df = pd.DataFrame(all_data)
    print(f"DataFrame created with shape: {df.shape}")
    
    return df

def preprocess_data(df):
    """
    Clean and preprocess the Spotify data
    
    Parameters:
    df (pandas.DataFrame): Raw Spotify data
    
    Returns:
    pandas.DataFrame: Preprocessed data
    """
    print("\nStarting data preprocessing...")
    start_time = time.time()
    
    # Make a copy to avoid modifying the original
    print("  - Creating working copy of DataFrame")
    df_clean = df.copy()
    
    # Convert timestamp to datetime
    print("  - Converting timestamps to datetime")
    df_clean['ts'] = pd.to_datetime(df_clean['ts'])
    
    # Extract date and time components
    print("  - Extracting date and time components")
    df_clean['date'] = df_clean['ts'].dt.date
    df_clean['year'] = df_clean['ts'].dt.year
    df_clean['month'] = df_clean['ts'].dt.month
    df_clean['day'] = df_clean['ts'].dt.day
    df_clean['hour'] = df_clean['ts'].dt.hour
    df_clean['day_of_week'] = df_clean['ts'].dt.dayofweek  # 0 = Monday, 6 = Sunday
    
    # Convert ms_played to minutes for easier interpretation
    print("  - Converting milliseconds to minutes")
    df_clean['minutes_played'] = df_clean['ms_played'] / 60000
    
    # Identify songs vs. podcasts vs. audiobooks
    print("  - Identifying content types")
    df_clean['content_type'] = 'song'
    df_clean.loc[~df_clean['episode_name'].isna(), 'content_type'] = 'podcast'
    df_clean.loc[~df_clean['audiobook_title'].isna(), 'content_type'] = 'audiobook'
    
    # Combine metadata for easier analysis
    print("  - Normalizing track, artist, and album names")
    df_clean['track_name'] = df_clean['master_metadata_track_name']
    df_clean['artist_name'] = df_clean['master_metadata_album_artist_name']
    df_clean['album_name'] = df_clean['master_metadata_album_album_name']
    
    # For podcasts, use episode and show names
    podcast_mask = df_clean['content_type'] == 'podcast'
    df_clean.loc[podcast_mask, 'track_name'] = df_clean.loc[podcast_mask, 'episode_name']
    df_clean.loc[podcast_mask, 'artist_name'] = df_clean.loc[podcast_mask, 'episode_show_name']
    
    # For audiobooks, use audiobook title
    audiobook_mask = df_clean['content_type'] == 'audiobook'
    df_clean.loc[audiobook_mask, 'track_name'] = df_clean.loc[audiobook_mask, 'audiobook_chapter_title']
    df_clean.loc[audiobook_mask, 'album_name'] = df_clean.loc[audiobook_mask, 'audiobook_title']
    
    elapsed_time = time.time() - start_time
    print(f"Preprocessing completed in {elapsed_time:.2f} seconds")
    
    return df_clean


# Load data
path = "/Users/student/Projects/Portfolio/SpotWrapped/SpotifyExtendedStreamingHistory"
df = load_spotify_data(path)

# Preprocess data
df_clean = preprocess_data(df)

df_clean.to_csv("spotify_data_combined.csv", index=False)
