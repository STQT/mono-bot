"""Шаблонные теги для админки: сохранение GET-параметров в форме поиска."""
from django import template
from django.contrib.admin.views.main import SEARCH_VAR

register = template.Library()


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
                if value:
                    params.append((key, value))
    return {'preserved_params': params, 'search_var': exclude}
