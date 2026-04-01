#!/usr/bin/env python3
"""
KoliUB - Telegram UserBot
Author: @zxbruh
GitHub: github.com/zxbruh/koliub
"""

import asyncio
import logging
import sys
import os
import time
from datetime import datetime
from telethon import TelegramClient, events, errors
from telethon.sessions import StringSession
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Импорт конфига
from config import *

# Настройка логирования
logging.basicConfig(
    format='\033[36m[%(levelname)s]\033[0m %(asctime)s - %(name)s: %(message)s',
    level=logging.INFO if not DEBUG else logging.DEBUG,
    handlers=[
        logging.FileHandler('koli.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ========== БАННЕР ==========
BANNER = f"""
\033[95m
    ██╗  ██╗ ██████╗ ██╗     ██╗██╗   ██╗██████╗ 
    ██║ ██╔╝██╔═══██╗██║     ██║██║   ██║██╔══██╗
    █████╔╝ ██║   ██║██║     ██║██║   ██║██████╔╝
    ██╔═██╗ ██║   ██║██║     ██║██║   ██║██╔══██╗
    ██║  ██╗╚██████╔╝███████╗██║╚██████╔╝██████╔╝
    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝ ╚═════╝ ╚═════╝ 
\033[0m
\033[93m⚡ KoliUB v{KOLI_VERSION} | Created by @zxbruh\033[0m
\033[90m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m
"""

def show_banner():
    """Показывает баннер при запуске"""
    print(BANNER)

# ========== БАЗА ДАННЫХ ==========
class Database:
    """Простая база данных на JSON"""
    
    def __init__(self, db_file="koli_data.json"):
        self.db_file = db_file
        self.data = self.load()
    
    def load(self):
        """Загрузка данных из файла"""
        import json
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save(self):
        """Сохранение данных в файл"""
        import json
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def get(self, key, default=None):
        """Получить значение"""
        return self.data.get(key, default)
    
    def set(self, key, value):
        """Установить значение"""
        self.data[key] = value
        self.save()
    
    def delete(self, key):
        """Удалить ключ"""
        if key in self.data:
            del self.data[key]
            self.save()
    
    def all(self):
        """Все данные"""
        return self.data

# ========== ОСНОВНОЙ КЛИЕНТ ==========
class KoliUB:
    """Основной класс юзербота"""
    
    def __init__(self):
        self.client = None
        self.prefix = PREFIX
        self.owner = OWNER_ID
        self.db = Database()
        self.start_time = datetime.now()
        self.loaded_modules = {}
        
    async def start(self):
        """Запуск и авторизация"""
        show_banner()
        logger.info(f"{CFG_EMOJI} Инициализация KoliUB v{KOLI_VERSION}")
        
        # Создание клиента
        if SESSION_STRING:
            logger.info("🔑 Использование SESSION_STRING")
            self.client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
        else:
            logger.info("📁 Использование файла сессии")
            self.client = TelegramClient("koli_session", API_ID, API_HASH)
        
        # Запуск клиента
        await self.client.start()
        
        # Проверка авторизации
        try:
            me = await self.client.get_me()
            logger.info(f"✅ Авторизован: {me.first_name} (@{me.username})")
            logger.info(f"🆔 ID: {me.id}")
            
            # Сохраняем информацию о пользователе
            self.user = me
            
        except Exception as e:
            logger.error(f"❌ Ошибка авторизации: {e}")
            await self.create_new_session()
    
    async def create_new_session(self):
        """Создание новой сессии через терминал"""
        logger.info("🆕 Создание новой сессии")
        
        print("\n" + "="*50)
        print("📱 АВТОРИЗАЦИЯ В TELEGRAM")
        print("="*50)
        
        phone = input("📱 Введите номер телефона (+79991234567): ")
        
        try:
            await self.client.send_code_request(phone)
            code = input("🔐 Введите код из Telegram: ")
            
            try:
                await self.client.sign_in(phone, code)
            except errors.SessionPasswordNeededError:
                password = input("🔒 Введите облачный пароль (2FA): ")
                await self.client.sign_in(password=password)
            
            me = await self.client.get_me()
            logger.info(f"✅ Добро пожаловать, {me.first_name}!")
            
            # Сохраняем SESSION_STRING
            session_str = self.client.session.save()
            print("\n" + "="*50)
            print("📝 СОХРАНИТЕ ЭТУ СТРОКУ:")
            print("="*50)
            print(f"\033[92m{session_str}\033[0m")
            print("="*50)
            print("💾 Добавьте её в .env файл как SESSION_STRING")
            
            # Спрашиваем про сохранение
            save = input("\n💾 Сохранить в .env? (y/n): ").lower()
            if save == 'y':
                self.save_session_to_env(session_str)
            
            return self.client
            
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")
            sys.exit(1)
    
    def save_session_to_env(self, session_string):
        """Сохраняет сессию в .env"""
        env_file = ".env"
        env_vars = {}
        
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, val = line.strip().split('=', 1)
                        env_vars[key] = val
        
        env_vars['SESSION_STRING'] = session_string
        
        with open(env_file, 'w') as f:
            for key, val in env_vars.items():
                f.write(f"{key}={val}\n")
        
        logger.info(f"✅ SESSION_STRING сохранен в {env_file}")
    
    async def load_commands(self):
        """Загрузка всех команд"""
        from commands import register_commands
        await register_commands(self.client, self.prefix, self.owner, self.db, CFG_EMOJI, self)
        logger.info(f"{CFG_EMOJI} Все команды загружены")
    
    async def run(self):
        """Запуск бота"""
        await self.start()
        await self.load_commands()
        
        # Базовая команда ping
        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}пинг$'))
        async def ping_cmd(event):
            if event.sender_id != self.owner:
                return
            start = time.time()
            msg = await event.reply("🏓")
            end = time.time()
            await msg.edit(f"🏓 Понг! `{round((end-start)*1000)}ms`")
        
        # Команда статус
        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}статус$'))
        async def status_cmd(event):
            if event.sender_id != self.owner:
                return
            
            uptime = datetime.now() - self.start_time
            hours = uptime.seconds // 3600
            minutes = (uptime.seconds % 3600) // 60
            
            status = f"""
{CFG_EMOJI} **KoliUB Статус**

👤 **Аккаунт:** {self.user.first_name}
🆔 **ID:** `{self.user.id}`
📊 **Модулей:** {len(self.loaded_modules)}
⏱️ **Аптайм:** {uptime.days}д {hours}ч {minutes}м
🔧 **Префикс:** `{self.prefix}`
💾 **БД:** {len(self.db.all())} записей
            """
            await event.reply(status)
        
        # Команда перезапуск
        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}рестарт$'))
        async def restart_cmd(event):
            if event.sender_id != self.owner:
                return
            await event.reply(f"{CFG_EMOJI} Перезапуск KoliUB...")
            logger.info("🔄 Перезапуск...")
            await self.client.disconnect()
            os.execl(sys.executable, sys.executable, *sys.argv)
        
        # Команда сессия
        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}сессия$'))
        async def session_cmd(event):
            if event.sender_id != self.owner:
                return
            session_str = self.client.session.save()
            await event.reply(f"""
**📱 Информация о сессии**

✅ Сессия активна
👤 Аккаунт: {self.user.first_name}
🆔 ID: `{self.user.id}`

**SESSION_STRING:**
`{session_str[:50]}...`

💾 Сохраните эту строку в .env
            """)
        
        logger.info(f"{CFG_EMOJI} KoliUB готов к работе! Префикс: {self.prefix}")
        await self.client.run_until_disconnected()

# ========== ЗАПУСК ==========
async def main():
    """Главная функция"""
    try:
        bot = KoliUB()
        await bot.run()
    except KeyboardInterrupt:
        logger.info("👋 KoliUB остановлен")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())