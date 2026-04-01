import os
import sys

# GitHub репозиторий
REPO_URL = "https://github.com/zxbruh/KoliUserbot"
REPO_NAME = "KoliUserbot"
AUTHOR = "@zxbruh"

# Telegram API (my.telegram.org)
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
SESSION_STRING = os.getenv("SESSION_STRING", "")

# Настройки KoliUB
PREFIX = os.getenv("PREFIX", ".")
OWNER_ID = int(os.getenv("OWNER_ID", 0))
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", 0)) if os.getenv("LOG_CHANNEL") else 0
LANGUAGE = os.getenv("LANGUAGE", "ru")

# Режимы
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
AUTO_BACKUP = os.getenv("AUTO_BACKUP", "True").lower() == "true"
AUTO_UPDATE = os.getenv("AUTO_UPDATE", "True").lower() == "true"

# Интерфейс
CFG_EMOJI = os.getenv("CFG_EMOJI", "🟢")
KOLI_VERSION = "1.0.0"

# Деплой
DEPLOY_PLATFORM = os.getenv("DEPLOY_PLATFORM", "local")
WEB_PORT = int(os.getenv("PORT", 8080))

def check_config():
    errors = []
    if API_ID == 0:
        errors.append("❌ API_ID не указан")
    if not API_HASH:
        errors.append("❌ API_HASH не указан")
    if OWNER_ID == 0:
        errors.append("❌ OWNER_ID не указан")
    
    if errors:
        print("\n".join(errors))
        print(f"\n📝 Создайте .env файл или получите API на my.telegram.org")
        print(f"\n🔗 Репозиторий: {REPO_URL}")
        return False
    return True

if not check_config():
    sys.exit(1)