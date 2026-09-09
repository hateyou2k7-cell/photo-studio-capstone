const TYPE_LABELS = {
  enlarger: "Máy phóng ảnh",
  camera: "Máy ảnh",
  scanner: "Máy quét film",
  lighting: "Đèn / chiếu sáng",
  tripod: "Chân máy",
  tank: "Tank tráng film",
  other: "Khác",
};
const CONDITION_LABELS = { excellent: "Rất tốt", good: "Tốt", fair: "Tạm ổn", poor: "Kém", broken: "Hỏng" };

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
const form = document.getElementById("equip-form");
const formError = document.getElementById("form-error");

function openForm(eq) {
  formError.style.display = "none";
  document.getElementById("form-title").textContent = eq ? `Sửa: ${eq.name}` : "Thêm thiết bị";
  document.getElementById("f-id").value = eq ? eq.id : "";
  document.getElementById("f-provider").value = eq ? eq.provider_id : "";
  document.getElementById("f-space").value = eq && eq.space_id ? eq.space_id : "";
  document.getElementById("f-name").value = eq ? eq.name : "";
  document.getElementById("f-model").value = eq ? eq.model_name || "" : "";
  document.getElementById("f-type").value = eq ? eq.type : "camera";
  document.getElementById("f-condition").value = eq ? eq.condition : "good";
  document.getElementById("f-description").value = eq ? eq.description || "" : "";
  document.getElementById("f-price").value = eq ? eq.price_per_hour : "";
  document.getElementById("f-available").checked = eq ? !!eq.is_available : true;
  modal.style.display = "flex";
}

document.getElementById("add-btn").addEventListener("click", () => openForm(null));
document.getElementById("form-cancel").addEventListener("click", () => (modal.style.display = "none"));

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  formError.style.display = "none";
  const id = document.getElementById("f-id").value;
  const base = {
    space_id: document.getElementById("f-space").value ? Number(document.getElementById("f-space").value) : undefined,
    name: document.getElementById("f-name").value.trim(),
    model_name: document.getElementById("f-model").value.trim() || undefined,
    type: document.getElementById("f-type").value,
    condition: document.getElementById("f-condition").value,
    description: document.getElementById("f-description").value.trim() || undefined,
    price_per_hour: Number(document.getElementById("f-price").value || 0),
    is_available: document.getElementById("f-available").checked,
  };
  const submitBtn = document.getElementById("form-submit");
  submitBtn.disabled = true;
  try {
    if (id) {
      await EquipmentApi.update(id, base);
    } else {
      await EquipmentApi.create({ ...base, provider_id: Number(document.getElementById("f-provider").value) });
    }
    modal.style.display = "none";
    load();
  } catch (err) {
    formError.textContent = err.message || "Lưu thất bại.";
    formError.style.display = "block";
  } finally {
    submitBtn.disabled = false;
  }
});

async function load() {
  tbody.innerHTML = `<tr><td colspan="7">Đang tải...</td></tr>`;
  try {
    const data = await EquipmentApi.list();
    const items = data.items || data || [];
    countEl.textContent = `${data.total ?? items.length} thiết bị`;
    if (!items.length) {
      tbody.innerHTML = `<tr><td colspan="7">Chưa có thiết bị nào.</td></tr>`;
      return;
    }
    tbody.innerHTML = items
      .map(
        (eq) => `
      <tr>
        <td>#${eq.id}</td>
        <td>${escapeHtml(eq.name)}</td>
        <td>${TYPE_LABELS[eq.type] || eq.type}</td>
        <td>${CONDITION_LABELS[eq.condition] || eq.condition}</td>
        <td>${formatPrice(eq.price_per_hour)}đ</td>
        <td><span class="badge ${eq.is_available ? "confirmed" : "cancelled"}">${eq.is_available ? "Còn trống" : "Đang thuê"}</span></td>
        <td class="actions">
          <button class="btn btn-ghost btn-sm edit-btn" data-id="${eq.id}">Sửa</button>
          <button class="btn btn-ghost btn-sm del-btn" data-id="${eq.id}">Xoá</button>
        </td>
      </tr>`
      )
      .join("");
    window.__equipment = items;
    document.querySelectorAll(".edit-btn").forEach((btn) =>
      btn.addEventListener("click", () => {
        const eq = window.__equipment.find((x) => String(x.id) === btn.dataset.id);
        openForm(eq);
      })
    );
    document.querySelectorAll(".del-btn").forEach((btn) =>
      btn.addEventListener("click", async () => {
        if (!confirm("Xoá thiết bị này?")) return;
        try {
          await EquipmentApi.remove(btn.dataset.id);
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
  initAdminNav("equipment");
  load();
}
