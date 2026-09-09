# Tài liệu API

API REST cho backend Photo Studio Capstone.

**Base URL**: `http://localhost:9999`  
**Swagger UI**: http://localhost:9999/docs

Tổng số endpoint: **65**, trong đó **25 yêu cầu JWT**.

---

## Xác thực

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
  "user_id": 1
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
  "email": "user@example.com",
  "role": "user"
}
```

Trong đó `role` (không bắt buộc) có thể là: `user`, `photographer`, `provider`, `expert` (mặc định `user`). Các giá trị `admin` và `manager` không được chấp nhận.

**Response** (201):
```json
{
  "username": "nguyenvana",
  "email": "nguyenvana@example.com"
}
```

Sau khi đăng ký, hệ thống tự động tạo:
- Bản ghi `users` với đầy đủ username, email, password_hash, full_name, role.
- Nếu role là `provider`, tự động tạo bản ghi `provider_profiles` với trạng thái `pending`.

### Kiểm tra sức khỏe router

```
GET /auth/check_router
```

### Sử dụng JWT

Với các endpoint yêu cầu JWT, thêm header:

```
Authorization: Bearer <token>
```

Payload JWT chứa: `user_id`, `role`, `exp`.

**Admin bypass**: Nếu JWT chứa role `admin`, nó sẽ vượt qua mọi kiểm tra JWT (unconditional access).

---

## Quản lý không gian (Spaces)

Không gian bao gồm: darkroom, studio, standard, vip, conference. Lưu ý: `rooms` đã deprecated, hãy dùng `spaces`.

### Công khai (không cần JWT)

```
GET    /spaces/                    Danh sách (có phân trang)
GET    /spaces/search              Tìm kiếm với bộ lọc
GET    /spaces/{id}                Chi tiết
```

### CRUD (chỉ admin/manager)

```
POST   /spaces/                    Tạo mới          @jwt_required: YES (admin/manager)
PUT    /spaces/{id}                Cập nhật         @jwt_required: YES (admin/manager)
DELETE /spaces/{id}                Xóa              @jwt_required: YES (admin/manager)
```

**Bộ lọc tìm kiếm** (`/spaces/search`):
- `q` (string): Từ khóa
- `space_type` (string): `darkroom`, `studio`, `standard`, `vip`, `conference`
- `min_price` (number): Giá tối thiểu
- `max_price` (number): Giá tối đa
- `min_capacity` (int): Sức chứa tối thiểu
- `available` (bool): Chỉ hiển thị không gian trống

**Dữ liệu của không gian**:
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

`provider_id` là tùy chọn (phòng không nhất thiết phải có provider).

---

## Hình ảnh không gian

Quản lý hình ảnh cho không gian. **Không yêu cầu JWT**.

```
POST   /spaces/{id}/images              Upload (multipart/form-data)
GET    /spaces/{id}/images              Danh sách
PUT    /spaces/{id}/images/{image_id}   Đặt làm ảnh chính
DELETE /spaces/{id}/images/{image_id}   Xóa
```

Chỉ chấp nhận các định dạng: jpg, png, webp. Dung lượng tối đa: 5MB.

---

## Lịch hoạt động của không gian

Quản lý lịch theo ngày trong tuần. **Không yêu cầu JWT**.

```
GET    /spaces/{id}/schedule                    Danh sách
POST   /spaces/{id}/schedule                    Thêm khung giờ
PUT    /spaces/{id}/schedule/{schedule_id}      Cập nhật
DELETE /spaces/{id}/schedule/{schedule_id}      Xóa
```

**Dữ liệu lịch**:
```json
{
  "day_of_week": 1,
  "start_time": "08:00",
  "end_time": "22:00",
  "is_available": true
}
```

`day_of_week`: 0=Chủ nhật, 1=Thứ 2, …, 7=Thứ 7.

---

## Đặt chỗ và hóa đơn

Đặt chỗ + tự động tạo hóa đơn. **25 endpoint yêu cầu JWT**.

### Danh sách và chi tiết (công khai)

```
GET    /v1/reservations/                    Danh sách
GET    /v1/reservations/{id}                Chi tiết
```

Bộ lọc: `user_id`, `provider_id`, `status`.

### Tạo đặt chỗ và hóa đơn (cần JWT)

```
POST   /v1/reservations/                    Tạo đặt chỗ + hóa đơn
```

**Request**:
```json
{
  "customer_name": "Nguyen Van A",
  "customer_email": "a@test.com",
  "customer_phone": "0909123456",
  "space_id": 1,
  "equipment_ids": [1, 2, 3],
  "start_time": "2026-09-10T09:00",
  "end_time": "2026-09-10T12:00",
  "provider_id": 1
}
```

**Response** (201):
```json
{
  "id": 1,
  "invoice_id": 1,
  "invoice_total": 450000,
  "breakdown": {
    "space": {
      "name": "Studio A",
      "price_per_hour": 150000,
      "hours": 2,
      "total": 300000
    },
    "equipment": [
      {"id": 1, "name": "Camera Canon", "price_per_hour": 50000, "total": 100000}
    ],
    "total": 450000
  }
}
```

**Luồng xử lý**:
1. Kiểm tra không gian tồn tại và trống lịch.
2. Tính giá: `space_price × hours + sum(equipment_price × hours)`.
3. Tạo Reservation (status = `pending`).
4. Tạo Customer trong Billing.
5. Tạo Invoice (status = `pending`) với các mục:
   - Mục 1: Thuê không gian
   - Mục 2…N: Thuê thiết bị

### Cập nhật và xóa (cần JWT)

```
PUT    /v1/reservations/{id}                Cập nhật
DELETE /v1/reservations/{id}                Xóa
```

### Chuyển trạng thái (cần JWT)

```
POST   /v1/reservations/{id}/approve        pending → approved
POST   /v1/reservations/{id}/confirm        approved → confirmed
POST   /v1/reservations/{id}/cancel         → cancelled
POST   /v1/reservations/{id}/checkin        → checked_in
POST   /v1/reservations/{id}/checkout       checked_in → checked_out
```

### Các mục trong đặt chỗ

```
GET    /v1/reservations/{id}/items          Danh sách (public)
POST   /v1/reservations/{id}/items          Thêm mục (public)
```

Loại mục: `space`, `resource`, `consumable`, `service`

```json
{
  "item_type": "resource",
  "item_id": 1,
  "quantity": 1,
  "price_at_booking": 100000
}
```

### Thanh toán

```
GET    /v1/reservations/{id}/payment        Xem (public)
POST   /v1/reservations/{id}/payment        Tạo (cần JWT)
POST   /v1/reservations/{id}/payment/confirm  Xác nhận (cần JWT)
```

Phương thức thanh toán: `vnpay`, `momo`, `cash`.

> Ghi chú: Thanh toán hiện là placeholder, QR code sẽ được bổ sung sau.

### Đánh giá

```
GET    /v1/reservations/{id}/reviews        Danh sách (public)
POST   /v1/reservations/{id}/reviews        Thêm (cần JWT)
```

**Request đánh giá**:
```json
{
  "user_id": 1,
  "space_id": 4,
  "rating": 5,
  "comment": "Phòng chụp rất tốt!"
}
```

---

## Thiết bị

Quản lý thiết bị nhiếp ảnh. **Không yêu cầu JWT**.

```
GET    /api/v1/equipment                    Danh sách
GET    /api/v1/equipment/{id}               Chi tiết
POST   /api/v1/equipment                    Tạo
PUT    /api/v1/equipment/{id}               Cập nhật
DELETE /api/v1/equipment/{id}               Xóa
```

Bộ lọc: `q`, `type`, `space_id`, `available`.

**Loại thiết bị**: `enlarger`, `camera`, `scanner`, `lighting`, `tripod`, `tank`, `other`

**Tình trạng**: `excellent`, `good`, `fair`, `poor`, `broken`

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

## Đặt gói dịch vụ

Đặt gói dịch vụ kèm kiểm tra xung đột tài nguyên. **Không yêu cầu JWT**.

```
GET    /api/v1/package-bookings                    Danh sách
GET    /api/v1/package-bookings/{id}               Chi tiết
POST   /api/v1/package-bookings                    Tạo
PATCH  /api/v1/package-bookings/{id}/cancel        Hủy
```

Bộ lọc: `package_id`, `customer_id`, `status`.

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
- Xung đột không gian (`find_conflicts`)
- Xung đột thiết bị (`find_equipment_conflicts`)
- Sử dụng advisory locks của PostgreSQL để tránh race condition.

---

## Hóa đơn và thanh toán (Billing)

Quản lý hóa đơn, khách hàng, sản phẩm, thanh toán. **11/19 endpoint yêu cầu JWT**.

### Hóa đơn

```
GET    /v1/billing/invoices              Danh sách (public)
GET    /v1/billing/invoices/{id}         Chi tiết (public)
POST   /v1/billing/invoices              Tạo (JWT)
PUT    /v1/billing/invoices/{id}         Cập nhật (JWT)
DELETE /v1/billing/invoices/{id}         Xóa (JWT)
```

Bộ lọc: `customer_id`, `status`.

### Mục hóa đơn

```
GET    /v1/billing/invoices/{id}/items   Danh sách (public)
POST   /v1/billing/invoices/{id}/items   Thêm (JWT)
```

### Thanh toán hóa đơn

```
GET    /v1/billing/invoices/{id}/payments  Danh sách (public)
POST   /v1/billing/invoices/{id}/payments  Thêm (JWT)
```

### Khách hàng

```
GET    /v1/billing/customers             Danh sách (public)
GET    /v1/billing/customers/{id}        Chi tiết (public)
POST   /v1/billing/customers             Tạo (JWT)
PUT    /v1/billing/customers/{id}        Cập nhật (JWT)
DELETE /v1/billing/customers/{id}        Xóa (JWT)
```

### Sản phẩm

```
GET    /v1/billing/products              Danh sách (public)
GET    /v1/billing/products/{id}         Chi tiết (public)
POST   /v1/billing/products              Tạo (JWT)
PUT    /v1/billing/products/{id}         Cập nhật (JWT)
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

Hệ thống sử dụng function calling với 4 công cụ:
1. `search_faq` – tìm kiếm trong FAQ.
2. `suggest_equipment` – gợi ý thiết bị.
3. `suggest_room` – gợi ý phòng.
4. `suggest_package` – gợi ý gói dịch vụ.

Fallback: Khi OpenAI không khả dụng, hệ thống trả lời từ FAQ và truy vấn cơ sở dữ liệu.

---

## Gợi ý thông minh

Gợi ý không gian dựa trên lịch sử đặt chỗ. **Không yêu cầu JWT**.

```
GET    /api/v1/recommendations/{user_id}
```

Thuật toán lọc nội dung:
- Phong cách nghệ thuật (35%)
- Loại không gian (25%)
- Khoảng giá (20%)
- Khoảng cách địa lý (20%, tính theo haversine)

Cold start: Trả về những không gian có rating/views cao nhất.

---

## Khóa học

Quản lý khóa học. **Không yêu cầu JWT**.

```
GET    /courses/                    Danh sách
GET    /courses/{id}               Chi tiết
POST   /courses/                   Tạo
PUT    /courses/{id}               Cập nhật
DELETE /courses/{id}               Xóa
```

Dữ liệu được lưu trong PostgreSQL.

---

## Tiện ích

```
GET    /                    Test GUI
GET    /swagger.json        OpenAPI spec
GET    /docs                Swagger UI
GET    /uploads/{filename}  File đã upload
OPTIONS /options            CORS preflight
```

---

## Phản hồi lỗi

```json
{
  "error": "Mô tả lỗi"
}
```

| Mã trạng thái | Ý nghĩa |
|---|---|
| 400 | Yêu cầu không hợp lệ |
| 401 | Không được phép (thiếu token / token hết hạn) |
| 404 | Không tìm thấy |
| 409 | Xung đột (trùng lịch) |
| 500 | Lỗi máy chủ nội bộ |
