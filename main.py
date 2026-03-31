import asyncio
import os
import sys
import importlib
from telethon import TelegramClient, events

# Подключаем твое ядро
try:
    from kolitl import database, loader
    import _internal
except ImportError:
    print("❌ Ошибка: Проверь папку 'kolitl' и файл '_internal.py'!")
    sys.exit(1)

class KoliUB:
    def __init__(self):
        self.db = database.KoliDatabase()
        # Твои ключи (можно заменить на свои)
        self.api_id = 2040
        self.api_hash = "b18441a1ff76511093122b083c27636e"
        self.clients = []

    def get_sessions(self):
        return [f.replace(".session", "") for f in os.listdir(".") if f.endswith(".session")]

    async def load_modules(self, client):
        """Автоматически ищет и регистрирует команды из modules/"""
        mod_files = [f[:-3] for f in os.listdir("modules") if f.endswith(".py")]
        for name in mod_files:
            try:
                # Динамически импортируем файл
                module = importlib.import_module(f"modules.{name}")
                # Ищем в файле функцию-обработчик (например, ping_handler)
                for item in dir(module):
                    obj = getattr(module, item)
                    if callable(obj) and hasattr(obj, "event_handler"):
                        client.add_event_handler(obj)
                print(f"✅ Модуль {name} подключен к чату")
            except Exception as e:
                print(f"⚠️ Не удалось загрузить {name}: {e}")

    async def start_client(self, session):
        client = TelegramClient(session, self.api_id, self.api_hash)
        await client.start()
        
        # СТЫКОВКА: Загружаем команды в этот клиент
        await self.load_modules(client)
        
        self.clients.append(client)
        print(f"📡 Аккаунт {session} готов к командам!")

    async def run(self):
        _internal.print_banner()
        self.db.setup()
        
        sessions = self.get_sessions()
        if not sessions:
            print("⚠️ Сессий нет. Сначала создай .session файл!")
            return

        await asyncio.gather(*(self.start_client(s) for s in sessions))
        print("\n🚀 Бот запущен! Попробуй написать .пинг в Telegram.")
        await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(KoliUB().run())
    except KeyboardInterrupt:
        print("\nВыключение...")
