"""
Database Module
Handles SQLite database operations for video storage
"""
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import config


class VideoDatabase:
    """Manage video records in SQLite database"""
    
    def __init__(self, db_path: Path = None):
        """Initialize database connection"""
        if db_path is None:
            db_path = config.OUTPUT_DIR / 'videos.db'
        self.db_path = db_path
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT,
                format TEXT,
                style TEXT,
                voice TEXT,
                script TEXT,
                keywords TEXT,
                negative_keywords TEXT,
                path TEXT NOT NULL,
                thumbnail_path TEXT,
                duration REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'completed'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_video(self, video_data: Dict) -> int:
        """
        Add a new video to the database
        
        Args:
            video_data: Dictionary containing video metadata
            
        Returns:
            ID of the newly created video record
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO videos (
                title, category, format, style, voice, script,
                keywords, negative_keywords, path, duration, created_at, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            video_data.get('title'),
            video_data.get('category'),
            video_data.get('format'),
            video_data.get('style'),
            video_data.get('voice'),
            video_data.get('script', ''),
            video_data.get('keywords', ''),
            video_data.get('negative_keywords', ''),
            video_data.get('path'),
            video_data.get('duration', 0.0),
            video_data.get('created_at', datetime.now().isoformat()),
            video_data.get('status', 'completed')
        ))
        
        video_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return video_id
    
    def get_video(self, video_id: int) -> Optional[Dict]:
        """Get a single video by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM videos WHERE id = ?', (video_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all_videos(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Get all videos from database
        
        Args:
            limit: Maximum number of videos to return
            offset: Number of videos to skip
            
        Returns:
            List of video dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM videos 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_video(self, video_id: int, updates: Dict) -> bool:
        """Update video metadata"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build dynamic UPDATE query
        fields = []
        values = []
        for key, value in updates.items():
            if key != 'id':  # Don't update ID
                fields.append(f"{key} = ?")
                values.append(value)
        
        if not fields:
            conn.close()
            return False
        
        values.append(video_id)
        query = f"UPDATE videos SET {', '.join(fields)} WHERE id = ?"
        
        cursor.execute(query, values)
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        return affected > 0
    
    def delete_video(self, video_id: int) -> bool:
        """Delete a video from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM videos WHERE id = ?', (video_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        return affected > 0
    
    def search_videos(self, query: str) -> List[Dict]:
        """Search videos by title or category"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        search_pattern = f'%{query}%'
        cursor.execute('''
            SELECT * FROM videos 
            WHERE title LIKE ? OR category LIKE ?
            ORDER BY created_at DESC
        ''', (search_pattern, search_pattern))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_video_count(self) -> int:
        """Get total number of videos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM videos')
        count = cursor.fetchone()[0]
        conn.close()
        
        return count


if __name__ == "__main__":
    # Test the database
    db = VideoDatabase()
    print(f"Database initialized at {db.db_path}")
    print(f"Total videos: {db.get_video_count()}")
