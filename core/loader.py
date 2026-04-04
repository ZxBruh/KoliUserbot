import importlib.util
import os

MODULES = {}

def load_module(path):
    name = os.path.basename(path).replace(".py", "")

    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    MODULES[name] = module
    return module
