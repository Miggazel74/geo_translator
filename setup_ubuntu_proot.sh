#!/bin/bash

echo "====================================================="
echo " АВТОМАТИЧЕСКАЯ УСТАНОВКА ОКРУЖЕНИЯ UBUNTU В TERMUX"
echo "====================================================="
echo ""

# Отключаем ограничение фоновых процессов в Android (Phantom Process Killer), если есть Root или ADB, но мы просто игнорируем, если не сработает
echo "[1/4] Подготовка Termux..."
pkg update -y || echo "ВНИМАНИЕ: Если скрипт сейчас прервется с ошибкой 404, выполните команду 'termux-change-repo', выберите все галочки и выберите 'Mirrors by Grimler', затем запустите скрипт заново."
pkg upgrade -y
pkg install proot-distro pulseaudio wget curl -y

# Настройка PulseAudio для проброса звука (Микрофон/Динамик) в Ubuntu
echo "[2/4] Настройка звукового моста PulseAudio..."
mkdir -p ~/.config/pulse
echo "load-module module-native-protocol-tcp auth-ip-acl=127.0.0.1 auth-anonymous=1" > ~/.config/pulse/default.pa
pulseaudio --start --exit-idle-time=-1 || true

echo "[3/4] Установка Ubuntu (может занять время)..."
proot-distro install ubuntu || true

# Создаем скрипт запуска внутри Ubuntu
cat << 'EOF' > ubuntu_setup.sh
#!/bin/bash
export DEBIAN_FRONTEND=noninteractive
export PULSE_SERVER=127.0.0.1

echo "-> Обновление пакетов Ubuntu..."
apt update -y && apt upgrade -y
apt install -y python3 python3-pip python3-venv python3-dev ffmpeg mpv libasound2-dev portaudio19-dev pulseaudio build-essential cmake

# Создаем виртуальное окружение, чтобы pip не ругался на "externally-managed-environment"
echo "-> Создание виртуального окружения Python..."
cd /root/geo_translator
python3 -m venv venv
source venv/bin/activate

echo "-> Обновление pip..."
pip install --upgrade pip

echo "-> Установка библиотек (может занять 15-30 минут!)..."
pip install -r requirements.txt

echo "-> Установка завершена!"
EOF

# Копируем проект и запускаем установку
echo "[4/4] Запуск настройки внутри Ubuntu..."
chmod +x ubuntu_setup.sh
# proot-distro login bind'ит папку с проектом в /root/geo_translator
proot-distro login ubuntu --bind "$PWD:/root/geo_translator" --bind ubuntu_setup.sh:/root/ubuntu_setup.sh -- bash /root/ubuntu_setup.sh

echo "====================================================="
echo "[УСПЕХ] УСТАНОВКА ЗАВЕРШЕНА!"
echo "====================================================="
echo "Для того, чтобы запустить переводчик в любой момент,"
echo "введите следующую команду в Termux (можете скопировать):"
echo ""
echo "proot-distro login ubuntu --bind $PWD:/root/geo_translator -- bash -c \"export PULSE_SERVER=127.0.0.1 && cd /root/geo_translator && source venv/bin/activate && python3 translator.py\""
echo "====================================================="

