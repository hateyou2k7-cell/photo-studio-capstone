const form = document.getElementById("filter-form");
const resultsArea = document.getElementById("results-area");
const resultsCount = document.getElementById("results-count");
const resetBtn = document.getElementById("reset-filters");

const TYPE_LABELS = {
  darkroom: "Phòng tối",
  studio: "Studio",
};

function currentFilters() {
  const data = new FormData(form);
  const filters = {
    q: data.get("q")?.trim() || "",
    space_type: data.get("space_type") || "",
    min_price: data.get("min_price") || "",
    max_price: data.get("max_price") || "",
    min_capacity: data.get("min_capacity") || "",
  };
  if (document.getElementById("available").checked) {
    filters.available = "true";
  }
  return filters;
}

function iconForType(type) {
  // Biểu tượng đơn giản: cuộn phim cho darkroom, khẩu độ máy ảnh cho studio
  if (type === "darkroom") {
    return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3">
      <rect x="3" y="5" width="18" height="14" rx="1.5"/>
      <circle cx="7" cy="8.3" r="0.6" fill="currentColor" stroke="none"/>
      <circle cx="7" cy="15.7" r="0.6" fill="currentColor" stroke="none"/>
      <circle cx="17" cy="8.3" r="0.6" fill="currentColor" stroke="none"/>
      <circle cx="17" cy="15.7" r="0.6" fill="currentColor" stroke="none"/>
      <circle cx="12" cy="12" r="3.4"/>
    </svg>`;
  }
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3">
    <path d="M4 8l2-2.5h3L11 8h6a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2z"/>
    <circle cx="13" cy="13" r="3.4"/>
  </svg>`;
}

function formatPrice(value) {
  return new Intl.NumberFormat("vi-VN").format(value);
}

function renderResults(spaces) {
  if (!spaces.length) {
    resultsArea.innerHTML = `<div class="empty-state">Không tìm thấy không gian nào phù hợp với bộ lọc hiện tại.</div>`;
    return;
  }

  resultsArea.innerHTML = `<div class="grid">${spaces
    .map(
      (space) => `
    <a class="card" href="detail.html?id=${space.id}">
      <div class="card-thumb">
        <span class="type-tag">${TYPE_LABELS[space.type] || space.type}</span>
        ${iconForType(space.type)}
      </div>
      <div class="card-body">
        <h3>${escapeHtml(space.name)}</h3>
        <div class="card-meta">${escapeHtml(space.address || "Chưa cập nhật địa chỉ")}${
          space.max_capacity ? ` · Tối đa ${space.max_capacity} người` : ""
        }</div>
        <div class="card-price">${formatPrice(space.base_price_per_hour)}đ <small>/ giờ</small></div>
      </div>
    </a>`
    )
    .join("")}</div>`;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

async function runSearch() {
  resultsArea.innerHTML = `<div class="loading-state">Đang tải danh sách phòng...</div>`;
  resultsCount.textContent = "";
  try {
    const data = await SpaceApi.search(currentFilters());
    const items = data.items || [];
    resultsCount.textContent = `${data.total ?? items.length} kết quả`;
    renderResults(items);
  } catch (err) {
    resultsArea.innerHTML = `<div class="error-state">Không tải được danh sách phòng: ${escapeHtml(
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
