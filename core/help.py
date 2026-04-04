from core.loader import MODULES

def build_help():
    text = "📚 Команды:\n\n"

    for name, mod in MODULES.items():
        cmds = getattr(mod, "commands", [])
        if cmds:
            text += f"▪️ {name}:\n"
            for c in cmds:
                text += f"  .{c}\n"
            text += "\n"

    return text
