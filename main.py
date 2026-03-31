import argparse
import asyncio
import base64
import binascii
import collections
import contextlib
import importlib
import json
import logging
import os
import random
import signal
import socket
import sqlite3
import string
import sys
import typing
import zlib
from getpass import getpass
from pathlib import Path

import aiohttp
import kolitl # Тотальная замена herokutl
from kolitl import events
from kolitl.errors import (
    ApiIdInvalidError,
    AuthKeyDuplicatedError,
    FloodWaitError,
    PasswordHashInvalidError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
)
from kolitl.network.connection import (
    ConnectionTcpFull,
    ConnectionTcpMTProxyRandomizedIntermediate,
)
from kolitl.password import compute_check
from kolitl.sessions import MemorySession, SQLiteSession
from kolitl.tl.functions.account import GetPasswordRequest
from kolitl.tl.functions.auth import CheckPasswordRequest
from kolitl.tl.functions.contacts import UnblockRequest

from . import database, loader, utils, version
from ._internal import print_banner, restart
from .dispatcher import CommandDispatcher
from .inline.token_obtainment import TokenObtainment
from .inline.utils import Utils as inutils
from .qr import QRCode
from .secure import patcher
from .tl_cache import CustomTelegramClient
from .translations import Translator
from .version import __version__

try:
    from .web import core
except ImportError:
    web_available = False
    logging.exception("Koli Engine: Unable to import web components")
else:
    web_available = True

BASE_DIR = (
    "/data"
    if "DOCKER" in os.environ
    else os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

BASE_PATH = Path(BASE_DIR)
CONFIG_PATH = BASE_PATH / "config.json"

# Тот самый огромный список для генерации имен (Koli Mock)
LATIN_MOCK = [
    "Amor", "Arbor", "Astra", "Aurum", "Bellum", "Caelum",
    "Calor", "Candor", "Carpe", "Celer", "Certo", "Cibus",
    "Civis", "Clemens", "Coetus", "Cogito", "Conexus",
    "Consilium", "Cresco", "Cura", "Cursus", "Decus",
    "Deus", "Dies", "Digitus", "Discipulus", "Dominus",
    "Donum", "Dulcis", "Durus", "Elementum", "Emendo",
    "Ensis", "Equus", "Espero", "Fidelis", "Fides",
    "Finis", "Flamma", "Flos", "Fortis", "Frater", "Fuga",
    "Fulgeo", "Genius", "Gloria", "Gratia", "Gravis",
    "Habitus", "Honor", "Hora", "Ignis", "Imago",
    "Imperium", "Inceptum", "Infinitus", "Ingenium",
    "Initium", "Intra", "Iunctus", "Iustitia", "Labor",
    "Laurus", "Lectus", "Legio", "Liberi", "Libertas",
    "Lumen", "Lux", "Magister", "Magnus", "Manus",
    "Memoria", "Mens", "Mors", "Mundo", "Natura",
    "Nexus", "Nobilis", "Nomen", "Novus", "Nox",
    "Oculus", "Omnis", "Opus", "Orbis", "Ordo", "Os",
    "Pax", "Perpetuus", "Persona", "Petra", "Pietas",
    "Pons", "Populus", "Potentia", "Primus", "Proelium",
    "Pulcher", "Purus", "Quaero", "Quies", "Ratio",
    "Regnum", "Sanguis", "Sapientia", "Sensus", "Serenus",
    "Sermo", "Signum", "Sol", "Solus", "Sors", "Spes",
    "Spiritus", "Stella", "Summus", "Teneo", "Terra",
    "Tigris", "Trans", "Tribuo", "Tristis", "Ultimus",
    "Unitas", "Universus", "Uterque", "Valde", "Vates",
    "Veritas", "Verus", "Vester", "Via", "Victoria",
    "Vita", "Vox", "Vultus", "Zephyrus", "Bimbalas", "Nywuctuu",
    "Anyone", "Draher", "Hackimo", "Silvyr",
]

def generate_koli_app_name() -> str:
    return " ".join(random.choices(LATIN_MOCK, k=3))

def get_koli_app_name() -> str:
    if not (app_name := get_config_key("koli_app_name")):
        app_name = generate_koli_app_name()
        save_config_key("koli_app_name", app_name)
    return app_name

def generate_random_system_version():
    """Полный список ОС для маскировки сессии Koli"""
    os_choices = [
        ("Windows", "11"), ("Windows", "10"), ("Windows", "7"),
        ("macOS", "14 Sonoma"), ("macOS", "13 Ventura"),
        ("iOS", "17.4"), ("Android", "14"), ("Android", "15"),
        ("Ubuntu", "24.04"), ("Debian", "12"), ("Arch Linux", "rolling"),
        ("Kali Linux", "2024.1"), ("FreeBSD", "14.0"), ("MS-DOS", "6.22")
    ]
    os_name, os_version = random.choice(os_choices)
    return f"{os_name} {os_version}"

def run_config():
    from . import configurator
    return configurator.api_config(None)

def get_config_key(key: str) -> typing.Union[str, bool]:
    try:
        return json.loads(CONFIG_PATH.read_text()).get(key, False)
    except FileNotFoundError:
        return False

def save_config_key(key: str, value: str) -> bool:
    try:
        config = json.loads(CONFIG_PATH.read_text())
    except FileNotFoundError:
        config = {}
    config[key] = value
    CONFIG_PATH.write_text(json.dumps(config, indent=4))
    return True

def gen_port(cfg: str = "port", no8080: bool = False) -> int:
    if "DOCKER" in os.environ and not no8080:
        return 8080
    if port := get_config_key(cfg):
        return port
    while port := random.randint(1024, 65536):
        if socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex(("localhost", port)):
            break
    return port

class SuperList(list):
    def __getattribute__(self, attr: str) -> typing.Any:
        if hasattr(list, attr):
            return list.__getattribute__(self, attr)
        for obj in self:
            attribute = getattr(obj, attr)
            if callable(attribute):
                if asyncio.iscoroutinefunction(attribute):
                    async def foobar(*args, **kwargs):
                        return [await getattr(_, attr)(*args, **kwargs) for _ in self]
                    return foobar
                return lambda *args, **kwargs: [getattr(_, attr)(*args, **kwargs) for _ in self]
            return [getattr(x, attr) for x in self]

class KoliInstance:
    """Главный класс Koli Userbot"""
    def __init__(self):
        global BASE_DIR, BASE_PATH, CONFIG_PATH
        self.omit_log = False
        self.arguments = self.parse_arguments()
        if self.arguments.no_git:
            os.environ["KOLI_NO_GIT"] = "1"
        if self.arguments.data_root:
            BASE_DIR = self.arguments.data_root
            BASE_PATH = Path(BASE_DIR)
            CONFIG_PATH = BASE_PATH / "config.json"
        
        # Исправляем ошибку asyncio loop со скрина
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

        self.clients = SuperList()
        self.ready = asyncio.Event()
        self._read_sessions()
        self._get_api_token()
        self._get_proxy()

    def parse_arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--port", dest="port", default=gen_port(), type=int)
        parser.add_argument("--phone", "-p", action="append")
        parser.add_argument("--no-web", dest="disable_web", action="store_true")
        parser.add_argument("--no-git", dest="no_git", action="store_true")
        parser.add_argument("--data-root", dest="data_root", default="")
        return parser.parse_args()

    def _read_sessions(self):
        """Парсинг только сессий Koli"""
        self.sessions = [
            SQLiteSession(os.path.join(BASE_DIR, f.rsplit(".session", 1)[0]))
            for f in os.listdir(BASE_DIR)
            if (f.startswith("koli-") or f.startswith("zxbruh-")) and f.endswith(".session")
        ]

    def _get_api_token(self):
        api_token_type = collections.namedtuple("api_token", ("ID", "HASH"))
        try:
            api_token = api_token_type(get_config_key("api_id"), get_config_key("api_hash"))
        except Exception:
            api_token = None
        self.api_token = api_token

    def _get_proxy(self):
        self.proxy, self.conn = None, ConnectionTcpFull

    async def save_client_session(self, client: CustomTelegramClient, *, delay_restart: bool = False):
        """Логика сохранения сессии с брендингом koli-"""
        me = await client.get_me()
        telegram_id = me.id
        session_name = f"koli-{telegram_id}"
        
        session = SQLiteSession(os.path.join(BASE_DIR, session_name))
        session.set_dc(client.session.dc_id, client.session.server_address, client.session.port)
        session.auth_key = client.session.auth_key
        session.save()

        if not delay_restart:
            client.disconnect()
            restart()
        
        print(f"✅ Сессия Koli успешно сохранена как {session_name}")

    async def main_logic(self):
        print_banner()
        print(f"🚀 Запуск огромной машины Koli на {generate_random_system_version()}...")
        # (Весь остальной объем логики авторизации и работы)
        await asyncio.gather(*[c.run_until_disconnected() for c in self.clients])

if __name__ == "__main__":
    koli_machine = KoliInstance()
    # Тот самый фикс для Firstbyte
    koli_machine.loop.run_until_complete(koli_machine.main_logic())
