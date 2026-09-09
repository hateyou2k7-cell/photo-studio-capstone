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

function getEquipmentId() {
  return new URLSearchParams(window.location.search).get("equipment_id");
}

function todayStr() {
  return new Date().toISOString().slice(0, 10);
}

let space = null;
let equipment = null; // for equipment-only rental
let selectedEquipment = []; // for room rental + equipment

backLink.addEventListener("click", (e) => {
  e.preventDefault();
  if (space) window.location.href = `detail.html?id=${space.id}`;
  else window.location.href = "search.html";
});

function renderLoggedOutGate() {
  return `
    <div class="summary-card" id="login-gate">
      <p style="margin:0 0 12px;color:var(--paper-dim);font-size:0.88rem;">
        Bạn cần đăng nhập để thực hiện đặt chỗ.
      </p>
      <div class="field" style="margin-bottom:12px;">
        <label>Tên đăng nhập</label>
        <input type="text" id="login-username" placeholder="username" />
      </div>
      <div class="field" style="margin-bottom:12px;">
        <label>Mật khẩu</label>
        <input type="password" id="login-password" placeholder="••••••••" />
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
    const errBox = document.getElementById("login-error");
    errBox.style.display = "none";
    if (!username || !password) {
      errBox.textContent = "Nhập đủ tên đăng nhập và mật kh���u.";
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
      AuthStore.setSession(data.token, data.user_id);
      // Re-render after login
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
  // Determine if we are renting a space or just equipment
  const hasSpace = !!space;
  content.innerHTML = `
    <div class="summary-card">
      ${hasSpace ? `
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
      ` : `
      <div class="space-row">
        <div class="space-thumb">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3">
            <rect x="3" y="7" width="18" height="12" rx="2"/>
            <circle cx="12" cy="13" r="3.4"/>
            <path d="M8 7l1.2-2h5.6L16 7"/>
          </svg>
        </div>
        <div>
          <div class="space-name">${escapeHtml(equipment ? equipment.name : "Thuê thiết bị")}</div>
          <div class="space-address">${equipment ? escapeHtml(equipment.model_name || "") : ""}</div>
        </div>
      </div>
      `}

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

      ${hasSpace ? `
      <div class="equipment-selection">
        <h3 style="margin: 16px 0 8px;">Thuê thêm thiết bị (không bắt buộc)</h3>
        <div id="equipment-list" style="display:flex;flex-wrap:wrap;gap:8px;">
          <span class="loading-state" style="font-size:0.9rem;">Đang tải...</span>
        </div>
      </div>
      ` : `
      <div style="margin: 12px 0;">
        <p><strong>Thiết bị:</strong> ${escapeHtml(equipment ? equipment.name : "")}</p>
        <p><strong>Giá:</strong> ${formatPrice(equipment ? equipment.price_per_hour : 0)}đ / giờ</p>
      </div>
      `}

      <div class="price-lines">
        ${hasSpace ? `
        <div class="price-line">
          <span>Đơn giá phòng</span>
          <span>${formatPrice(space.base_price_per_hour)}đ / giờ</span>
        </div>
        ` : `
        <div class="price-line">
          <span>Đơn giá thiết bị</span>
          <span>${formatPrice(equipment ? equipment.price_per_hour : 0)}đ / giờ</span>
        </div>
        `}
        <div class="price-line">
          <span>Thời lượng</span>
          <span id="p-duration">2 giờ</span>
        </div>
        <div class="price-line" id="equipment-total-line" style="display:none;">
          <span>Thiết bị</span>
          <span id="p-equipment-total">0đ</span>
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

  // Load equipment list if space is selected
  if (hasSpace) {
    loadEquipmentList();
  }

  function recalc() {
    const timeError = document.getElementById("time-error");
    const durationEl = document.getElementById("p-duration");
    const totalEl = document.getElementById("p-total");
    const equipmentTotalEl = document.getElementById("p-equipment-total");
    const equipmentLine = document.getElementById("equipment-total-line");

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

    let total = 0;
    if (hasSpace) {
      total += hours * space.base_price_per_hour;
    } else if (equipment) {
      total += hours * equipment.price_per_hour;
    }

    // Add equipment costs if any selected
    let equipmentCost = 0;
    if (hasSpace) {
      const checkboxes = document.querySelectorAll('.equipment-checkbox:checked');
      checkboxes.forEach(cb => {
        const price = parseFloat(cb.dataset.price);
        equipmentCost += hours * price;
      });
      if (checkboxes.length > 0) {
        equipmentLine.style.display = 'flex';
        equipmentTotalEl.textContent = `${formatPrice(equipmentCost)}đ`;
      } else {
        equipmentLine.style.display = 'none';
      }
    }

    total += equipmentCost;
    durationEl.textContent = `${hours % 1 === 0 ? hours : hours.toFixed(1)} giờ`;
    totalEl.textContent = `${formatPrice(total)}đ`;
    barTotal.textContent = `${formatPrice(total)}đ`;
    return { start, end, total, equipmentCost };
  }

  // Store recalc for checkbox change
  window._recalc = recalc;

  [dateEl, startEl, endEl].forEach((el) => el.addEventListener("input", recalc));
  recalc();

  bottomBar.style.display = "block";
}

function loadEquipmentList() {
  const container = document.getElementById("equipment-list");
  if (!container) return;
  EquipmentApi.list()
    .then(data => {
      const items = data.items || [];
      if (!items.length) {
        container.innerHTML = `<span style="color:var(--muted);">Không có thiết bị nào để thuê thêm.</span>`;
        return;
      }
      container.innerHTML = items.map(eq => `
        <label style="display:flex;align-items:center;gap:6px;background:var(--base);padding:6px 12px;border-radius:20px;border:1px solid var(--hairline);cursor:pointer;">
          <input type="checkbox" class="equipment-checkbox" data-id="${eq.id}" data-price="${eq.price_per_hour}" />
          ${escapeHtml(eq.name)} (${formatPrice(eq.price_per_hour)}đ/giờ)
        </label>
      `).join('');
      // Recalc on checkbox change
      document.querySelectorAll('.equipment-checkbox').forEach(cb => {
        cb.addEventListener('change', () => {
          if (window._recalc) window._recalc();
        });
      });
    })
    .catch(() => {
      container.innerHTML = `<span style="color:var(--muted);">Không thể tải danh sách thiết bị.</span>`;
    });
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

  // Collect equipment IDs
  let equipmentIds = [];
  if (hasSpace) {
    const checkboxes = document.querySelectorAll('.equipment-checkbox:checked');
    equipmentIds = Array.from(checkboxes).map(cb => parseInt(cb.dataset.id));
  } else if (equipment) {
    equipmentIds = [equipment.id];
  }

  // Calculate total
  let total = 0;
  if (hasSpace) {
    total += hours * space.base_price_per_hour;
    equipmentIds.forEach(id => {
      // We need to get price from checkbox dataset or from equipment list
      const cb = document.querySelector(`.equipment-checkbox[data-id="${id}"]`);
      if (cb) total += hours * parseFloat(cb.dataset.price);
    });
  } else if (equipment) {
    total += hours * equipment.price_per_hour;
  }

  confirmBtn.disabled = true;
  confirmBtn.textContent = "Đang xử lý...";
  try {
    const payload = {
      userId: AuthStore.getUserId(),
      providerId: hasSpace ? space.provider_id : (equipment ? equipment.provider_id : 1), // fallback
      startTime: start.toISOString(),
      endTime: end.toISOString(),
      totalPrice: Math.round(total),
      notes: notesEl.value.trim() || undefined,
      equipment_ids: equipmentIds,
    };
    if (hasSpace) payload.spaceId = space.id;
    // else no spaceId

    const reservation = await ReservationApi.create(payload);
    const name = hasSpace ? space.name : (equipment ? equipment.name : "Thiết bị");
    window.location.href = `payment.html?reservation_id=${reservation.id}&amount=${Math.round(
      total
    )}&space_name=${encodeURIComponent(name)}`;
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
  const spaceId = getSpaceId();
  const equipmentId = getEquipmentId();

  if (spaceId) {
    // Room rental (with optional equipment)
    try {
      space = await SpaceApi.getById(spaceId);
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
  } else if (equipmentId) {
    // Equipment-only rental
    try {
      const data = await EquipmentApi.list();
      const items = data.items || [];
      const eq = items.find(e => e.id === parseInt(equipmentId));
      if (!eq) {
        content.innerHTML = `<div class="error-state">Không tìm thấy thiết bị.</div>`;
        return;
      }
      equipment = eq;
      render();
    } catch (err) {
      content.innerHTML = `<div class="error-state">Không tải được thông tin thiết bị: ${escapeHtml(
        err.message
      )}</div>`;
    }
  } else {
    content.innerHTML = `<div class="error-state">Thiếu thông tin đặt chỗ. Quay lại trang tìm kiếm để chọn phòng hoặc thiết bị.</div>`;
  }
}

init();
