import asyncio
import os
import sys
import random
import logging
from telethon import TelegramClient, events

# Импорты ядра
try:
    from kolitl import database, loader, utils
    import _internal
except ImportError as e:
    print(f"❌ Критическая ошибка импорта: {e}")
    print("Убедитесь, что папка 'kolitl' создана и содержит __init__.py")
    sys.exit(1)

# Данные для маскировки (чтобы Telegram видел обычное устройство)
SYSTEMS = [
    ("Windows", "11", "Desktop"),
    ("Ubuntu", "24.04", "Server"),
    ("Android", "14", "Realme C75"),
    ("iOS", "17.2", "iPhone 15")
]

class KoliUB:
    def __init__(self):
        self.db = database.KoliDatabase()
        self.mod_loader = loader.ModuleLoader()
        self.clients = []
        self.loop = asyncio.get_event_loop()

    def get_sessions(self):
        return [f.replace(".session", "") for f in os.listdir(".") if f.endswith(".session")]

    async def authorize(self):
        print("\n🔑 --- РЕГИСТРАЦИЯ НОВОЙ СЕССИИ KOLI ---")
        api_id = input("Введите API ID: ")
        api_hash = input("Введите API HASH: ")
        phone = input("Введите номер телефона (с +): ")
        
        session_name = f"koli-{phone.replace('+', '')}"
        client = TelegramClient(session_name, int(api_id), api_hash)
        
        await client.start(phone=lambda: phone)
        print(f"✅ Сессия {session_name} успешно создана!")
        await client.disconnect()
        return session_name

    async def start_client(self, session_name):
        # Используем стандартные ключи или просим ввести, если сессия новая
        api_id = 2040 
        api_hash = "b18441a1ff76511093122b083c27636e"
        
        sys_name, sys_ver, device = random.choice(SYSTEMS)
        
        client = TelegramClient(
            session_name, 
            api_id, 
            api_hash,
            system_version=sys_ver,
            device_model=device,
            app_version="1.0.0 Koli"
        )

        # Обработчик команд
        @client.on(events.NewMessage(outgoing=True))
        async def cmd_handler(event):
            if event.raw_text.startswith("."):
                await self.mod_loader.handle_command(event)

        try:
            await client.start()
            self.clients.append(client)
            print(f"📡 Аккаунт {session_name} подключен (Имитация: {sys_name})")
        except Exception as e:
            print(f"💥 Ошибка запуска {session_name}: {e}")

    async def run(self):
        _internal.clear_console()
        _internal.print_banner()
        
        self.db.setup()
        self.mod_loader.load_all()

        sessions = self.get_sessions()
        
        if not sessions:
            print("⚠️ Сессии не найдены. Требуется вход.")
            new_s = await self.authorize()
            sessions = [new_s]

        # Запуск всех сессий
        for s in sessions:
            await self.start_client(s)

        print("\n🚀 KoliUB запущен. Жду команд в Telegram...")
        await asyncio.Event().wait()

if __name__ == "__main__":
    ub = KoliUB()
    try:
        ub.loop.run_until_complete(ub.run())
    except KeyboardInterrupt:
        print("\n🛑 KoliUB остановлен.")
