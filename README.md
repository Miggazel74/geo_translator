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
В папке проекта напишите:
```bash
python3 translator.py
```
> [!WARNING]
> Самый первый раз потребуется ВАЙФАЙ (интернет), так как скрипту нужно скачать веса трёх нейросетей суммарно на 1.5 ГБ (NLLB-200, Whisper и TTS_ka). Как только они скачаются и вы сделаете первый перевод, скрипт закеширует всё в память телефона. После этого интернет вам больше никогда не понадобится в этой программе.
