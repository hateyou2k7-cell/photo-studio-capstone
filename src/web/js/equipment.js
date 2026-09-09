const form = document.getElementById("filter-form");
const resultsArea = document.getElementById("results-area");
const resultsCount = document.getElementById("results-count");
const resetBtn = document.getElementById("reset-filters");

const TYPE_LABELS = {
  camera: "Máy ảnh",
  lighting: "Đèn chiếu sáng",
  enlarger: "Máy phóng ảnh",
  scanner: "Máy quét phim",
  tripod: "Chân máy",
  tank: "Bình tráng phim",
  other: "Khác",
};

const CONDITION_LABELS = {
  excellent: "Rất tốt",
  good: "Tốt",
  fair: "Khá",
  poor: "Cũ",
  broken: "Hỏng",
};

function formatPrice(value) {
  return new Intl.NumberFormat("vi-VN").format(value || 0);
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

function currentFilters() {
  const data = new FormData(form);
  const filters = {
    q: data.get("q")?.trim() || "",
    type: data.get("type") || "",
  };
  if (document.getElementById("available").checked) {
    filters.available = "true";
  }
  return filters;
}

function renderResults(items) {
  if (!items.length) {
    resultsArea.innerHTML = `<div class="empty-state">Không tìm thấy thiết bị nào phù hợp.</div>`;
    return;
  }

  resultsArea.innerHTML = `<div class="grid">${items
    .map(
      (eq) => {
        const imageUrl = `https://picsum.photos/seed/equipment_${eq.id}/400/300`;
        const isAvailable = eq.is_available;
        return `
    <div class="card" style="cursor:default;">
      <div class="card-thumb">
        <span class="type-tag">${TYPE_LABELS[eq.type] || eq.type}</span>
        <img src="${imageUrl}" alt="${escapeHtml(eq.name)}" style="width:100%;height:100%;object-fit:cover;border-radius:4px;" />
      </div>
      <div class="card-body">
        <h3>${escapeHtml(eq.name)}</h3>
        <div class="card-meta">
          ${eq.model_name ? escapeHtml(eq.model_name) + " · " : ""}Tình trạng: ${
            CONDITION_LABELS[eq.condition] || eq.condition
          }
        </div>
        ${eq.description ? `<div class="card-meta">${escapeHtml(eq.description)}</div>` : ""}
        <div class="card-price">${formatPrice(eq.price_per_hour)}đ <small>/ giờ</small></div>
        <div style="margin-top:8px;display:flex;justify-content:space-between;align-items:center;">
          <span class="status-pill ${isAvailable ? "open" : "closed"}">
            ${isAvailable ? "Còn trống" : "Đang được thuê"}
          </span>
          ${isAvailable ? `<a href="confirm.html?equipment_id=${eq.id}" class="btn btn-primary" style="width:auto;padding:6px 14px;font-size:0.8rem;">Thuê</a>` : ""}
        </div>
      </div>
    </div>`;
      }
    )
    .join("")}</div>`;
}

async function runSearch() {
  resultsArea.innerHTML = `<div class="loading-state">Đang tải danh sách thiết bị...</div>`;
  resultsCount.textContent = "";
  try {
    const data = await EquipmentApi.list(currentFilters());
    const items = data.items || [];
    resultsCount.textContent = `${data.total ?? items.length} kết quả`;
    renderResults(items);
  } catch (err) {
    resultsArea.innerHTML = `<div class="error-state">Không tải được danh sách thiết bị: ${escapeHtml(
      err.message
    )}<br/><small>Kiểm tra server API đang chạy tại ${API_BASE}</small></div>`;
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  runSearch();
});

resetBtn.addEventListener("click", () => {
  form.reset();
  runSearch();
});

runSearch();
