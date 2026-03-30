import os, sys, asyncio, psutil, subprocess, importlib.util, time
from pathlib import Path
from datetime import datetime
from telethon import TelegramClient, events, Button
from database import db
from dotenv import load_dotenv, set_key

load_dotenv()
MOD_PATH = Path("modules/")
MOD_PATH.mkdir(exist_ok=True)

def setup():
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")
    bot_token = os.getenv("BOT_TOKEN")
    if not all([api_id, api_hash, bot_token]):
        sys.exit("❌ Ошибка в .env")
    return int(api_id), api_hash, bot_token

API_ID, API_HASH, BOT_TOKEN = setup()
loop = asyncio.get_event_loop()
client = TelegramClient('koli_user', API_ID, API_HASH, loop=loop)
bot = TelegramClient('koli_bot', API_ID, API_HASH, loop=loop)
START_TIME = time.time()

def load_modules():
    count = 0
    for file in MOD_PATH.glob("*.py"):
        try:
            name = file.stem
            spec = importlib.util.spec_from_file_location(name, file)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            client.add_event_handler(mod.handler, events.NewMessage(outgoing=True))
            count += 1
        except: pass
    return count

MAIN_BTNS = [
    [Button.inline("🛰 Ядро", data="core"), Button.inline("📦 Внешние", data="mods")],
    [Button.inline("🔄 Обновить", data="upd"), Button.inline("🔻 Закрыть", data="close")]
]

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
    elif cmd == "конфиг":
        me = await bot.get_me()
        res = await client.inline_query(me.username, "menu")
        await res[0].click(event.chat_id)
        await event.delete()
    elif cmd == "загрузить":
        if not event.is_reply: return await event.edit("<b>❌ Ответь на .py файл!</b>")
        reply = await event.get_reply_message()
        fname = reply.file.name
        await client.download_media(reply, f"modules/{fname}")
        await event.edit(f"<b>✅ Модуль {fname} готов!</b>\nРестарт...")
        os.execl(sys.executable, sys.executable, *sys.argv)
    elif cmd == "рестарт":
        await event.edit("<b>⏳ Рестарт...</b>")
        os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on(events.InlineQuery)
async def inline_handler(event):
    if event.query.query == "menu":
        await event.answer([event.builder.article("KoliUB", text="⚙️ **Меню управления:**", buttons=MAIN_BTNS)])

@bot.on(events.CallbackQuery)
async def call_handler(event):
    if event.data == b"close": await event.edit("❌ Закрыто")
    elif event.data == b"back": await event.edit("⚙️ **Меню управления:**", buttons=MAIN_BTNS)
    
    # ЛОГИКА ЯДРА
    elif event.data == b"core":
        txt = f"🛰 **Ядро KoliUB**\nПрефикс: `{db.get('prefix') or '.'}`"
        btns = [[Button.inline("Префикс .", data="p_."), Button.inline("Префикс !", data="p_!")], [Button.inline("⬅️ Назад", data="back")]]
        await event.edit(txt, buttons=btns)
    elif event.data.startswith(b"p_"):
        db.set("prefix", event.data.decode().split("_")[1])
        await event.answer("✅ Готово", alert=True)
        await event.edit("⚙️ **Меню управления:**", buttons=MAIN_BTNS)

    # ЛОГИКА ВНЕШНИХ МОДУЛЕЙ (ТО ЧТО ТЫ ПРОСИЛ)
    elif event.data == b"mods":
        files = [f.name for f in MOD_PATH.glob("*.py")]
        txt = "📦 **Загруженные модули:**\n\n" + ("\n".join([f"• `{f}`" for f in files]) if files else "Пусто...")
        # Если есть модуль 'секрет', добавим кнопку для него
        btns = []
        if "secret.py" in files:
            btns.append([Button.inline("🤫 Настройки Secret", data="mod_secret")])
        btns.append([Button.inline("⬅️ Назад", data="back")])
        await event.edit(txt, buttons=btns)

    # ПЕРЕХОД В КОНФИГ МОДУЛЯ (Пример для модуля secret)
    elif event.data == b"mod_secret":
        await event.edit("🤫 **Конфиг модуля Secret:**\nТут можно что-то включить...", buttons=[Button.inline("⬅️ Назад в модули", data="mods")])

async def start():
    await client.start()
    await bot.start(bot_token=BOT_TOKEN)
    load_modules()
    await asyncio.gather(client.run_until_disconnected(), bot.run_until_disconnected())

if __name__ == "__main__":
    loop.run_until_complete(start())
