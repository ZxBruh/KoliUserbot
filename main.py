import os, sys, time, asyncio, platform, psutil, subprocess, importlib.util
from pathlib import Path
from datetime import datetime
from telethon import TelegramClient, events
from database import db
from dotenv import load_dotenv, set_key

# --- КОНФИГУРАЦИЯ И ПАПКИ ---
env_path = Path(".env")
load_dotenv(dotenv_path=env_path)
MOD_PATH = Path("modules/")

# Создаем нужные папки корректно
for p in [MOD_PATH, Path("downloads"), Path("data")]:
    p.mkdir(exist_ok=True)

def setup_wizard():
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")
    if not api_id or not api_hash:
        print("\n🔧 ПЕРВИЧНАЯ НАСТРОЙКА KOLI")
        api_id = input("Введите API ID: ").strip()
        api_hash = input("Введите API HASH: ").strip()
        set_key(str(env_path), "API_ID", api_id)
        set_key(str(env_path), "API_HASH", api_hash)
    return int(api_id), api_hash

API_ID, API_HASH = setup_wizard()
client = TelegramClient('koli_user', API_ID, API_HASH)
START_TIME = time.time()

# --- ОСНОВНОЙ ОБРАБОТЧИК КОМАНД ---
@client.on(events.NewMessage(outgoing=True))
async def koli_main_handler(event):
    pref = db.get("prefix") or "."
    text = event.raw_text
    
    if not text.startswith(pref):
        return

    # Разбираем команду и аргументы
    cmd_part = text[len(pref):].split(maxsplit=1)
    cmd = cmd_part[0].lower()
    args = cmd_part[1] if len(cmd_part) > 1 else ""

    # 1. КОМАНДА .ИНФО
    if cmd == "инфо":
        uptime = str(datetime.now() - datetime.fromtimestamp(START_TIME)).split('.')[0]
        ram = psutil.virtual_memory().percent
        cpu = psutil.cpu_percent()
        
        # Замер пинга
        t1 = datetime.now()
        await client.get_me()
        ping = (datetime.now() - t1).microseconds / 1000
        
        text_info = (
            "<b>🪐 KoliUserbot</b>\n\n"
            f"⏱ <b>Uptime:</b> <code>{uptime}</code>\n"
            f"📡 <b>Ping:</b> <code>{ping} ms</code>\n"
            f"📊 <b>RAM:</b> <code>{ram}%</code>\n"
            f"🔥 <b>CPU:</b> <code>{cpu}%</code>\n"
            f"💻 <b>OS:</b> <code>{platform.system()}</code>"
        )
        await event.edit(text_info, parse_mode='html')

    # 2. КОМАНДА .ХЕЛП
    elif cmd == "хелп":
        help_text = (
            "<b>❓ Меню помощи KoliUB</b>\n\n"
            f"<code>{pref}инфо</code> — Статус бота\n"
            f"<code>{pref}хелп</code> — Список команд\n"
            f"<code>{pref}restart</code> — Перезагрузка\n"
            f"<code>{pref}обнова</code> — Обновить с GitHub\n"
            f"<code>{pref}bash [код]</code> — Консоль"
        )
        await event.edit(help_text, parse_mode='html')

    # 3. КОМАНДА .RESTART
    elif cmd == "restart":
        await event.edit("<b>⏳ Перезагрузка...</b>", parse_mode='html')
        db.set_temp("restart_chat", event.chat_id)
        os.execl(sys.executable, sys.executable, *sys.argv)

    # 4. КОМАНДА .ОБНОВА
    elif cmd == "обнова":
        await event.edit("<b>🔄 Обновляюсь...</b>", parse_mode='html')
        try:
            subprocess.check_output(["git", "pull"])
            await event.respond("<b>✅ Файлы обновлены! Перезапуск...</b>", parse_mode='html')
            os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as e:
            await event.edit(f"❌ Ошибка обновления: <code>{e}</code>", parse_mode='html')

    # 5. КОМАНДА .BASH
    elif cmd in ["bash", "терм"]:
        if not args:
            return await event.edit("<b>❌ Введите команду!</b>", parse_mode='html')
        
        proc = await asyncio.create_subprocess_shell(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = await proc.communicate()
        res = (out + err).decode()
        await event.edit(f"<b>💻 Shell:</b>\n<code>{res[:4000]}</code>", parse_mode='html')

# --- ЗАГРУЗКА ВНЕШНИХ МОДУЛЕЙ ---
def load_external():
    count = 0
    for file in MOD_PATH.glob("*.py"):
        try:
            spec = importlib.util.spec_from_file_location(file.stem, file)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            count += 1
        except:
            continue
    return count

# --- ЗАПУСК ---
async def start_koli():
    await client.start()
    
    # Сообщение после рестарта
    chat_id = db.get_temp("restart_chat")
    if chat_id:
        await client.send_message(int(chat_id), "<b>🚀 Бот запущен и готов!</b>", parse_mode='html')
        db.del_temp("restart_chat")
    
    mods_count = load_external()
    print(f"🚀 KoliUserbot онлайн! Модулей: {mods_count}")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(start_koli())
