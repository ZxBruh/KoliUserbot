import os
import sys

# Telegram API (получить на my.telegram.org)
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")

# Сессия (опционально, если уже есть)
SESSION_STRING = os.getenv("SESSION_STRING", "")

# Настройки KoliUB
PREFIX = os.getenv("PREFIX", ".")
OWNER_ID = int(os.getenv("OWNER_ID", 0))
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", 0)) if os.getenv("LOG_CHANNEL") else 0

# Режимы
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Интерфейс
CFG_EMOJI = os.getenv("CFG_EMOJI", "🟢")
KOLI_VERSION = "1.0.0"

# Проверка конфигурации
def check_config():
    """Проверка обязательных параметров"""
    errors = []
    
    if API_ID == 0:
        errors.append("❌ API_ID не указан")
    if not API_HASH:
        errors.append("❌ API_HASH не указан")
    if OWNER_ID == 0:
        errors.append("❌ OWNER_ID не указан (ваш Telegram ID)")
    
    if errors:
        print("\n".join(errors))
        print("\n📝 Создайте файл .env со следующими параметрами:")
        print("""
API_ID=123456
API_HASH=your_api_hash_here
OWNER_ID=123456789  # ваш Telegram ID
PREFIX=.
CFG_EMOJI=🟢
DEBUG=False
        """)
        return False
    
    return True

if not check_config():
    sys.exit(1)