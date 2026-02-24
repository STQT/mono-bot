"""Шаблонные теги и фильтры для админки."""
from django import template
from django.contrib.admin.views.main import SEARCH_VAR
from urllib.parse import unquote

register = template.Library()


@register.filter
def query_param_name(query_string):
    """Из query_string вида '?param=value' возвращает имя параметра без ведущего '?'."""
    if not query_string:
        return ''
    parts = str(query_string).split('=', 1)
    name = unquote(parts[0]) if parts else ''
    return name.lstrip('?')


@register.filter
def query_param_value(query_string):
    """Из query_string вида 'param=value' возвращает значение (для value в option)."""
    if not query_string:
        return ''
    parts = str(query_string).split('=', 1)
    return unquote(parts[1]) if len(parts) > 1 else ''


@register.inclusion_tag('admin/includes/preserved_get_params.html', takes_context=True)
def preserved_get_params_hidden(context, exclude_var=None):
    """
    Контекст для вывода скрытых input'ов со всеми request.GET (кроме поиска),
    чтобы кнопка «Найти» не сбрасывала активные фильтры.
    """
    request = context.get('request')
    exclude = exclude_var or SEARCH_VAR
    params = []
    if request and request.GET:
        for key in request.GET:
            if key == exclude:
                continue
            for value in request.GET.getlist(key):
                params.append((key, value))
    return {'preserved_params': params, 'search_var': exclude}
