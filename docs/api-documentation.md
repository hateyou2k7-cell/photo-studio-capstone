# API Documentation

Photo Studio Capstone Backend REST API.

**Base URL**: `http://localhost:9999`
**Swagger UI**: http://localhost:9999/docs

Tổng: **75 endpoints**, trong đó **22 endpoints yêu cầu JWT**.

---

## Authentication

### Đăng nhập

```
POST /auth/login
```

**Request**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Response** (200):
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "username": "user1"
}
```

### Đăng ký

```
POST /auth/signup
```

**Request**:
```json
{
  "username": "string",
  "password": "string",
  "passwordconfirm": "string",
  "email": "user@example.com"
}
```

**Response** (201):
```json
{
  "username": "nguyenvana",
  "email": "nguyenvana@example.com"
}
```

Đăng ký tự động tạo 2 records:
- `auth_users`: username, email, password_hash (dùng cho login)
- `users`: email, password_hash, full_name, role='user' (dùng cho reservation, billing...)

**Roles**: `user` | `photographer` | `provider` | `expert` | `admin`

### Health check

```
GET /auth/check_router
```

### Sử dụng JWT

Thêm header cho các endpoint có `@jwt_required`:

```
Authorization: Bearer <token>
```

---

## Rooms (Legacy)

Bảng `rooms` riêng biệt với `spaces`. CRUD đầy đủ, **không yêu cầu JWT**.

```
GET    /rooms/              Danh sách
GET    /rooms/{id}          Chi tiết
POST   /rooms/              Tạo          @jwt_required: NO
PUT    /rooms/{id}          Sửa          @jwt_required: NO
DELETE /rooms/{id}          Xóa          @jwt_required: NO
```

**Room Types**: `standard`, `vip`, `studio`, `conference`
**Status**: `available`, `booked`, `maintenance`

---

## Spaces

Quản lý không gian nhiếp ảnh (darkroom, studio). **Không yêu cầu JWT**.

### CRUD

```
GET    /spaces/                    Danh sách (paginated)
GET    /spaces/search              Tìm kiếm với filters
GET    /spaces/{id}                Chi tiết
POST   /spaces/                    Tạo
PUT    /spaces/{id}                Sửa
DELETE /spaces/{id}                Xóa
```

**Search filters** (`/spaces/search`):
- `q` (string): Từ khóa
- `space_type` (string): `darkroom` | `studio`
- `min_price` (number): Giá tối thiểu
- `max_price` (number): Giá tối đa
- `min_capacity` (int): Sức chứa tối thiểu
- `available` (bool): Chỉ hiện trống

**Space fields** (request):
```json
{
  "provider_id": 1,
  "name": "Studio A",
  "space_type": "studio",
  "description": "Phòng chụp ánh sáng tự nhiên",
  "address": "123 Đường ABC",
  "max_capacity": 10,
  "base_price_per_hour": 200000,
  "status": true
}
```

**Lưu ý**: Domain model có nhiều fields hơn (art_style, lighting, ventilation, acoustics, amenities, operating_hours, latitude, longitude) nhưng schema hiện tại chỉ validate các field trên.

---

## Space Images

Quản lý hình ảnh không gian. **Không yêu cầu JWT**.

```
POST   /spaces/{id}/images              Upload (multipart/form-data)
GET    /spaces/{id}/images              Danh sách
PUT    /spaces/{id}/images/{image_id}   Đặt làm primary
DELETE /spaces/{id}/images/{image_id}   Xóa
```

Allowed extensions: jpg, png, webp. Max size: 5MB/file.

---

## Space Schedules

Lịch hoạt động theo ngày trong tuần. **Không yêu cầu JWT**.

```
GET    /spaces/{id}/schedule                    Danh sách
POST   /spaces/{id}/schedule                    Thêm khung giờ
PUT    /spaces/{id}/schedule/{schedule_id}      Sửa
DELETE /spaces/{id}/schedule/{schedule_id}      Xóa
```

**Schedule fields**:
```json
{
  "day_of_week": 1,
  "start_time": "08:00",
  "end_time": "22:00",
  "is_available": true
}
```

`day_of_week`: 0=Chủ nhật, 1=Thứ 2, ..., 7=Thứ 7

---

## Reservations

Đặt chỗ với state machine và conflict detection. **11/17 endpoints yêu cầu JWT**.

### Danh sách & Chi tiết (public)

```
GET    /v1/reservations/                    Danh sách
GET    /v1/reservations/{id}                Chi tiết
```

**Filters**: `user_id`, `provider_id`, `status`

### CRUD (JWT required)

```
POST   /v1/reservations/                    Tạo đặt chỗ
PUT    /v1/reservations/{id}                Sửa
DELETE /v1/reservations/{id}                Xóa
```

**Request**:
```json
{
  "user_id": 1,
  "provider_id": 2,
  "space_id": 4,
  "package_id": null,
  "start_time": "2026-11-01T09:00:00",
  "end_time": "2026-11-01T11:00:00",
  "total_price": 400000,
  "qr_code": "RES-001"
}
```

### State transitions (JWT required)

```
POST   /v1/reservations/{id}/approve        pending → approved
POST   /v1/reservations/{id}/confirm        approved → confirmed
POST   /v1/reservations/{id}/cancel         → cancelled
POST   /v1/reservations/{id}/checkin        → checked_in
POST   /v1/reservations/{id}/checkout       checked_in → checked_out
```

### Reservation Items

```
GET    /v1/reservations/{id}/items          Danh sách (public)
POST   /v1/reservations/{id}/items          Thêm item (public)
```

**Item types**: `space`, `resource`, `consumable`, `service`

```json
{
  "item_type": "equipment",
  "item_id": 1,
  "quantity": 1,
  "price_at_booking": 100000
}
```

### Payments

```
GET    /v1/reservations/{id}/payment        Xem (public)
POST   /v1/reservations/{id}/payment        Tạo (JWT required)
POST   /v1/reservations/{id}/payment/confirm  Xác nhận (JWT required)
```

**Payment methods**: `vnpay`, `momo`, `cash`

### Reviews

```
GET    /v1/reservations/{id}/reviews        Danh sách (public)
POST   /v1/reservations/{id}/reviews        Thêm (JWT required)
```

**Review request**:
```json
{
  "user_id": 1,
  "space_id": 4,
  "rating": 5,
  "comment": "Phòng chụp rất tốt!"
}
```

---

## Equipment

Thiết bị nhiếp ảnh. **Không yêu cầu JWT**.

```
GET    /api/v1/equipment                    Danh sách
GET    /api/v1/equipment/{id}               Chi tiết
POST   /api/v1/equipment                    Tạo
PUT    /api/v1/equipment/{id}               Sửa
DELETE /api/v1/equipment/{id}               Xóa
```

**Filters**: `q`, `type`, `space_id`, `available`

**Equipment types**: `enlarger`, `camera`, `scanner`, `lighting`, `tripod`, `tank`, `other`

**Conditions**: `excellent`, `good`, `fair`, `poor`, `broken`

```json
{
  "provider_id": 2,
  "space_id": 4,
  "name": "Canon EOS R5",
  "model_name": "EOS R5",
  "type": "camera",
  "compatibility": "RF mount",
  "condition": "excellent",
  "price_per_hour": 100000,
  "is_available": true
}
```

---

## Package Bookings

Đặt gói dịch vụ với resource conflict detection. **Không yêu cầu JWT**.

```
GET    /api/v1/package-bookings                    Danh sách
GET    /api/v1/package-bookings/{id}               Chi tiết
POST   /api/v1/package-bookings                    Tạo
PATCH  /api/v1/package-bookings/{id}/cancel        Hủy
```

**Filters**: `package_id`, `customer_id`, `status`

```json
{
  "package_id": 1,
  "space_id": 4,
  "customer_id": 1,
  "start_time": "2026-11-01T09:00:00",
  "end_time": "2026-11-01T17:00:00",
  "notes": "Muốn chụp phim đen trắng"
}
```

Hệ thống tự động kiểm tra:
- Space conflict (`find_conflicts`)
- Equipment conflict (`find_equipment_conflicts`)
- PostgreSQL advisory locks để ngăn race condition

---

## Billing

Hóa đơn, khách hàng, sản phẩm, thanh toán. **11/19 endpoints yêu cầu JWT**.

### Invoices

```
GET    /v1/billing/invoices              Danh sách (public)
GET    /v1/billing/invoices/{id}         Chi tiết (public)
POST   /v1/billing/invoices              Tạo (JWT)
PUT    /v1/billing/invoices/{id}         Sửa (JWT)
DELETE /v1/billing/invoices/{id}         Xóa (JWT)
```

**Filters**: `customer_id`, `status`

### Invoice Items

```
GET    /v1/billing/invoices/{id}/items   Danh sách (public)
POST   /v1/billing/invoices/{id}/items   Thêm (JWT)
```

### Invoice Payments

```
GET    /v1/billing/invoices/{id}/payments  Danh sách (public)
POST   /v1/billing/invoices/{id}/payments  Thêm (JWT)
```

### Customers

```
GET    /v1/billing/customers             Danh sách (public)
GET    /v1/billing/customers/{id}        Chi tiết (public)
POST   /v1/billing/customers             Tạo (JWT)
PUT    /v1/billing/customers/{id}        Sửa (JWT)
DELETE /v1/billing/customers/{id}        Xóa (JWT)
```

### Products

```
GET    /v1/billing/products              Danh sách (public)
GET    /v1/billing/products/{id}         Chi tiết (public)
POST   /v1/billing/products              Tạo (JWT)
PUT    /v1/billing/products/{id}         Sửa (JWT)
DELETE /v1/billing/products/{id}         Xóa (JWT)
```

---

## Chatbot AI

Trợ lý AI sử dụng OpenAI GPT-4o-mini. **Không yêu cầu JWT**.

```
POST   /api/v1/chatbot/ask               Hỏi trợ lý
GET    /api/v1/chatbot/health            Kiểm tra trạng thái OpenAI
```

**Request**:
```json
{
  "message": "Phim 35mm là gì?"
}
```

Hệ thống sử dụng function calling với 4 tools:
1. `search_faq` - Tìm kiếm trong FAQ
2. `suggest_equipment` - Gợi ý thiết bị
3. `suggest_room` - Gợi ý phòng
4. `suggest_package` - Gợi ý gói dịch vụ

Fallback: Khi OpenAI không khả dụng, trả lời từ local FAQ + database queries.

---

## Recommendations

Gợi ý không gian theo lịch sử đặt chỗ. **Không yêu cầu JWT**.

```
GET    /api/v1/recommendations/{user_id}
```

Thuật toán content-based filtering:
- Art style (35%)
- Space type (25%)
- Price range (20%)
- Location distance (20%, haversine)

Cold start: Trả về top spaces theo rating/views.

---

## Courses

Quản lý khóa học. **Không yêu cầu JWT**.

```
GET    /courses/                    Danh sách
GET    /courses/{id}               Chi tiết
POST   /courses/                   Tạo
PUT    /courses/{id}               Sửa
DELETE /courses/{id}               Xóa
```

Repository dùng PostgreSQL database, persist data.

---

## Utility

```
GET    /                    Test GUI (HTML page)
GET    /swagger.json        OpenAPI spec
GET    /docs                Swagger UI
GET    /uploads/{filename}  Uploaded files
OPTIONS /options            CORS preflight
```

---

## Error Response

```json
{
  "error": "Mô tả lỗi"
}
```

| Status | Mô tả |
|---|---|
| 400 | Bad Request |
| 401 | Unauthorized (thiếu token / token hết hạn) |
| 404 | Not Found |
| 409 | Conflict (trùng lịch) |
| 500 | Internal Server Error |
