from django import template
from main.locales import get_text

register = template.Library()

class TranslateNode(template.Node):
    def __init__(self, key):
        self.key = key

    def render(self, context):
        lang = context.get('current_lang', 'ru')
        key = self.key.strip("'\"")
        return get_text(key, lang)

@register.tag('t')
def translate_tag(parser, token):
    try:
        parts = token.split_contents()
        key = parts[1]
    except (ValueError, IndexError):
        raise template.TemplateSyntaxError("{% t 'key' %} requires one argument")
    return TranslateNode(key)
