import os
import sys
import subprocess
import google.generativeai as genai

# ==================== КЛЮЧ API ====================
# Вставьте ваш ключ Gemini API сюда:
GEMINI_API_KEY = "ВСТАВЬТЕ_ВАШИ_КЛЮЧ_СЮДА"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ==================== ЗАПИСЬ ГОЛОСА ====================
TERMUX_MIC = "/data/data/com.termux/files/usr/bin/termux-microphone-record"
TEMP_FILE  = "/tmp/voice.aac"
DURATION   = 5

def record():
    if os.path.exists(TEMP_FILE):
        os.remove(TEMP_FILE)
    print(f"\n[ЗАПИСЬ] Говорите... ({DURATION} сек)")
    subprocess.run([TERMUX_MIC, "-l", str(DURATION), "-o", TEMP_FILE])
    if not os.path.exists(TEMP_FILE) or os.path.getsize(TEMP_FILE) < 100:
        print("[ОШИБКА] Файл не записан. Проверьте разрешение на микрофон у Termux:API.")
        return False
    print("[OK] Запись окончена.")
    return True

# ==================== ПЕРЕВОД ЧЕРЕЗ GEMINI ====================
def translate(mode):
    if mode == "1":
        prompt = "Ты переводчик. Прослушай аудио и переведи речь с РУССКОГО на ГРУЗИНСКИЙ. Напиши только перевод, без объяснений."
    else:
        prompt = "Ты переводчик. Прослушай аудио и переведи речь с ГРУЗИНСКОГО на РУССКИЙ. Напиши только перевод, без объяснений."

    print("[Отправка в Gemini...]")
    with open(TEMP_FILE, "rb") as f:
        audio_data = f.read()

    response = model.generate_content([
        prompt,
        {"mime_type": "audio/aac", "data": audio_data}
    ])
    return response.text.strip()

# ==================== ГЛАВНЫЙ ЦИКЛ ====================
def main():
    print("\n" + "="*40)
    print("  ПЕРЕВОДЧИК Русский <-> Грузинский  ")
    print("         (онлайн, через Gemini)       ")
    print("="*40)

    while True:
        try:
            print("\n1 - Я говорю по-РУССКИ  (-> Грузинский)")
            print("2 - Мне говорят по-ГРУЗИНСКИ (-> Русский)")
            print("0 - Выход")
            mode = input("\nВыбор: ").strip()

            if mode == "0":
                break
            elif mode in ("1", "2"):
                if record():
                    result = translate(mode)
                    print("\n" + "="*40)
                    print(f"ПЕРЕВОД: {result}")
                    print("="*40)
            else:
                print("Введите 1, 2 или 0.")

        except KeyboardInterrupt:
            print("\nВыход.")
            break
        except Exception as e:
            print(f"[ОШИБКА]: {e}")

if __name__ == "__main__":
    main()
