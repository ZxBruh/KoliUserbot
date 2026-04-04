# core/github.py

import requests
from core.config import REPO, UPDATE_CHANNEL


def get_branch():
    return "main" if UPDATE_CHANNEL == "main" else "dev"


def get_version():
    branch = get_branch()

    url = f"https://raw.githubusercontent.com/{REPO}/{branch}/version.txt"
    r = requests.get(url, timeout=5)

    return r.text.strip()


def get_commit():
    branch = get_branch()

    url = f"https://api.github.com/repos/{REPO}/commits/{branch}"
    r = requests.get(url, timeout=5).json()

    return r["sha"][:7], r["commit"]["message"]