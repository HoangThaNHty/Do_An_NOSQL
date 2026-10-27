/* ============================================================
   main.js - JavaScript cho giao dien Tin Tức NoSQL
   ============================================================ */

document.addEventListener("DOMContentLoaded", function () {

    // 1. Xac nhan truoc khi xoa bài viết
    document.querySelectorAll(".js-confirm-delete").forEach(function (form) {
        form.addEventListener("submit", function (event) {
            if (!confirm("Bạn có chắc muốn xóa bài viết này?")) {
                event.preventDefault();
            }
        });
    });

    // 2. Tu dong an thong bao sau 5 giây
    document.querySelectorAll(".alert").forEach(function (box) {
        setTimeout(function () {
            var instance = bootstrap.Alert.getOrCreateInstance(box);
            instance.close();
        }, 5000);
    });

    // 3. Đã xuất bản ngay hom nay o thanh tren cung
    var todayEl = document.getElementById("today");
    if (todayEl) {
        var now = new Date();
        var days = ["Chủ nhật", "Thứ hai", "Thứ ba", "Thứ tư", "Thứ năm", "Thứ sáu", "Thứ bảy"];
        todayEl.textContent =
            days[now.getDay()] + ", ngày " + now.getDate() + "/" + (now.getMonth() + 1) + "/" + now.getFullYear();
    }

    // 4. Lam moi so lieu cache (trang quan tri cache) moi 10 giây
    var hitsEl = document.getElementById("live-hits");
    var missEl = document.getElementById("live-misses");
    if (hitsEl || missEl) {
        setInterval(function () {
            fetch("/api/cache/stats")
                .then(function (r) { return r.json(); })
                .then(function (data) {
                    if (!data.success) return;
                    if (hitsEl) hitsEl.textContent = data.data.hits;
                    if (missEl) missEl.textContent = data.data.misses;
                    var waits = document.getElementById("live-lock-waits");
                    var timeouts = document.getElementById("live-lock-timeouts");
                    if (waits) waits.textContent = data.data.lock_waits;
                    if (timeouts) timeouts.textContent = data.data.lock_timeouts;
                })
                .catch(function () { /* bo qua loi mang */ });
        }, 10000);
    }
});
