from core.github import get_commit
from core.config import config

def check_update():
    return get_commit(config["repo"])
