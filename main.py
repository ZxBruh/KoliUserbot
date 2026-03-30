import os, sys, time, asyncio, platform, psutil, subprocess, importlib.util
from pathlib import Path
from datetime import datetime
from telethon import TelegramClient, events
from database import db
from dotenv import load_dotenv, set_key

# --- ПОДГОТОВКА ---
env_path = Path(".env")
load_dotenv(dotenv_path=env_path)
MOD_PATH = Path("modules/")
for folder in [MOD_PATH, Path("downloads"), Path("data")]: 
    folder.mkdir(exist_ok=True)

def setup_wizard():
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")
    if not api_id or not api_hash:
        print("\n🔧 ПЕРВИЧНАЯ НАСТРОЙКА")
        api_id = input("Введите API ID: ").strip()
        api_hash = input("Введите API HASH: ").strip()
        set_key(str(env_path), "API_ID", api_id)
        set_key(str(env_path), "API_HASH", api_hash)
    return int(api_id), api_hash

API_ID, API_HASH = setup_wizard()
client = TelegramClient('koli_user', API_ID, API_HASH)
START_TIME = time.time()

# --- ВСТРОЕННЫЕ КОМАНДЫ (ВСЕГДА РАБОТАЮТ) ---

@client.on(events.NewMessage(outgoing=True))
async def koli_handler(event):
    pref = db.get("prefix") or "."
    text = event.raw_text
    if not text.startswith(pref): return
    
    cmd = text[len(pref):].split(maxsplit=1)[0].lower()
    args = text[len(pref):].split(maxsplit=1)[1] if len(text.split()) > 1 else ""

    # 1. КОМАНДА ХЕЛП
    if cmd == "хелп":
        help_text = (
            "<b>❓ Помощь KoliUserbot</b>\n\n"
            f"<code>{pref}инфо</code> - Статус сервера и бота\n"
            f"<code>{pref}хелп</code> - Список команд\n"
            f"<code>{pref}restart</code> - Перезагрузка\n"
            f"<code>{pref}обнова</code> - Обновить с GitHub\n"
            f"<code>{pref}bash [команда]</code> - Терминал"
        )
        await event.edit(help_text, parse_mode='html')

    # 2. КОМАНДА ИНФО
    elif cmd == "инфо":
        uptime = str(datetime.now() - datetime.fromtimestamp(START_TIME)).split('.')[0]
        ram = psutil.virtual_memory().percent
        cpu = psutil.cpu_percent()
        ping_start = datetime.now()
        await client.get_me()
        ping = (datetime.now() - ping_start).microseconds / 1000
        
        info_text = (
            "<b>🪐 KoliUserbot Status</b>\n\n"
            f"⏱ <b>Uptime:</b> <code>{uptime}</code>\n"
            f"📡 <b>Ping:</b> <code>{ping} ms</code>\n"
            f"📊 <b>RAM:</b> <code>{ram}%</code>\n"
            f"🔥 <b>CPU:</b> <code>{cpu}%</code>\n"
            f"💻 <b>OS:</b> <code>{platform.system()}</code>"
        )
        await event.edit(info_text, parse_mode='html')

    # 3. РЕСТАРТ
    elif cmd == "restart":
        await event.edit("<b>⏳ Перезагрузка...</b>", parse_mode='html')
        db.set_temp("restart_chat", event.chat_id)
        os.execl(sys.executable, sys.executable, *sys.argv)

    # 4. ОБНОВА
    elif cmd
