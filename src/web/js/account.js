const main = document.getElementById("account-main");

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

function formatPrice(v) {
  return new Intl.NumberFormat("vi-VN").format(v || 0);
}

function formatDateTime(v) {
  if (!v) return "—";
  const d = new Date(v);
  if (isNaN(d.getTime())) return v;
  return d.toLocaleString("vi-VN");
}

const STATUS_LABELS = {
  pending: "Chờ duyệt",
  approved: "Đã duyệt",
  confirmed: "Đã xác nhận",
  checked_in: "Đã nhận phòng",
  checked_out: "Đã trả phòng",
  completed: "Hoàn tất",
  cancelled: "Đã huỷ",
};

function renderLoginGate() {
  main.innerHTML = `
    <div class="empty-state" style="max-width:420px;margin:60px auto;">
      Bạn cần đăng nhập để xem thông tin tài khoản và lịch sử đặt phòng.<br/><br/>
      <a href="login.html?next=account.html" class="btn btn-primary" style="display:inline-block;width:auto;padding:10px 22px;text-decoration:none;">Đăng nhập</a>
    </div>`;
}

function renderShell() {
  const userId = AuthStore.getUserId();
  const role = AuthStore.getRole();
  main.innerHTML = `
    <div class="account-header">
      <div class="account-avatar">#${userId}</div>
      <div>
        <h1 class="display">Tài khoản #${userId}</h1>
        <div class="role-tag">${role === "admin" ? "Quản trị viên" : "Khách hàng"}</div>
      </div>
    </div>

    <div class="results-header">
      <h1 class="display" style="font-size:1.4rem;">Lịch sử đặt phòng</h1>
    </div>
    <div id="bookings-area">
      <div class="loading-state">Đang tải đơn đặt phòng...</div>
    </div>
  `;
}

async function loadSpaceNames(spaceIds) {
  const map = {};
  await Promise.all(
    [...new Set(spaceIds)].map(async (id) => {
      try {
        const space = await SpaceApi.getById(id);
        map[id] = space.name;
      } catch (_) {
        map[id] = `Không gian #${id}`;
      }
    })
  );
  return map;
}

async function loadBookings() {
  const area = document.getElementById("bookings-area");
  try {
    const data = await ReservationApi.list({ user_id: AuthStore.getUserId() });
    const items = data.items || data || [];
    if (!items.length) {
      area.innerHTML = `<div class="empty-state">Bạn chưa có đơn đặt phòng nào. <a href="search.html" style="color:var(--safelight);">Tìm phòng ngay</a></div>`;
      return;
    }
    const nameMap = await loadSpaceNames(items.map((r) => r.space_id));
    area.innerHTML = `
      <div class="admin-table-wrap">
        <table class="admin-table">
          <thead>
            <tr>
              <th>Mã đơn</th>
              <th>Không gian</th>
              <th>Bắt đầu</th>
              <th>Kết thúc</th>
              <th>Trạng thái</th>
              <th>Tổng tiền</th>
              <th>Hành động</th>
            </tr>
          </thead>
          <tbody>
            ${items
              .map(
                (r) => `
              <tr>
                <td>#${r.id}</td>
                <td>${escapeHtml(nameMap[r.space_id] || `Không gian #${r.space_id}`)}</td>
                <td>${formatDateTime(r.start_time)}</td>
                <td>${formatDateTime(r.end_time)}</td>
                <td><span class="badge ${r.status}">${STATUS_LABELS[r.status] || r.status}</span></td>
                <td>${formatPrice(r.total_price)}đ</td>
                <td class="actions">
                  ${
                    r.status === "pending"
                      ? `<a class="btn btn-primary btn-sm" style="text-decoration:none;" href="payment.html?id=${r.id}">Thanh toán</a>
                         <button type="button" class="btn btn-ghost btn-sm" data-cancel="${r.id}">Huỷ</button>`
                      : ""
                  }
                </td>
              </tr>`
              )
              .join("")}
          </tbody>
        </table>
      </div>
    `;

    area.querySelectorAll("[data-cancel]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        if (!confirm("Bạn chắc chắn muốn huỷ đơn này?")) return;
        btn.disabled = true;
        try {
          await ReservationApi.cancel(btn.dataset.cancel);
          loadBookings();
        } catch (err) {
          alert(`Không huỷ được: ${err.message}`);
          btn.disabled = false;
        }
      });
    });
  } catch (err) {
    area.innerHTML = `<div class="error-state">Không tải được lịch sử đặt phòng: ${escapeHtml(
      err.message
    )}</div>`;
  }
}

if (!AuthStore.isLoggedIn()) {
  renderLoginGate();
} else {
  renderShell();
  loadBookings();
}
