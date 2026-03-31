import sys, asyncio, os
from koli import koli_client, bot
from koli.utils import load_plugins
from database import db

async def start_koli_engine():
    print("🚀 Инициализация Koli-машины...")
    
    # Авторизация (ввод номера, кода и 2FA)
    await koli_client.start()
    await bot.start(bot_token=os.getenv("BOT_TOKEN"))
    
    # Загрузка всех модулей Koli
    plugins_count = load_plugins()
    print(f"✅ KoliUB запущен! Активно модулей: {plugins_count}")
    
    # Работа обоих клиентов без конфликтов
    await asyncio.gather(
        koli_client.run_until_disconnected(),
        bot.run_until_disconnected()
    )

if __name__ == "__main__":
    # Фикс ошибки "No current event loop" со скрина 2597.jpg
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_koli_engine())
