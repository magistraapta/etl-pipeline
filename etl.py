import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

from sqlalchemy import create_engine, MetaData, Table, Column, String, Float
import pandas as pd
import logging
import datetime

load_dotenv()

def extract_data(limit):
    
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET_ID"),
        redirect_uri="http://localhost:8888/callback",
        scope="user-read-recently-played"
    ))
    
    try:
        recently_played = sp.current_user_recently_played(limit=limit)
        
        tracks_data=[]
        current_time = datetime.datetime.now()
        
        for item in recently_played['items']:
            song_name = item['track']['name']
            artist_name = item['track']['artists'][0]['name']
            played_at = item["played_at"]
            timestamp = pd.to_datetime(played_at).strftime("%Y-%m-%d %H:%M:%S")
            
            played_at_time = pd.to_datetime(played_at).tz_localize(None)
            listening_duration = current_time - played_at_time
            listening_hours = listening_duration.total_seconds() / 3600
            
            tracks_data.append({
                "song_name": song_name,
                "artist_name": artist_name,
                "played_at": played_at,
                "timestamp": timestamp,
                "listening_hours": listening_hours
            })
            
        
        tracks_df = pd.DataFrame(tracks_data)
            
        return tracks_df
    except Exception as e:
        print(f"Error extract data: {e}")
        raise
    
def load_data_to_postgres(data: pd.DataFrame, db_url: str):
    """
    Load data into a PostgreSQL database.

    Args:
        data (pd.DataFrame): DataFrame containing the following columns:
            - song_name: Name of the song.
            - artist_name: Name of the artist.
            - played_at: Timestamp when the song was played (primary key).
            - timestamp: Formatted timestamp of when the song was played.
        db_url (str): PostgreSQL database URL (e.g., 'postgresql://user:password@localhost/dbname').

    Returns:
        None
    """
    try:
        # Create the database engine
        engine = create_engine(db_url)
        meta = MetaData()

        # Define the table schema
        songs_table = Table(
            "my_played_tracks",
            meta,
            Column("song_name", String, nullable=False),
            Column("artist_name", String, nullable=False),
            Column("played_at", String, primary_key=True),
            Column("timestamp", String, nullable=False),
            Column("listening_hours", Float, nullable=False)  # New column for listening hours
        )

        # Create the table if it doesn't exist
        meta.create_all(engine)

        # Insert data into the database
        data.to_sql("recently_played", engine, if_exists="append", index=False)

        logging.info("Data successfully loaded into the PostgreSQL database.")

    except Exception as e:
        logging.error(f"Error loading data into the database: {e}")
        raise


if __name__ == "__main__":
    data = extract_data(limit=50)
    load_data_to_postgres(data=data, db_url=os.getenv("DATABASE_URL"))
