// ============================================================
// Cấu hình API — đổi API_BASE nếu server chạy ở địa chỉ khác
// ============================================================
const API_BASE = window.location.origin;
const TOKEN_KEY = "sf_auth_token";
const CURRENT_USER_KEY = "sf_current_user_id";

async function apiRequest(path, { method = "GET", body, auth = false } = {}) {
  const headers = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (auth) {
    const token = AuthStore.getToken();
    if (!token) {
      const err = new Error("Bạn cần đăng nhập để tiếp tục.");
      err.code = "NO_TOKEN";
      throw err;
    }
    headers["Authorization"] = `Bearer ${token}`;
  }
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  let payload = null;
  try {
    payload = await res.json();
  } catch (_) {}
  if (!res.ok) {
    const message = (payload && (payload.message || payload.error)) || `Lỗi ${res.status}`;
    const err = new Error(message);
    err.status = res.status;
    err.body = payload;
    throw err;
  }
  return payload;
}

const apiGet = (path) => apiRequest(path);

// ------------------------------------------------------------
// Token JWT lưu ở localStorage — chỉ để chạy demo luồng đặt phòng.
// Trang cần đăng nhập thật sẽ set 2 key này sau khi gọi /auth/login.
// ------------------------------------------------------------
const AuthStore = {
  getToken() {
    return localStorage.getItem(TOKEN_KEY);
  },
  getUserId() {
    const v = localStorage.getItem(CURRENT_USER_KEY);
    return v ? Number(v) : null;
  },
  setSession(token, userId) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(CURRENT_USER_KEY, String(userId));
  },
  isLoggedIn() {
    return !!this.getToken() && !!this.getUserId();
  },
  // Đọc role từ payload của JWT (chỉ để hiển thị UI, backend vẫn tự kiểm tra lại).
  getRole() {
    const token = this.getToken();
    if (!token) return null;
    try {
      const payloadPart = token.split(".")[1];
      const json = decodeURIComponent(
        atob(payloadPart.replace(/-/g, "+").replace(/_/g, "/"))
          .split("")
          .map((c) => "%" + c.charCodeAt(0).toString(16).padStart(2, "0"))
          .join("")
      );
      return JSON.parse(json).role || null;
    } catch (_) {
      return null;
    }
  },
  isAdmin() {
    return this.isLoggedIn() && this.getRole() === "admin";
  },
  logout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(CURRENT_USER_KEY);
  },
};

// ------------------------------------------------------------
// Bảo vệ các trang quản trị: gọi ở đầu mỗi file *-admin.js.
// Trả về true nếu được phép chạy tiếp, false nếu đã điều hướng đi nơi khác.
// ------------------------------------------------------------
function requireAdmin() {
  if (!AuthStore.isAdmin()) {
    // If already on login page, don't redirect (prevent infinite loop)
    if (window.location.pathname.includes('/login.html')) {
      return false;
    }
    // Clear any stale token to prevent redirect loops
    AuthStore.logout();
    const next = encodeURIComponent(window.location.pathname.replace(/^.*\/web\//, ""));
    window.location.href = `../login.html?next=${next}`;
    return false;
  }
  const userEl = document.getElementById("admin-user");
  if (userEl) userEl.textContent = `User #${AuthStore.getUserId()}`;
  const logoutEl = document.getElementById("admin-logout");
  if (logoutEl) {
    logoutEl.addEventListener("click", (e) => {
      e.preventDefault();
      AuthStore.logout();
      window.location.href = "../index.html";
    });
  }
  return true;
}

// Đánh dấu mục đang active trên sidebar quản trị.
function initAdminNav(current) {
  document.querySelectorAll("[data-admin-nav]").forEach((el) => {
    if (el.dataset.adminNav === current) el.classList.add("active");
  });
}

const AuthApi = {
  // POST /auth/login
  login(username, password) {
    return apiRequest("/auth/login", { method: "POST", body: { username, password } });
  },
  // POST /auth/signup
  register({ username, email, password, passwordconfirm, role }) {
    return apiRequest("/auth/signup", {
      method: "POST",
      body: { username, email, password, passwordconfirm, role: role || "user" },
    });
  },
};

const ChatbotApi = {
  // POST /api/v1/chatbot/ask
  ask(message) {
    return apiRequest("/api/v1/chatbot/ask", {
      method: "POST",
      body: { message, user_id: AuthStore.getUserId() || undefined },
    });
  },
};

const RecommendationApi = {
  // GET /api/v1/recommendations/<user_id>?limit=
  get(userId, limit = 3) {
    return apiGet(`/api/v1/recommendations/${userId}?limit=${limit}`);
  },
};

const SpaceApi = {
  // GET /spaces/search?q=&space_type=&min_price=&max_price=&min_capacity=&available=
  search(filters = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== "" && value !== null && value !== undefined) {
        params.set(key, value);
      }
    });
    const qs = params.toString();
    return apiGet(`/spaces/search${qs ? `?${qs}` : ""}`);
  },

  // GET /spaces/<id>
  getById(id) {
    return apiGet(`/spaces/${id}`);
  },

  // GET /spaces/<id>/images
  getImages(id) {
    return apiGet(`/spaces/${id}/images`);
  },

  // GET /spaces/  (danh sách đầy đủ, dùng cho trang quản trị)
  list() {
    return apiGet("/spaces/");
  },

  // POST /spaces/
  create(payload) {
    return apiRequest("/spaces/", { method: "POST", auth: true, body: payload });
  },

  // PUT /spaces/<id>
  update(id, payload) {
    return apiRequest(`/spaces/${id}`, { method: "PUT", auth: true, body: payload });
  },

  // DELETE /spaces/<id>
  remove(id) {
    return apiRequest(`/spaces/${id}`, { method: "DELETE", auth: true });
  },
};

const EquipmentApi = {
  // GET /api/v1/equipment?q=&type=&space_id=&available=
  list(filters = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== "" && value !== null && value !== undefined) {
        params.set(key, value);
      }
    });
    const qs = params.toString();
    return apiGet(`/api/v1/equipment${qs ? `?${qs}` : ""}`);
  },

  // GET /api/v1/equipment/<id>
  getById(id) {
    return apiGet(`/api/v1/equipment/${id}`);
  },

  // POST /api/v1/equipment
  create(payload) {
    return apiRequest("/api/v1/equipment", { method: "POST", auth: true, body: payload });
  },

  // PUT /api/v1/equipment/<id>
  update(id, payload) {
    return apiRequest(`/api/v1/equipment/${id}`, { method: "PUT", auth: true, body: payload });
  },

  // DELETE /api/v1/equipment/<id>
  remove(id) {
    return apiRequest(`/api/v1/equipment/${id}`, { method: "DELETE", auth: true });
  },
};

const CourseApi = {
  // GET /courses/  (trả về mảng thuần, không bọc trong { items })
  list() {
    return apiGet("/courses/");
  },

  // GET /courses/<id>
  getById(id) {
    return apiGet(`/courses/${id}`);
  },

  // POST /courses/
  create(payload) {
    return apiRequest("/courses/", { method: "POST", body: payload });
  },

  // PUT /courses/<id>
  update(id, payload) {
    return apiRequest(`/courses/${id}`, { method: "PUT", body: payload });
  },

  // DELETE /courses/<id>
  remove(id) {
    return apiRequest(`/courses/${id}`, { method: "DELETE" });
  },
};

const BillingApi = {
  // ---- Hoá đơn ----
  listInvoices() {
    return apiGet("/v1/billing/invoices");
  },
  createInvoice(payload) {
    return apiRequest("/v1/billing/invoices", { method: "POST", auth: true, body: payload });
  },
  updateInvoice(id, payload) {
    return apiRequest(`/v1/billing/invoices/${id}`, { method: "PUT", auth: true, body: payload });
  },
  removeInvoice(id) {
    return apiRequest(`/v1/billing/invoices/${id}`, { method: "DELETE", auth: true });
  },

  // ---- Khách hàng ----
  listCustomers() {
    return apiGet("/v1/billing/customers");
  },
  createCustomer(payload) {
    return apiRequest("/v1/billing/customers", { method: "POST", auth: true, body: payload });
  },
  updateCustomer(id, payload) {
    return apiRequest(`/v1/billing/customers/${id}`, { method: "PUT", auth: true, body: payload });
  },
  removeCustomer(id) {
    return apiRequest(`/v1/billing/customers/${id}`, { method: "DELETE", auth: true });
  },

  // ---- Sản phẩm / Dịch vụ ----
  listProducts() {
    return apiGet("/v1/billing/products");
  },
  createProduct(payload) {
    return apiRequest("/v1/billing/products", { method: "POST", auth: true, body: payload });
  },
  updateProduct(id, payload) {
    return apiRequest(`/v1/billing/products/${id}`, { method: "PUT", auth: true, body: payload });
  },
  removeProduct(id) {
    return apiRequest(`/v1/billing/products/${id}`, { method: "DELETE", auth: true });
  },
};

const ReservationApi = {
  // POST /v1/reservations/  (yêu cầu đăng nhập)
  create({ userId, providerId, spaceId, startTime, endTime, totalPrice, notes }) {
    return apiRequest("/v1/reservations/", {
      method: "POST",
      auth: true,
      body: {
        user_id: userId,
        provider_id: providerId,
        space_id: spaceId,
        start_time: startTime,
        end_time: endTime,
        total_price: totalPrice,
        status: "pending",
        qr_code: notes || undefined,
      },
    });
  },

  // GET /v1/reservations/<id>
  getById(id) {
    return apiGet(`/v1/reservations/${id}`);
  },

  // POST /v1/reservations/<id>/payment  (yêu cầu đăng nhập)
  createPayment(reservationId, { userId, amount, method }) {
    return apiRequest(`/v1/reservations/${reservationId}/payment`, {
      method: "POST",
      auth: true,
      body: { user_id: userId, amount, method },
    });
  },

  // POST /v1/reservations/<id>/payment/confirm  (yêu cầu đăng nhập)
  confirmPayment(reservationId) {
    return apiRequest(`/v1/reservations/${reservationId}/payment/confirm`, {
      method: "POST",
      auth: true,
    });
  },

  // GET /v1/reservations/?status=&user_id=&provider_id=  (dùng cho trang quản trị)
  list(filters = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== "" && value !== null && value !== undefined) {
        params.set(key, value);
      }
    });
    const qs = params.toString();
    return apiGet(`/v1/reservations/${qs ? `?${qs}` : ""}`);
  },

  approve(id) {
    return apiRequest(`/v1/reservations/${id}/approve`, { method: "POST", auth: true });
  },
  confirm(id) {
    return apiRequest(`/v1/reservations/${id}/confirm`, { method: "POST", auth: true });
  },
  cancel(id) {
    return apiRequest(`/v1/reservations/${id}/cancel`, { method: "POST", auth: true });
  },
  checkIn(id) {
    return apiRequest(`/v1/reservations/${id}/checkin`, { method: "POST", auth: true });
  },
  checkOut(id) {
    return apiRequest(`/v1/reservations/${id}/checkout`, { method: "POST", auth: true });
  },
};
