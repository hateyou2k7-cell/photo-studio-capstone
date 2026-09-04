const content = document.getElementById("confirm-content");
const bottomBar = document.getElementById("bottom-bar");
const barTotal = document.getElementById("bar-total");
const confirmBtn = document.getElementById("confirm-btn");
const backLink = document.getElementById("back-link");

const TYPE_LABELS = { darkroom: "Phòng tối", studio: "Studio" };

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

function formatPrice(v) {
  return new Intl.NumberFormat("vi-VN").format(Math.max(0, Math.round(v)));
}

function getSpaceId() {
  return new URLSearchParams(window.location.search).get("space_id");
}

function todayStr() {
  return new Date().toISOString().slice(0, 10);
}

let space = null;

backLink.addEventListener("click", (e) => {
  e.preventDefault();
  if (space) window.location.href = `detail.html?id=${space.id}`;
  else window.location.href = "search.html";
});

function renderLoggedOutGate() {
  return `
    <div class="summary-card" id="login-gate">
      <p style="margin:0 0 12px;color:var(--paper-dim);font-size:0.88rem;">
        Bạn cần đăng nhập để đặt phòng này.
      </p>
      <div class="field" style="margin-bottom:12px;">
        <label>Tên đăng nhập</label>
        <input type="text" id="login-username" placeholder="username" />
      </div>
      <div class="field" style="margin-bottom:12px;">
        <label>Mật khẩu</label>
        <input type="password" id="login-password" placeholder="••••••••" />
      </div>
      <div class="field" style="margin-bottom:14px;">
        <label>Mã khách hàng (user id)</label>
        <input type="number" id="login-user-id" placeholder="vd: 2" />
      </div>
      <button type="button" class="btn btn-primary" id="login-submit">Đăng nhập &amp; tiếp tục</button>
      <div class="inline-error" id="login-error" style="display:none;"></div>
    </div>`;
}

function bindLoginGate() {
  const btn = document.getElementById("login-submit");
  if (!btn) return;
  btn.addEventListener("click", async () => {
    const username = document.getElementById("login-username").value.trim();
    const password = document.getElementById("login-password").value;
    const userId = Number(document.getElementById("login-user-id").value);
    const errBox = document.getElementById("login-error");
    errBox.style.display = "none";
    if (!username || !password || !userId) {
      errBox.textContent = "Nhập đủ tên đăng nhập, mật khẩu và mã khách hàng.";
      errBox.style.display = "block";
      return;
    }
    btn.disabled = true;
    btn.textContent = "Đang đăng nhập...";
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Đăng nhập thất bại");
      AuthStore.setSession(data.token, userId);
      render();
    } catch (err) {
      errBox.textContent = err.message;
      errBox.style.display = "block";
    } finally {
      btn.disabled = false;
      btn.textContent = "Đăng nhập & tiếp tục";
    }
  });
}

function render() {
  const loggedIn = AuthStore.isLoggedIn();
  content.innerHTML = `
    <div class="summary-card">
      <div class="space-row">
        <div class="space-thumb">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3">
            <path d="M4 8l2-2.5h3L11 8h6a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2z"/>
            <circle cx="13" cy="13" r="3.4"/>
          </svg>
        </div>
        <div>
          <div class="space-name">${escapeHtml(space.name)}</div>
          <div class="space-address">${escapeHtml(space.address || "Chưa cập nhật địa chỉ")} · ${
    TYPE_LABELS[space.type] || space.type
  }</div>
        </div>
      </div>

      <div class="field-row">
        <div class="field" style="grid-column: 1 / -1;">
          <label>Ngày sử dụng</label>
          <input type="date" id="f-date" min="${todayStr()}" value="${todayStr()}" />
        </div>
      </div>
      <div class="field-row">
        <div class="field">
          <label>Giờ bắt đầu</label>
          <input type="time" id="f-start" value="09:00" />
        </div>
        <div class="field">
          <label>Giờ kết thúc</label>
          <input type="time" id="f-end" value="11:00" />
        </div>
      </div>

      <div class="price-lines">
        <div class="price-line">
          <span>Đơn giá</span>
          <span>${formatPrice(space.base_price_per_hour)}đ / giờ</span>
        </div>
        <div class="price-line">
          <span>Thời lượng</span>
          <span id="p-duration">2 giờ</span>
        </div>
        <div class="price-line total">
          <span>Tổng cộng</span>
          <span class="amount" id="p-total">0đ</span>
        </div>
      </div>
      <div class="inline-error" id="time-error" style="display:none;"></div>
    </div>

    <h2 class="section-title">Ghi chú cho chủ phòng (không bắt buộc)</h2>
    <div class="note-box">
      <textarea id="f-notes" placeholder="Ví dụ: cần thêm đèn nền, mang theo máy quét film..."></textarea>
    </div>

    ${!loggedIn ? renderLoggedOutGate() : ""}
    <div class="inline-error" id="submit-error" style="display:none;"></div>
  `;

  bindLoginGate();

  const dateEl = document.getElementById("f-date");
  const startEl = document.getElementById("f-start");
  const endEl = document.getElementById("f-end");

  function recalc() {
    const timeError = document.getElementById("time-error");
    const durationEl = document.getElementById("p-duration");
    const totalEl = document.getElementById("p-total");

    const start = new Date(`${dateEl.value}T${startEl.value}`);
    const end = new Date(`${dateEl.value}T${endEl.value}`);
    const hours = (end - start) / 3600000;

    if (!dateEl.value || !startEl.value || !endEl.value || hours <= 0) {
      timeError.textContent = "Giờ kết thúc phải sau giờ bắt đầu.";
      timeError.style.display = "block";
      confirmBtn.disabled = true;
      barTotal.textContent = "—";
      return null;
    }
    timeError.style.display = "none";
    confirmBtn.disabled = false;

    const total = hours * space.base_price_per_hour;
    durationEl.textContent = `${hours % 1 === 0 ? hours : hours.toFixed(1)} giờ`;
    totalEl.textContent = `${formatPrice(total)}đ`;
    barTotal.textContent = `${formatPrice(total)}đ`;
    return { start, end, total };
  }

  [dateEl, startEl, endEl].forEach((el) => el.addEventListener("input", recalc));
  recalc();

  bottomBar.style.display = "block";
}

confirmBtn.addEventListener("click", async () => {
  const dateEl = document.getElementById("f-date");
  const startEl = document.getElementById("f-start");
  const endEl = document.getElementById("f-end");
  const notesEl = document.getElementById("f-notes");
  const submitError = document.getElementById("submit-error");
  submitError.style.display = "none";

  if (!AuthStore.isLoggedIn()) {
    document.getElementById("login-gate")?.scrollIntoView({ behavior: "smooth" });
    return;
  }

  const start = new Date(`${dateEl.value}T${startEl.value}`);
  const end = new Date(`${dateEl.value}T${endEl.value}`);
  const hours = (end - start) / 3600000;
  if (hours <= 0) return;
  const total = hours * space.base_price_per_hour;

  confirmBtn.disabled = true;
  confirmBtn.textContent = "Đang xử lý...";
  try {
    const reservation = await ReservationApi.create({
      userId: AuthStore.getUserId(),
      providerId: space.provider_id,
      spaceId: space.id,
      startTime: start.toISOString(),
      endTime: end.toISOString(),
      totalPrice: Math.round(total),
      notes: notesEl.value.trim() || undefined,
    });
    window.location.href = `payment.html?reservation_id=${reservation.id}&amount=${Math.round(
      total
    )}&space_name=${encodeURIComponent(space.name)}`;
  } catch (err) {
    submitError.textContent =
      err.status === 400
        ? `Không đặt được: ${err.message}`
        : `Có lỗi xảy ra: ${err.message}`;
    submitError.style.display = "block";
    confirmBtn.disabled = false;
    confirmBtn.textContent = "Xác nhận đặt phòng";
  }
});

async function init() {
  const id = getSpaceId();
  if (!id) {
    content.innerHTML = `<div class="error-state">Thiếu thông tin phòng. Quay lại trang tìm kiếm để chọn phòng.</div>`;
    return;
  }
  try {
    space = await SpaceApi.getById(id);
    if (!space.status) {
      content.innerHTML = `<div class="error-state">Phòng này hiện đang tạm ngừng nhận đặt lịch.</div>`;
      return;
    }
    render();
  } catch (err) {
    content.innerHTML = `<div class="error-state">Không tải được thông tin phòng: ${escapeHtml(
      err.message
    )}</div>`;
  }
}

init();
