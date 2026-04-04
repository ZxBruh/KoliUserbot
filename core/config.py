import json
from pathlib import Path

PATH = Path("data/config.json")

DEFAULT = {
    "prefix": ".",
    "repo": "Zxbruh/KoliUserbot",
    "branch": "main",
    "modules": ["ping", "help", "system", "loader"]
}

def load():
    if not PATH.exists():
        PATH.parent.mkdir(parents=True, exist_ok=True)
        PATH.write_text(json.dumps(DEFAULT, indent=2), encoding="utf-8")
    return json.loads(PATH.read_text(encoding="utf-8"))

config = load()
