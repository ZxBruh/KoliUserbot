import os, sys, asyncio, platform, psutil, subprocess, importlib.util, time
from pathlib import Path
from datetime import datetime
from telethon import TelegramClient, events, Button
from database import db
from dotenv import load_dotenv, set_key

# --- СИСТЕМНЫЙ БЛОК (ЛОАДЕР) ---
load_dotenv()
MOD_PATH = Path("modules/")
MOD_PATH.mkdir(exist_ok=True)

def setup():
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")
    bot_token = os.getenv("BOT_TOKEN")
    if not all([api_id, api_hash, bot_token]):
        print("🔧 Первая настройка...")
        api_id = input("API ID: "); api_hash = input("API HASH: "); bot_token = input("BOT TOKEN: ")
        set_key(".env", "API_ID", api_id); set_key(".env", "API_HASH", api_hash); set_key(".env", "BOT_TOKEN", bot_token)
    return int(api_id), api_hash, bot_token

API_ID, API_HASH, BOT_TOKEN = setup()
loop = asyncio.get_event_loop()
client = TelegramClient('koli_user', API_ID, API_HASH, loop=loop)
bot = TelegramClient('koli_bot', API_ID, API_HASH, loop=loop)
START_TIME = time.time()

# --- ХРАНИЛИЩЕ МОДУЛЕЙ ---
LOADED_MODULES = {}

def load_all_modules():
    count = 0
    for file in MOD_PATH.glob("*.py"):
        try:
            name = file.stem
            spec = importlib.util.spec_from_file_location(name, file)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            LOADED_MODULES[name] = mod
            count += 1
        except Exception as e: print(f"❌ Ошибка в {file.name}: {e}")
    return count

# --- ОСНОВНЫЕ ФУНКЦИИ (ВШИТЫ) ---
@client.on(events.NewMessage(outgoing=True))
async def manager(event):
    pref = db.get("prefix") or "."
    if not event.raw_text.startswith(pref): return
    
    cmd = event.raw_text[len(pref):].split(maxsplit=1)[0].lower()
    
    # ПИНГ
    if cmd == "пинг":
        start = datetime.now()
        await client.get_me()
        p = (datetime.now() - start).microseconds / 1000
        await event.edit(f"<b>🚀 Понг!</b>\n<code>{p} ms</code>", parse_mode='html')

    # КОНФИГ (ИНЛАЙН)
    elif cmd == "конфиг":
        me = await bot.get_me()
        res = await client.inline_query(me.username, "main")
        await res[0].click(event.chat_id)
        await event.delete()

    # РЕСТАРТ / ОБНОВА
    elif cmd == "restart":
        await event.edit("<b>⏳ Перезагрузка...</b>", parse_mode='html')
        os.execl(sys.executable, sys.executable, *sys.argv)

# --- ИНЛАЙН ИНТЕРФЕЙС (КОНФИГ) ---
@bot.on(events.InlineQuery)
async def inline(event):
    if event.query.query == "main":
        b = [
            [Button.inline("Встроенные 🛰", data="core"), Button.inline("Модули 📦", data="mods")],
            [Button.inline("Обновить 🔄", data="update"), Button.inline("Закрыть 🔻", data="close")]
        ]
        await event.answer([event.builder.article("KoliUB Config", text="🪐 **Настройки KoliUserbot**", buttons=b)])

@bot.on(events.CallbackQuery)
async def callbacks(event):
    if event.data == b"close": await event.edit("❌ Меню закрыто")
    elif event.data == b"core":
        await event.edit("⚙️ **Ядро:**\nПрефикс: `.`\nВерсия: `1.0.0`", buttons=[Button.inline("⬅️ Назад", data="main")])
    elif event.data == b"main":
        b = [[Button.inline("Встроенные 🛰", data="core"), Button.inline("Модули 📦", data="mods")], [Button.inline("Закрыть 🔻", data="close")]]
        await event.edit("🪐 **Настройки KoliUserbot**", buttons=b)

# --- СТАРТ ---
async def start():
    await client.start()
    await bot.start(bot_token=BOT_TOKEN)
    mods = load_all_modules()
    print(f"🚀 Бот запущен! Загружено модулей: {mods}")
    await asyncio.gather(client.run_until_disconnected(), bot.run_until_disconnected())

if __name__ == "__main__":
    loop.run_until_complete(start())
