1. Tắt Real-Time Protection của Window Defender

2. Chạy lệnh tạo biến môi trường
```bash
cp .env.example .env
```

3. Tạo môi trường ảo
```bash
python -m venv .venv
```

4. Kích hoạt môi trường ảo
## Windows
```bash
cmd .venv\Scripts\activate
```

## Linux 
```bash
Linux source .venv/bin/activate
```

5. Tắt môi trường ảo
```bash
deactivate
```

6. Chạy lệnh cài đặt thư viện
```bash
pip install -r requirements.txt
```

7. Chạy hệ thống
```bash
python main.py
```