/* ============================================================
   main.js - JavaScript cho giao dien Tin Tuc NoSQL
   ============================================================ */

document.addEventListener("DOMContentLoaded", function () {

    // 1. Xac nhan truoc khi xoa bai viet
    document.querySelectorAll(".js-confirm-delete").forEach(function (form) {
        form.addEventListener("submit", function (event) {
            if (!confirm("Ban chac chan muon xoa bai viet nay?")) {
                event.preventDefault();
            }
        });
    });

    // 2. Tu dong an thong bao sau 5 giay
    document.querySelectorAll(".alert").forEach(function (box) {
        setTimeout(function () {
            var instance = bootstrap.Alert.getOrCreateInstance(box);
            instance.close();
        }, 5000);
    });

    // 3. Hien thi ngay hom nay o thanh tren cung
    var todayEl = document.getElementById("today");
    if (todayEl) {
        var now = new Date();
        var days = ["Chu nhan", "Thu hai", "Thu ba", "Thu tu", "Thu nam", "Thu sau", "Chu nhat"];
        todayEl.textContent =
            days[now.getDay()] + ", ngay " + now.getDate() + "/" + (now.getMonth() + 1) + "/" + now.getFullYear();
    }

    // 4. Lam moi so lieu cache (trang quan tri cache) moi 10 giay
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
                })
                .catch(function () { /* bo qua loi mang */ });
        }, 10000);
    }
});
