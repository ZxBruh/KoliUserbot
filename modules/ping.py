from telethon import events
import time

@events.register(events.NewMessage(outgoing=True, pattern=r"\.пинг"))
async def ping(event):
    start = time.time()
    await event.edit("<code>Проверка...</code>")
    end = time.time()
    await event.edit(f"<b>🏓 Понг!</b>\n<code>{(end - start) * 1000:.2f}мс</code>")
