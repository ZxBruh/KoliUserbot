
#!/usr/bin/env python3
"""
KoliUB - Telegram UserBot
GitHub: github.com/zxbruh/KoliUserbot
"""

import asyncio
import logging
import sys
import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

load_dotenv()

from config import *
from database import Database
from bot import KoliBot

logging.basicConfig(
    format='[%(levelname)s] %(asctime)s - %(name)s: %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BANNER = """
\033[95m
    ██╗  ██╗ ██████╗ ██╗     ██╗██╗   ██╗██████╗ 
    ██║ ██╔╝██╔═══██╗██║     ██║██║   ██║██╔══██╗
    █████╔╝ ██║   ██║██║     ██║██║   ██║██████╔╝
    ██╔═██╗ ██║   ██║██║     ██║██║   ██║██╔══██╗
    ██║  ██╗╚██████╔╝███████╗██║╚██████╔╝██████╔╝
    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝ ╚═════╝ ╚═════╝ 
\033[0m
\033[93m⚡ KoliUB v1.0 | Created by @zxbruh\033[0m
"""

async def main():
    print(BANNER)
    logger.info("Запуск KoliUB...")
    
    bot = KoliBot()
    await bot.start()
    await bot.load_handlers()
    await bot.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("KoliUB остановлен")
        sys.exit(0)