import os
import sys
import subprocess
import argparse
import numpy as np
import warnings

warnings.filterwarnings("ignore")

# ==================== АРГУМЕНТЫ ====================
parser = argparse.ArgumentParser()
parser.add_argument("--lang", type=str, default="ru",
                    help="Язык входного аудио: ru или ka")
args = parser.parse_args()

# ==================== ЗАГРУЗКА НЕЙРОСЕТЕЙ ====================
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, WhisperProcessor, WhisperForConditionalGeneration

print("=== [1/3] Загрузка переводчика NLLB-200... ===")
nllb_tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
nllb_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")

def translate_text(text, src_lang, tgt_lang):
    nllb_tokenizer.src_lang = src_lang
    inputs = nllb_tokenizer(text, return_tensors="pt")
    forced_bos_token_id = nllb_tokenizer.convert_tokens_to_ids(tgt_lang)
    translated_tokens = nllb_model.generate(
        **inputs, forced_bos_token_id=forced_bos_token_id, max_length=400
    )
    return nllb_tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]

print("=== [2/3] Загрузка распознавания речи Whisper (small)... ===")
stt_model_id = "openai/whisper-small"
processor = WhisperProcessor.from_pretrained(stt_model_id)
stt_model = WhisperForConditionalGeneration.from_pretrained(stt_model_id)
stt_model.config.forced_decoder_ids = None

def transcribe_audio(audio_data, language="ru"):
    input_features = processor(
        audio_data, sampling_rate=16000, return_tensors="pt"
    ).input_features
    predicted_ids = stt_model.generate(input_features, language=language)
    return processor.batch_decode(predicted_ids, skip_special_tokens=True)[0].strip()

print("=== [3/3] Подготовка синтезатора TTS_ka... ===")
def speak_georgian(text):
    print(f"\n[ОЗВУЧИВАНИЕ]: {text}")
    subprocess.run([sys.executable, "-m", "TTS_ka", text, "--lang", "ka"])

# ==================== ЗАПИСЬ ЧЕРЕЗ TERMUX API ====================
# Путь к termux-microphone-record доступен из Ubuntu через полный путь
TERMUX_MIC = "/data/data/com.termux/files/usr/bin/termux-microphone-record"
TEMP_WAV   = "/tmp/geo_voice.wav"
DURATION   = 5

def record_audio():
    """Записывает голос через Termux API прямо из Ubuntu."""
    if not os.path.exists(TERMUX_MIC):
        print("[ОШИБКА]: termux-microphone-record не найден.")
        print("Установите Termux:API: pkg install termux-api")
        return None

    # Удаляем старый файл если остался
    if os.path.exists(TEMP_WAV):
        os.remove(TEMP_WAV)

    print(f"[ЗАПИСЬ] Говорите... ({DURATION} секунд)")
    result = subprocess.run(
        [TERMUX_MIC, "-l", str(DURATION), "-f", "WAV", "-o", TEMP_WAV],
        capture_output=True, text=True
    )

    if not os.path.exists(TEMP_WAV):
        print(f"[ОШИБКА ЗАПИСИ]: {result.stderr}")
        return None

    return TEMP_WAV

# ==================== ЧТЕНИЕ И ОБРАБОТКА WAV ====================
def load_wav(file_path):
    import soundfile as sf
    import scipy.signal as sps

    audio_data, sample_rate = sf.read(file_path, dtype="float32")

    # Стерео -> моно
    if len(audio_data.shape) > 1:
        audio_data = audio_data[:, 0]

    # Пересэмплирование в 16kHz если нужно
    if sample_rate != 16000:
        num_samples = int(len(audio_data) * 16000 / sample_rate)
        audio_data = sps.resample(audio_data, num_samples)

    max_amp = np.max(np.abs(audio_data))
    print(f"[УРОВЕНЬ СИГНАЛА]: {max_amp:.6f}")

    if max_amp < 0.0001:
        print("[ВНИМАНИЕ]: Записана тишина. Проверьте, что Termux:API имеет разрешение на микрофон.")
        return None

    return audio_data

def process(source_lang):
    # 1. Запись
    wav_file = record_audio()
    if wav_file is None:
        return

    # 2. Загружаем аудио
    audio_data = load_wav(wav_file)
    if audio_data is None:
        return

    # 3. Распознавание
    print("[Распознавание...]")
    recognized = transcribe_audio(audio_data, language=source_lang)
    print(f"[РАСПОЗНАНО]: {recognized}")
    if not recognized:
        return

    # 4. Перевод
    src_code = "rus_Cyrl" if source_lang == "ru" else "kat_Geor"
    tgt_code = "kat_Geor" if source_lang == "ru" else "rus_Cyrl"
    translated = translate_text(recognized, src_code, tgt_code)
    print(f"[ПЕРЕВОД]: {translated}")

    # 5. Синтез (только рус->груз)
    if source_lang == "ru":
        speak_georgian(translated)

# ==================== ГЛАВНЫЙ ЦИКЛ ====================
def main():
    print("\n" + "="*40)
    print("УМНЫЙ ОФЛАЙН-ПЕРЕВОДЧИК ГОТОВ!")
    print("="*40)

    while True:
        try:
            mode = input("\nВыберите (1 - Русский->Грузинский, 2 - Грузинский->Русский, 0 - Выход): ").strip()
            if mode == "1":
                process(source_lang="ru")
            elif mode == "2":
                process(source_lang="ka")
            elif mode == "0":
                print("Выход.")
                break
            else:
                print("Неверный ввод.")
        except KeyboardInterrupt:
            print("\nПрограмма завершена.")
            break

if __name__ == "__main__":
    main()
