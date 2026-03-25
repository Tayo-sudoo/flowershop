from twilio.rest import Client
import random
import string
from django.core.cache import cache

# Настройки Twilio (получи на twilio.com)
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = '+1234567890'


def generate_verification_code():
    """Генерирует 6-значный код"""
    return ''.join(random.choices(string.digits, k=6))


def send_verification_sms(phone_number):
    """Отправляет SMS с кодом подтверждения"""
    code = generate_verification_code()

    # Сохраняем код в кэш на 5 минут
    cache.set(f'verify_{phone_number}', code, timeout=300)

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f'Ваш код подтверждения: {code}',
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return True, code
    except Exception as e:
        print(f"Ошибка отправки SMS: {e}")
        return False, None


def verify_code(phone_number, code):
    """Проверяет код подтверждения"""
    saved_code = cache.get(f'verify_{phone_number}')
    return saved_code == code