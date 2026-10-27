/* Gợi ý tìm kiếm dùng chung; hỗ trợ bàn phím, hủy request cũ và nội dung an toàn. */
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-live-search]').forEach(function (input, index) {
        const host = input.parentElement;
        const form = input.closest('form');
        const panel = document.createElement('div');
        panel.className = 'search-suggestions';
        panel.hidden = true;
        const status = document.createElement('div');
        status.className = 'search-suggestion-status';
        status.setAttribute('role', 'status');
        const list = document.createElement('div');
        list.id = 'search-options-' + index;
        list.setAttribute('role', 'listbox');
        list.setAttribute('aria-label', 'Bài viết gợi ý');
        panel.append(status, list);
        host.appendChild(panel);
        input.setAttribute('role', 'combobox');
        input.setAttribute('aria-autocomplete', 'list');
        input.setAttribute('aria-controls', list.id);
        input.setAttribute('aria-expanded', 'false');
        input.setAttribute('autocomplete', 'off');
        input.setAttribute('maxlength', '120');
        if (!input.hasAttribute('aria-label')) input.setAttribute('aria-label', 'Tìm kiếm bài viết');
        let timer, controller, sequence = 0, active = -1, options = [];

        function hide() {
            clearTimeout(timer);
            sequence += 1;
            if (controller) controller.abort();
            panel.hidden = true;
            input.setAttribute('aria-expanded', 'false');
            input.removeAttribute('aria-activedescendant');
            active = -1;
        }
        function show(message) {
            panel.hidden = false;
            status.textContent = message;
            input.setAttribute('aria-expanded', 'true');
        }
        function setActive(value) {
            active = value;
            options.forEach(function (option, i) {
                option.setAttribute('aria-selected', String(i === active));
            });
            if (options[active]) {
                input.setAttribute('aria-activedescendant', options[active].id);
                options[active].scrollIntoView({block: 'nearest'});
            }
        }
        function render(data, query) {
            list.replaceChildren();
            options = [];
            active = -1;
            input.removeAttribute('aria-activedescendant');
            show(data.items.length ? 'Bài viết phù hợp' : 'Không có bài phù hợp. Hãy thử từ khóa khác.');
            data.items.forEach(function (article, i) {
                const link = document.createElement('a');
                link.className = 'search-suggestion-item';
                link.id = list.id + '-' + i;
                link.href = '/articles/' + encodeURIComponent(article._id);
                link.setAttribute('role', 'option');
                link.setAttribute('aria-selected', 'false');
                const image = document.createElement('img');
                image.src = article.image;
                image.alt = '';
                const body = document.createElement('span');
                const category = document.createElement('small');
                category.textContent = article.category;
                const title = document.createElement('strong');
                title.textContent = article.title;
                body.append(category, title);
                link.append(image, body);
                list.appendChild(link);
                options.push(link);
            });
            if (data.total) {
                const all = document.createElement('a');
                const params = new URLSearchParams({q: query, sort: 'relevance'});
                const category = form.querySelector('[name="category"]');
                if (category) params.set('category', category.value);
                all.className = 'search-suggestion-all';
                all.textContent = 'Xem tất cả ' + data.total + ' kết quả';
                all.href = '/articles?' + params.toString();
                list.appendChild(all);
            }
        }
        input.addEventListener('input', function () {
            hide();
            list.replaceChildren();
            options = [];
            const query = input.value.trim();
            if (query.length < 2) return;
            const ticket = sequence;
            timer = setTimeout(async function () {
                controller = new AbortController();
                show('Đang tìm bài viết…');
                const params = new URLSearchParams({q: query});
                const category = form.querySelector('[name="category"]');
                if (category) params.set('category', category.value);
                try {
                    const response = await fetch('/api/articles/suggestions?' + params.toString(), {signal: controller.signal});
                    if (!response.ok) throw new Error('suggestions');
                    const result = await response.json();
                    if (ticket !== sequence || input.value.trim() !== query) return;
                    render(result.data, query);
                } catch (error) {
                    if (error.name !== 'AbortError' && ticket === sequence) {
                        show('Chưa tải được gợi ý. Nhấn Enter để tìm kiếm.');
                    }
                }
            }, 220);
        });
        input.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') { hide(); return; }
            if (panel.hidden || !options.length) return;
            if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
                event.preventDefault();
                const next = active < 0 ? (event.key === 'ArrowDown' ? 0 : options.length - 1)
                    : (active + (event.key === 'ArrowDown' ? 1 : -1) + options.length) % options.length;
                setActive(next);
            } else if (event.key === 'Enter' && options[active]) {
                event.preventDefault();
                options[active].click();
            }
        });
        form.addEventListener('submit', hide);
        const category = form.querySelector('[name="category"]');
        if (category) category.addEventListener('change', hide);
        document.addEventListener('pointerdown', function (event) {
            if (!host.contains(event.target)) hide();
        });
        host.addEventListener('focusout', function () {
            setTimeout(function () { if (!host.contains(document.activeElement)) hide(); }, 0);
        });
    });
});
