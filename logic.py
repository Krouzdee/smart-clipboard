import sqlite3
import re
from pathlib import Path
import os
from datetime import datetime
import subprocess

def get_db_path():
    data_dir = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    path = Path(data_dir) / "smclip"
    path.mkdir(parents=True, exist_ok=True)
    return str(path / "history.db")

class ClipboardManager:
    def __init__(self, db_path=None):
        self.db_path = db_path or get_db_path()
        self.init_database()

    def init_database(self):
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                type TEXT NOT NULL DEFAULT 'text',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute(
            'CREATE UNIQUE INDEX IF NOT EXISTS idx_content_type ON history(content, type)'
        )
        
        db.commit()
        db.close()
    
    def add_to_db(self, text, max_records=50):
        content_type = self.get_type_content(text)

        try:
            db = sqlite3.connect(self.db_path)
            cursor = db.cursor()

            cursor.execute(
                "INSERT INTO history (content, type) VALUES (?, ?)",
                (text, content_type)
            )

            cursor.execute('''
                DELETE FROM history
                WHERE id NOT IN (
                    SELECT id FROM history
                    ORDER BY timestamp DESC
                    LIMIT ?
                )
              
            ''', (max_records,))

            db.commit()
            db.close()
            return True
        except sqlite3.IntegrityError:
            db.close()
            return False

    def get_history(self, limit=50):
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        cursor.execute(
            "SELECT content, type, timestamp FROM history ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )

        records = cursor.fetchall()
        db.close()
        return records

    def get_type_content(self, text):
        if self.is_url(text):
            return 'url'
        elif self.is_color(text):
            return 'color'
        else:
            return 'text'
            
    @staticmethod
    def format_entry(content, content_type):
        """Formatting based on content type"""
        if content_type == 'url':
            return f"[URL] {content}"
        elif content_type == 'color':
            return f"[COLOR] {content}"
        return content

    @staticmethod
    def set_content(text: str):
        """Writes text to the clipboard"""
        try:
            subprocess.run(['wl-copy'], input=text, text=True, check=True)
        except Exception as e:
            return f"Error writing to clipboard: {e}"

    @staticmethod
    def is_url(text):
        pattern = r"^https?://[^\s]+$"
        return bool(re.match(pattern, text))
    
    @staticmethod
    def is_color(text):
        hex_pattern = r"#(?:[0-9a-fA-F]{3,4}){1,2}\b"
        rgb_pattern = r"rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*(?:,\s*[\d.]+\s*)?\)"
        return bool(re.match(hex_pattern, text) or re.match(rgb_pattern, text))
