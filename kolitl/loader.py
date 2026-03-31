import os
import importlib

class ModuleLoader:
    def __init__(self, folder="modules"):
        self.folder = folder
        self.loaded = []

    def load_all(self):
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        
        files = [f for f in os.listdir(self.folder) if f.endswith(".py")]
        for f in files:
            self.loaded.append(f[:-3])
        
        print(f"📥 Модули загружены: {', '.join(self.loaded) if self.loaded else 'Пусто'}")

    async def handle_command(self, event):
        # Базовая логика: если в папке modules есть файл, совпадающий с командой
        cmd = event.raw_text.split()[0][1:] # .help -> help
        if cmd in self.loaded:
            # Здесь вызывается логика из конкретного файла
            await event.edit(f"⚙️ Выполняю команду: **{cmd}**...")
