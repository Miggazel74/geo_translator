#!/bin/bash

echo "================================================="
echo "УСТАНОВКА ЗАВИСИМОСТЕЙ В СУЩЕСТВУЮЩУЮ UBUNTU"
echo "================================================="
echo "Обновление системных пакетов..."
apt update -y
apt install -y python3-pip python3-venv python3-dev portaudio19-dev libasound2-dev ffmpeg mpv cmake

echo "Обновление pip..."
pip install --break-system-packages --upgrade pip

echo "Установка Python-библиотек (Numpy, Torch, Transformers, Audio)..."
pip install --break-system-packages -r requirements.txt

echo "================================================="
echo "[УСПЕХ] Все нужные пакеты установлены в вашу Ubuntu!"
echo "================================================="
