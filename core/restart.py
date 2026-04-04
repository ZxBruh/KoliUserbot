import os
import sys
import time

def restart():
    start = time.time()
    print(f"Бот перезагружен за {int(time.time() - start)} секунд!")
    os.execv(sys.executable, [sys.executable] + sys.argv)
