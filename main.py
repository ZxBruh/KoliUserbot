from core.config import config
from core.loader import load_module, MODULES
from core.help import build_help
from core.restart import restart
from core.updater import check_update

import os

PREFIX = config["prefix"]


# загрузка модулей при старте
def init_modules():
    for m in config["modules"]:
        path = f"modules/{m}.py"
        if os.path.exists(path):
            load_module(path)


init_modules()


# --- УПРОЩЁННЫЙ ДИСПЕТЧЕР (заглушка логики) ---
def handle_command(cmd: str):
    cmd = cmd.replace(PREFIX, "")

    if cmd == "хелп":
        return build_help()

    if cmd == "пинг":
        return "🏓 pong"

    if cmd == "рестарт":
        restart()

    if cmd == "обнова":
        return check_update()

    return "❌ команда не найдена"


# --- ТЕСТОВЫЙ CLI (пока без Telegram API) ---
if __name__ == "__main__":
    print("KoliUserbot запущен")

    while True:
        inp = input(">>> ")
        print(handle_command(inp))