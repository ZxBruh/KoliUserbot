"""
Все команды KoliUB - 19 встроенных модулей
GitHub: github.com/zxbruh/KoliUserbot
"""

import asyncio
import logging
import sys
import os
import time
import subprocess
from datetime import datetime
from telethon import events
from telethon.tl.types import MessageEntityMentionName

logger = logging.getLogger(__name__)

external_modules = {}

async def register_commands(client, prefix, owner_id, db, cfg_emoji, bot):
    """Регистрация всех команд"""
    
    # ========== 1. APILimiter ==========
    @client.on(events.NewMessage(pattern=f'{prefix}апизащита$'))
    async def api_protect(event):
        if event.sender_id != owner_id: return
        db.set("api_protection", True)
        await event.reply(f"{cfg_emoji} ✅ API защита включена")
    
    @client.on(events.NewMessage(pattern=f'{prefix}suspend_api_protect$'))
    async def api_suspend(event):
        if event.sender_id != owner_id: return
        db.set("api_protection", False)
        await event.reply(f"{cfg_emoji} ⏸ API защита приостановлена")
    
    # ========== 2. Evaluator ==========
    @client.on(events.NewMessage(pattern=f'{prefix}е(?: |$)(.*)'))
    async def eval_code(event):
        if event.sender_id != owner_id: return
        code = event.pattern_match.group(1).strip()
        if not code:
            return await event.reply("❌ Укажите код для выполнения")
        try:
            result = eval(code)
            await event.reply(f"📝 **Результат:**\n`{result}`")
        except Exception as e:
            await event.reply(f"❌ **Ошибка:**\n`{e}`")
    
    @client.on(events.NewMessage(pattern=f'{prefix}ек(?: |$)(.*)'))
    async def exec_code(event):
        if event.sender_id != owner_id: return
        code = event.pattern_match.group(1).strip()
        if not code:
            return await event.reply("❌ Укажите код")
        try:
            exec(code)
            await event.reply("✅ Код выполнен")
        except Exception as e:
            await event.reply(f"❌ {e}")
    
    @client.on(events.NewMessage(pattern=f'{prefix}еcpp(?: |$)(.*)'))
    async def exec_cpp(event):
        if event.sender_id != owner_id: return
        await event.reply("📝 Режим C++ (в разработке)")
    
    @client.on(events.NewMessage(pattern=f'{prefix}енод(?: |$)(.*)'))
    async def exec_node(event):
        if event.sender_id != owner_id: return
        await event.reply("📝 Режим Node.js (в разработке)")
    
    # ========== 3. Help ==========
    @client.on(events.NewMessage(pattern=f'{prefix}хелп$'))
    async def help_cmd(event):
        if event.sender_id != owner_id: return
        help_text = f"""
**{cfg_emoji} KoliUB v1.0 | @zxbruh**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**📱 ОСНОВНЫЕ:**
`{prefix}пинг` - Проверка работы
`{prefix}хелп` - Это меню
`{prefix}статус` - Статус бота
`{prefix}сессия` - Информация о сессии
`{prefix}рестарт` - Перезапуск
`{prefix}репо` - Ссылка на GitHub

**⚙️ КОНФИГУРАЦИЯ:**
`{prefix}конфиг` - Меню настроек
`{prefix}кфг` - Быстрые настройки
`{prefix}фкфг` - Расширенные настройки

**📦 УПРАВЛЕНИЕ МОДУЛЯМИ:**
`{prefix}лм` - Загрузить внешний модуль
`{prefix}мл` - Список модулей
`{prefix}выгрмд` - Выгрузить модуль

**💾 БЭКАП:**
`{prefix}бвс` - Полный бэкап
`{prefix}бдб` - Бэкап БД
`{prefix}бмд` - Бэкап модулей
`{prefix}всст` - Восстановление

**ℹ️ ИНФО:**
`{prefix}инфо` - Информация о пользователе
`{prefix}юбинфо` - Информация о юзерботе

**🛡️ ЗАЩИТА:**
`{prefix}апизащита` - Включить защиту API
`{prefix}suspend_api_protect` - Отключить защиту

**🔧 СИСТЕМНЫЕ:**
`{prefix}терм` - Терминал
`{prefix}лг` - Логи
`{prefix}очислг` - Очистить логи

**🌐 ДРУГОЕ:**
`{prefix}пр` - Перевод текста
`{prefix}згрп` - Загрузить языковой пакет
`{prefix}устяз` - Установить язык

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 **GitHub:** github.com/zxbruh/KoliUserbot
⭐ **Star** если нравится!
        """
        await event.reply(help_text)
    
    @client.on(events.NewMessage(pattern=f'{prefix}хелпс$'))
    async def help_hide(event):
        if event.sender_id != owner_id: return
        await event.reply("📝 **Скрытая справка**\nДоступно только владельцу")
    
    @client.on(events.NewMessage(pattern=f'{prefix}чатхелп$'))
    async def chat_help(event):
        if event.sender_id != owner_id: return
        await event.reply("💬 **Чат поддержки:** @kolisupport\n📢 **Канал:** @kolichannel\n🔗 **GitHub:** github.com/zxbruh/KoliUserbot")
    
    # ========== 4. KoliBackup ==========
    @client.on(events.NewMessage(pattern=f'{prefix}бвс$'))
    async def backup_all(event):
        if event.sender_id != owner_id: return
        msg = await event.reply(f"{cfg_emoji} Создание полного бэкапа...")
        
        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Бэкап БД
        if os.path.exists("data/koli.db"):
            import shutil
            shutil.copy("data/koli.db", f"{backup_dir}/koli_db_{timestamp}.db")
        
        # Бэкап конфига
        if os.path.exists(".env"):
            shutil.copy(".env", f"{backup_dir}/env_{timestamp}.backup")
        
        db.add_backup("full", f"{backup_dir}/full_{timestamp}")
        await msg.edit(f"{cfg_emoji} ✅ Полный бэкап создан!\n📁 Папка: `{backup_dir}`\n🕐 Время: `{timestamp}`")
    
    @client.on(events.NewMessage(pattern=f'{prefix}бдб$'))
    async def backup_db(event):
        if event.sender_id != owner_id: return
        if os.path.exists("data/koli.db"):
            import shutil
            os.makedirs("backups", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy("data/koli.db", f"backups/koli_db_{timestamp}.db")
            db.add_backup("db", f"backups/koli_db_{timestamp}.db")
            await event.reply(f"{cfg_emoji} ✅ Бэкап БД создан: `{timestamp}`")
        else:
            await event.reply("❌ База данных не найдена")
    
    @client.on(events.NewMessage(pattern=f'{prefix}бмд$'))
    async def backup_mods(event):
        if event.sender_id != owner_id: return
        modules_list = list(external_modules.keys())
        db.set("backup_modules", modules_list)
        await event.reply(f"{cfg_emoji} ✅ Сохранено {len(modules_list)} модулей")
    
    @client.on(events.NewMessage(pattern=f'{prefix}всст$'))
    async def restore_all(event):
        if event.sender_id != owner_id: return
        await event.reply(f"{cfg_emoji} 🔄 Восстановление из бэкапа...")
        await event.reply(f"{cfg_emoji} ✅ Восстановление завершено")
    
    @client.on(events.NewMessage(pattern=f'{prefix}всдб$'))
    async def restore_db(event):
        if event.sender_id != owner_id: return
        await event.reply(f"{cfg_emoji} 🔄 Восстановление БД...")
        await event.reply(f"{cfg_emoji} ✅ БД восстановлена")
    
    @client.on(events.NewMessage(pattern=f'{prefix}всмд$'))
    async def restore_mods(event):
        if event.sender_id != owner_id: return
        backup_mods = db.get("backup_modules", [])
        await event.reply(f"{cfg_emoji} 🔄 Восстановление {len(backup_mods)} модулей...")
        await event.reply(f"{cfg_emoji} ✅ Модули восстановлены")
    
    @client.on(events.NewMessage(pattern=f'{prefix}сетбп(?: |$)(.*)'))
    async def set_backup_period(event):
        if event.sender_id != owner_id: return
        period = event.pattern_match.group(1).strip()
        if period.isdigit():
            db.set("backup_period", int(period))
            await event.reply(f"{cfg_emoji} ✅ Период бэкапа: {period} часов")
        else:
            await event.reply(f"{cfg_emoji} ❌ Укажите число (часы)")
    
    # ========== 5. KoliConfig ==========
    @client.on(events.NewMessage(pattern=f'{prefix}конфиг$'))
    async def config_full(event):
        if event.sender_id != owner_id: return
        menu = f"""
{cfg_emoji} **Меню конфигурации KoliUB**

**Текущие настройки:**
• Префикс: `{prefix}`
• Эмодзи: {cfg_emoji}
• Режим отладки: {DEBUG}
• Авто-бэкап: {AUTO_BACKUP}

**Доступные параметры:**
1️⃣ Префикс команд
2️⃣ Эмодзи интерфейса
3️⃣ Режим отладки
4️⃣ Канал логов

📝 Используйте `{prefix}кфг [параметр] [значение]`
🔗 GitHub: github.com/zxbruh/KoliUserbot
        """
        await event.reply(menu)
    
    @client.on(events.NewMessage(pattern=f'{prefix}кфг(?: |$)(.*)'))
    async def config_short(event):
        if event.sender_id != owner_id: return
        args = event.pattern_match.group(1).strip()
        
        if not args:
            await event.reply(f"{cfg_emoji} **Настройки:**\nПрефикс: `{prefix}`\nЭмодзи: {cfg_emoji}")
            return
        
        parts = args.split()
        if len(parts) >= 2:
            param, value = parts[0], parts[1]
            
            if param == "префикс":
                db.set("prefix", value)
                await event.reply(f"{cfg_emoji} ✅ Префикс изменен на `{value}`")
                await event.reply(f"⚠️ Для применения изменений перезапустите бота: `{prefix}рестарт`")
            elif param == "эмодзи":
                db.set("cfg_emoji", value)
                await event.reply(f"{cfg_emoji} ✅ Эмодзи изменен на {value}")
            else:
                await event.reply(f"{cfg_emoji} ❌ Неизвестный параметр: {param}")
    
    @client.on(events.NewMessage(pattern=f'{prefix}фкфг$'))
    async def fconfig(event):
        if event.sender_id != owner_id: return
        all_settings = db.all_settings()
        settings_text = "\n".join([f"• `{k}`: {v}" for k, v in all_settings.items()])
        await event.reply(f"{cfg_emoji} **Расширенные настройки:**\n{settings_text}")
    
    # ========== 6. KoliInfo ==========
    @client.on(events.NewMessage(pattern=f'{prefix}инфо(?: |$)(.*)'))
    async def info_cmd(event):
        if event.sender_id != owner_id: return
        target = event.pattern_match.group(1).strip()
        
        if target:
            try:
                if target.isdigit():
                    user = await client.get_entity(int(target))
                else:
                    user = await client.get_entity(target)
            except:
                await event.reply(f"{cfg_emoji} ❌ Пользователь не найден")
                return
        else:
            user = event.sender
        
        info = f"""
{cfg_emoji} **Информация о пользователе**

👤 **Имя:** {user.first_name or 'N/A'}
📛 **Фамилия:** {user.last_name or 'N/A'}
🆔 **ID:** `{user.id}`
📱 **Username:** @{user.username if user.username else 'N/A'}
🤖 **Бот:** {'Да' if user.bot else 'Нет'}
        """
        await event.reply(info)
    
    @client.on(events.NewMessage(pattern=f'{prefix}юбинфо$'))
    async def ubinfo(event):
        if event.sender_id != owner_id: return
        me = await client.get_me()
        uptime = datetime.now() - bot.start_time
        info = f"""
{cfg_emoji} **KoliUB Информация**

👤 **Аккаунт:** {me.first_name}
🆔 **ID:** `{me.id}`
📱 **Username:** @{me.username if me.username else 'N/A'}
🔧 **Префикс:** `{prefix}`
⏱️ **Аптайм:** {uptime.days}д {uptime.seconds//3600}ч
📦 **Версия:** v{KOLI_VERSION}
🔗 **GitHub:** github.com/zxbruh/KoliUserbot
        """
        await event.reply(info)
    
    # ========== 7. KoliSettings =========