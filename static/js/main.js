/* ============================================================
   main.js - JavaScript cho giao dien
   ============================================================ */

document.addEventListener("DOMContentLoaded", function () {
    // 1. Xac nhan truoc khi xoa bai viet
    document.querySelectorAll(".js-confirm-delete").forEach(function (form) {
        form.addEventListener("submit", function (event) {
            if (!confirm("Ban chac chan muon xoa bai viet nay?\nCache lien quan cung se bi xoa.")) {
                event.preventDefault();
            }
        });
    });

    // 2. Tu dong an thong bao sau 5 giay
    document.querySelectorAll(".alert").forEach(function (alertBox) {
        setTimeout(function () {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(alertBox);
            bsAlert.close();
        }, 5000);
    });

    // 3. Tu lam moi so lieu cache tren trang quan tri (moi 10 giay)
    var statsBox = document.getElementById("live-cache-stats");
    if (statsBox) {
        setInterval(function () {
            fetch("/api/cache/stats")
                .then(function (r) { return r.json(); })
                .then(function (data) {
                    if (!data.success) return;
                    var el = document.getElementById("live-hits");
                    var el2 = document.getElementById("live-misses");
                    if (el) el.textContent = data.data.hits;
                    if (el2) el2.textContent = data.data.misses;
                })
                .catch(function () { /* bo qua loi mang */ });
        }, 10000);
    }
});
