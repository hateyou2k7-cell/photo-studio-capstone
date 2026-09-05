const content = document.getElementById("payment-content");
const bottomBar = document.getElementById("bottom-bar");
const barTotal = document.getElementById("bar-total");
const payBtn = document.getElementById("pay-btn");
const stepIndicator = document.getElementById("step-indicator");

function formatPrice(v) {
  return new Intl.NumberFormat("vi-VN").format(Math.round(v));
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

function params() {
  const p = new URLSearchParams(window.location.search);
  return {
    reservationId: p.get("reservation_id"),
    amount: Number(p.get("amount") || 0),
    spaceName: p.get("space_name") || "",
  };
}

const METHODS = [
  { id: "vnpay", name: "VNPay", sub: "Thẻ ATM / Internet Banking", icon: "VN" },
  { id: "momo", name: "MoMo", sub: "Ví điện tử MoMo", icon: "M" },
  { id: "cash", name: "Tiền mặt", sub: "Thanh toán trực tiếp tại phòng", icon: "₫" },
];

let selectedMethod = "vnpay";

function renderMethodStep({ reservationId, amount, spaceName }) {
  content.innerHTML = `
    <div class="summary-card" style="margin-bottom:22px;">
      <div class="price-line"><span>Phòng</span><span>${escapeHtml(spaceName || "—")}</span></div>
      <div class="price-line"><span>Mã đơn</span><span>#${escapeHtml(reservationId)}</span></div>
      <div class="price-line total"><span>Tổng thanh toán</span><span class="amount">${formatPrice(
        amount
      )}đ</span></div>
    </div>

    <h2 class="section-title">Chọn phương thức thanh toán</h2>
    <div class="method-list" id="method-list">
      ${METHODS.map(
        (m) => `
        <label class="method-card ${m.id === selectedMethod ? "selected" : ""}" data-method="${m.id}">
          <input type="radio" name="method" value="${m.id}" ${m.id === selectedMethod ? "checked" : ""} />
          <div class="method-icon">${m.icon}</div>
          <div>
            <div class="method-name">${m.name}</div>
            <div class="method-sub">${m.sub}</div>
          </div>
        </label>`
      ).join("")}
    </div>
    <div class="inline-error" id="pay-error" style="display:none;"></div>
  `;

  document.querySelectorAll(".method-card").forEach((card) => {
    card.addEventListener("click", () => {
      selectedMethod = card.dataset.method;
      document.querySelectorAll(".method-card").forEach((c) => c.classList.remove("selected"));
      card.classList.add("selected");
      card.querySelector("input").checked = true;
    });
  });

  barTotal.textContent = `${formatPrice(amount)}đ`;
  bottomBar.style.display = "block";
  payBtn.textContent = "Thanh toán";
  payBtn.disabled = false;
}

function renderSuccess({ reservationId, amount, spaceName }) {
  stepIndicator.querySelectorAll(".step").forEach((s) => s.classList.add("done"));
  content.innerHTML = `
    <div class="success-view">
      <div class="check-circle">
        <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
      </div>
      <h2 class="display">Đặt phòng thành công</h2>
      <p>${escapeHtml(spaceName || "Phòng")} đã được giữ chỗ cho bạn. Chủ phòng sẽ liên hệ xác nhận sớm.</p>
      <div class="booking-code">Mã đơn #${escapeHtml(reservationId)}</div>
      <br/>
      <a href="search.html" class="btn btn-primary" style="display:inline-block;text-decoration:none;padding:12px 26px;">
        Về trang tìm phòng
      </a>
    </div>
  `;
  bottomBar.style.display = "none";
}

async function handlePay() {
  const { reservationId, amount, spaceName } = params();
  const errBox = document.getElementById("pay-error");
  errBox.style.display = "none";

  if (!AuthStore.isLoggedIn()) {
    errBox.textContent = "Phiên đăng nhập đã hết hạn, quay lại bước xác nhận để đăng nhập lại.";
    errBox.style.display = "block";
    return;
  }

  payBtn.disabled = true;
  payBtn.textContent = "Đang xử lý...";
  try {
    const payment = await ReservationApi.createPayment(reservationId, {
      userId: AuthStore.getUserId(),
      amount,
      method: selectedMethod,
    });
    // Demo: xác nhận thanh toán ngay (thực tế bước này do cổng VNPay/MoMo callback về)
    await ReservationApi.confirmPayment(reservationId);
    renderSuccess({ reservationId, amount, spaceName });
  } catch (err) {
    errBox.textContent = `Thanh toán thất bại: ${err.message}`;
    errBox.style.display = "block";
    payBtn.disabled = false;
    payBtn.textContent = "Thanh toán";
  }
}

function init() {
  const p = params();
  if (!p.reservationId) {
    content.innerHTML = `<div class="error-state">Thiếu thông tin đơn đặt phòng. Quay lại bước xác nhận.</div>`;
    return;
  }
  renderMethodStep(p);
  payBtn.addEventListener("click", handlePay);
}

init();
