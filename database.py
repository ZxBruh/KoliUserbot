import sqlite3
import json
import os
from datetime import datetime

DB_PATH = "data/koli.db"

class Database:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.init_db()
    
    def init_db(self):
        with sqlite3.connect(DB_PATH) as conn:
            # Настройки
            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP
                )
            """)
            # Модули
            conn.execute("""
                CREATE TABLE IF NOT EXISTS modules (
                    name TEXT PRIMARY KEY,
                    enabled INTEGER DEFAULT 1,
                    loaded_at TIMESTAMP
                )
            """)
            # Черный список
            conn.execute("""
                CREATE TABLE IF NOT EXISTS blacklist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    reason TEXT,
                    created_at TIMESTAMP
                )
            """)
            # Бэкапы
            conn.execute("""
                CREATE TABLE IF NOT EXISTS backups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    path TEXT,
                    created_at TIMESTAMP
                )
            """)
            # Команды
            conn.execute("""
                CREATE TABLE IF NOT EXISTS commands (
                    name TEXT PRIMARY KEY,
                    enabled INTEGER DEFAULT 1,
                    module TEXT
                )
            """)
            conn.commit()
    
    def get(self, key, default=None):
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cur.fetchone()
            if row:
                try:
                    return json.loads(row[0])
                except:
                    return row[0]
            return default
    
    def set(self, key, value):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
                (key, json.dumps(value), datetime.now())
            )
            conn.commit()
    
    def delete(self, key):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("DELETE FROM settings WHERE key = ?", (key,))
            conn.commit()
    
    def all_settings(self):
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute("SELECT key, value FROM settings")
            return {row[0]: json.loads(row[1]) for row in cur.fetchall()}
    
    def module_enabled(self, name):
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute("SELECT enabled FROM modules WHERE name = ?", (name,))
            row = cur.fetchone()
            return bool(row[0]) if row else True
    
    def toggle_module(self, name, enabled=None):
        with sqlite3.connect(DB_PATH) as conn:
            if enabled is None:
                enabled = not self.module_enabled(name)
            conn.execute(
                "INSERT OR REPLACE INTO modules (name, enabled, loaded_at) VALUES (?, ?, ?)",
                (name, 1 if enabled else 0, datetime.now())
            )
            conn.commit()
            return enabled
    
    def add_blacklist(self, user_id, reason=""):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO blacklist (user_id, reason, created_at) VALUES (?, ?, ?)",
                (user_id, reason, datetime.now())
            )
            conn.commit()
    
    def remove_blacklist(self, user_id):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("DELETE FROM blacklist WHERE user_id = ?", (user_id,))
            conn.commit()
    
    def is_blacklisted(self, user_id):
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute("SELECT 1 FROM blacklist WHERE user_id = ?", (user_id,))
            return cur.fetchone() is not None
    
    def add_backup(self, backup_type, path):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO backups (type, path, created_at) VALUES (?, ?, ?)",
                (backup_type, path, datetime.now())
            )
            conn.commit()
    
    def command_enabled(self, name):
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute("SELECT enabled FROM commands WHERE name = ?", (name,))
            row = cur.fetchone()
            return bool(row[0]) if row else True
    
    def toggle_command(self, name, enabled=None):
        with sqlite3.connect(DB_PATH) as conn:
            if enabled is None:
                enabled = not self.command_enabled(name)
            conn.execute(
                "INSERT OR REPLACE INTO commands (name, enabled, module) VALUES (?, ?, ?)",
                (name, 1 if enabled else 0, "core")
            )
            conn.commit()
            return enabled