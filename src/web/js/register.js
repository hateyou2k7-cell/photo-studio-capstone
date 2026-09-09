(function () {
  const form = document.getElementById("register-form");
  const btn = document.getElementById("register-btn");
  const msg = document.getElementById("register-msg");

  function showMsg(text, type) {
    msg.textContent = text;
    msg.className = "login-msg show " + type;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const passwordconfirm = document.getElementById("passwordconfirm").value;
    const role = document.getElementById("role").value;

    if (password !== passwordconfirm) {
      showMsg("Mật khẩu xác nhận không khớp.", "err");
      return;
    }

    btn.disabled = true;
    btn.textContent = "Đang đăng ký...";

    try {
      await AuthApi.register({ username, email, password, passwordconfirm, role });
      showMsg("Đăng ký thành công! Đang chuyển sang trang đăng nhập...", "ok");
      setTimeout(() => {
        window.location.href = `login.html?next=${encodeURIComponent("index.html")}`;
      }, 900);
    } catch (err) {
      showMsg(err.message || "Đăng ký thất bại.", "err");
    } finally {
      btn.disabled = false;
      btn.textContent = "Đăng ký";
    }
  });
})();
