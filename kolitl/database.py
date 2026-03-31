import sqlite3
import os

class KoliDatabase:
    def __init__(self, db_path="koli_core.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def setup(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS config (key TEXT, value TEXT)")
        self.conn.commit()
      
