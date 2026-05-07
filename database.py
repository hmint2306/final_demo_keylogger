import sqlite3
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

db_name = os.getenv("DB_NAME", "notes.db")
DB_PATH = Path(__file__).with_name(db_name)

def init_db() -> None:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        connection.commit()

def register_user(username, password):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()

def login_user(username, password):
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()

def save_note(user_id, note_id, title, content, now):
    with sqlite3.connect(DB_PATH) as conn:
        if note_id is None:
            cursor = conn.execute(
                "INSERT INTO notes (user_id, title, content, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (user_id, title, content, now, now)
            )
            return int(cursor.lastrowid)
        else:
            conn.execute(
                "UPDATE notes SET title = ?, content = ?, updated_at = ? WHERE id = ? AND user_id = ?",
                (title, content, now, note_id, user_id)
            )
            return note_id

def delete_note(note_id, user_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id))
        conn.commit()

def fetch_notes(user_id, query=""):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        if query:
            rows = conn.execute(
                "SELECT * FROM notes WHERE user_id = ? AND (title LIKE ? OR content LIKE ?) ORDER BY updated_at DESC",
                (user_id, f"%{query}%", f"%{query}%")
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM notes WHERE user_id = ? ORDER BY updated_at DESC", 
                (user_id,)
            ).fetchall()
    return [dict(row) for row in rows]

def get_note(note_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        return dict(row) if row else None
    
def get_user_info(user_id):
    """Hàm lấy thông tin username hiện tại để hiển thị lên Form"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT username, password FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None

def update_user_info(user_id, new_username, new_password):
    """Hàm lưu thông tin username và password mới vào SQLite"""
    with sqlite3.connect(DB_PATH) as conn:
        try:
            conn.execute("UPDATE users SET username = ?, password = ? WHERE id = ?", (new_username, new_password, user_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False