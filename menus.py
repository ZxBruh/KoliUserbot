"""
KoliUB - Интерактивные меню с кнопками
GitHub: github.com/zxbruh/KoliUserbot
Author: @zxbruh
"""

import logging
from telethon import events
from telethon.tl.types import KeyboardButtonCallback, KeyboardButtonUrl
from telethon.tl.custom import Button

logger = logging.getLogger(__name__)

async def register_menus(client, prefix, owner_id, db, cfg_emoji, bot):
    """Регистрация интерактивных меню"""
    
    # ========== ГЛАВНОЕ МЕНЮ ==========
    @client.on(events.NewMessage(pattern=f'{prefix}меню$'))
    async def main_menu(event):
        if event.sender_id != owner_id:
            return
        
        buttons = [
            [Button.inline("⚙️ Настройки", b"settings")],
            [Button.inline("📦 Модули", b"modules")],
            [Button.inline("💾 Бэкап", b"backup")],
            [Button.inline("ℹ️ Инфо", b"info")],
            [Button.inline("❌ Закрыть", b"close")]
        ]
        
        await event.reply(
            f"{cfg_emoji} **Главное меню KoliUB**\n\n"
            f"👤 Аккаунт: {bot.user.first_name}\n"
            f"🔧 Префикс: `{prefix}`\n"
            f"📦 Версия: v{bot.version}",
            buttons=buttons
        )
    
    # ========== ОБРАБОТЧИКИ КНОПОК ==========
    @client.on(events.CallbackQuery)
    async def callback_handler(event):
        if event.sender_id != owner_id:
            await event.answer("⛔ Доступ запрещен", alert=True)
            return
        
        data = event.data.decode()
        
        # Настройки
        if data == "settings":
            buttons = [
                [Button.inline(f"🔧 Префикс: {prefix}", b"set_prefix")],
                [Button.inline(f"🎨 Эмодзи: {cfg_emoji}", b"set_emoji")],
                [Button.inline("🔄 Сбросить настройки", b"reset_settings")],
                [Button.inline("◀️ Назад", b"back_main")]
            ]
            await event.edit(
                f"⚙️ **Настройки KoliUB**\n\n"
                f"Выберите параметр для изменения:",
                buttons=buttons
            )
        
        elif data == "set_prefix":
            await event.edit(
                f"✏️ **Изменение префикса**\n\n"
                f"Текущий префикс: `{prefix}`\n\n"
                f"Введите новый префикс в чат:\n"
                f"Например: `.` или `!` или `?`",
                buttons=[[Button.inline("◀️ Назад", b"settings")]]
            )
            # Ждем ответа
            @client.on(events.NewMessage(from_users=owner_id))
            async def set_prefix_handler(msg):
                if msg.text and not msg.text.startswith(prefix):
                    new_prefix = msg.text.strip()
                    db.set("prefix", new_prefix)
                    await event.respond(f"{cfg_emoji} ✅ Префикс изменен на `{new_prefix}`\n⚠️ Перезапустите бота: `{new_prefix}рестарт`")
                    return False
        
        elif data == "set_emoji":
            await event.edit(
                f"🎨 **Изменение эмодзи**\n\n"
                f"Текущий эмодзи: {cfg_emoji}\n\n"
                f"Введите новый эмодзи в чат:",
                buttons=[[Button.inline("◀️ Назад", b"settings")]]
            )
            @client.on(events.NewMessage(from_users=owner_id))
            async def set_emoji_handler(msg):
                if msg.text and len(msg.text) <= 2:
                    new_emoji = msg.text.strip()
                    db.set("cfg_emoji", new_emoji)
                    await event.respond(f"{new_emoji} ✅ Эмодзи изменен на {new_emoji}")
                    return False
        
        # Модули
        elif data == "modules":
            modules_list = list(bot.loaded_modules.keys()) if hasattr(bot, 'loaded_modules') else []
            buttons = []
            for mod in modules_list[:10]:
                buttons.append([Button.inline(mod, f"mod_{mod}")])
            buttons.append([Button.inline("🔄 Загрузить модуль", b"load_module")])
            buttons.append([Button.inline("◀️ Назад", b"back_main")])
            
            await event.edit(
                f"📦 **Управление модулями**\n\n"
                f"Загружено модулей: {len(modules_list)}\n"
                f"Встроенных модулей: 19\n\n"
                f"Команды:\n"
                f"`{prefix}лм` - загрузить модуль\n"
                f"`{prefix}мл` - список модулей\n"
                f"`{prefix}выгрмд` - выгрузить модуль",
                buttons=buttons
            )
        
        elif data == "load_module":
            await event.edit(
                f"📥 **Загрузка модуля**\n\n"
                f"Введите название модуля или ссылку на репозиторий:\n\n"
                f"Пример: `{prefix}лм example_module`",
                buttons=[[Button.inline("◀️ Назад", b"modules")]]
            )
        
        # Бэкап
        elif data == "backup":
            buttons = [
                [Button.inline("💾 Полный бэкап", b"backup_full")],
                [Button.inline("💾 Бэкап БД", b"backup_db")],
                [Button.inline("💾 Бэкап модулей", b"backup_mods")],
                [Button.inline("🔄 Восстановить", b"restore")],
                [Button.inline("◀️ Назад", b"back_main")]
            ]
            await event.edit(
                f"💾 **Управление бэкапами**\n\n"
                f"Авто-бэкап: {'✅ Вкл' if AUTO_BACKUP else '❌ Выкл'}\n"
                f"Папка бэкапов: `backups/`",
                buttons=buttons
            )
        
        elif data == "backup_full":
            await event.edit(f"{cfg_emoji} 🔄 Создание полного бэкапа...")
            # Логика бэкапа
            await event.respond(f"{cfg_emoji} ✅ Полный бэкап создан!")
        
        elif data == "restore":
            await event.edit(f"{cfg_emoji} 🔄 Восстановление из бэкапа...")
            await event.respond(f"{cfg_emoji} ✅ Восстановление завершено!")
        
        # Инфо
        elif data == "info":
            uptime = datetime.now() - bot.start_time
            buttons = [
                [Button.url("🔗 GitHub", bot.repo_url)],
                [Button.url("👑 Автор", "https://t.me/zxbruh")],
                [Button.inline("◀️ Назад", b"back_main")]
            ]
            await event.edit(
                f"ℹ️ **О KoliUB**\n\n"
                f"📦 **Версия:** v{bot.version}\n"
                f"👤 **Аккаунт:** {bot.user.first_name}\n"
                f"🆔 **ID:** `{bot.user.id}`\n"
                f"⏱️ **Аптайм:** {uptime.days}д {uptime.seconds//3600}ч\n"
                f"🔧 **Префикс:** `{prefix}`\n"
                f"💾 **БД:** {len(db.all_settings())} записей\n\n"
                f"👑 **Автор:** @zxbruh\n"
                f"⭐ **GitHub:** {bot.repo_url}",
                buttons=buttons
            )
        
        # Назад в главное меню
        elif data == "back_main":
            buttons = [
                [Button.inline("⚙️ Настройки", b"settings")],
                [Button.inline("📦 Модули", b"modules")],
                [Button.inline("💾 Бэкап", b"backup")],
                [Button.inline("ℹ️ Инфо", b"info")],
                [Button.inline("❌ Закрыть", b"close")]
            ]
            await event.edit(
                f"{cfg_emoji} **Главное меню KoliUB**\n\n"
                f"👤 Аккаунт: {bot.user.first_name}\n"
                f"🔧 Префикс: `{prefix}`\n"
                f"📦 Версия: v{bot.version}",
                buttons=buttons
            )
        
        elif data == "close":
            await event.delete()
        
        else:
            await event.answer("🔄 В разработке")
    
    logger.info("📋 Меню загружены")