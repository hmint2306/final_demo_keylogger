đóng gói
pyinstaller --noconfirm --onedir --windowed --add-data "icons;icons/" --add-data ".env;."  "main.py"

đóng gói mac
pyinstaller --noconfirm --onedir --windowed --add-data "icons:icons/" --add-data ".env:."  "main.py"