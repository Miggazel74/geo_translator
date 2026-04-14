import os
import sys
import subprocess
import argparse
import numpy as np
import soundfile as sf
import warnings

warnings.filterwarnings("ignore")

# ==================== АРГУМЕНТЫ КОМАНДНОЙ СТРОКИ ====================
parser = argparse.ArgumentParser()
parser.add_argument("--file", type=str, default=None,
                    help="Путь к WAV-файлу с голосом (если не указан - интерактивный режим)")
parser.add_argument("--lang", type=str, default="ru",
                    help="Язык входного аудио: ru (русский) или ka (грузинский)")
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
    print(f"\n[ОЗВУЧИВАНИЕ ГРУЗИНСКОГО]: {text}")
    subprocess.run([sys.executable, "-m", "TTS_ka", text, "--lang", "ka"])

# ==================== ЧТЕНИЕ АУДИО ИЗ ФАЙЛА ====================
def load_audio_file(file_path):
    """Читает WAV-файл и возвращает numpy-массив на 16kHz."""
    print(f"[ЧТЕНИЕ ФАЙЛА]: {file_path}")
    if not os.path.exists(file_path):
        print(f"[ОШИБКА]: Файл не найден: {file_path}")
        return None

    audio_data, sample_rate = sf.read(file_path, dtype="float32")

    # Если стерео - берем только один канал
    if len(audio_data.shape) > 1:
        audio_data = audio_data[:, 0]

    # Если частота не 16kHz - пересэмплируем
    if sample_rate != 16000:
        import scipy.signal as sps
        num_samples = int(len(audio_data) * 16000 / sample_rate)
        audio_data = sps.resample(audio_data, num_samples)

    # Проверяем, есть ли вообще звук
    max_amp = np.max(np.abs(audio_data))
    print(f"[УРОВЕНЬ СИГНАЛА]: {max_amp:.6f}")
    if max_amp < 0.0001:
        print("[ВНИМАНИЕ]: Файл содержит тишину. Проверьте запись.")
        return None

    return audio_data

# ==================== ОБРАБОТКА ОДНОГО АУДИО-ФАЙЛА ====================
def process_file(file_path, source_lang="ru"):
    audio_data = load_audio_file(file_path)
    if audio_data is None:
        return

    target_lang = "ka" if source_lang == "ru" else "ru"

    print("[Распознавание речи...]")
    recognized_text = transcribe_audio(audio_data, language=source_lang)
    print(f"[РАСПОЗНАНО]: {recognized_text}")

    if not recognized_text:
        print("[ОШИБКА]: Текст не распознан.")
        return

    src_code = "rus_Cyrl" if source_lang == "ru" else "kat_Geor"
    tgt_code = "kat_Geor" if source_lang == "ru" else "rus_Cyrl"
    translated_text = translate_text(recognized_text, src_code, tgt_code)
    print(f"[ПЕРЕВОД]: {translated_text}")

    if target_lang == "ka":
        speak_georgian(translated_text)

# ==================== ИНТЕРАКТИВНЫЙ РЕЖИМ (через файл) ====================
def interactive_mode():
    """
    Интерактивный цикл.
    Запись теперь делается в Termux командой:
        termux-microphone-record -l 5 -f WAV -o ~/geo_translator/voice_input.wav
    После записи нажать Enter здесь для обработки.
    """
    SHARED_FILE = os.path.join(os.path.dirname(__file__), "voice_input.wav")

    print("\n" + "="*50)
    print("УМНЫЙ ОФЛАЙН-ПЕРЕВОДЧИК ГОТОВ!")
    print("="*50)
    print("\nИНСТРУКЦИЯ:")
    print("  1. Откройте НОВОЕ ОКНО в Termux (не Ubuntu)")
    print("  2. Введите команду записи:")
    print("     record.sh")
    print("  3. Говорите 5 секунд")
    print("  4. Вернитесь сюда и нажмите ENTER")
    print("="*50)

    while True:
        try:
            mode = input("\nВыберите язык (1 - Русский->Грузинский, 2 - Грузинский->Русский, 0 - Выход): ").strip()

            if mode == "0":
                print("Завершение работы.")
                break
            elif mode not in ("1", "2"):
                print("Неверный ввод.")
                continue

            source_lang = "ru" if mode == "1" else "ka"
            lang_name = "РУССКИЙ" if source_lang == "ru" else "ГРУЗИНСКИЙ"

            print(f"\n[{lang_name}] Ожидание файла...")
            print(f"Запустите в Termux: bash ~/geo_translator/record.sh")
            input("Когда запись закончится - нажмите ENTER здесь...")

            process_file(SHARED_FILE, source_lang=source_lang)

        except KeyboardInterrupt:
            print("\nПрограмма завершена.")
            break
        except Exception as e:
            print(f"Ошибка: {e}")

# ==================== ТОЧКА ВХОДА ====================
if __name__ == "__main__":
    if args.file:
        # Режим одноразовой обработки файла
        process_file(args.file, source_lang=args.lang)
    else:
        # Интерактивный режим
        interactive_mode()
