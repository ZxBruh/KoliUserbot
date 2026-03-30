import os
import sys
import time
import asyncio
import platform
import psutil
import subprocess
import importlib.util
from pathlib import Path
from datetime import datetime

# Telegram библиотеки
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from database import db
from dotenv import load_dotenv, set_key

# --- 1. АВТО-ЗАЩИТА (.gitignore) ---
def create_gitignore():
    path = Path(".gitignore")
    if not path.exists():
        content = ".env\n*.session\n*.session-journal\n*.db\n__pycache__/\ndownloads/\n"
        with open(path, "w") as f:
            f.write(content)
        print("🛡 .gitignore создан (ваши данные защищены).")

create_gitignore()

# --- 2. МАСТЕР НАСТРОЙКИ ---
env_path = Path(".env")
load_dotenv(dotenv_path=env_path)

def setup_wizard():
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")
    bot_token = os.getenv("BOT_TOKEN")

    if not api_id or not api_hash:
        print("\n🔧 --- ПЕРВИЧНАЯ НАСТРОЙКА KOLI ---")
        api_id = input("🔢 Введите API ID: ").strip()
        api_hash = input("✍️ Введите API HASH: ").strip()
        bot_token = input("🤖 Введите BOT TOKEN (из @BotFather): ").strip()

        if not env_path.exists(): env_path.touch()
        set_key(str(env_path), "API_ID", api_id)
        set_key(str(env_path), "API_HASH", api_hash)
        set_key(str(env_path), "BOT_TOKEN", bot_token)
        print("✅ Настройки сохранены в .env")
        return int(api_id), api_hash, bot_token
    return int(api_id), api_hash, bot_token

API_ID, API_HASH, BOT_TOKEN = setup_wizard()
REPO_URL = "https://github.com/zxbruh/KoliUserbot"

# --- 3. ИНИЦИАЛИЗАЦИЯ ---
client = TelegramClient('koli_user', API_ID, API_HASH)
bot = TelegramClient('koli_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

START_TIME = time.time()
MOD_PATH = Path("modules/")
for folder in [MOD_PATH, "downloads", "data"]: folder.mkdir(exist_ok=True)

# --- 4. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
async def get_stats():
    t1 = datetime.now()
    await client.get_me()
    ping = f"{(datetime.now() - t1).microseconds / 1000:.2f}ms"
    uptime_sec = int(time.time() - START_TIME)
    me = await client.get_me()
    
    # Определение хостинга
    host = "Heroku" if "DYNO" in os.environ else platform.node()
    plat = "Cloud" if "DYNO" in os.environ else "VPS/Local"

    return {
        "{me}": f"@{
