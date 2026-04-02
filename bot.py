import asyncio, logging, sys, os, time, subprocess
from datetime import datetime
from telethon import TelegramClient, events, errors
from telethon.tl.custom import Button
from config import *
from database import Database

logger = logging.getLogger(__name__)

class KoliBot:
    def __init__(self):
        self.client = None; self.db = Database(); self.start_time = datetime.now()
        self.prefix = PREFIX; self.owner = OWNER_ID; self.user = None
        self.version = KOLI_VERSION; self.repo_url = REPO_URL; self.loaded_modules = {}
        self.api_id = None; self.api_hash = None

    async def start(self):
        print("\n" + "="*50 + "\n🔐 АВТОРИЗАЦИЯ KOLIUB\n" + "="*50)
        while not self.api_id:
            try: self.api_id = int(input("🆔 API ID: "))
            except: print("❌ Число!")
        while not self.api_hash:
            self.api_hash = input("🔑 API HASH: ")
            if len(self.api_hash) < 30: print("❌ 30+ символов"); self.api_hash = None
        phone = input("📱 Номер (+79991234567): ")
        self.client = TelegramClient("koli_session", self.api_id, self.api_hash)
        await self.client.connect()
        await self.client.send_code_request(phone)
        code = input("🔐 Код из Telegram: ")
        try: await self.client.sign_in(phone, code)
        except errors.SessionPasswordNeededError:
            await self.client.sign_in(password=input("🔒 2FA пароль: "))
        self.user = await self.client.get_me()
        print(f"\n✅ Добро пожаловать, {self.user.first_name}!")
        o = input(f"👑 ID владельца (Enter={self.user.id}): ")
        if o and o.isdigit(): self.owner = int(o)
        p = input(f"🔧 Префикс (Enter={self.prefix}): ")
        if p: self.prefix = p
        self.save_config()
        s = self.client.session.save()
        print(f"\n📝 SESSION_STRING:\n{s}\n")
        self.save_session(s)
        print("✅ Готов!")

    def save_config(self):
        with open(".env", "w") as f:
            f.write(f"API_ID={self.api_id}\nAPI_HASH={self.api_hash}\nPREFIX={self.prefix}\nOWNER_ID={self.owner}\nCFG_EMOJI={CFG_EMOJI}\n")
    def save_session(self, s):
        with open(".env", "a") as f: f.write(f"SESSION_STRING={s}\n")

    async def load_handlers(self):
        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}пинг$'))
        async def p(e):
            if e.sender_id!=self.owner: return
            s=time.time(); m=await e.reply("🏓"); await m.edit(f"🏓 Понг! {round((time.time()-s)*1000)}ms")
        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}статус$'))
        async def s(e):
            if e.sender_id!=self.owner: return
            u=datetime.now()-self.start_time
            await e.reply(f"{CFG_EMOJI} **KoliUB**\n👤 {self.user.first_name}\n🆔 `{self.user.id}`\n🔧 `{self.prefix}`\n⏱️ {u.days}д {u.seconds//3600}ч\n🔗 {self.repo_url}")
        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}хелп$'))
        async def h(e):
            if e.sender_id!=self.owner: return
            await e.reply(f"**{CFG_EMOJI} KoliUB**\n`{self.prefix}пинг` - Пинг\n`{self.prefix}статус` - Статус\n`{self.prefix}хелп` - Помощь\n`{self.prefix}сессия` - Сессия\n`{self.prefix}рестарт` - Рестарт\n`{self.prefix}репо` - GitHub")
        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}сессия$'))
        async def se(e):
            if e.sender_id!=self.owner: return
            await e.reply(f"SESSION_STRING:\n`{self.client.session.save()[:50]}...`")
        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}рестарт$'))
        async def r(e):
            if e.sender_id!=self.owner: return
            await e.reply("🔄 Перезапуск...")
            await self.client.disconnect(); os.execl(sys.executable, sys.executable, *sys.argv)
        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}репо$'))
        async def rp(e):
            if e.sender_id!=self.owner: return
            await e.reply(f"🔗 {self.repo_url}")
        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}меню$'))
        async def m(e):
            if e.sender_id!=self.owner: return
            await e.reply(f"{CFG_EMOJI} Меню", buttons=[[Button.inline("📊 Статус",b"st"),Button.inline("❌",b"cl")]])
        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}терм(?: |$)(.*)'))
        async def t(e):
            if e.sender_id!=self.owner: return
            c=e.pattern_match.group(1).strip()
            if not c: return await e.reply("❌ Укажите команду")
            m=await e.reply(f"Выполнение: `{c}`...")
            try:
                r=subprocess.run(c,shell=True,capture_output=True,text=True,timeout=30)
                o=r.stdout or r.stderr or "✅ Выполнено"
                await m.edit(f"```bash\n{o[:3500]}\n```")
            except: await m.edit("❌ Ошибка")
        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}инфо(?: |$)(.*)'))
        async def i(e):
            if e.sender_id!=self.owner: return
            t=e.pattern_match.group(1).strip()
            try: u=await self.client.get_entity(int(t) if t and t.isdigit() else t) if t else e.sender
            except: return await e.reply("❌ Не найден")
            await e.reply(f"👤 {u.first_name}\n🆔 `{u.id}`\n📱 @{u.username if u.username else 'Нет'}")
        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}кфг(?: |$)(.*)'))
        async def k(e):
            if e.sender_id!=self.owner: return
            a=e.pattern_match.group(1).strip()
            if not a: return await e.reply(f"Префикс: `{self.prefix}`\nЭмодзи: {CFG_EMOJI}")
            p,v=a.split()[:2]
            if p=="префикс": self.db.set("prefix",v); await e.reply(f"✅ Префикс `{v}`\n⚠️ Перезапустите: `{v}рестарт`")
            elif p=="эмодзи": self.db.set("cfg_emoji",v); await e.reply(f"✅ Эмодзи {v}")
        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}лм(?: |$)(.*)'))
        async def lm(e):
            if e.sender_id!=self.owner: return
            n=e.pattern_match.group(1).strip()
            if n: self.loaded_modules[n]=True; await e.reply(f"✅ Модуль `{n}` загружен")
        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}мл$'))
        async def lm2(e):
            if e.sender_id!=self.owner: return
            await e.reply(f"📦 Загружено: {len(self.loaded_modules)} модулей")
        @self.client.on(events.NewMessage(pattern=f'^{self.prefix}выгрмд(?: |$)(.*)'))
        async def ul(e):
            if e.sender_id!=self.owner: return
            n=e.pattern_match.group(1).strip()
            if n in self.loaded_modules: del self.loaded_modules[n]; await e.reply(f"✅ Модуль `{n}` выгружен")
        @self.client.on(events.CallbackQuery)
        async def cb(e):
            if e.sender_id!=self.owner: return await e.answer("⛔")
            if e.data==b"st": await e.edit("📊 KoliUB работает!")
            elif e.data==b"cl": await e.delete()
        logger.info(f"{CFG_EMOJI} Команды загружены")

    async def run(self):
        logger.info(f"{CFG_EMOJI} KoliUB готов! Префикс: {self.prefix}")
        await self.client.run_until_disconnected()