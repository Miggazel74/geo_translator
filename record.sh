#!/data/data/com.termux/files/usr/bin/bash
# Этот скрипт запускается в ОСНОВНОМ Termux (не в Ubuntu)
# Он записывает голос через родной микрофон Android
# и сохраняет в общую папку, откуда Ubuntu сможет его прочитать

DURATION=5
OUTPUT_FILE="$HOME/geo_translator/voice_input.wav"

echo ""
echo "=== ЗАПИСЬ ГОЛОСА ==="
echo "Говорите в течение ${DURATION} секунд..."
echo ""

termux-microphone-record -l ${DURATION} -f WAV -o "$OUTPUT_FILE"

echo ""
echo "[OK] Запись сохранена. Переключитесь в окно Ubuntu и нажмите ENTER."
