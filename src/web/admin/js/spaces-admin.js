const TYPE_LABELS = { darkroom: "Phòng tối", studio: "Studio" };

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}
function formatPrice(v) {
  return new Intl.NumberFormat("vi-VN").format(Math.round(v || 0));
}

const tbody = document.getElementById("table-body");
const countEl = document.getElementById("results-count");
const modal = document.getElementById("form-modal");
const form = document.getElementById("space-form");
const formError = document.getElementById("form-error");

async function openForm(space) {
  formError.style.display = "none";
  document.getElementById("form-title").textContent = space ? `Sửa: ${space.name}` : "Thêm không gian";
  document.getElementById("f-id").value = space ? space.id : "";
  document.getElementById("f-name").value = space ? space.name : "";
  document.getElementById("f-type").value = space ? space.type : "darkroom";
  document.getElementById("f-address").value = space ? space.address || "" : "";
  document.getElementById("f-description").value = space ? space.description || "" : "";
  document.getElementById("f-capacity").value = space ? space.max_capacity || "" : "";
  document.getElementById("f-price").value = space ? space.base_price_per_hour : "";
  document.getElementById("f-status").checked = space ? !!space.status : true;
  if (space) {
    document.getElementById("f-provider").value = space.provider_id || "";
  } else {
    const pid = await fetchProviderId();
    document.getElementById("f-provider").value = pid || "";
  }
  modal.style.display = "flex";
}

document.getElementById("add-btn").addEventListener("click", () => openForm(null));
document.getElementById("form-cancel").addEventListener("click", () => (modal.style.display = "none"));

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  formError.style.display = "none";
  const id = document.getElementById("f-id").value;
  const providerVal = document.getElementById("f-provider").value;
  const payload = {
    provider_id: providerVal ? Number(providerVal) : undefined,
    name: document.getElementById("f-name").value.trim(),
    space_type: document.getElementById("f-type").value,
    address: document.getElementById("f-address").value.trim() || undefined,
    description: document.getElementById("f-description").value.trim() || undefined,
    max_capacity: document.getElementById("f-capacity").value ? Number(document.getElementById("f-capacity").value) : undefined,
    base_price_per_hour: Number(document.getElementById("f-price").value),
    status: document.getElementById("f-status").checked,
  };
  const submitBtn = document.getElementById("form-submit");
  submitBtn.disabled = true;
  try {
    if (id) await SpaceApi.update(id, payload);
    else await SpaceApi.create(payload);
    modal.style.display = "none";
    load();
  } catch (err) {
    formError.textContent = err.message || "Lưu thất bại.";
    formError.style.display = "block";
  } finally {
    submitBtn.disabled = false;
  }
});

async function fetchProviderId() {
  const userId = AuthStore.getUserId();
  const token = AuthStore.getToken();
  if (!userId || !token) return null;
  try {
    const res = await fetch(`${API_BASE}/providers/user/${userId}`, {
      headers: { "Authorization": `Bearer ${token}` }
    });
    if (!res.ok) return null;
    const data = await res.json();
    return data.id || null;
  } catch { return null; }
}

async function load() {
  tbody.innerHTML = `<tr><td colspan="7">Đang tải...</td></tr>`;
  try {
    const data = await SpaceApi.list();
    const items = data.items || data || [];
    countEl.textContent = `${data.total ?? items.length} không gian`;
    if (!items.length) {
      tbody.innerHTML = `<tr><td colspan="7">Chưa có không gian nào.</td></tr>`;
      return;
    }
    tbody.innerHTML = items
      .map(
        (s) => `
      <tr>
        <td>#${s.id}</td>
        <td>${escapeHtml(s.name)}</td>
        <td>${TYPE_LABELS[s.type] || s.type}</td>
        <td>${formatPrice(s.base_price_per_hour)}đ</td>
        <td>${s.max_capacity ?? "—"}</td>
        <td><span class="badge ${s.status ? "confirmed" : "cancelled"}">${s.status ? "Mở" : "Đóng"}</span></td>
        <td class="actions">
          <button class="btn btn-ghost btn-sm edit-btn" data-id="${s.id}">Sửa</button>
          <button class="btn btn-ghost btn-sm del-btn" data-id="${s.id}">Xoá</button>
        </td>
      </tr>`
      )
      .join("");
    window.__spaces = items;
    document.querySelectorAll(".edit-btn").forEach((btn) =>
      btn.addEventListener("click", () => {
        const space = window.__spaces.find((s) => String(s.id) === btn.dataset.id);
        openForm(space);
      })
    );
    document.querySelectorAll(".del-btn").forEach((btn) =>
      btn.addEventListener("click", async () => {
        if (!confirm("Xoá không gian này?")) return;
        try {
          await SpaceApi.remove(btn.dataset.id);
          load();
        } catch (err) {
          alert(`Không xoá được: ${err.message}`);
        }
      })
    );
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7">Không tải được dữ liệu: ${escapeHtml(err.message)}</td></tr>`;
  }
}

if (requireAdmin()) {
  initAdminNav("spaces");
  load();
}
