# Photo Studio Capstone

Nền tảng kết nối cộng đồng nhiếp ảnh phim với dịch vụ phòng tối & phòng chụp.

**Film Photography Community & Creative Space Booking Platform**

---

## Quick Start

```bash
git clone https://github.com/hateyou2k7-cell/photo-studio-capstone.git
cd photo-studio-capstone/src

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env

python app.py
```

Mở `http://localhost:9999` để thấy GUI.

Tài khoản admin: `admin` / `admin123`

> **Database đã bao gồm.** Không cần cài PostgreSQL. Dữ liệu lưu trên Supabase cloud miễn phí.

---

## Trạng thái

| Luồng nghiệp vụ | Hoàn thành | Mô tả |
|:---|:---:|:---|
| Đăng ký / Đăng nhập | 80% | JWT auth, signup đồng bộ auth_users + users,role-based |
| Quản lý Không gian | 80% | CRUD, search, images, schedules |
| Quản lý Thiết bị | 50% | Equipment CRUD, thiếu consumables/resources |
| Đặt chỗ & Phân bổ | 70% | Reservation + conflict detection + payments |
| Phiên Sử dụng | 60% | Check-in/out, chưa QR code generation |
| Gói Dịch vụ | 50% | Package booking, thiếu Package CRUD API |
| Cộng đồng | 5% | Chỉ có DB model, chưa có API |
| AI Features | 25% | Chatbot + recommendation |
| Hóa đơn / Thanh toán | 60% | Billing CRUD, invoices, customers, products |

---

## Công nghệ

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

## Cài đặt

### Yêu cầu

- Python 3.8+
- pip

> **Không cần cài PostgreSQL.** Database đã bao gồm trên Supabase cloud miễn phí.

### Kiểm tra Python

```bash
python --version
# hoặc
python3 --version
```

### Bước 1: Clone repository

```bash
git clone https://github.com/hateyou2k7-cell/photo-studio-capstone.git
cd photo-studio-capstone
```

### Bước 2: Tạo môi trường ảo

**Windows:**

```bash
py -m venv .venv
```

**Unix/macOS:**

```bash
python3 -m venv .venv
```

### Bước 3: Kích hoạt môi trường ảo

**Windows (PowerShell):**

```bash
.venv\Scripts\activate.ps1
```

> Nếu gặp lỗi `Set-ExecutionPolicy`, chạy PowerShell với quyền Administrator:
> ```powershell
> Set-ExecutionPolicy RemoteSigned -Force
> ```

**Unix/macOS:**

```bash
source .venv/bin/activate
```

### Bước 4: Cài đặt dependencies

```bash
cd src
pip install -r requirements.txt
```

### Bước 5: Copy file cấu hình

```bash
cp .env.example .env
```

> File `.env.example` đã chứa sẵn database URL. Không cần chỉnh sửa gì thêm.

### Bước 6: Chạy ứng dụng

```bash
python app.py
```

### Truy cập

| URL | Mô tả |
|:---|:---|
| http://localhost:9999/ | Test GUI |
| http://localhost:9999/docs | Swagger UI |
| http://localhost:9999/swagger.json | OpenAPI spec |

---

## Cấu trúc dự án

```
photo-studio-capstone/
├── docs/
│   ├── api-documentation.md       # Chi tiết 75 API endpoints
│   ├── architecture.md             # Kiến trúc, data flow
│   ├── database-schema.md          # ERD, 44 bảng database
│   └── deployment-guide.md         # Hướng dẫn deploy
├── src/
│   ├── api/                        # API Layer
│   │   ├── controllers/            # 12 Flask Blueprint controllers
│   │   ├── schemas/                # Marshmallow validation schemas
│   │   ├── middleware.py           # Request/response middleware
│   │   ├── auth_middleware.py      # @jwt_required, @jwt_optional
│   │   ├── responses.py           # Standardized JSON responses
│   │   ├── pagination.py          # Pagination utility
│   │   └── swagger.py             # OpenAPI/Swagger setup
│   ├── business/                   # Business Logic Layer
│   │   ├── constants.py           # App constants
│   │   ├── exceptions.py          # Custom exceptions
│   │   └── models/                # Domain models + repository interfaces (ABC)
│   ├── services/                   # Service Layer (business logic)
│   ├── database/                   # Data Access Layer
│   │   ├── databases/             # PostgreSQL/MSSQL adapters (Factory pattern)
│   │   ├── repositories/          # Concrete repository implementations
│   │   └── models/                # SQLAlchemy ORM models (36 tables)
│   ├── tests/                      # Test suite
│   ├── uploads/                    # Uploaded files
│   ├── app.py                      # Entry point
│   ├── config.py                   # Configuration (Dev/Testing/Production)
│   └── requirements.txt            # Python dependencies
├── README.md
└── .gitignore
```

---

## Kiến trúc

```
HTTP Request
    │
    ▼
┌──────────────────────────────────────────┐
│  API Layer        (api/controllers/)     │
│  ↓ Validation    (api/schemas/)          │
│  ↓ Auth          (api/auth_middleware.py)│
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

Xem chi tiết tại [Architecture Documentation](docs/architecture.md).

---

## API Endpoints

Tổng: **75 endpoints** | JWT Protected: **22** | Public: **53**

| Module | Prefix | Endpoints | JWT |
|:---|:---|:---:|:---:|
| Auth | `/auth` | 3 | 0 |
| Rooms | `/rooms` | 5 | 0 |
| Spaces | `/spaces` | 6 | 0 |
| Space Images | `/spaces/{id}/images` | 4 | 0 |
| Space Schedules | `/spaces/{id}/schedule` | 4 | 0 |
| Reservations | `/v1/reservations` | 17 | 11 |
| Equipment | `/api/v1/equipment` | 5 | 0 |
| Package Bookings | `/api/v1/package-bookings` | 4 | 0 |
| Billing | `/v1/billing` | 19 | 11 |
| Chatbot | `/api/v1/chatbot` | 2 | 0 |
| Recommendations | `/api/v1/recommendations` | 1 | 0 |
| Courses | `/courses` | 5 | 0 |

Xem chi tiết tại [API Documentation](docs/api-documentation.md).

---

## Database

PostgreSQL (Supabase cloud miễn phí) với SQLAlchemy ORM. **44 bảng** trong đó 12 bảng đã có API.

> Database đã bao gồm. Không cần cài đặt hay cấu hình gì thêm.

Tài khoản có sẵn:
| Username | Password | Role | Ghi chú |
|:---|:---|:---|:---|
| admin | admin123 | admin | Quản trị viên |

> User đăng ký mới tự động có role `user` (quyền cơ bản).

Xem chi tiết tại [Database Schema](docs/database-schema.md).

---

## Testing

```bash
cd src
pytest
```

---

## Deploy

Xem hướng dẫn chi tiết tại [Deployment Guide](docs/deployment-guide.md).

- **Local**: `python app.py`
- **Render / Railway / Heroku**: Web service deploy

---

## License

MIT
