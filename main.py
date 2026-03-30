import os, sys, asyncio, psutil, time, importlib
from pathlib import Path
from telethon import TelegramClient, events, Button
from database import db
from dotenv import load_dotenv

load_dotenv()

# --- КОНФИГУРАЦИЯ ---
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MOD_PATH = Path("modules/")
MOD_PATH.mkdir(exist_ok=True)

# Инициализация клиентов
client = TelegramClient('koli_user', API_ID, API_HASH)
bot = TelegramClient('koli_bot', API_ID, API_HASH)

# Реестр команд и модулей
CMD_HELP = {}
LOADED_MODS = {}

# --- ЛОАДЕР (ПРОФЕССИОНАЛЬНЫЙ) ---
def load_plugins():
    import logging
    logging.basicConfig(level=logging.ERROR)
    
    count = 0
    for file in MOD_PATH.glob("*.py"):
        name = file.stem
        path = f"modules.{name}"
        try:
            spec = importlib.util.spec_from_file_location(path, file)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            LOADED_MODS[name] = load
            count += 1
        except Exception as e:
            print(f"❌ Ошибка в {name}: {e}")
    return count

# --- СИСТЕМНЫЕ КНОПКИ ---
MAIN_MENU = [
    [Button.inline("🛰 Ядро", data="core"), Button.inline("📦 Плагины", data="mods")],
    [Button.inline("🔄 Рестарт", data="restart"), Button.inline("🔻 Закрыть", data="close")]
]

# --- ОБРАБОТЧИК ЮЗЕРБОТА ---
@client.on(events.NewMessage(outgoing=True))
async def global_handler(event):
    pref = db.get("prefix") or "."
    text = event.raw_text
    if not text.startswith(pref): return
    
    cmd = text[len(pref):].split(maxsplit=1)[0].lower()

    # Базовые команды ядра
    if cmd == "конфиг":
        bot_me = await bot.get_me()
        res = await client.inline_query(bot_me.username, "main")
        await res[0].click(event.chat_id)
        await event.delete()
    
    elif cmd == "пинг":
        start = time.time()
        await client.get_me()
        end = round((time.time() - start) * 1000)
        await event.edit(f"🚀 **Понг!**\n`{end} ms`")

# --- ИНЛАЙН УПРАВЛЕНИЕ ---
@bot.on(events.InlineQuery)
async def inline_base(event):
    if event.query.query == "main":
        await event.answer([event.builder.article("KoliUB", text="⚙️ **Центр управления KoliUserbot**", buttons=MAIN_MENU)])

@bot.on(events.CallbackQuery)
async def callback_manager(event):
    data = event.data.decode()
    pref = db.get("prefix") or "."

    if data == "close": await event.edit("❌ Меню закрыто")
    elif data == "restart":
        await event.edit("🔄 **Перезагрузка системы...**")
        os.execl(sys.executable, sys.executable, *sys.argv)
    
    elif data == "core":
        await event.edit(f"🛰 **Настройки Ядра**\n\nПрефикс: `{pref}`", buttons=[
            [Button.inline("Точка .", data="sp_."), Button.inline("Воскл !", data="sp_!")],
            [Button.inline("⬅️ Назад", data="back")]
        ])
    
    elif data.startswith("sp_"):
        new = data.split("_")[1]
        db.set("prefix", new)
        await event.answer(f"Префикс: {new}", alert=True)
        await event.edit("⚙️ **Центр управления KoliUserbot**", buttons=MAIN_MENU)

    elif data == "mods":
        btns = []
        for name in LOADED_MODS.keys():
            btns.append([Button.inline(f"🛠 {name}", data=f"set_{name}")])
        btns.append([Button.inline("⬅️ Назад", data="back")])
        await event.edit("📦 **Список активных модулей:**", buttons=btns)

    elif data == "back":
        await event.edit("⚙️ **Центр управления KoliUserbot**", buttons=MAIN_MENU)

# --- ЗАПУСК ---
async def start_ub():
    await client.start()
    await bot.start(bot_token=BOT_TOKEN)
    m_count = load_plugins()
    print(f"✅ Юзербот запущен! Модулей: {m_count}")
    await asyncio.gather(client.run_until_disconnected(), bot.run_until_disconnected())

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_ub())
