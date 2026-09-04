const detailArea = document.getElementById("detail-area");

const TYPE_LABELS = {
  darkroom: "Phòng tối (Darkroom)",
  studio: "Studio chụp",
};

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

function formatPrice(value) {
  return new Intl.NumberFormat("vi-VN").format(value);
}

function getSpaceId() {
  const params = new URLSearchParams(window.location.search);
  return params.get("id");
}

function renderGallery(images) {
  if (!images.length) {
    return `
      <div class="gallery-main">
        <span class="placeholder">Chưa có ảnh cho không gian này</span>
      </div>`;
  }
  const sorted = [...images].sort((a, b) => {
    if (a.is_primary !== b.is_primary) return a.is_primary ? -1 : 1;
    return (a.sort_order ?? 0) - (b.sort_order ?? 0);
  });
  const mainId = `main-img`;
  return `
    <div class="gallery-main">
      <img id="${mainId}" src="${sorted[0].url}" alt="Ảnh không gian" />
    </div>
    ${
      sorted.length > 1
        ? `<div class="gallery-strip">
      ${sorted
        .map(
          (img, i) => `
        <button type="button" class="${i === 0 ? "active" : ""}" data-src="${img.url}">
          <img src="${img.url}" alt="" />
        </button>`
        )
        .join("")}
    </div>`
        : ""
    }`;
}

function bindGallery() {
  const buttons = document.querySelectorAll(".gallery-strip button");
  const mainImg = document.getElementById("main-img");
  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      mainImg.src = btn.dataset.src;
      buttons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
    });
  });
}

function renderDetail(space, images) {
  const statusOpen = space.status;
  detailArea.innerHTML = `
    <div class="detail-layout">
      <div class="gallery">
        ${renderGallery(images)}
      </div>
      <div class="detail-info">
        <span class="type-tag">${TYPE_LABELS[space.type] || space.type}</span>
        <h1>${escapeHtml(space.name)}</h1>
        <div class="detail-address">${escapeHtml(space.address || "Chưa cập nhật địa chỉ")}</div>

        <div class="status-pill ${statusOpen ? "open" : "closed"}">
          ${statusOpen ? "Đang nhận đặt lịch" : "Tạm ngừng nhận đặt"}
        </div>

        <div class="detail-price">
          ${formatPrice(space.base_price_per_hour)}đ <small>/ giờ</small>
        </div>

        <div class="spec-grid">
          <div class="spec-item">
            <label>Sức chứa tối đa</label>
            <span>${space.max_capacity ? `${space.max_capacity} người` : "Chưa cập nhật"}</span>
          </div>
          <div class="spec-item">
            <label>Loại không gian</label>
            <span>${TYPE_LABELS[space.type] || space.type}</span>
          </div>
        </div>

        <div class="detail-desc">
          <h2>Giới thiệu</h2>
          <p>${escapeHtml(space.description || "Chủ phòng chưa cập nhật mô tả cho không gian này.")}</p>
        </div>

        <a class="btn btn-primary" style="display:inline-block;text-decoration:none;text-align:center;margin-top:8px;"
           href="confirm.html?space_id=${space.id}">
          ${statusOpen ? "Đặt phòng này" : "Phòng tạm ngừng nhận đặt"}
        </a>
      </div>
    </div>
  `;
  bindGallery();
}

async function loadDetail() {
  const id = getSpaceId();
  if (!id) {
    detailArea.innerHTML = `<div class="error-state">Thiếu id phòng trên đường dẫn. Quay lại trang tìm kiếm và chọn 1 phòng.</div>`;
    return;
  }
  try {
    const [space, images] = await Promise.all([
      SpaceApi.getById(id),
      SpaceApi.getImages(id).catch(() => []), // ảnh là phụ, lỗi ảnh không chặn hiển thị thông tin phòng
    ]);
    renderDetail(space, images);
  } catch (err) {
    detailArea.innerHTML = `<div class="error-state">Không tải được thông tin phòng: ${escapeHtml(
      err.message
    )}<br/><small>Kiểm tra server API đang chạy tại ${API_BASE}</small></div>`;
  }
}

loadDetail();
