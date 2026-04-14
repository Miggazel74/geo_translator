#!/bin/bash

# 1. Запускаем звуковой сервер с поддержкой микрофона (SLES)
echo "[1/2] Настройка аудио-моста..."
pulseaudio --kill 2>/dev/null || true
pulseaudio --start --load="module-native-protocol-tcp auth-ip-acl=127.0.0.1 auth-anonymous=1" --load="module-sles-source" --exit-idle-time=-1

# 2. Входим в Ubuntu и запускаем переводчик
echo "[2/2] Вход в Ubuntu и запуск..."
export PULSE_SERVER=127.0.0.1
# Мы используем ~/geo_translator, так как это стандартный путь после git clone внутри Ubuntu
proot-distro login ubuntu -- bash -c "export PULSE_SERVER=127.0.0.1 && cd ~/geo_translator && python3 translator.py"

