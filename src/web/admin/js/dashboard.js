const STATUS_LABELS = {
  pending: "Chờ duyệt",
  approved: "Đã duyệt",
  confirmed: "Đã xác nhận",
  checked_in: "Đang sử dụng",
  checked_out: "Đã trả phòng",
  completed: "Hoàn tất",
  cancelled: "Đã huỷ",
};

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

function formatPrice(v) {
  return new Intl.NumberFormat("vi-VN").format(Math.round(v || 0));
}

function formatDateTime(v) {
  if (!v) return "—";
  const d = new Date(v);
  if (isNaN(d)) return String(v);
  return d.toLocaleString("vi-VN", { dateStyle: "short", timeStyle: "short" });
}

function setStat(index, value) {
  const cards = document.querySelectorAll("#stat-row .stat-card .num");
  if (cards[index]) cards[index].textContent = value;
}

async function loadStats() {
  SpaceApi.list()
    .then((d) => setStat(0, d.total ?? (d.items || []).length))
    .catch(() => setStat(0, "—"));
  EquipmentApi.list()
    .then((d) => setStat(1, d.total ?? (d.items || []).length))
    .catch(() => setStat(1, "—"));
  ReservationApi.list()
    .then((d) => setStat(2, d.total ?? (d.items || []).length))
    .catch(() => setStat(2, "—"));
  CourseApi.list()
    .then((d) => setStat(3, (Array.isArray(d) ? d : d.items || []).length))
    .catch(() => setStat(3, "—"));
  BillingApi.listInvoices()
    .then((d) => setStat(4, d.total ?? (d.items || []).length))
    .catch(() => setStat(4, "—"));
}

async function loadRecent() {
  const tbody = document.querySelector("#recent-table tbody");
  try {
    const data = await ReservationApi.list();
    const items = (data.items || []).slice().sort((a, b) => b.id - a.id).slice(0, 8);
    if (!items.length) {
      tbody.innerHTML = `<tr><td colspan="6">Chưa có đơn đặt phòng nào.</td></tr>`;
      return;
    }
    const spaceIds = [...new Set(items.filter((r) => r.space_id).map((r) => r.space_id))];
    const spaceMap = {};
    await Promise.all(
      spaceIds.map((id) => SpaceApi.getById(id).then((s) => (spaceMap[id] = s.name)).catch(() => {}))
    );
    tbody.innerHTML = items
      .map(
        (r) => `
      <tr>
        <td>#${r.id}</td>
        <td>User #${r.user_id}</td>
        <td>${escapeHtml(spaceMap[r.space_id] || `#${r.space_id ?? "—"}`)}</td>
        <td>${formatDateTime(r.start_time)}</td>
        <td><span class="badge ${r.status}">${STATUS_LABELS[r.status] || r.status}</span></td>
        <td>${formatPrice(r.total_price)}đ</td>
      </tr>`
      )
      .join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6">Không tải được dữ liệu: ${escapeHtml(err.message)}</td></tr>`;
  }
}

if (requireAdmin()) {
  initAdminNav("dashboard");
  loadStats();
  loadRecent();
}
