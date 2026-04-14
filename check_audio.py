import sounddevice as sd
import numpy as np
import time

def test_audio():
    print("=== [ТЕСТ АУДИО-УСТРОЙСТВ] ===")
    
    # 1. Список устройств
    try:
        devices = sd.query_devices()
        print("\nДоступные устройства:")
        print(devices)
        
        default_input = sd.default.device[0]
        print(f"\n[!] Устройство ввода по умолчанию: ID {default_input}")
    except Exception as e:
        print(f"\n[ОШИБКА ИНИЦИАЛИЗАЦИИ]: {e}")
        return
    
    # 2. Попытка записи
    duration = 3  # секунды
    fs = 16000    # частота дискретизации
    
    print(f"\n[ТЕСТ ЗАПИСИ]: Сейчас начнется запись ({duration} сек).")
    print("Пожалуйста, ГОВОРИТЕ В МИКРОФОН или ПОШУМИТЕ...")
    
    try:
        time.sleep(1)
        print(">>> ЗАПИСЬ...")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        print(">>> ЗАПИСЬ ОКОНЧЕНА.")
        
        # Анализ амплитуды
        max_val = np.max(np.abs(recording))
        mean_val = np.mean(np.abs(recording))
        
        print(f"\nСтатистика сигнала:")
        print(f"- Максимальная амплитуда: {max_val:.6f}")
        print(f"- Средняя амплитуда: {mean_val:.6f}")
        
        if max_val < 0.00001:
            print("\n[РЕЗУЛЬТАТ]: АБСОЛЮТНАЯ ТИШИНА. Вероятно, аудио-карта выдает нули.")
        elif max_val < 0.0001:
            print("\n[РЕЗУЛЬТАТ]: ПОЧТИ ТИШИНА. Звук почти не поступает.")
        elif max_val < 0.01:
            print("\n[РЕЗУЛЬТАТ]: ОЧЕНЬ ТИХО. Проверьте настройки усиления.")
        else:
            print("\n[РЕЗУЛЬТАТ]: СИГНАЛ ЕСТЬ! Микрофон работает корректно.")

    except Exception as e:
        print(f"\n[ОШИБКА ПРИ ТЕСТЕ]: {e}")

if __name__ == "__main__":
    test_audio()
