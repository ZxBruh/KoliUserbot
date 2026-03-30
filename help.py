from telethon import events
from database import db

@events.register(events.NewMessage(outgoing=True))
async def handler(event):
    pref = db.get("prefix") or "."
    if event.raw_text.lower() == f"{pref}хелп":
        text = (
            "<b>🗂 Список команд KoliUB:</b>\n\n"
            f"<code>{pref}инфо</code> — Состояние сервера\n"
            f"<code>{pref}хелп</code> — Это меню\n"
            f"<code>{pref}restart</code> — Перезагрузить бота\n"
            f"<code>{pref}обнова</code> — Обновить с GitHub"
        )
        await event.edit(text, parse_mode='html')
