import platform, psutil
from telethon import events
from database import db

@events.register(events.NewMessage(outgoing=True))
async def handler(event):
    pref = db.get("prefix") or "."
    if event.raw_text.lower() == f"{pref}инфо":
        ram = psutil.virtual_memory().percent
        cpu = psutil.cpu_percent()
        text = (
            "<b>🪐 KoliUserbot Status</b>\n"
            f"💻 <b>Система:</b> {platform.system()} {platform.release()}\n"
            f"📊 <b>Загрузка RAM:</b> {ram}%\n"
            f"🔥 <b>Загрузка CPU:</b> {cpu}%"
        )
        await event.edit(text, parse_mode='html')
