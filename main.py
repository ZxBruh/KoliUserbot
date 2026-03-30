import os, sys, time, asyncio, platform, psutil, subprocess, importlib.util
from pathlib import Path
from telethon import TelegramClient, events
from database import db
from dotenv import load_dotenv, set_key

# --- Инициализация папок ---
env_path = Path(".env")
load_dotenv(dotenv_path=env_path)
MOD_PATH = Path("modules/")
for folder in [MOD_PATH, Path("downloads"), Path("data")]: folder.mkdir(exist_ok=True)

def setup_wizard():
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")
    if not api_id or not api_hash:
        print("\n🔧 ПЕРВИЧНАЯ НАСТРОЙКА")
        api_id = input("API ID: "); api_hash = input("API HASH: ")
        set_key(str(env_path), "API_ID", api_id); set_key(str(env_path), "API_HASH", api_hash)
    return int(api_id), api_hash

API_ID, API_HASH = setup_wizard()
client = TelegramClient('koli_user', API_ID, API_HASH)

# --- Загрузчик модулей ---
def load_modules():
    count = 0
    for file in MOD_PATH.glob("*.py"):
        spec = importlib.util.spec_from_file_location(file.stem, file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, 'handler'):
            client.add_event_handler(mod.handler)
        count += 1
    return count

# --- Базовые команды (Рестарт и Обнова) ---
@client.on(events.NewMessage(outgoing=True))
async def base_handler(event):
    pref = db.get("prefix") or "."
    if not event.raw_text.startswith(pref): return
    cmd = event.raw_text[len(pref):].split(maxsplit=1)[0].lower()
    
    if cmd == "restart":
        await event.edit("<b>⏳ Перезагрузка...</b>", parse_mode='html')
        db.set_temp("restart_chat", event.chat_id); db.set_temp("restart_msg", event.id)
        os.execl(sys.executable, sys.executable, *sys.argv)
    
    elif cmd == "обнова":
        await event.edit("<b>🔄 Подтягиваю файлы с GitHub...</b>", parse_mode='html')
        try:
            subprocess.check_output(["git", "pull"])
            await event.respond("<b>🚀 Обновлено! Перезапускаюсь...</b>", parse_mode='html')
            os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as e:
            await event.edit(f"❌ Ошибка обновления: {e}")

# --- Запуск ---
async def start_bot():
    await client.start()
    # Проверка рестарта
    c_id = db.get_temp("restart_chat")
    if c_id:
        await client.send_message(int(c_id), "<b>✅ Бот успешно запущен и обновлен!</b>", parse_mode='html')
        db.del_temp("restart_chat")

    loaded = load_modules()
    print(f"📦 Загружено модулей: {loaded}")
    print("🚀 KoliUserbot запущен!")

if __name__ == "__main__":
    client.loop.run_until_complete(start_bot())
    client.run_until_disconnected()
