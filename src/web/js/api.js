// ============================================================
// Cấu hình API — đổi API_BASE nếu server chạy ở địa chỉ khác
// ============================================================
const API_BASE = "http://localhost:9999";
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
};
