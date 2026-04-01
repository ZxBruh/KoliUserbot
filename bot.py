import asyncio
import logging
import sys
import os
import time
from datetime import datetime
from telethon import TelegramClient, events, errors
from telethon.sessions import StringSession
from telethon.tl.types import Message

from config import *
from database import Database
from commands import register_commands
from menus import register_menus
from web import start_web_server

logger = logging.getLogger(__name__)

class KoliBot:
    def __init__(self):
        self.client = None
        self.db = Database()
        self.start_time = datetime.now()
        self.prefix = PREFIX
        self.owner = OWNER_ID
        self.user = None
        
    async def start(self):
        """Автоматическая авторизация"""
        
        # Создание клиента
        if SESSION_STRING:
            logger.info("🔑 Использование SESSION_STRING")
            self.client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
        else:
            logger.info("📁 Использование файла сессии")
            self.client = TelegramClient("koli_session", API_ID, API_HASH)
        
        await self.client.start()
        
        # Проверка авторизации
        try:
            self.user = await self.client.get_me()
            logger.info(f"✅ Авторизован: {self.user.first_name} (@{self.user.username})")
            logger.info(f"🆔 ID: {self.user.id}")
            
            # Проверка владельца
            if self.owner:
                try:
                    owner = await self.client.get_entity(self.owner)
                    logger.info(f"👑 Владелец: {owner.first_name}")
                except:
                    logger.warning("⚠️ Владелец не найден, проверьте OWNER_ID")
                    
        except errors.RPCError as e:
            logger.error(f"❌ Ошибка авторизации: {e}")
            await self.create_session()
    
    async def create_session(self):
        """Создание новой сессии"""
        print("\n" + "="*50)
        print("🆕 СОЗДАНИЕ НОВОЙ СЕССИИ")
        print("="*50)
        
        phone = input("📱 Номер телефона (+79991234567): ")
        
        try:
            await self.client.send_code_request(phone)
            code = input("🔐 Код из Telegram: ")
            
            try:
                await self.client.sign_in(phone, code)
            except errors.SessionPasswordNeededError:
                password = input("🔒 Облачный пароль (2FA): ")
                await self.client.sign_in(password=password)
            
            self.user = await self.client.get_me()
            logger.info(f"✅ Добро пожаловать, {self.user.first_name}!")
            
            # Показываем SESSION_STRING
            session_str = self.client.session.save()
            print("\n" + "="*50)
            print("📝 СОХРАНИТЕ ЭТУ СТРОКУ:")
            print("="*50)
            print(f"\033[92m{session_str}\033[0m")
            print("="*50)
            print("💾 Добавьте её в .env как SESSION_STRING")
            print(f"🔗 Репозиторий: {REPO_URL}")
            
            # Автосохранение
            save = input("\n💾 Автосохранить в .env? (y/n): ").lower()
            if save == 'y':
                self.save_session(session_str)
                
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")
            sys.exit(1)
    
    def save_session(self, session_string):
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
    
    async def load_handlers(self):
        """Загрузка всех обработчиков"""
        await register_commands(self.client, self.prefix, self.owner, self.db, CFG_EMOJI, self)
        await register_menus(self.client, self.prefix, self.owner, self.db, CFG_EMOJI, self)
        logger.info(f"{CFG_EMOJI} Все обработчики загружены")
    
    async def run(self):
        """Запуск бота"""
        await self.load_handlers()
        
        # Запуск веб-сервера для статуса
        if DEPLOY_PLATFORM != "local":
            start_web_server()
        
        # Команда ping
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
            days = uptime.days
            hours = uptime.seconds // 3600
            minutes = (uptime.seconds % 3600) // 60
            
            status = f"""
{CFG_EMOJI} **KoliUB v{KOLI_VERSION}**

👤 **Аккаунт:** {self.user.first_name}
🆔 **ID:** `{self.user.id}`
🔧 **Префикс:** `{self.prefix}`
⏱️ **Аптайм:** {days}д {hours}ч {minutes}м
💾 **БД:** {len(self.db.all_settings())} записей
📦 **Модулей:** встроенных 19

🔗 **GitHub:** [KoliUserbot]({REPO_URL})
👑 **Автор:** {AUTHOR}
            """
            await event.reply(status)
        
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

💾 Сохраните в .env
🔗 {REPO_URL}
            """)
        
        # Команда рестарт
        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}рестарт$'))
        async def restart_cmd(event):
            if event.sender_id != self.owner:
                return
            await event.reply(f"{CFG_EMOJI} Перезапуск KoliUB...")
            logger.info("🔄 Перезапуск...")
            await self.client.disconnect()
            os.execl(sys.executable, sys.executable, *sys.argv)
        
        # Команда репо
        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}репо$'))
        async def repo_cmd(event):
            if event.sender_id != self.owner:
                return
            await event.reply(f"""
**📦 KoliUB Repository**

🔗 **GitHub:** {REPO_URL}
👑 **Author:** {AUTHOR}
⭐ **Star** на GitHub если нравится!

**Установка:**