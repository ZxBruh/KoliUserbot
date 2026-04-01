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
from datetime import datetime
from telethon import TelegramClient, events, errors
from telethon.sessions import StringSession

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
        self.api_id = None
        self.api_hash = None
        
    async def start(self):
        """Полная авторизация через терминал"""
        
        print("\n" + "="*60)
        print("🔐 АВТОРИЗАЦИЯ KOLIUB")
        print("="*60)
        
        # 1. Запрашиваем API ID
        print("\n📝 Получить API ID и API HASH можно на:")
        print("   https://my.telegram.org/apps")
        print("="*60)
        
        while not self.api_id:
            try:
                api_id_input = input("🆔 Введите API ID: ").strip()
                if api_id_input.isdigit():
                    self.api_id = int(api_id_input)
                else:
                    print("❌ API ID должен быть числом!")
            except KeyboardInterrupt:
                print("\n👋 Выход...")
                sys.exit(0)
        
        # 2. Запрашиваем API HASH
        while not self.api_hash:
            api_hash_input = input("🔑 Введите API HASH: ").strip()
            if api_hash_input and len(api_hash_input) >= 30:
                self.api_hash = api_hash_input
            else:
                print("❌ API HASH должен быть строкой из 30+ символов!")
        
        # 3. Запрашиваем номер телефона
        print("\n" + "="*60)
        print("📱 АВТОРИЗАЦИЯ В TELEGRAM")
        print("="*60)
        
        phone = None
        while not phone:
            phone = input("📱 Введите номер телефона (+79991234567): ").strip()
            if not phone:
                print("❌ Номер телефона обязателен!")
        
        # Создаем клиент с введенными данными
        self.client = TelegramClient("koli_session", self.api_id, self.api_hash)
        
        try:
            # Отправляем запрос на код
            await self.client.send_code_request(phone)
            print("✅ Код подтверждения отправлен в Telegram!")
            
            # 4. Запрашиваем код
            code = None
            while not code:
                code = input("🔐 Введите код из Telegram: ").strip()
                if not code:
                    print("❌ Код не может быть пустым!")
            
            # Пытаемся войти
            try:
                await self.client.sign_in(phone, code)
                
            except errors.SessionPasswordNeededError:
                # 5. Запрашиваем 2FA пароль
                print("\n🔒 Обнаружена двухфакторная аутентификация (2FA)")
                password = None
                while not password:
                    password = input("🔒 Введите облачный пароль: ").strip()
                    if not password:
                        print("❌ Пароль не может быть пустым!")
                
                await self.client.sign_in(password=password)
            
            # Получаем информацию о пользователе
            self.user = await self.client.get_me()
            
            print("\n" + "="*60)
            print(f"✅ ДОБРО ПОЖАЛОВАТЬ, {self.user.first_name.upper()}!")
            print("="*60)
            print(f"👤 Имя: {self.user.first_name}")
            print(f"🆔 ID: {self.user.id}")
            print(f"📱 Username: @{self.user.username if self.user.username else 'Нет'}")
            
            # 6. Запрашиваем OWNER_ID
            print("\n" + "="*60)
            print("⚙️ НАСТРОЙКА ВЛАДЕЛЬЦА")
            print("="*60)
            print(f"Ваш Telegram ID: {self.user.id}")
            
            owner_input = input(f"👑 Введите ID владельца (Enter = {self.user.id}): ").strip()
            if owner_input and owner_input.isdigit():
                self.owner = int(owner_input)
            else:
                self.owner = self.user.id
            
            # 7. Запрашиваем префикс
            prefix_input = input(f"🔧 Введите префикс команд (Enter = {self.prefix}): ").strip()
            if prefix_input:
                self.prefix = prefix_input
            
            # Сохраняем настройки в .env
            self.save_config()
            
            # Показываем SESSION_STRING
            session_str = self.client.session.save()
            print("\n" + "="*60)
            print("📝 СОХРАНИТЕ ЭТУ СТРОКУ (SESSION_STRING):")
            print("="*60)
            print(f"\033[92m{session_str}\033[0m")
            print("="*60)
            
            # Сохраняем сессию в .env
            self.save_session(session_str)
            
            print("\n✅ Авторизация завершена!")
            print(f"🚀 KoliUB готов к работе! Префикс: {self.prefix}")
            
        except errors.PhoneCodeInvalidError:
            print("❌ Неверный код подтверждения!")
            sys.exit(1)
        except errors.PhoneCodeExpiredError:
            print("❌ Код истек! Запросите новый.")
            sys.exit(1)
        except errors.FloodWaitError as e:
            print(f"❌ Слишком много попыток! Подождите {e.seconds} секунд.")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            sys.exit(1)
    
    def save_config(self):
        """Сохраняет API ID и HASH в .env"""
        env_file = ".env"
        env_vars = {}
        
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, val = line.strip().split('=', 1)
                        env_vars[key] = val
        
        env_vars['API_ID'] = str(self.api_id)
        env_vars['API_HASH'] = self.api_hash
        env_vars['PREFIX'] = self.prefix
        env_vars['OWNER_ID'] = str(self.owner)
        
        with open(env_file, 'w') as f:
            for key, val in env_vars.items():
                f.write(f"{key}={val}\n")
        
        print(f"✅ Конфигурация сохранена в {env_file}")
    
    def save_session(self, session_string):
        """Сохраняет SESSION_STRING в .env"""
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
        
        print(f"✅ SESSION_STRING сохранен в {env_file}")
    
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
python3 main.py    """)

logger.info(f"{CFG_EMOJI} KoliUB готов! Префикс: {self.prefix}")

# Отправка приветствия владельцу
try:
    await self.client.send_message(self.owner, 
        f"{CFG_EMOJI} **KoliUB v{self.version} запущен!**\n\n"
        f"👤 Аккаунт: {self.user.first_name}\n"
        f"🔧 Префикс: `{self.prefix}`\n"
        f"📝 Команда помощи: `{self.prefix}хелп`")
except:
    pass

await self.client.run_until_disconnected()


## А также нужно создать `menus.py` (был пустой):

``python
"""
KoliUB - Интерактивные меню
"""

import logging
from datetime import datetime
from telethon import events
from telethon.tl.custom import Button

logger = logging.getLogger(__name__)

async def register_menus(client, prefix, owner_id, db, cfg_emoji, bot):
    """Регистрация меню"""
    
    @client.on(events.NewMessage(pattern=f'{prefix}меню$'))
    async def main_menu(event):
        if event.sender_id != owner_id:
            return
        
        buttons = [
            [Button.inline("⚙️ Настройки", b"settings")],
            [Button.inline("📦 Модули", b"modules")],
            [Button.inline("ℹ️ Инфо", b"info")],
            [Button.inline("❌ Закрыть", b"close")]
        ]
        
        await event.reply(
            f"{cfg_emoji} **Главное меню KoliUB**\n\n"
            f"👤 Аккаунт: {bot.user.first_name}\n"
            f"🔧 Префикс: `{prefix}`",
            buttons=buttons
        )
    
    @client.on(events.CallbackQuery)
    async def callback_handler(event):
        if event.sender_id != owner_id:
            await event.answer("⛔ Доступ запрещен", alert=True)
            return
        
        data = event.data.decode()
        
        if data == "settings":
            await event.edit("⚙️ Настройки (в разработке)")
        elif data == "modules":
            await event.edit("📦 Модули (в разработке)")
        elif data == "info":
            uptime = datetime.now() - bot.start_time
            await event.edit(
                f"ℹ️ **О KoliUB**\n\n"
                f"📦 Версия: v{bot.version}\n"
                f"👤 Аккаунт: {bot.user.first_name}\n"
                f"⏱️ Аптайм: {uptime.days}д {uptime.seconds//3600}ч\n"
                f"👑 Автор: @zxbruh\n"
                f"🔗 GitHub: {bot.repo_url}"
            )
        elif data == "close":
            await event.delete()
    
    logger.info("📋 Меню загружены")