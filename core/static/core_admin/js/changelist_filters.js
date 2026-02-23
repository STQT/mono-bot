(function() {
    'use strict';
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

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCollapsibleRangeFilter);
    } else {
        initCollapsibleRangeFilter();
    }
})();
