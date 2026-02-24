(function() {
    'use strict';

    // -------------------------------------------------------
    // Авто-сабмит select-фильтров при изменении.
    // Jazzmin даёт: data-name=param_name, value=param_value
    // -------------------------------------------------------
    function initFilterRedirect() {
        var sidebar = document.getElementById('changelist-filter');
        if (!sidebar) return;
        sidebar.addEventListener('change', function(e) {
            var select = e.target;
            if (!select || !select.classList.contains('search-filter')) return;
            var opt = select.options[select.selectedIndex];

            // Jazzmin: data-name = точное имя параметра, value = значение
            var name = opt && opt.getAttribute('data-name');
            var val  = opt ? opt.value : '';

            // «Все» — пустой data-name, берём data-filter-param с select'а
            if (!name) {
                name = select.getAttribute('data-filter-param') || '';
            }

            var params = new URLSearchParams(window.location.search);
            if (name) {
                if (val) {
                    params.set(name, val);
                } else {
                    params.delete(name);
                }
            }
            window.location = window.location.pathname + '?' + params.toString();
        });
    }

    // -------------------------------------------------------
    // Кнопка «Найти» — собирает ВСЕ фильтры:
    //  • select-фильтры (через data-filter-param / data-name)
    //  • rangefilter date/time инпуты (через name-атрибут)
    // -------------------------------------------------------
    window.applyAllFilters = function() {
        var sidebar = document.getElementById('changelist-filter');
        if (!sidebar) {
            window.location.reload();
            return;
        }

        // Сохраняем строку поиска
        var currentParams = new URLSearchParams(window.location.search);
        var params = new URLSearchParams();
        var q = currentParams.get('q');
        if (q) params.set('q', q);

        // 1. Собираем значения select-фильтров
        var selects = sidebar.querySelectorAll('select.search-filter');
        selects.forEach(function(select) {
            var opt = select.options[select.selectedIndex];
            var name = opt && opt.getAttribute('data-name');
            var val  = opt ? opt.value : '';
            if (!name) {
                name = select.getAttribute('data-filter-param') || '';
            }
            if (name && val) {
                params.set(name, val);
            }
        });

        // 2. Собираем rangefilter date/time инпуты
        var dateInputs = sidebar.querySelectorAll('.admindatefilter input[name]');
        dateInputs.forEach(function(input) {
            if (input.value) {
                params.set(input.name, input.value);
            }
        });

        window.location = window.location.pathname + '?' + params.toString();
    };

    // -------------------------------------------------------
    // Collapse/expand для rangefilter (по заголовку h3)
    // -------------------------------------------------------
    function initCollapsibleRangeFilter() {
        var filterSidebar = document.getElementById('changelist-filter');
        if (!filterSidebar) return;

        var headings = filterSidebar.querySelectorAll('h3, h2, .rangefilter-title, [class*="rangefilter"]');
        var targetHeading = null;
        for (var i = 0; i < headings.length; i++) {
            var text = (headings[i].textContent || '').trim();
            if (text.indexOf('Дата регистрации') !== -1 || text.indexOf('диапазон') !== -1) {
                targetHeading = headings[i];
                break;
            }
        }

        if (!targetHeading) return;

        var wrapper = targetHeading.closest('li') || targetHeading.closest('.rangefilter-wrapper') || targetHeading.parentElement;
        if (!wrapper) wrapper = targetHeading.parentElement;

        var content = targetHeading.nextElementSibling;
        if (!content && wrapper) {
            content = wrapper.querySelector('.rangefilter-content, .rf-datetime, .admindatefilter, div');
        }
        if (!content) return;

        wrapper.classList.add('rangefilter-wrapper', 'rangefilter-collapsed');
        if (content && !content.classList.contains('rangefilter-content')) {
            content.classList.add('rangefilter-content');
        }

        var toggle = targetHeading;
        if (!toggle.classList.contains('rangefilter-toggle')) {
            toggle.classList.add('rangefilter-toggle');
        }

        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            wrapper.classList.toggle('rangefilter-collapsed');
        });
    }

    function init() {
        initFilterRedirect();
        initCollapsibleRangeFilter();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
