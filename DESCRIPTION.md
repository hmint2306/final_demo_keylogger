# MÔ TẢ CHI TIẾT DỰ ÁN DEMO: TOPIC 4 - KEYLOGGER & ANTI-KEYLOGGER

## 1. Tên dự án: Papa Note (Ứng dụng Ghi chú Thông minh)
Dự án được thiết kế dưới dạng một phần mềm ghi chú (Note-taking app) thông thường nhưng bên trong ẩn chứa một module Keylogger hoạt động ngầm. Mục tiêu là minh họa cách thức mã độc lẩn trốn trong các ứng dụng hợp pháp để thu thập dữ liệu người dùng.

---

## 2. Kiến trúc Hệ thống

### A. Thành phần Người dùng thấy (Legitimate Frontend)
- **Giao diện:** Xây dựng bằng thư viện đồ họa (ví dụ: Tkinter hoặc PyQt).
- **Tính năng:** Tạo ghi chú, xóa ghi chú, tìm kiếm.
- **Lưu trữ:** Sử dụng SQLite Database để lưu các bản ghi chú cục bộ, tạo cảm giác chuyên nghiệp và tin cậy.
- **Phân phối:** Đóng gói thành file `.exe` duy nhất bằng `PyInstaller` để người dùng dễ dàng cài đặt.

### B. Thành phần Ngầm (Malicious Background)
- **Module Keylogger:** Chạy trên một luồng (thread) riêng biệt ngay khi ứng dụng được mở.
- **Cơ chế Hooking:** Sử dụng kỹ thuật **Low-Level Keyboard Hook** (WH_KEYBOARD_LL) thông qua thư viện `ctypes` hoặc `pynput` để đánh chặn các sự kiện bàn phím từ hệ điều hành.
- **Phạm vi:** Không chỉ bắt phím trong ứng dụng ghi chú mà bắt toàn cục hệ thống (khi người dùng mở trình duyệt, đăng nhập ngân hàng, v.v.).

### C. Cơ chế Chuyển giao dữ liệu (Data Exfiltration)
- **Tần suất:** Cứ sau mỗi 5 phút hoặc khi file log đạt 500 ký tự.
- **Giao thức:** Sử dụng SMTP (Simple Mail Transfer Protocol) để gửi email tự động.
- **Bảo mật hacker:** Log được đính kèm dưới dạng file `.txt` hoặc nội dung text trực tiếp trong email gửi đến địa chỉ của hacker.

---

## 3. Kịch bản Demo (Scenario)

### Giai đoạn 1: Sự lừa dối (The Deception)
1. Hacker gửi file `PapaNote_Setup.exe` cho nạn nhân (hoặc giả lập việc tải từ một trang web).
2. Nạn nhân cài đặt và mở ứng dụng. Giao diện ghi chú hiện lên rất bình thường.
3. Nạn nhân thử tạo một ghi chú với tiêu đề "Kế hoạch chi tiêu" và lưu lại.

### Giai đoạn 2: Sự phản bội (The Violation)
1. Nạn nhân để ứng dụng ghi chú chạy dưới khay hệ thống (System Tray).
2. Nạn nhân mở trình duyệt Chrome, truy cập vào một trang web (ví dụ: Gmail hoặc Facebook) và thực hiện đăng nhập.
3. Keylogger ngầm ghi lại toàn bộ chuỗi ký tự: `www.facebook.com[ENTER]user_abc[TAB]password123[ENTER]`.

### Giai đoạn 3: Thu hoạch (The Harvest)
1. Sau khoảng thời gian định sẵn, một email tự động được gửi đi từ máy nạn nhân.
2. Hacker mở hộp thư đến và thấy log chi tiết các hành động của nạn nhân.

---

## 4. Giải pháp Phòng chống (Anti-Keylogger Demonstration)

Dự án cung cấp một mục **"Security Center"** bên trong ứng dụng để giáo dục người dùng:
- **Virtual Keyboard (Bàn phím ảo):** Một bàn phím trên màn hình tích hợp sẵn. Khi người dùng click chuột vào các phím ảo, dữ liệu được truyền thẳng vào ứng dụng thông qua sự kiện chuột (Mouse Events), hoàn toàn bypass (vượt qua) các hook bàn phím vật lý mà Keylogger đang lắng nghe.
- **Giải thích kỹ thuật:** Demo sẽ chỉ ra rằng file log của hacker sẽ bị **TRỐNG** ở những đoạn người dùng nhập bằng bàn phím ảo, minh chứng cho tính hiệu quả của phương pháp này.

---

## 5. Công nghệ sử dụng
- **Ngôn ngữ:** Python 3.10+.
- **Thư viện UI:** CustomTkinter.
- **Thư viện Keylogger:** `pynput` hoặc `ctypes` (tương tác trực tiếp Win32 API).
- **Database:** SQLite3.
- **Đóng gói:** PyInstaller.
- **Giao thức mạng:** `smtplib`, `ssl`.

---

## 6. Lưu ý an toàn (Safety Disclaimer)
Dự án này chỉ nhằm mục đích giáo dục và nghiên cứu học thuật tại Ton Duc Thang University. Nghiêm cấm sử dụng mã nguồn này vào mục đích xâm phạm quyền riêng tư hoặc vi phạm pháp luật. Mọi thông tin gửi đi trong demo phải sử dụng email giả lập hoặc tài khoản thử nghiệm của nhóm dự án.