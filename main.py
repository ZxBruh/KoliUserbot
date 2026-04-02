#!/usr/bin/env python3
import asyncio, logging, sys
from telethon import TelegramClient
from bot import KoliBot

logging.basicConfig(format='[%(levelname)s] %(asctime)s - %(name)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BANNER = "\033[95m\n    ██╗  ██╗ ██████╗ ██╗     ██╗██╗   ██╗██████╗ \n    ██║ ██╔╝██╔═══██╗██║     ██║██║   ██║██╔══██╗\n    █████╔╝ ██║   ██║██║     ██║██║   ██║██████╔╝\n    ██╔═██╗ ██║   ██║██║     ██║██║   ██║██╔══██╗\n    ██║  ██╗╚██████╔╝███████╗██║╚██████╔╝██████╔╝\n    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝ ╚═════╝ ╚═════╝ \n\033[0m\033[93m⚡ KoliUB v1.0 | @zxbruh\033[0m"

async def main():
    print(BANNER)
    bot = KoliBot()
    await bot.start()
    await bot.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("KoliUB остановлен")