"""
Кастомные template tags для мультиязычности Web App.
Использует translations.py вместо стандартных .po файлов Django.
"""
from django import template
from django.conf import settings
from bot.translations import TRANSLATIONS

register = template.Library()


@register.simple_tag(takes_context=True)
def trans(context, key, **kwargs):
    """
    Кастомный тег {% trans %} для использования переводов из translations.py.
    
    Использование:
        {% load webapp_i18n %}
        {% trans "WEBAPP_YOUR_POINTS" %}
        {% trans "WEBAPP_POINTS" points=100 %}
    """
    # Получаем язык из контекста (передается из webapp_view)
    language = context.get('user_language', 'uz_latin')
    
    # Если язык не установлен, используем по умолчанию
    if not language or language not in TRANSLATIONS:
        language = 'uz_latin'
    
    # Получаем переводы для текущего языка
    translations = TRANSLATIONS.get(language, TRANSLATIONS.get('uz_latin', {}))
    
    # Получаем текст
    text = translations.get(key, key)
    
    # Форматируем с параметрами, если они есть
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text
    
    return text


@register.simple_tag(takes_context=True)
def blocktrans(context, key, **kwargs):
    """
    Аналог {% blocktrans %} для использования переводов из translations.py.
    
    Использование:
        {% load webapp_i18n %}
        {% blocktrans "WEBAPP_POINTS" points=100 %}Ваши баллы: {{ points }}{% endblocktrans %}
    """
    return trans(context, key, **kwargs)

