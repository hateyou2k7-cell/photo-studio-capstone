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

const tbody = document.getElementById("table-body");
const countEl = document.getElementById("results-count");
const statusFilter = document.getElementById("f-status");

function actionsFor(res) {
  const acts = [];
  if (res.status === "pending") {
    acts.push(`<button class="btn btn-ghost btn-sm act-btn" data-action="approve" data-id="${res.id}">Duyệt</button>`);
  }
  if (res.status === "approved") {
    acts.push(`<button class="btn btn-ghost btn-sm act-btn" data-action="confirm" data-id="${res.id}">Xác nhận</button>`);
  }
  if (res.status === "confirmed") {
    acts.push(`<button class="btn btn-ghost btn-sm act-btn" data-action="checkIn" data-id="${res.id}">Check-in</button>`);
  }
  if (res.status === "checked_in") {
    acts.push(`<button class="btn btn-ghost btn-sm act-btn" data-action="checkOut" data-id="${res.id}">Check-out</button>`);
  }
  if (["pending", "approved", "confirmed"].includes(res.status)) {
    acts.push(`<button class="btn btn-ghost btn-sm act-btn" data-action="cancel" data-id="${res.id}">Huỷ</button>`);
  }
  return acts.join("");
}

async function load() {
  tbody.innerHTML = `<tr><td colspan="8">Đang tải...</td></tr>`;
  try {
    const filters = {};
    if (statusFilter.value) filters.status = statusFilter.value;
    const data = await ReservationApi.list(filters);
    const items = (data.items || []).slice().sort((a, b) => b.id - a.id);
    countEl.textContent = `${data.total ?? items.length} đơn`;
    if (!items.length) {
      tbody.innerHTML = `<tr><td colspan="8">Không có đơn nào.</td></tr>`;
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
        <td>${formatDateTime(r.end_time)}</td>
        <td>${formatPrice(r.total_price)}đ</td>
        <td><span class="badge ${r.status}">${STATUS_LABELS[r.status] || r.status}</span></td>
        <td class="actions">${actionsFor(r) || "—"}</td>
      </tr>`
      )
      .join("");

    document.querySelectorAll(".act-btn").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const { action, id } = btn.dataset;
        if (action === "cancel" && !confirm("Huỷ đơn này?")) return;
        btn.disabled = true;
        try {
          await ReservationApi[action](id);
          load();
        } catch (err) {
          alert(`Thao tác thất bại: ${err.message}`);
          btn.disabled = false;
        }
      });
    });
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="8">Không tải được dữ liệu: ${escapeHtml(err.message)}</td></tr>`;
  }
}

statusFilter.addEventListener("change", load);

if (requireAdmin()) {
  initAdminNav("reservations");
  load();
}
