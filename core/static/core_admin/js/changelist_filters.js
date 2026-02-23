(function() {
    'use strict';

    function initFilterRedirect() {
        var sidebar = document.getElementById('changelist-filter');
        if (!sidebar) return;
        sidebar.addEventListener('change', function(e) {
            var select = e.target;
            if (!select || !select.classList.contains('search-filter')) return;
            var opt = select.options[select.selectedIndex];
            var name = opt && opt.getAttribute('data-name');
            var val = opt ? opt.value : '';
            if (!name && !val) {
                name = select.getAttribute('data-filter-param') || '';
            }
            var params = new URLSearchParams(window.location.search);
            if (name) {
                if (val) params.set(name, val);
                else params.delete(name);
            }
            window.location = window.location.pathname + '?' + params.toString();
        });
    }

    function initCollapsibleRangeFilter() {
        var filterSidebar = document.getElementById('changelist-filter');
        if (!filterSidebar) return;

        // Ищем блок фильтра по заголовку "Дата регистрации (диапазон)" или по классу rangefilter
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

        // Родительский блок фильтра: либо обёртка rangefilter, либо li/div родитель
        var wrapper = targetHeading.closest('li') || targetHeading.closest('.rangefilter-wrapper') || targetHeading.parentElement;
        if (!wrapper) wrapper = targetHeading.parentElement;

        var content = targetHeading.nextElementSibling;
        if (!content && wrapper) {
            content = wrapper.querySelector('.rangefilter-content, .rf-datetime, form, div');
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

    function initFilterFormPreserveParams() {
        var sidebar = document.getElementById('changelist-filter');
        if (!sidebar) return;
        var forms = sidebar.querySelectorAll('form[method="get"]');
        forms.forEach(function(form) {
            form.addEventListener('submit', function() {
                var currentParams = new URLSearchParams(window.location.search);
                var formNames = {};
                var i, el, n;
                for (i = 0; i < form.elements.length; i++) {
                    el = form.elements[i];
                    n = el.name;
                    if (n) formNames[n] = true;
                }
                currentParams.forEach(function(value, key) {
                    if (!formNames[key]) {
                        var hidden = document.createElement('input');
                        hidden.type = 'hidden';
                        hidden.name = key;
                        hidden.value = value;
                        form.appendChild(hidden);
                    }
                });
            });
        });
    }

    function init() {
        initFilterRedirect();
        initCollapsibleRangeFilter();
        initFilterFormPreserveParams();
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
