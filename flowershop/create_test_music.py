import wave
import struct
import math
import os

# Создаем папку если её нет
os.makedirs('static/music', exist_ok=True)

# Создаем простую мелодию
with wave.open('static/music/background.wav', 'w') as wav_file:
    wav_file.setnchannels(1)  # Моно
    wav_file.setsampwidth(2)  # 16-bit
    wav_file.setframerate(44100)  # 44.1 кГц

    # Генерируем простую мелодию
    duration = 5  # секунд
    sample_rate = 44100

    for i in range(sample_rate * duration):
        # Простая синусоида с изменением частоты
        t = i / sample_rate
        freq = 440 + 100 * math.sin(t * 2)  # Меняющаяся частота
        value = int(16384 * math.sin(2 * math.pi * freq * t))
        packed_value = struct.pack('<h', value)
        wav_file.writeframes(packed_value)

print("✅ Тестовый музыкальный файл создан: static/music/background.wav")