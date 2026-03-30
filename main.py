import os, sys, asyncio, psutil, subprocess, importlib.util, time
from pathlib import Path
from datetime import datetime
from telethon import TelegramClient, events, Button
from database import db
from dotenv import load_dotenv, set_key

# --- ИНИЦИАЛИЗАЦИЯ ---
load_dotenv()
MOD_PATH = Path("modules/")
MOD_PATH.mkdir(exist_ok=True)

def setup():
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")
    bot_token = os.getenv("BOT_TOKEN")
    if not all([api_id, api_hash, bot_token]):
        print("❌ Ошибка: Проверь .env файл!")
        sys.exit()
    return int(api_id), api_hash, bot_token

API_ID, API_HASH, BOT_TOKEN = setup()
loop = asyncio.get_event_loop()
client = TelegramClient('koli_user', API_ID, API_HASH, loop=loop)
bot = TelegramClient('koli_bot', API_ID, API_HASH, loop=loop)
START_TIME = time.time()

# --- ЛОАДЕР МОДУЛЕЙ (ИСПРАВЛЕННЫЙ) ---
def load_modules():
    count = 0
    for file in MOD_PATH.glob("*.py"):
        try:
            name = file.stem
            spec = importlib.util.spec_from_file_location(name, file)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            # Фикс ошибки AttributeError: передаем только текстовые сообщения
            client.add_event_handler(mod.handler, events.NewMessage(outgoing=True))
            count += 1
        except Exception as e:
            print(f"❌ Ошибка в модуле {file.name}: {e}")
    return count

# --- КНОПКИ ---
MAIN_BTNS = [
    [Button.inline("🛰 Ядро", data="core"), Button.inline("📦 Внешние", data="mods")],
    [Button.inline("🔄 Обновить", data="upd"), Button.inline("🔻 Закрыть", data="close")]
]

# --- ОБРАБОТЧИК ЯДРА ---
@client.on(events.NewMessage(outgoing=True))
async def koli_handler(event):
    pref = db.get("prefix") or "."
    msg = event.raw_text
    if not msg.startswith(pref): return
    
    cmd = msg[len(pref):].split(maxsplit=1)[0].lower()

    if cmd == "пинг":
        start = datetime.now()
        await client.get_me()
        p = (datetime.now() - start).microseconds / 1000
        await event.edit(f"<b>🚀 Понг!</b>\n<code>{p} ms</code>", parse_mode='html')

    elif cmd == "инфо":
        uptime = str(datetime.now() - datetime.fromtimestamp(START_TIME)).split('.')[0]
        ram = psutil.virtual_memory().percent
        await event.edit(f"<b>🪐 KoliUB</b>\n\n⏱ <b>Аптайм:</b> <code>{uptime}</code>\n📊 <b>ОЗУ:</b> <code>{ram}%</code>", parse_mode='html')

    elif cmd == "конфиг":
        me = await bot.get_me()
        res = await client.inline_query(me.username, "menu")
        await res[0].click(event.chat_id)
        await event.delete()

    elif cmd == "загрузить":
        if not event.is_reply: return await event.edit("<b>❌ Ответь на .py файл!</b>", parse_mode='html')
        reply = await event.get_reply_message()
        if not reply.file or not reply.file.name.endswith(".py"): return await event.edit("<b>❌ Это не файл модуля!</b>")
        
        fname = reply.file.name
        await client.download_media(reply, f"modules/{fname}")
        await event.edit(f"<b>✅ Модуль <code>{fname}</code> установлен!</b>\nРестарт...", parse_mode='html')
        await asyncio.sleep(1)
        os.execl(sys.executable, sys.executable, *sys.argv)

    elif cmd == "рестарт":
        await event.edit("<b>⏳ Перезагрузка...</b>", parse_mode='html')
        os.execl(sys.executable, sys.executable, *sys.argv)

# --- ЛОГИКА ИНЛАЙН-БОТА ---
@bot.on(events.InlineQuery)
async def inline_handler(event):
    if event.query.query == "menu":
        await event.answer([event.builder.article("KoliUB", text="⚙️ **Выберите категорию:**", buttons=MAIN_BTNS)])

@bot.on(events.CallbackQuery)
async def call_handler(event):
    pref = db.get("prefix") or "."
    if event.data == b"close": await event.edit("❌ Меню закрыто")
    elif event.data == b"core":
        txt = f"🛰 **Настройки Ядра**\n\nПрефикс: `{pref}`\nВерсия: `1.1.0`"
        btns = [[Button.inline("Префикс .", data="p_."), Button.inline("Префикс !", data="p_!")], [Button.inline("⬅️ Назад", data="back")]]
        await event.edit(txt, buttons=btns)
    elif event.data.startswith(b"p_"):
        new_p = event.data.decode().split("_")[1]
        db.set("prefix", new_p)
        await event.answer(f"✅ Префикс: {new_p}", alert=True)
        await event.edit("⚙️ **Выберите категорию:**", buttons=MAIN_BTNS)
    elif event.data == b"back":
        await event.edit("⚙️ **Выберите категорию:**", buttons=MAIN_BTNS)

# --- СТАРТ ---
async def start():
    await client.start()
    await bot.start(bot_token=BOT_TOKEN)
    m_count = load_modules()
    print(f"🚀 Бот онлайн! Загружено модулей: {m_count}")
    await asyncio.gather(client.run_until_disconnected(), bot.run_until_disconnected())

if __name__ == "__main__":
    loop.run_until_complete(start())
