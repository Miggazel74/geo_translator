#!/bin/bash
echo "Обновление системы..."
apt update && apt upgrade -y

echo "Установка системных зависимостей..."
apt install -y python3 python3-pip python3-dev portaudio19-dev libasound2-dev ffmpeg mpv

echo "Установка Python библиотек..."
pip3 install -r requirements.txt

echo "==========================================="
echo "Установка завершена! Запустите: python3 translator.py"
echo "ВАЖНО: При первом запуске нужен ИНТЕРНЕТ для скачивания моделей (~1.5 Гб)."
echo "После первого перевода интернет можно выключать."
