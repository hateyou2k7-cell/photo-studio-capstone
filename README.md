# Photo Studio Capstone

Nền tảng kết nối cộng đồng nhiếp ảnh phim với dịch vụ phòng tối & phòng chụp.

**Film Photography Community & Creative Space Booking Platform**

---

## Quick Start

### Linux / macOS

```bash
git clone https://github.com/hateyou2k7-cell/photo-studio-capstone.git
cd photo-studio-capstone/src

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env

python3 app.py
```

### Windows (PowerShell)

```powershell
git clone https://github.com/hateyou2k7-cell/photo-studio-capstone.git
cd photo-studio-capstone\src

py -m venv .venv
.venv\Scripts\activate.ps1

pip install -r requirements.txt
Copy-Item .env.example .env

python app.py
```

> Nếu gặp lỗi `Set-ExecutionPolicy`, chạy PowerShell với quyền Administrator:
> ```powershell
> Set-ExecutionPolicy RemoteSigned -Force
> ```

Mở `http://localhost:9999` để thấy GUI.

Tài khoản admin: `admin` / `admin123`

---

## Trạng thái

| Luồng nghiệp vụ | Hoàn thành | Mô tả |
|:---|:---:|:---|
| Đăng ký / Đăng nhập | 80% | JWT auth, signup đồng bộ auth_users + users, role-based |
| Quản lý Không gian | 80% | CRUD, search, images, schedules |
| Quản lý Thiết bị | 50% | Equipment CRUD, thiếu consumables/resources |
| Đặt chỗ & Phân bổ | 70% | Reservation + conflict detection + payments |
| Phiên Sử dụng | 60% | Check-in/out, chưa QR code generation |
| Gói Dịch vụ | 50% | Package booking, thiếu Package CRUD API |
| Cộng đồng | 85% | Posts, Comments, Workshops, Registrations — CRUD hoàn chỉnh |
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
- PostgreSQL (hoặc dùng Supabase cloud)
- pip

### Kiểm tra Python

```bash
python --version
# hoặc
python3 --version
```

### Bước 1: Clone repository

```bash
git clone <repository-url>
cd photo-studio-capstone
```

### Bước 2: Tạo môi trường ảo

**Windows:**

```powershell
py -m venv .venv
```

**Linux / macOS:**

```bash
python3 -m venv .venv
```

### Bước 3: Kích hoạt môi trường ảo

**Windows (PowerShell):**

```powershell
.venv\Scripts\activate.ps1
```

> Nếu gặp lỗi `Set-ExecutionPolicy`, chạy PowerShell với quyền Administrator:
> ```powershell
> Set-ExecutionPolicy RemoteSigned -Force
> ```

**Windows (CMD):**

```cmd
.venv\Scripts\activate.bat
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

### Bước 4: Cài đặt dependencies

```bash
cd src
pip install -r requirements.txt
```

### Bước 5: Cấu hình môi trường

Tạo file `.env` trong thư mục `src/`:

**Linux / macOS:**

```bash
cp .env.example .env
```

**Windows (PowerShell):**

```powershell
Copy-Item .env.example .env
```

**Windows (CMD):**

```cmd
copy .env.example .env
```

Nội dung `.env`:

```env
# Flask
FLASK_ENV=development
SECRET_KEY=your_secret_key_here

# PostgreSQL (Supabase)
POSTGREE_DATABASE_URL="postgresql+psycopg2://postgres.xxx:password@aws-0-ap-south-1.pooler.supabase.com:5432/postgres"
```

> **Lưu ý:** File `.env` phải nằm trong thư mục `src/`, không phải thư mục gốc project.

### Bước 6: Chạy ứng dụng

**Linux / macOS:**

```bash
python3 app.py
```

**Windows:**

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

## Docker (tùy chọn)

### Pull PostgreSQL image

```bash
docker pull postgres:16-alpine
```

### Chạy PostgreSQL container

**Linux / macOS:**

```bash
docker run -e POSTGRES_DB=photo_studio \
           -e POSTGRES_USER=postgres \
           -e POSTGRES_PASSWORD=your_password \
           -p 5432:5432 \
           --name photo-studio-db \
           -d postgres:16-alpine
```

**Windows (PowerShell):**

```powershell
docker run -e POSTGRES_DB=photo_studio `
           -e POSTGRES_USER=postgres `
           -e POSTGRES_PASSWORD=your_password `
           -p 5432:5432 `
           --name photo-studio-db `
           -d postgres:16-alpine
```

### Cập nhật .env

```env
POSTGREE_DATABASE_URL="postgresql+psycopg2://postgres:your_password@localhost:5432/photo_studio"
```

---

## Cấu trúc dự án

```
photo-studio-capstone/
├── docs/
│   ├── api-documentation.md       # Chi tiết 91 API endpoints
│   ├── architecture.md             # Kiến trúc, data flow
│   ├── database-schema.md          # ERD, 44 bảng database
│   └── deployment-guide.md         # Hướng dẫn deploy
├── src/
│   ├── api/                        # API Layer
│   │   ├── controllers/            # 14 Flask Blueprint controllers
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
│   │   └── models/                # SQLAlchemy ORM models (44 tables)
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

Tổng: **91 endpoints** | JWT Protected: **38** | Public: **53**

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
| Community | `/api/v1/community` | 16 | 8 |

Xem chi tiết tại [API Documentation](docs/api-documentation.md).

---

## Database

PostgreSQL với SQLAlchemy ORM. **44 bảng** trong đó 13 bảng đã có API.

Tài khoản có sẵn:
| Username | Password | Role | Ghi chú |
|:---|:---|:---|:---|
| admin | admin123 | admin | Quản trị viên |

> User đăng ký mới tự động có role `user` (quyền cơ bản).

Xem chi tiết tại [Database Schema](docs/database-schema.md).

---

## Testing

**Linux / macOS:**

```bash
cd src
python3 -m pytest
```

**Windows:**

```bash
cd src
python -m pytest
```

---

## Deploy

Xem hướng dẫn chi tiết tại [Deployment Guide](docs/deployment-guide.md).

- **Local**: `python app.py`
- **Docker**: `docker-compose up -d --build`
- **Supabase**: Cloud PostgreSQL
- **Render / Railway / Heroku**: Web service deploy

---

## Troubleshooting

### Lỗi `DATABASE_URI is None` trên Windows

Nguyên nhân: File `.env` không được load đúng.

Giải pháp:
1. Kiểm tra file `.env` nằm trong thư mục `src/`
2. Kiểm tra nội dung `.env` đúng format (có dấu `"` bao quanh URL)
3. Kiểm tra variable name đúng là `POSTGREE_DATABASE_URL` (không phải `DATABASE_URL`)

### Lỗi `Set-ExecutionPolicy` trên Windows

```powershell
# Chạy PowerShell với quyền Administrator
Set-ExecutionPolicy RemoteSigned -Force
```

### Lỗi `psycopg2` not found

```bash
pip install psycopg2-binary
```

### Port 9999 đang được sử dụng

**Linux / macOS:**

```bash
lsof -i :9999
kill -9 <PID>
```

**Windows:**

```cmd
netstat -ano | findstr :9999
taskkill /PID <PID> /F
```

---

## License

MIT
