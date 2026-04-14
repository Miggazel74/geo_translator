# Офлайн переводчик: Русский <-> Грузинский

Полностью автономный голосовой переводчик без использования интернета для запуска на смартфонах через Termux.

## 📱 Шаг 1: Настройка телефона (Termux + Ubuntu)
1. Установите [Termux](https://f-droid.org/en/packages/com.termux/).
2. В консоли Termux выполните установку эмулятора Ubuntu:
   ```bash
   pkg update
   pkg install proot-distro pulseaudio
   proot-distro install ubuntu
   ```
3. Пробросьте аудио в Ubuntu (важно для микрофона!), каждый раз перед стартом Ubuntu вводите в Termux:
   ```bash
   pulseaudio --start --load="module-native-protocol-tcp auth-ip-acl=127.0.0.1 auth-anonymous=1" --exit-idle-time=-1
   export PULSE_SERVER=127.0.0.1
   proot-distro login ubuntu
   ```

## 🛠 Шаг 2: Установка скрипта
Находясь внутри эмулятора Ubuntu:
1. Клонируем проект из GitHub (здесь будет ваша ссылка):
   ```bash
   git clone <ССЫЛКА_НА_GITHUB>
   cd geo_translator
   ```
2. Разрешаем запуск установщика:
   ```bash
   chmod +x setup_termux.sh
   ./setup_termux.sh
   ```

## 🚀 Шаг 3: Запуск программы
В папке проекта (внутри Ubuntu) напишите:
```bash
python3 translator.py
```
Или используйте готовый скрипт запуска (из-под Termux):
```bash
chmod +x start_geo.sh
./start_geo.sh
```

## 🎤 Если вас не слышно (решение проблем)
Если программа запускается, но "не слышит" голос:

1. **Проверьте разрешения Android**: 
   Зайдите в Настройки -> Приложения -> Termux -> Разрешения -> Микрофон (должно быть "Разрешено").
2. **Активируйте микрофон в PulseAudio**:
   Перед входом в Ubuntu выполните в Termux:
   ```bash
   pulseaudio --kill
   pulseaudio --start --load="module-native-protocol-tcp auth-ip-acl=127.0.0.1 auth-anonymous=1" --load="module-sles-source" --exit-idle-time=-1
   ```
3. **Запустите тест**:
   Внутри Ubuntu выполните:
   ```bash
   export PULSE_SERVER=127.0.0.1
   python3 check_audio.py
   ```
   Если амплитуда в тесте стала больше 0.000000 — значит всё работает.

> [!WARNING]
> Самый первый раз потребуется ВАЙФАЙ...
