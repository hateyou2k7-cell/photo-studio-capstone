(function () {
  const form = document.getElementById("login-form");
  const btn = document.getElementById("login-btn");
  const msg = document.getElementById("login-msg");

  function showMsg(text, type) {
    msg.textContent = text;
    msg.className = "login-msg show " + type;
  }

  // Nếu đã đăng nhập rồi thì chuyển thẳng, khỏi bắt điền lại form.
  if (AuthStore.isLoggedIn()) {
    redirectAfterLogin();
  }

  function redirectAfterLogin() {
    const params = new URLSearchParams(window.location.search);
    const next = params.get("next");
    if (next) {
      window.location.href = next;
    } else if (AuthStore.isAdmin()) {
      window.location.href = "admin/index.html";
    } else {
      window.location.href = "search.html";
    }
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;
    if (!username || !password) return;

    btn.disabled = true;
    btn.textContent = "Đang đăng nhập...";

    try {
      const payload = await apiRequest("/auth/login", {
        method: "POST",
        body: { username, password },
      });
      const token = payload.token || (payload.data && payload.data.token);
      const userId = payload.user_id || (payload.data && payload.data.user_id);
      if (!token) throw new Error("Không nhận được token từ server.");

      AuthStore.setSession(token, userId);
      showMsg("Đăng nhập thành công, đang chuyển trang...", "ok");
      setTimeout(redirectAfterLogin, 400);
    } catch (err) {
      showMsg(err.message || "Đăng nhập thất bại.", "err");
    } finally {
      btn.disabled = false;
      btn.textContent = "Đăng nhập";
    }
  });
})();
