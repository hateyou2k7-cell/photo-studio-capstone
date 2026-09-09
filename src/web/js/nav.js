// ============================================================
// nav.js — dùng chung cho mọi trang phía khách hàng.
// Yêu cầu: đã load js/api.js trước; thẻ <body data-nav="..."> để
// đánh dấu mục đang active; có <span id="nav-auth"></span> trong nav.
// ============================================================
(function () {
  function renderAuthSlot() {
    const slot = document.getElementById("nav-auth");
    if (!slot) return;

    if (AuthStore.isLoggedIn()) {
      const adminLink = AuthStore.isAdmin()
        ? '<a href="admin/index.html">Quản trị</a><span class="nav-sep">·</span>'
        : "";
      slot.innerHTML =
        adminLink +
        `<a href="account.html">Tài khoản #${AuthStore.getUserId()}</a>` +
        '<span class="nav-sep">·</span><a href="#" id="nav-logout">Đăng xuất</a>';
      const logoutLink = document.getElementById("nav-logout");
      logoutLink.addEventListener("click", (e) => {
        e.preventDefault();
        AuthStore.logout();
        window.location.href = "index.html";
      });
    } else {
      slot.innerHTML = '<a href="login.html">Đăng nhập</a>';
    }
  }

  function markActive() {
    const current = document.body.dataset.nav;
    if (!current) return;
    document.querySelectorAll("nav a[data-nav]").forEach((a) => {
      if (a.dataset.nav === current) a.classList.add("active");
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    renderAuthSlot();
    markActive();
  });
})();
