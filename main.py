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
    
    host = "Heroku" if "DYNO" in os.environ else platform.node()
    plat = "Cloud" if "DYNO" in os.environ else "VPS/Local"

    return {
        "{me}": f"@{me.username}" if me.username else me.first_name,
        "{prefix}": db.get("prefix"),
        "{platform}": plat,
        "{uptime}": f"{uptime_sec // 3600}h {(uptime_sec % 3600) // 60}m",
        "{ram_usage}": f"{psutil.virtual_memory().percent()}%",
        "{hostname}": host,
        "{os}": platform.system(),
        "{ping}": ping
    }

# --- 5. АВТОРИЗАЦИЯ И РЕСТАРТ-РЕПОРТ ---
async def start_koli():
    await client.connect()
    if not await client.is_user_authorized():
        phone = input("📱 Номер телефона (с +): ")
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input("🔢 Код из Телеграм: "))
        except SessionPasswordNeededError:
            await client.sign_in(password=input("🔐 Облачный пароль: "))

    c_id = db.get_temp("restart_chat")
    m_id = db.get_temp("restart_msg")
    if c_id and m_id:
        try:
            await client.edit_message(int(c_id), int(m_id), "<b>✅ KoliUserbot успешно перезапущен!</b>", parse_mode='html')
        except: pass
        db.del_temp("restart_chat")
        db.del_temp("restart_msg")

# --- 6. ОБРАБОТКА КОМАНД ---
@client.on(events.NewMessage(outgoing=True))
async def main_handler(event):
    prefix = db.get("prefix")
    if not event.raw_text.startswith(prefix): return
    
    parts = event.raw_text[len(prefix):].split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    if cmd == "restart":
        msg = await event.edit("<b>⏳ Перезагрузка...</b>", parse_mode='html')
        db.set_temp("restart_chat", event.chat_id)
        db.set_temp("restart_msg", msg.id)
        os.execl(sys.executable, sys.executable, *sys.argv)

    elif cmd == "обнова":
        await event.edit("<b>🔄 Проверка обновлений...</b>", parse_mode='html')
        try:
            subprocess.check_output(["git", "pull", REPO_URL])
            msg = await event.respond("<b>🚀 Обновление скачано! Перезапуск...</b>")
            db.set_temp("restart_chat", event.chat_id)
            db.set_temp("restart_msg", msg.id)
            os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as e:
            await event.edit(f"❌ Ошибка Git: `{e}`")

    elif cmd == "инфо":
        template = db.get("info_template")
        stats = await get_stats()
        for k, v in stats.items():
            template = template.replace(k, str(v))
        await event.edit(template)

    elif cmd == "префикс" and args:
        db.set("prefix", args)
        await event.edit(f"✅ Новый префикс: `{args}`")

    elif cmd in ["терм", "bash"] and args:
        proc = await asyncio.create_subprocess_shell(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = await proc.communicate()
        await event.edit(f"<b>💻 Shell:</b>\n<code>{(out + err).decode()[:4000]}</code>", parse_mode='html')

# --- ЗАПУСК ---
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_koli())
    print("🚀 [Koli] Активен и готов.")
    loop.run_until_complete(asyncio.gather(client.run_until_disconnected(), bot.run_until_disconnected()))
