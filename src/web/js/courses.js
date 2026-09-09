const resultsArea = document.getElementById("results-area");
const resultsCount = document.getElementById("results-count");

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

function formatDate(value) {
  if (!value) return null;
  const d = new Date(value);
  if (isNaN(d.getTime())) return value;
  return d.toLocaleDateString("vi-VN");
}

function isActiveStatus(status) {
  return ["open", "ongoing", "upcoming", "active"].includes((status || "").toLowerCase());
}

function renderCourses(courses) {
  if (!courses.length) {
    resultsArea.innerHTML = `<div class="empty-state">Hiện chưa có khoá học nào được mở.</div>`;
    return;
  }

  resultsArea.innerHTML = `<div class="grid">${courses
    .map((c) => {
      const start = formatDate(c.start_date);
      const end = formatDate(c.end_date);
      const dates =
        start || end
          ? `${start || "?"} &rarr; ${end || "?"}`
          : "Lịch khai giảng sẽ thông báo sau";
      return `
      <div class="course-card">
        <span class="status-pill ${isActiveStatus(c.status) ? "open" : "closed"}">${escapeHtml(
          c.status || ""
        )}</span>
        <h3>${escapeHtml(c.course_name)}</h3>
        <div class="course-dates">${dates}</div>
        <p>${escapeHtml(c.description || "")}</p>
      </div>`;
    })
    .join("")}</div>`;
}

async function loadCourses() {
  resultsArea.innerHTML = `<div class="loading-state">Đang tải danh sách khoá học...</div>`;
  try {
    const courses = await CourseApi.list();
    resultsCount.textContent = `${courses.length} khoá học`;
    renderCourses(courses);
  } catch (err) {
    resultsArea.innerHTML = `<div class="error-state">Không tải được danh sách khoá học: ${escapeHtml(
      err.message
    )}<br/><small>Kiểm tra server API đang chạy tại ${API_BASE}</small></div>`;
  }
}

loadCourses();
