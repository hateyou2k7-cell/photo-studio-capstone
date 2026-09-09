const TYPE_LABELS = { darkroom: "Phòng tối", studio: "Studio" };

function iconForType(type) {
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

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

async function loadFeaturedSpaces() {
  const area = document.getElementById("featured-area");
  try {
    const data = await SpaceApi.search({ available: "true" });
    const items = (data.items || []).slice(0, 4);
    if (!items.length) {
      area.innerHTML = `<div class="empty-state">Chưa có không gian nào khả dụng lúc này.</div>`;
      return;
    }
    area.innerHTML = `<div class="grid">${items
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
  } catch (err) {
    area.innerHTML = `<div class="error-state">Không tải được danh sách: ${escapeHtml(err.message)}</div>`;
  }
}

loadFeaturedSpaces();
