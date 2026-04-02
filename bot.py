import asyncio, logging, sys, os, time, subprocess, json
from datetime import datetime
from telethon import TelegramClient, events, errors
from telethon.tl.custom import Button

logger = logging.getLogger(__name__)
CFG_FILE = "koli_config.json"

class KoliBot:
    def __init__(self):
        self.client = None
        self.start_time = datetime.now()
        self.prefix = "."
        self.owner = None
        self.user = None
        self.version = "1.0"
        self.repo_url = "https://github.com/zxbruh/KoliUserbot"
        self.loaded_modules = {}
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(CFG_FILE):
            with open(CFG_FILE, 'r') as f:
                return json.load(f)
        return {}

    def save_config(self):
        with open(CFG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)

    async def start(self):
        print("\n" + "="*50)
        print("🔐 ПЕРВЫЙ ЗАПУСК KOLIUB")
        print("="*50)
        print("📝 API ID и HASH: https://my.telegram.org/apps")
        print("="*50)

        api_id = int(input("🆔 API ID: "))
        api_hash = input("🔑 API HASH: ")
        phone = input("📱 Номер (+79991234567): ")

        self.client = TelegramClient("koli_session", api_id, api_hash)
        await self.client.connect()
        await self.client.send_code_request(phone)
        code = input("🔐 Код из Telegram: ")

        try:
            await self.client.sign_in(phone, code)
        except errors.SessionPasswordNeededError:
            await self.client.sign_in(password=input("🔒 2FA пароль: "))

        self.user = await self.client.get_me()
        print(f"\n✅ Добро пожаловать, {self.user.first_name}!")

        o = input(f"👑 ID владельца (Enter={self.user.id}): ")
        self.owner = int(o) if o and o.isdigit() else self.user.id

        p = input(f"🔧 Префикс команд (Enter={self.prefix}): ")
        if p: self.prefix = p

        self.config['api_id'] = api_id
        self.config['api_hash'] = api_hash
        self.config['phone'] = phone
        self.config['prefix'] = self.prefix
        self.config['owner'] = self.owner
        self.save_config()

        print("\n✅ Настройки сохранены!")
        await self.load_handlers()

    async def load_handlers(self):
        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}пинг$'))
        async def p(e):
            if e.sender_id != self.owner: return
            s = time.time()
            m = await e.reply("🏓")
            await m.edit(f"🏓 Понг! {round((time.time()-s)*1000)}ms")

        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}статус$'))
        async def st(e):
            if e.sender_id != self.owner: return
            u = datetime.now() - self.start_time
            await e.reply(f"🟢 **KoliUB**\n👤 {self.user.first_name}\n🆔 `{self.user.id}`\n🔧 `{self.prefix}`\n⏱️ {u.days}д {u.seconds//3600}ч")

        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}хелп$'))
        async def h(e):
            if e.sender_id != self.owner: return
            await e.reply(f"**KoliUB Команды**\n`{self.prefix}пинг` - Проверка\n`{self.prefix}статус` - Статус\n`{self.prefix}хелп` - Помощь\n`{self.prefix}сессия` - Сессия\n`{self.prefix}рестарт` - Рестарт\n`{self.prefix}репо` - GitHub")

        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}сессия$'))
        async def se(e):
            if e.sender_id != self.owner: return
            await e.reply(f"SESSION_STRING:\n`{self.client.session.save()[:50]}...`")

        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}рестарт$'))
        async def r(e):
            if e.sender_id != self.owner: return
            await e.reply("🔄 Перезапуск...")
            await self.client.disconnect()
            os.execl(sys.executable, sys.executable, *sys.argv)

        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}репо$'))
        async def rp(e):
            if e.sender_id != self.owner: return
            await e.reply(f"🔗 {self.repo_url}")

        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}меню$'))
        async def m(e):
            if e.sender_id != self.owner: return
            await e.reply("📋 Меню", buttons=[[Button.inline("📊 Статус", b"st"), Button.inline("❌", b"cl")]])

        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}терм(?: |$)(.*)'))
        async def t(e):
            if e.sender_id != self.owner: return
            cmd = e.pattern_match.group(1).strip()
            if not cmd: return await e.reply("❌ Укажите команду")
            msg = await e.reply(f"Выполнение: `{cmd}`...")
            try:
                r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                out = r.stdout or r.stderr or "✅ Выполнено"
                await msg.edit(f"```bash\n{out[:3500]}\n```")
            except: await msg.edit("❌ Ошибка")

        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}инфо(?: |$)(.*)'))
        async def i(e):
            if e.sender_id != self.owner: return
            t = e.pattern_match.group(1).strip()
            try:
                if t:
                    u = await self.client.get_entity(int(t) if t.isdigit() else t)
                else:
                    u = e.sender
            except:
                return await e.reply("❌ Не найден")
            await e.reply(f"👤 {u.first_name}\n🆔 `{u.id}`\n📱 @{u.username if u.username else 'Нет'}")

        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}кфг(?: |$)(.*)'))
        async def k(e):
            if e.sender_id != self.owner: return
            a = e.pattern_match.group(1).strip()
            if not a:
                return await e.reply(f"🔧 Префикс: `{self.prefix}`")
            p, v = a.split()[:2]
            if p == "префикс":
                self.prefix = v
                self.config['prefix'] = v
                self.save_config()
                await e.reply(f"✅ Префикс `{v}`\n⚠️ Рестарт: `{v}рестарт`")

        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}лм(?: |$)(.*)'))
        async def lm(e):
            if e.sender_id != self.owner: return
            n = e.pattern_match.group(1).strip()
            if n:
                self.loaded_modules[n] = True
                await e.reply(f"✅ Модуль `{n}` загружен")

        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}мл$'))
        async def lml(e):
            if e.sender_id != self.owner: return
            await e.reply(f"📦 Загружено: {len(self.loaded_modules)} модулей")

        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}выгрмд(?: |$)(.*)'))
        async def ul(e):
            if e.sender_id != self.owner: return
            n = e.pattern_match.group(1).strip()
            if n in self.loaded_modules:
                del self.loaded_modules[n]
                await e.reply(f"✅ Модуль `{n}` выгружен")

        @self.client.on(events.CallbackQuery)
        async def cb(e):
            if e.sender_id != self.owner:
                return await e.answer("⛔ Доступ запрещен", alert=True)
            if e.data == b"st":
                await e.edit("📊 KoliUB работает!")
            elif e.data == b"cl":
                await e.delete()

        logger.info("✅ Команды загружены")

    async def run(self):
        logger.info(f"🚀 KoliUB готов! Префикс: {self.prefix}")
        await self.client.run_until_disconnected()