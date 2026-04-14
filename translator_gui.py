import streamlit as st
import torch
import numpy as np
import speech_recognition as sr
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, WhisperProcessor, WhisperForConditionalGeneration
import sys
import subprocess
import warnings

warnings.filterwarnings("ignore")

# ==================== НАСТРОЙКИ СТРАНИЦЫ ====================
st.set_page_config(page_title="GeoTranslator Офлайн", page_icon="🇬🇪", layout="centered")

st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        width: 100%;
        height: 100px;
        font-size: 24px;
        border-radius: 20px;
        margin-bottom: 20px;
    }
    .ru-button>button {
        background-color: #0052cc;
        color: white;
    }
    .ka-button>button {
        background-color: #cc0000;
        color: white;
    }
    .result-box {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #0052cc;
        margin-top: 20px;
        font-size: 30px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== ЗАГРУЗКА МОДЕЛЕЙ (С КЭШИРОВАНИЕМ) ====================
@st.cache_resource
def load_models():
    # Загружаем всё один раз при старте
    nllb_tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
    nllb_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")
    
    stt_model_id = "openai/whisper-small"
    processor = WhisperProcessor.from_pretrained(stt_model_id)
    stt_model = WhisperForConditionalGeneration.from_pretrained(stt_model_id)
    
    return nllb_tokenizer, nllb_model, processor, stt_model

# Инициализация моделей
with st.spinner("Загрузка нейросетей... Ждите, это один раз."):
    nllb_tok, nllb_mod, whisper_proc, whisper_mod = load_models()

# ==================== ФУНКЦИИ ОБРАБОТКИ ====================

def translate(text, src_lang, tgt_lang):
    nllb_tok.src_lang = src_lang
    inputs = nllb_tok(text, return_tensors="pt")
    forced_bos_token_id = nllb_tok.convert_tokens_to_ids(tgt_lang)
    translated_tokens = nllb_mod.generate(**inputs, forced_bos_token_id=forced_bos_token_id, max_length=400)
    return nllb_tok.batch_decode(translated_tokens, skip_special_tokens=True)[0]

def transcribe(audio_data, language="ru"):
    input_features = whisper_proc(audio_data, sampling_rate=16000, return_tensors="pt").input_features
    predicted_ids = whisper_mod.generate(input_features, language=language)
    return whisper_proc.batch_decode(predicted_ids, skip_special_tokens=True)[0].strip()

def speak(text):
    subprocess.run([sys.executable, "-m", "TTS_ka", text, "--lang", "ka"])

# ==================== ИНТЕРФЕЙС ====================

st.title("🇬🇪 Грузинский Офлайн Переводчик")
st.write("Нажми кнопку и говори. Программа сама переведет и озвучит.")

r = sr.Recognizer()

col1, col2 = st.columns(2)

def process_voice(source_lang, target_lang):
    try:
        with sr.Microphone(sample_rate=16000) as source:
            st.info("Слушаю... Говорите!")
            audio = r.listen(source, phrase_time_limit=10)
            
        st.warning("Распознаю речь...")
        audio_data = np.frombuffer(audio.get_raw_data(), np.int16).astype(np.float32) / 32768.0
        text = transcribe(audio_data, language=source_lang)
        
        if text:
            st.success(f"Вы сказали: {text}")
            
            src_code = "rus_Cyrl" if source_lang == "ru" else "kat_Geor"
            tgt_code = "kat_Geor" if source_lang == "ru" else "rus_Cyrl"
            
            translated = translate(text, src_code, tgt_code)
            
            st.markdown(f'<div class="result-box">{translated}</div>', unsafe_allow_html=True)
            
            if target_lang == "ka":
                speak(translated)
        else:
            st.error("Не удалось разобрать речь.")
            
    except Exception as e:
        st.error(f"Ошибка микрофона или обработки: {e}")

with col1:
    st.markdown('<div class="ru-button">', unsafe_allow_html=True)
    if st.button("🇷🇺 Я ГОВОРЮ"):
        process_voice("ru", "ka")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="ka-button">', unsafe_allow_html=True)
    if st.button("🇬🇪 МНЕ ГОВОРЯТ"):
        process_voice("ka", "ru")
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.caption("Работает полностью без интернета на моделях Whisper и NLLB-200.")
