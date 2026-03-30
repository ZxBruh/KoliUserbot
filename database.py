import sqlite3

class Database:
    def __init__(self):
        # Создаем файл базы данных koli.db
        self.conn = sqlite3.connect("koli.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._setup()

    def _setup(self):
        # Таблица для постоянных настроек
        self.cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
        # Таблица для временных данных (чтобы бот помнил сообщение при .restart)
        self.cursor.execute("CREATE TABLE IF NOT EXISTS temp_data (key TEXT PRIMARY KEY, value TEXT)")
        
        # Настройки по умолчанию
        defaults = [
            ('prefix', '.'),
            ('info_template', "🪐 **Koli UB**\n\n👤 **User:** {me}\n🌐 **Host:** {hostname}\n💻 **OS:** {os}\n⏱ **Ping:** {ping}\n📊 **RAM:** {ram_usage}")
        ]
        for key, val in defaults:
            self.cursor.execute("INSERT OR IGNORE INTO settings VALUES (?, ?)", (key, val))
        self.conn.commit()

    def get(self, key):
        self.cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
        res = self.cursor.fetchone()
        return res[0] if res else None

    def set(self, key, val):
        self.cursor.execute("UPDATE settings SET value=? WHERE key=?", (val, key))
        self.conn.commit()

    def set_temp(self, key, val):
        self.cursor.execute("INSERT OR REPLACE INTO temp_data VALUES (?, ?)", (key, str(val)))
        self.conn.commit()

    def get_temp(self, key):
        self.cursor.execute("SELECT value FROM temp_data WHERE key=?", (key,))
        res = self.cursor.fetchone()
        return res[0] if res else None

    def del_temp(self, key):
        self.cursor.execute("DELETE FROM temp_data WHERE key=?", (key,))
        self.conn.commit()

# Создаем экземпляр базы для использования в main.py
db = Database()
