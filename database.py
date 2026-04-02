import sqlite3, json, os
DB_PATH = "data/koli.db"

class Database:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    def get(self, key, default=None):
        with sqlite3.connect(DB_PATH) as conn:
            row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
            return json.loads(row[0]) if row else default
    def set(self, key, value):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)", (key, json.dumps(value)))
    def all_settings(self):
        with sqlite3.connect(DB_PATH) as conn:
            return {k: json.loads(v) for k,v in conn.execute("SELECT key, value FROM settings").fetchall()}