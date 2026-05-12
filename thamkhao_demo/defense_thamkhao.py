import tkinter as tk

# Hàm xử lý khi người dùng dùng CHUỘT click vào phím ảo
def button_click(char):
    # Chèn trực tiếp ký tự vào ô nhập liệu mà KHÔNG dùng bàn phím vật lý
    password_entry.insert(tk.END, char)

# Thiết lập giao diện
root = tk.Tk()
root.title("Anti-Keylogger: Secure OSK")
root.geometry("400x250")
root.attributes('-topmost', True) # Luôn nổi trên cùng

# Ô nhập liệu mô phỏng form đăng nhập (Mock Login Form)
tk.Label(root, text="Nhập mật khẩu (SecurePass):", font=("Arial", 12)).pack(pady=10)
password_entry = tk.Entry(root, show="*", font=("Arial", 14), width=20)
password_entry.pack(pady=5)

# Khung chứa các phím ảo
keyboard_frame = tk.Frame(root)
keyboard_frame.pack(pady=10)

# Danh sách các phím mô phỏng
keys = [
    's', 'e', 'c', 'u', 'r',
    'P', 'a', 's', 's', '1', '2', '3'
]

# Tạo các nút bấm tương ứng với phím
row_val = 0
col_val = 0
for key in keys:
    tk.Button(
        keyboard_frame, text=key, width=5, height=2,
        command=lambda k=key: button_click(k) # Bắt sự kiện click chuột
    ).grid(row=row_val, column=col_val, padx=2, pady=2)
    
    col_val += 1
    if col_val > 4:
        col_val = 0
        row_val += 1

tk.Button(root, text="Clear", command=lambda: password_entry.delete(0, tk.END)).pack()

root.mainloop()