import os
import queue
import sounddevice as sd
import numpy as np
from transformers import pipeline, WhisperProcessor, WhisperForConditionalGeneration
import speech_recognition as sr
import warnings

warnings.filterwarnings("ignore")

# ==================== НАСТРОЙКИ НЕЙРОСЕТЕЙ ====================
print("=== [1/3] Загрузка переводчика NLLB-200... ===")
# NLLB-200 для перевода. При первом запуске скачает ~1.2 Гб, потом будет работать офлайн
translator = pipeline(
    "translation", 
    model="facebook/nllb-200-distilled-600M",
    device=-1 # -1 = CPU
)

def translate_text(text, src_lang, tgt_lang):
    # Коды языков: rus_Cyrl (Русский), kat_Geor (Грузинский)
    result = translator(text, src_lang=src_lang, tgt_lang=tgt_lang, max_length=400)
    return result[0]['translation_text']

print("=== [2/3] Загрузка распознавания речи Whisper (tiny)... ===")
# При первом запуске скачает модель (~150 МБ)
stt_model_id = "openai/whisper-tiny"
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
    print(f"\n[🔊 ОЗВУЧИВАНИЕ ГРУЗИНСКОГО]: {text}")
    # Библиотека TTS_ka скачивает свою модель автоматически и говорит
    os.system(f"python3 -m TTS_ka \"{text}\" --lang ka")

# ==================== ЛОГИКА РАБОТЫ ====================
r = sr.Recognizer()

def listen_and_process(microphone, source_lang="ru", target_lang="ka"):
    print(f"\n[{'🔴 ГОВОРИТЕ (Русский)' if source_lang == 'ru' else '🔴 ГОВОРИТЕ (Грузинский)'}] Слушаю...")
    
    try:
        with microphone as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            # Слушаем максимум 10 секунд
            audio = r.listen(source, phrase_time_limit=10, timeout=10) 
    except sr.WaitTimeoutError:
        print("[Ничего не было сказано]")
        return
        
    print("[Обработка звука...]")
    # Конвертируем звук во Float массив для Whisper
    audio_data = np.frombuffer(audio.get_raw_data(), np.int16).astype(np.float32) / 32768.0
    
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
    mic = sr.Microphone(sample_rate=16000)
    
    print("\n" + "="*40)
    print("УМНЫЙ ОФЛАЙН-ПЕРЕВОДЧИК ГОТОВ!")
    print("="*40)
    
    while True:
        try:
            mode = input("\nВыберите действие (1 - Сказать на русском, 2 - Послушать грузинский, 0 - Выход): ").strip()
            
            if mode == '1':
                listen_and_process(mic, source_lang="ru", target_lang="ka")
            elif mode == '2':
                listen_and_process(mic, source_lang="ka", target_lang="ru")
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
