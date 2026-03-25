# main/context_processors.py
from .locales import get_text


def language_processor(request):
    """Добавляет функцию перевода в шаблоны"""

    current_lang = request.session.get('language', 'ru')

    def t(key):
        return get_text(key, current_lang)

    return {
        't': t,
        'current_lang': current_lang,
        'languages': [
            {'code': 'ru', 'name': 'Русский', 'flag': '🇷🇺'},
            {'code': 'uz', 'name': 'O\'zbek', 'flag': '🇺🇿'},
            {'code': 'en', 'name': 'English', 'flag': '🇬🇧'},
        ]
    }