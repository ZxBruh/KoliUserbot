import os
import importlib

class ModuleLoader:
    def __init__(self, module_dir="modules"):
        self.module_dir = module_dir

    def load_all(self):
        if not os.path.exists(self.module_dir):
            os.makedirs(self.module_dir)
        print("📥 Модули Koli загружены.")
      
