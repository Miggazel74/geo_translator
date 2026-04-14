#!/bin/bash

# 1. Запускаем звуковой сервер в базовом Termux, чтобы Ubuntu могла слушать микрофон
echo "[Запуск звукового моста...]"
pulseaudio --start --exit-idle-time=-1 --load="module-native-protocol-tcp auth-ip-acl=127.0.0.1 auth-anonymous=1" 2>/dev/null || true

# 2. Проваливаемся в вашу Ubuntu, передаем ей IP звукового сервера и сразу запускаем скрипт
echo "[Вход в Ubuntu и запуск переводчика...]"
proot-distro login ubuntu -- bash -c "export PULSE_SERVER=127.0.0.1 && cd $(pwd) && python3 translator.py"
