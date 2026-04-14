#!/data/data/com.termux/files/usr/bin/bash
# Запускается из ОСНОВНОГО Termux
# Заходит в Ubuntu и запускает переводчик

echo "[1/1] Запуск переводчика в Ubuntu..."
proot-distro login ubuntu -- bash -c "cd ~/geo_translator && python3 translator.py"
