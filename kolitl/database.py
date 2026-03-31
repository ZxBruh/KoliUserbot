import sqlite3
import os

class KoliDatabase:
    def __init__(self, db_name="koli_data.db"):
        self.db_name = db_name
        self.conn = None

    def setup(self):
        self.conn = sqlite3.connect(self.db_name)
        cursor = self.conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
        self.conn.commit()
        print("🗄 База данных Koli готова.")
