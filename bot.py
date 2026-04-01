"""
KoliUB - Основной класс бота
GitHub: github.com/zxbruh/KoliUserbot
Author: @zxbruh
"""

import asyncio
import logging
import sys
import os
import time
import subprocess
from datetime import datetime
from telethon import TelegramClient, errors
from telethon.sessions import StringSession
from telethon.tl.types import Message

from config import *
from database import Database
from commands import register_commands
from menus import register_menus

logger = logging.getLogger(__name__)

class KoliBot:
    """Основной класс KoliUB"""
    
    def __init__(self):
        self.client = None
        self.db = Database()
        self.start_time = datetime.now()
        self.prefix = PREFIX
        self.owner = OWNER_ID
        self.user = None
        self.version = KOLI_VERSION
        self.repo_url = REPO_URL
        self.loaded_modules = {}
        
    async def start(self):
        """Автоматическая авторизация"""
        
        # Создание клиента
        if SESSION_STRING:
            logger.info("🔑 Использование SESSION_STRING")
            self.client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
            await self.client.start()
            
            try:
                self.user = await self.client.get_me()
                logger.info(f"✅ Авторизован: {self.user.first_name} (@{self.user.username})")
                return
            except Exception as e:
                logger.error(f"❌ Невалидная SESSION_STRING: {e}")
                logger.info("🔄 Создаем новую сессию...")
        
        # Если нет сессии или она невалидна
        logger.info("📁 Создание новой сессии")
        self.client = TelegramClient("koli_session", API_ID, API_HASH)
        
        # Запрашиваем номер телефона
        print("\n" + "="*50)
        print("🔐 АВТОРИЗАЦИЯ В TELEGRAM")
        print("="*50)
        print("Для авторизации вам потребуется:")
        print("1. Номер телефона")
        print("2. Код из Telegram")
        print("3. Пароль 2FA (если включен)")
        print("="*50)
        
        phone = input("\n📱 Введите номер телефона (в формате +79991234567): ").strip()
        
        try:
            # Отправляем запрос на код
            await self.client.send_code_request(phone)
            print("✅ Код отправлен в Telegram")
            
            # Запрашиваем код
            code = input("🔐 Введите код из Telegram: ").strip()
            
            # Пытаемся войти
            try:
                await self.client.sign_in(phone, code)
                logger.info("✅ Авторизация успешна!")
                
            except errors.SessionPasswordNeededError:
                # Если требуется облачный пароль (2FA)
                print("\n🔒 Требуется облачный пароль (2FA)")
                password = input("🔒 Введите пароль: ").strip()
                await self.client.sign_in(password=password)
                logger.info("✅ Авторизация с 2FA успешна!")
            
            # Получаем информацию о пользователе
            self.user = await self.client.get_me()
            logger.info(f"👤 Добро пожаловать, {self.user.first_name}!")
            
            # Сохраняем SESSION_STRING
            session_str = self.client.session.save()
            print("\n" + "="*60)
            print("📝 СОХРАНИТЕ ЭТУ СТРОКУ:")
            print("="*60)
            print(f"\033[92m{session_str}\033[0m")
            print("="*60)
            print("💾 Добавьте её в .env файл:")
            print(f"SESSION_STRING={session_str}")
            print(f"🔗 Репозиторий: {self.repo_url}")
            
            # Автосохранение
            save = input("\n💾 Автосохранить в .env? (y/n): ").lower()
            if save == 'y':
                self.save_session(session_str)
            
        except errors.PhoneCodeInvalidError:
            logger.error("❌ Неверный код подтверждения")
            sys.exit(1)
        except errors.PhoneCodeExpiredError:
            logger.error("❌ Код истек, запросите новый")
            sys.exit(1)
        except errors.FloodWaitError as e:
            logger.error(f"❌ Слишком много попыток. Подождите {e.seconds} секунд")
            sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Ошибка авторизации: {e}")
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
        
        # ========== ВСТРОЕННЫЕ КОМАНДЫ ==========
        
        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}пинг$'))
        async def ping_cmd(event):
            if event.sender_id != self.owner:
                return
            start = time.time()
            msg = await event.reply("🏓")
            end = time.time()
            await msg.edit(f"🏓 Понг! `{round((end-start)*1000)}ms`")
        
        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}статус$'))
        async def status_cmd(event):
            if event.sender_id != self.owner:
                return
            
            uptime = datetime.now() - self.start_time
            days = uptime.days
            hours = uptime.seconds // 3600
            minutes = (uptime.seconds % 3600) // 60
            
            status = f"""
{CFG_EMOJI} **KoliUB v{self.version}**

👤 **Аккаунт:** {self.user.first_name}
🆔 **ID:** `{self.user.id}`
🔧 **Префикс:** `{self.prefix}`
⏱️ **Аптайм:** {days}д {hours}ч {minutes}м
💾 **БД:** {len(self.db.all_settings())} записей
📦 **Модулей:** {len(self.loaded_modules)} загружено

🔗 **GitHub:** [KoliUserbot]({self.repo_url})
👑 **Автор:** {AUTHOR}
⭐ **Star** если нравится!
            """
            await event.reply(status)
        
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
🔗 {self.repo_url}
            """)
        
        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}рестарт$'))
        async def restart_cmd(event):
            if event.sender_id != self.owner:
                return
            await event.reply(f"{CFG_EMOJI} 🔄 Перезапуск KoliUB...")
            logger.info("🔄 Перезапуск KoliUB")
            await self.client.disconnect()
            os.execl(sys.executable, sys.executable, *sys.argv)
        
        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}репо$'))
        async def repo_cmd(event):
            if event.sender_id != self.owner:
                return
            await event.reply(f"""
**📦 KoliUB Repository**

🔗 **GitHub:** {self.repo_url}
👑 **Author:** {AUTHOR}
⭐ **Star** на GitHub если нравится!

**Быстрая установка:**
```bash
git clone {self.repo_url}
cd KoliUserbot
pip install -r requirements.txt
python3 main.py