document.querySelectorAll('[data-save-article]').forEach(button => {
    button.addEventListener('click', async () => {
        const saved = button.dataset.saved === 'true';
        const message = button.parentElement.querySelector('[data-save-message]');
        button.disabled = true;
        try {
            const response = await fetch(`/api/saved/${encodeURIComponent(button.dataset.saveArticle)}`, {
                method: saved ? 'DELETE' : 'PUT', headers: {'Accept': 'application/json'}
            });
            if (response.status === 401) {
                window.location.assign('/login?next=' + encodeURIComponent(window.location.pathname));
                return;
            }
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Chưa thể cập nhật bài đã lưu.');
            button.dataset.saved = String(data.saved);
            button.setAttribute('aria-pressed', String(data.saved));
            button.textContent = data.saved ? 'Đã lưu · Bỏ lưu' : 'Lưu để đọc sau';
            if (message) message.textContent = data.saved ? 'Đã thêm vào Bài đã lưu.' : 'Đã bỏ lưu bài viết.';
            if (button.closest('[data-saved-card]')) window.location.reload();
        } catch (error) {
            if (message) message.textContent = error.message;
        } finally {
            button.disabled = false;
        }
    });
});
