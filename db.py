import sqlite3

conn = sqlite3.connect("notes.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
    user_id INTEGER,
    note TEXT
)
""")

conn.commit()

def add_note(user_id: int, note: str):
    cursor.execute(
        "INSERT INTO notes (user_id, note) VALUES (?, ?)",
        (user_id, note)
    )
    conn.commit()

def get_notes(user_id: int):
    cursor.execute(
        "SELECT note FROM notes WHERE user_id = ?",
        (user_id,)
    )
    return cursor.fetchall()
