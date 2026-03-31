import sqlite3

class Database:
    def __init__(self, name="koli.db"):
        self.conn = sqlite3.connect(name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)")
        self.conn.commit()

    def get(self, key):
        self.cursor.execute("SELECT value FROM config WHERE key=?", (key,))
        res = self.cursor.fetchone()
        return res[0] if res else None

    def set(self, key, value):
        self.cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, str(value)))
        self.conn.commit()

db = Database()
