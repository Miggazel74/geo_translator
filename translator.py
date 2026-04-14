import os
import sys
import subprocess
import queue
import sounddevice as sd
import numpy as np
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, WhisperProcessor, WhisperForConditionalGeneration
import speech_recognition as sr
import warnings

warnings.filterwarnings("ignore")

# ==================== НАСТРОЙКИ НЕЙРОСЕТЕЙ ====================
print("=== [1/3] Загрузка переводчика NLLB-200... ===")
# NLLB-200 для перевода. При первом запуске скачает ~1.2 Гб, потом будет работать офлайн
nllb_tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
nllb_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")

def translate_text(text, src_lang, tgt_lang):
    # Коды языков: rus_Cyrl (Русский), kat_Geor (Грузинский)
    nllb_tokenizer.src_lang = src_lang
    inputs = nllb_tokenizer(text, return_tensors="pt")
    forced_bos_token_id = nllb_tokenizer.convert_tokens_to_ids(tgt_lang)
    translated_tokens = nllb_model.generate(**inputs, forced_bos_token_id=forced_bos_token_id, max_length=400)
    return nllb_tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]

print("=== [2/3] Загрузка распознавания речи Whisper (small)... ===")
# Модель small (~960 МБ) обеспечивает лучшее соотношение максимальной точности и приемлемой скорости для телефона
stt_model_id = "openai/whisper-small"
processor = WhisperProcessor.from_pretrained(stt_model_id)
stt_model = WhisperForConditionalGeneration.from_pretrained(stt_model_id)
stt_model.config.forced_decoder_ids = None

def transcribe_audio(audio_data, language="ru"):
    # audio_data - это np.array формата 16kHz
    input_features = processor(audio_data, sampling_rate=16000, return_tensors="pt").input_features
    # Указываем язык, чтобы модель не гадала
    predicted_ids = stt_model.generate(input_features, language=language)
    translation = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
    return translation.strip()

print("=== [3/3] Подготовка синтезатора TTS_ka... ===")
def speak_georgian(text):
    print(f"\n[ОЗВУЧИВАНИЕ ГРУЗИНСКОГО]: {text}")
    # Библиотека TTS_ka скачивает свою модель автоматически и говорит
    subprocess.run([sys.executable, "-m", "TTS_ka", text, "--lang", "ka"])

# ==================== ЛОГИКА РАБОТЫ ====================
def listen_and_process(source_lang="ru", target_lang="ka"):
    duration = 5  # Записываем 5 секунд ровно
    print(f"\n[{'ГОВОРИТЕ (Русский)' if source_lang == 'ru' else 'ГОВОРИТЕ (Грузинский)'}] Слушаю {duration} секунд...")
    
    try:
        # Запись звука напрямую без умных пауз
        record_data = sd.rec(int(duration * 16000), samplerate=16000, channels=1, dtype='float32')
        sd.wait()
        audio_data = record_data.flatten()
        
        # Проверка на то, передал ли Android вообще громкость
        volume = np.abs(audio_data).mean()
        if volume < 0.0001:
            print("[ВНИМАНИЕ]: Микрофон записал абсолютную тишину. Пpoвepьтe громкость и разрешения в Android.")
            return

    except Exception as e:
        print(f"[ОШИБКА ЗАПИСИ]: {e}")
        return
        
    print("[Обработка звука...]")
    
    # 1. Распознавание (Голос -> Текст)
    recognized_text = transcribe_audio(audio_data, language=source_lang)
    print(f"[РАСПОЗНАНО]: {recognized_text}")
    
    if not recognized_text:
        return

    # 2. Перевод (Текст -> Текст)
    src_code = "rus_Cyrl" if source_lang == "ru" else "kat_Geor"
    tgt_code = "kat_Geor" if source_lang == "ru" else "rus_Cyrl"
    translated_text = translate_text(recognized_text, src_code, tgt_code)
    
    print(f"[ПЕРЕВОД]: {translated_text}")

    # 3. Синтез голоса (только если перевели на грузинский)
    if target_lang == "ka":
        speak_georgian(translated_text)

def main():
    print("\n" + "="*40)
    print("УМНЫЙ ОФЛАЙН-ПЕРЕВОДЧИК ГОТОВ!")
    print("="*40)
    
    while True:
        try:
            mode = input("\nВыберите действие (1 - Сказать на русском, 2 - Послушать грузинский, 0 - Выход): ").strip()
            
            if mode == '1':
                listen_and_process(source_lang="ru", target_lang="ka")
            elif mode == '2':
                listen_and_process(source_lang="ka", target_lang="ru")
            elif mode == '0':
                print("Завершение работы.")
                break
            else:
                print("Неверный ввод.")
        except KeyboardInterrupt:
            print("\nПрограмма завершена.")
            break
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
