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
    if not all([api_id, api_hash, bot_token]): sys.exit("❌ Ошибка .env")
    return int(api_id), api_hash, bot_token

API_ID, API_HASH, BOT_TOKEN = setup()
loop = asyncio.get_event_loop()
client = TelegramClient('koli_user', API_ID, API_HASH, loop=loop)
bot = TelegramClient('koli_bot', API_ID, API_HASH, loop=loop)

# Хранилище загруженных модулей для доступа к их функциям настроек
LOADED_MODS = {}

def load_modules():
    LOADED_MODS.clear()
    count = 0
    for file in MOD_PATH.glob("*.py"):
        try:
            name = file.stem
            spec = importlib.util.spec_from_file_location(name, file)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            client.add_event_handler(mod.handler, events.NewMessage(outgoing=True))
            LOADED_MODS[name] = mod # Сохраняем модуль
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
    if not event.raw_text.startswith(pref): return
    cmd = event.raw_text[len(pref):].split(maxsplit=1)[0].lower()

    if cmd == "конфиг":
        me = await bot.get_me()
        res = await client.inline_query(me.username, "menu")
        await res[0].click(event.chat_id); await event.delete()
    elif cmd == "загрузить":
        if not event.is_reply: return await event.edit("<b>❌ Ответь на файл!</b>")
        reply = await event.get_reply_message()
        await client.download_media(reply, f"modules/{reply.file.name}")
        await event.edit("<b>✅ Модуль загружен! Рестарт...</b>")
        os.execl(sys.executable, sys.executable, *sys.argv)
    elif cmd == "рестарт":
        await event.edit("<b>⏳ Рестарт...</b>"); os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on(events.InlineQuery)
async def inline_handler(event):
    if event.query.query == "menu":
        await event.answer([event.builder.article("KoliUB", text="⚙️ **Меню управления:**", buttons=MAIN_BTNS)])

@bot.on(events.CallbackQuery)
async def call_handler(event):
    data = event.data.decode()
    
    if data == "close": await event.edit("❌ Закрыто")
    elif data == "back": await event.edit("⚙️ **Меню управления:**", buttons=MAIN_BTNS)
    
    # Кнопка "Внешние" — генерирует список кнопок для модулей
    elif data == "mods":
        btns = []
        # Проходим по всем загруженным модулям и ищем функцию 'get_buttons'
        for name, mod in LOADED_MODS.items():
            if hasattr(mod, "get_buttons"):
                btns.append([Button.inline(f"⚙️ {name}", data=f"set_{name}")])
        
        btns.append([Button.inline("⬅️ Назад", data="back")])
        await event.edit("📦 **Настройка внешних модулей:**", buttons=btns)

    # Обработка нажатия на конкретный модуль (динамически)
    elif data.startswith("set_"):
        mod_name = data.split("_")[1]
        if mod_name in LOADED_MODS:
            mod = LOADED_MODS[mod_name]
            # Вызываем функцию настроек самого модуля
            if hasattr(mod, "get_settings"):
                text, btns = await mod.get_settings(event)
                await event.edit(text, buttons=btns)

    # Переброс кликов обратно в модули (для их внутренних кнопок)
    elif data.startswith("mod_"):
        mod_name = data.split("_")[1]
        if mod_name in LOADED_MODS:
            await LOADED_MODS[mod_name].callback_handler(event)

    # Базовые настройки Ядра
    elif data == "core":
        btns = [[Button.inline("Префикс .", data="p_."), Button.inline("Префикс !", data="p_!")], [Button.inline("⬅️ Назад", data="back")]]
        await event.edit(f"🛰 **Ядро**\nПрефикс: `{db.get('prefix') or '.'}`", buttons=btns)
    elif data.startswith("p_"):
        db.set("prefix", data.split("_")[1]); await event.answer("✅ Ок", alert=True)
        await event.edit("⚙️ **Меню управления:**", buttons=MAIN_BTNS)

async def start():
    await client.start(); await bot.start(bot_token=BOT_TOKEN)
    load_modules(); await asyncio.gather(client.run_until_disconnected(), bot.run_until_disconnected())

if __name__ == "__main__": loop.run_until_complete(start())
