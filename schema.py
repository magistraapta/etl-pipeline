from sqlalchemy import  Column, Integer, String, DateTime, ForeignKey, Float, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class Artist(Base):
    __tablename__ = 'artists'
    
    artist_id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())
    
    # Relationships
    albums = relationship("Album", back_populates="artist")

class Album(Base):
    __tablename__ = 'albums'
    
    album_id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    artist_id = Column(String(50), ForeignKey('artists.artist_id'))
    release_date = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    artist = relationship("Artist", back_populates="albums")
    tracks = relationship("Track", back_populates="album")

class Track(Base):
    __tablename__ = 'tracks'
    
    track_id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    album_id = Column(String(50), ForeignKey('albums.album_id'))
    duration_ms = Column(Integer)
    popularity = Column(Integer)
    updated_at = Column(DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())
    
    album = relationship("Album", back_populates="tracks")
    listening_history = relationship("ListeningHistory", back_populates="track")

class ListeningHistory(Base):
    __tablename__ = 'listening_history'
    
    id = Column(Integer, primary_key=True)
    track_id = Column(String(50), ForeignKey('tracks.track_id'))
    played_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())
    
    track = relationship("Track", back_populates="listening_history")
    
    __table_args__ = (UniqueConstraint('track_id', 'played_at', name='uix_track_played_at'),)