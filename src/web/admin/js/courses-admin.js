const STATUS_LABELS = {
  open: "Đang mở",
  closed: "Đã đóng",
  upcoming: "Sắp khai giảng",
};

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}
function formatDate(v) {
  if (!v) return "—";
  const d = new Date(v);
  if (isNaN(d)) return String(v);
  return d.toLocaleDateString("vi-VN");
}

const tbody = document.getElementById("table-body");
const countEl = document.getElementById("results-count");
const modal = document.getElementById("form-modal");
const form = document.getElementById("course-form");
const formError = document.getElementById("form-error");

function openForm(course) {
  formError.style.display = "none";
  document.getElementById("form-title").textContent = course ? `Sửa: ${course.course_name}` : "Thêm khoá học";
  document.getElementById("f-id").value = course ? course.id : "";
  document.getElementById("f-name").value = course ? course.course_name : "";
  document.getElementById("f-description").value = course ? course.description || "" : "";
  document.getElementById("f-status").value = course ? course.status : "open";
  document.getElementById("f-start").value = course && course.start_date ? course.start_date.slice(0, 10) : "";
  document.getElementById("f-end").value = course && course.end_date ? course.end_date.slice(0, 10) : "";
  modal.style.display = "flex";
}

document.getElementById("add-btn").addEventListener("click", () => openForm(null));
document.getElementById("form-cancel").addEventListener("click", () => (modal.style.display = "none"));

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  formError.style.display = "none";
  const id = document.getElementById("f-id").value;
  const payload = {
    course_name: document.getElementById("f-name").value.trim(),
    description: document.getElementById("f-description").value.trim(),
    status: document.getElementById("f-status").value,
    start_date: document.getElementById("f-start").value || undefined,
    end_date: document.getElementById("f-end").value || undefined,
  };
  const submitBtn = document.getElementById("form-submit");
  submitBtn.disabled = true;
  try {
    if (id) await CourseApi.update(id, payload);
    else await CourseApi.create(payload);
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
  tbody.innerHTML = `<tr><td colspan="6">Đang tải...</td></tr>`;
  try {
    const data = await CourseApi.list();
    const items = Array.isArray(data) ? data : data.items || [];
    countEl.textContent = `${items.length} khoá học`;
    if (!items.length) {
      tbody.innerHTML = `<tr><td colspan="6">Chưa có khoá học nào.</td></tr>`;
      return;
    }
    tbody.innerHTML = items
      .map(
        (c) => `
      <tr>
        <td>#${c.id}</td>
        <td>${escapeHtml(c.course_name)}</td>
        <td>${formatDate(c.start_date)}</td>
        <td>${formatDate(c.end_date)}</td>
        <td><span class="badge ${c.status === "open" ? "confirmed" : c.status === "closed" ? "cancelled" : "pending"}">${
          STATUS_LABELS[c.status] || c.status
        }</span></td>
        <td class="actions">
          <button class="btn btn-ghost btn-sm edit-btn" data-id="${c.id}">Sửa</button>
          <button class="btn btn-ghost btn-sm del-btn" data-id="${c.id}">Xoá</button>
        </td>
      </tr>`
      )
      .join("");
    window.__courses = items;
    document.querySelectorAll(".edit-btn").forEach((btn) =>
      btn.addEventListener("click", () => {
        const course = window.__courses.find((x) => String(x.id) === btn.dataset.id);
        openForm(course);
      })
    );
    document.querySelectorAll(".del-btn").forEach((btn) =>
      btn.addEventListener("click", async () => {
        if (!confirm("Xoá khoá học này?")) return;
        try {
          await CourseApi.remove(btn.dataset.id);
          load();
        } catch (err) {
          alert(`Không xoá được: ${err.message}`);
        }
      })
    );
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6">Không tải được dữ liệu: ${escapeHtml(err.message)}</td></tr>`;
  }
}

if (requireAdmin()) {
  initAdminNav("courses");
  load();
}
