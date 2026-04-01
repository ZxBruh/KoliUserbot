#!/usr/bin/env python3
"""
KoliUB - Fully Automated Telegram UserBot
GitHub: https://github.com/zxbruh/KoliUserbot
Author: @zxbruh
Version: 1.0.0
"""

import asyncio
import logging
import sys
import os
import signal
from datetime import datetime
from telethon import TelegramClient, errors
from telethon.sessions import StringSession
from dotenv import load_dotenv

load_dotenv()
from config import *
from database import Database
from bot import KoliBot

# Логирование
logging.basicConfig(
    format='\033[36m[%(levelname)s]\033[0m %(asctime)s - %(name)s: %(message)s',
    level=logging.INFO if not DEBUG else logging.DEBUG,
    handlers=[
        logging.FileHandler('koli.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Баннер
BANNER = f"""
\033[95m
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    ██╗  ██╗ ██████╗ ██╗     ██╗██╗   ██╗██████╗             ║
║    ██║ ██╔╝██╔═══██╗██║     ██║██║   ██║██╔══██╗            ║
║    █████╔╝ ██║   ██║██║     ██║██║   ██║██████╔╝            ║
║    ██╔═██╗ ██║   ██║██║     ██║██║   ██║██╔══██╗            ║
║    ██║  ██╗╚██████╔╝███████╗██║╚██████╔╝██████╔╝            ║
║    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝ ╚═════╝ ╚═════╝             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
\033[0m
\033[93m⚡ KoliUB v{KOLI_VERSION} | GitHub: github.com/zxbruh/KoliUserbot\033[0m
\033[90m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m
"""

def show_banner():
    print(BANNER)

def signal_handler(sig, frame):
    logger.info("👋 KoliUB остановлен")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

async def main():
    show_banner()
    logger.info(f"{CFG_EMOJI} Запуск KoliUB v{KOLI_VERSION}")
    logger.info(f"📦 Репозиторий: github.com/zxbruh/KoliUserbot")
    
    bot = KoliBot()
    await bot.start()
    await bot.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 KoliUB остановлен")
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        sys.exit(1)