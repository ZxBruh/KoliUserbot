import os, sys, asyncio, time, importlib
from pathlib import Path
from telethon import TelegramClient, events, Button
from database import db
from dotenv import load_dotenv

# --- ИНИЦИАЛИЗАЦИЯ KoliUB ---
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Пути ребрендинга
MOD_PATH = Path("modules/")
MOD_PATH.mkdir(exist_ok=True)

# Клиенты Koli
client = TelegramClient('koli_session', API_ID, API_HASH)
bot = TelegramClient('koli_config_bot', API_ID, API_HASH)

# Реестры (как в оригинале, но для Koli)
KOLI_CMD_HELP = {}
LOADED_PLUGINS = {}

# --- СИСТЕМА РЕГИСТРАЦИИ КОМАНД (Koli-Decorator) ---
def koli_cmd(pattern=None, **kwargs):
    def decorator(func):
        # Автоматически добавляем префикс из БД
        pref = db.get("prefix") or "."
        actual_pattern = rf"\{pref}{pattern}" if pattern else None
        
        client.add_event_handler(
            func, 
            events.NewMessage(outgoing=True, pattern=actual_pattern, **kwargs)
        )
        return func
    return decorator

# --- ДИНАМИЧЕСКИЙ ЛОАДЕР ПЛАГИНОВ ---
def load_koli_plugins():
    count = 0
    for file in MOD_PATH.glob("*.py"):
        name = file.stem
        try:
            spec = importlib.util.spec_from_file_location(f"modules.{name}", file)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            LOADED_PLUGINS[name] = mod
            count += 1
        except Exception as e:
            print(f"⚠️ Ошибка загрузки модуля Koli [{name}]: {e}")
    return count

# --- КОМАНДЫ ЯДРА KOLI ---
@koli_cmd(pattern="пинг")
async def ping_koli(event):
    start = time.time()
    await client.get_me()
    end = round((time.time() - start) * 1000, 2)
    await event.edit(f"🛰 **KoliUB Online**\n⏱ **Отклик:** `{end} ms`")

@koli_cmd(pattern="конфиг")
async def config_koli(event):
    me = await bot.get_me()
    res = await client.inline_query(me.username, "koli_main")
    await res[0].click(event.chat_id)
    await event.delete()

# --- ИНЛАЙН ИНТЕРФЕЙС KOLI ---
@bot.on(events.InlineQuery)
async def koli_inline(event):
    if event.query.query == "koli_main":
        buttons = [
            [Button.inline("🛰 Koli Core", data="k_core"), Button.inline("📦 Koli Mods", data="k_mods")],
            [Button.inline("🔄 Перезапуск", data="k_re"), Button.inline("❌ Закрыть", data="k_cl")]
        ]
        await event.answer([event.builder.article("KoliUB Control", text="🛠 **Панель управления Koli Userbot**", buttons=buttons)])

@bot.on(events.CallbackQuery)
async def koli_callback(event):
    data = event.data.decode()
    if data == "k_cl": await event.edit("🔒 **Доступ закрыт**")
    elif data == "k_re":
        await event.edit("♻️ **KoliUB: Выполняется перезагрузка...**")
        os.execl(sys.executable, sys.executable, *sys.argv)
    elif data == "k_core":
        p = db.get("prefix") or "."
        await event.edit(f"🛰 **Ядро Koli**\n\nПрефикс: `{p}`\nВерсия: `2.0.0-Koli`", buttons=[[Button.inline("⬅️ Назад", data="k_back")]])
    elif data == "k_back":
        # Возврат в главное меню (повтор логики koli_inline)
        os.execl(sys.executable, sys.executable, *sys.argv) # Простейший способ обновить стейт

# --- СТАРТ СИСТЕМЫ ---
async def start_koli():
    print("🚀 Запуск Koli Userbot...")
    await client.start()
    await bot.start(bot_token=BOT_TOKEN)
    num = load_koli_plugins()
    print(f"✅ KoliUB готов. Загружено плагинов: {num}")
    await asyncio.gather(client.run_until_disconnected(), bot.run_until_disconnected())

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_koli())
