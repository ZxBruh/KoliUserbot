import os, sys, time, asyncio, platform, psutil, subprocess, importlib.util
from pathlib import Path
from datetime import datetime
from telethon import TelegramClient, events, Button
from database import db
from dotenv import load_dotenv, set_key

# --- ПОДГОТОВКА СРЕДЫ ---
env_path = Path(".env")
load_dotenv(dotenv_path=env_path)
MOD_PATH = Path("modules/")
for p in [MOD_PATH, Path("downloads"), Path("data")]: p.mkdir(exist_ok=True)

def setup_wizard():
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")
    bot_token = os.getenv("BOT_TOKEN") # Токен для кнопок
    if not api_id or not api_hash or not bot_token:
        print("\n🔧 ПЕРВИЧНАЯ НАСТРОЙКА KOLI")
        api_id = input("Введите API ID: ").strip()
        api_hash = input("Введите API HASH: ").strip()
        bot_token = input("Введите BOT TOKEN (от @BotFather): ").strip()
        set_key(str(env_path), "API_ID", api_id)
        set_key(str(env_path), "API_HASH", api_hash)
        set_key(str(env_path), "BOT_TOKEN", bot_token)
    return int(api_id), api_hash, bot_token

API_ID, API_HASH, BOT_TOKEN = setup_wizard()

# Клиент юзербота и клиент бота для кнопок
client = TelegramClient('koli_user', API_ID, API_HASH)
bot = TelegramClient('koli_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
START_TIME = time.time()

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
async def get_ping():
    t1 = datetime.now()
    await client.get_me()
    return f"{(datetime.now() - t1).microseconds / 1000:.2f}"

# --- ОБРАБОТЧИК КОМАНД ЮЗЕРБОТА ---
@client.on(events.NewMessage(outgoing=True))
async def koli_handler(event):
    pref = db.get("prefix") or "."
    text = event.raw_text
    if not text.startswith(pref): return

    parts = text[len(pref):].split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    # 1. ПИНГ
    if cmd in ["пинг", "ping"]:
        p = await get_ping()
        await event.edit(f"<b>🚀 Понг!</b>\n<code>{p} ms</code>", parse_mode='html')

    # 2. ИНФО
    elif cmd == "инфо":
        uptime = str(datetime.now() - datetime.fromtimestamp(START_TIME)).split('.')[0]
        ram = psutil.virtual_memory().percent
        p = await get_ping()
        await event.edit(
            f"<b>🪐 KoliUserbot</b>\n\n"
            f"⏱ <b>Uptime:</b> <code>{uptime}</code>\n"
            f"📡 <b>Ping:</b> <code>{p} ms</code>\n"
            f"📊 <b>RAM:</b> <code>{ram}%</code>", parse_mode='html'
        )

    # 3. ХЕЛП
    elif cmd == "хелп":
        await event.edit(
            f"<b>❓ Список команд:</b>\n"
            f"<code>{pref}пинг</code>, <code>{pref}инфо</code>, "
            f"<code>{pref}конфиг</code>, <code>{pref}restart</code>, "
            f"<code>{pref}обнова</code>", parse_mode='html'
        )

    # 4. КОНФИГ (МЕНЮ С КНОПКАМИ КАК НА ФОТО)
    elif cmd == "конфиг":
        # Используем инлайн-запрос через бота-помощника
        bot_user = await bot.get_me()
        results = await client.inline_query(bot_user.username, "main_config")
        await results[0].click(event.chat_id)
        await event.delete()

    # 5. СИСТЕМНЫЕ
    elif cmd == "restart":
        await event.edit("<b>⏳ Рестарт...</b>", parse_mode='html')
        db.set_temp("restart_chat", event.chat_id)
        os.execl(sys.executable, sys.executable, *sys.argv)

    elif cmd == "обнова":
        await event.edit("<b>🔄 Обновление...</b>", parse_mode='html')
        subprocess.check_output(["git", "pull"])
        os.execl(sys.executable, sys.executable, *sys.argv)

# --- ЛОГИКА КНОПОК (ИНЛАЙН МЕНЮ) ---
@bot.on(events.InlineQuery)
async def inline_handler(event):
    if event.query.query == "main_config":
        builder = event.builder
        buttons = [
            [Button.inline("Встроенные 🛰", data="cfg_core")],
            [Button.inline("Внешние 🛸", data="cfg_mods")],
            [Button.inline("Закрыть 🔻", data="cfg_close")]
        ]
        await event.answer([builder.article(
            "Настройки", 
            text="⚙️ **Выберите категорию для настройки**", 
            buttons=buttons
        )])

@bot.on(events.CallbackQuery)
async def callback_handler(event):
    if event.data == b"cfg_close":
        await event.edit("<b>❌ Меню закрыто</b>", parse_mode='html')
    elif event.data == b"cfg_core":
        await event.edit("<b>🛰 Настройки ядра:</b>\n\nЗдесь будет выбор префикса и эмодзи", 
                         buttons=[Button.inline("⬅️ Назад", data="main_config")])

# --- ЗАПУСК ---
async def start_koli():
    await client.start()
    chat_id = db.get_temp("restart_chat")
    if chat_id:
        await client.send_message(int(chat_id), "<b>✅ Бот онлайн!</b>", parse_mode='html')
        db.del_temp("restart_chat")
    print("🚀 Бот запущен!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(start_koli())
