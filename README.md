# Photo Studio Capstone

**Nền tảng kết nối cộng đồng nhiếp ảnh phim – đặt phòng tối và phòng chụp.**

Đây là một ứng dụng đặt chỗ dành riêng cho giới nhiếp ảnh phim, nơi bạn có thể tìm kiếm, so sánh và đặt các không gian như darkroom, studio, cùng thiết bị chuyên dụng. Dự án được xây dựng theo kiến trúc sạch, chia tách rõ ràng các lớp, giúp dễ bảo trì và mở rộng.

---

## Bắt đầu nhanh

```bash
git clone https://github.com/hateyou2k7-cell/photo-studio-capstone.git
cd photo-studio-capstone/src

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env

python app.py
```

Sau đó mở `http://localhost:9999` trong trình duyệt.

Tài khoản admin mặc định: `admin` / `admin123`

> **Lưu ý:** Bạn không cần cài PostgreSQL. Dữ liệu được lưu trên Supabase cloud (miễn phí) – file `.env.example` đã có sẵn URL kết nối.

---

## Tình trạng hiện tại

| Luồng nghiệp vụ | Hoàn thành | Ghi chú |
|:---|:---:|:---|
| Đăng ký / Đăng nhập | 90% | Xác thực JWT qua bảng `users`, phân quyền cơ bản |
| Quản lý không gian | 90% | CRUD, tìm kiếm, 5 loại không gian, quyền admin/manager |
| Quản lý thiết bị | 70% | CRUD, liên kết với đặt chỗ |
| Đặt chỗ & Hóa đơn | 85% | Máy trạng thái, tự động xuất hóa đơn, chọn thiết bị |
| Phiên sử dụng | 60% | Check-in/out, chưa có QR code |
| Gói dịch vụ | 50% | Đặt gói, nhưng chưa có CRUD cho gói |
| Cộng đồng | 5% | Mới chỉ có model DB |
| AI | 25% | Chatbot + gợi ý thông minh |
| Hóa đơn / Thanh toán | 70% | Tự động tạo hóa đơn, thanh toán đang ở dạng placeholder |

---

## Công nghệ sử dụng

| Thành phần | Công nghệ |
|:---|:---|
| Backend | Flask (Python) |
| ORM | SQLAlchemy |
| Database | PostgreSQL (Supabase) |
| Validation | Marshmallow |
| Auth | JWT (PyJWT) |
| API Docs | Swagger UI (Flasgger) |
| AI | OpenAI GPT-4o-mini |

---

## Cài đặt chi tiết

### Yêu cầu

- Python 3.8 trở lên
- pip

### Kiểm tra Python

```bash
python --version
# hoặc
python3 --version
```

### 1. Clone dự án

```bash
git clone https://github.com/hateyou2k7-cell/photo-studio-capstone.git
cd photo-studio-capstone
```

### 2. Tạo môi trường ảo

**Windows:**
```bash
py -m venv .venv
```

**Unix/macOS:**
```bash
python3 -m venv .venv
```

### 3. Kích hoạt môi trường ảo

**Windows (PowerShell):**
```bash
.venv\Scripts\activate.ps1
```
Nếu gặp lỗi về ExecutionPolicy, hãy chạy PowerShell với quyền Administrator:
```powershell
Set-ExecutionPolicy RemoteSigned -Force
```

**Unix/macOS:**
```bash
source .venv/bin/activate
```

### 4. Cài dependencies

```bash
cd src
pip install -r requirements.txt
```

### 5. Tạo file cấu hình

```bash
cp .env.example .env
```

### 6. Chạy ứng dụng

```bash
python app.py
```

### Các địa chỉ truy cập

| URL | Mô tả |
|:---|:---|
| http://localhost:9999/ | Giao diện test (GUI) |
| http://localhost:9999/docs | Swagger UI |
| http://localhost:9999/swagger.json | OpenAPI spec |

---

## Cấu trúc dự án

```
photo-studio-capstone/
├── docs/
│   ├── api-documentation.md       # 75 API endpoints
│   ├── architecture.md             # Kiến trúc 4 lớp
│   ├── database-schema.md          # ERD, 44 bảng
│   └── deployment-guide.md         # Hướng dẫn deploy
├── src/
│   ├── api/                        # API Layer
│   │   ├── controllers/            # 12 Flask Blueprint controllers
│   │   ├── schemas/                # Marshmallow schemas
│   │   ├── middleware.py           # Request/response middleware
│   │   ├── auth_middleware.py      # @jwt_required, @jwt_optional
│   │   ├── responses.py            # JSON responses chuẩn
│   │   ├── pagination.py           # Pagination
│   │   └── swagger.py              # OpenAPI/Swagger
│   ├── business/                   # Business Logic Layer
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   └── models/                 # Domain models + repository interfaces (ABC)
│   ├── services/                   # Service Layer (business logic)
│   ├── database/                   # Data Access Layer
│   │   ├── databases/              # PostgreSQL/MSSQL adapters (Factory pattern)
│   │   ├── repositories/           # Repository implementations
│   │   └── models/                 # SQLAlchemy ORM models (36 tables)
│   ├── tests/                      # Test suite
│   ├── uploads/                    # Uploaded files
│   ├── app.py                      # Entry point
│   ├���─ config.py                   # Configuration
│   └── requirements.txt
├── README.md
└── .gitignore
```

---

## Kiến trúc chi tiết

Luồng xử lý từ HTTP request đến database:

```
HTTP Request
    │
    ▼
┌──────────────────────────────────────────┐
│  API Layer        (api/controllers/)     │
│  - Validation     (api/schemas/)         │
│  - Auth           (api/auth_middleware.py)│
└──────────────────┬───────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────┐
│  Service Layer   (services/)             │
│  Business logic, state machine           │
└──────────────────┬───────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────┐
│  Business Layer  (business/models/)      │
│  Domain models + Repository interfaces   │
└──────────────────┬───────────────────────┘
                   │ implements
                   ▼
┌──────────────────────────────────────────┐
│  Database Layer  (database/)             │
│  Repository impl + ORM models + DB       │
└──────────────────┬───────────────────────┘
                   │
                   ▼
              PostgreSQL
```

Tham khảo thêm tại [Architecture Documentation](docs/architecture.md).

---

## API Endpoints

**Tổng:** 65 endpoints | **JWT Protected:** 25 | **Public:** 40

| Module | Prefix | Số endpoint | JWT |
|:---|:---|:---:|:---:|
| Auth | `/auth` | 3 | 0 |
| Spaces | `/spaces` | 6 | 3 (admin/manager) |
| Space Images | `/spaces/{id}/images` | 4 | 0 |
| Space Schedules | `/spaces/{id}/schedule` | 4 | 0 |
| Reservations + Invoice | `/v1/reservations` | 17 | 11 |
| Equipment | `/api/v1/equipment` | 5 | 0 |
| Package Bookings | `/api/v1/package-bookings` | 4 | 0 |
| Billing | `/v1/billing` | 19 | 11 |
| Chatbot | `/api/v1/chatbot` | 2 | 0 |
| Recommendations | `/api/v1/recommendations` | 1 | 0 |
| Courses | `/courses` | 5 | 0 |

Xem chi tiết tại [API Documentation](docs/api-documentation.md).

---

## Database

PostgreSQL trên Supabase cloud, dùng SQLAlchemy ORM. Hiện có **44 bảng**, trong đó 28 bảng đã có API.

> Bạn không cần cài đặt hay cấu hình thêm – kết nối đã có sẵn qua file `.env`.

Tài khoản mặc định:
| Username | Password | Role | Ghi chú |
|:---|:---|:---|:---|
| admin | admin123 | admin | Quản trị viên |

User đăng ký mới sẽ có role `user` (quyền cơ bản).

Xem thêm tại [Database Schema](docs/database-schema.md).

---

## Chạy test

```bash
cd src
pytest
```

---

## Triển khai

Hướng dẫn chi tiết có trong [Deployment Guide](docs/deployment-guide.md).

- **Local:** `python app.py`
- **Render / Railway / Heroku:** Deploy web service thông thường.

---

## Giấy phép

MIT
