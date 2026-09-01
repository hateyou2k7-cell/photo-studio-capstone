# Photo Studio Capstone - Documentation

Nền tảng kết nối cộng đồng nhiếp ảnh phim với dịch vụ phòng tối & phòng chụp.

---

## Tài liệu

| File | Mô tả |
|---|---|
| [API Documentation](api-documentation.md) | 75 endpoints, request/response, JWT auth |
| [Architecture](architecture.md) | Clean Architecture, 4 layers, data flow |
| [Database Schema](database-schema.md) | 35+ bảng, ORM models, relationships |
| [Deployment Guide](deployment-guide.md) | Local, Docker, Supabase, Render, Railway |

---

## Trạng thái dự án

| Luồng | % | Ghi chú |
|---|---|---|
| Quản lý Không gian | 80% | CRUD, images, schedules |
| Quản lý Thiết bị | 50% | Equipment CRUD, thiếu consumables/resources |
| Đặt chỗ | 70% | Reservation + conflict detection + payments |
| Phiên sử dụng | 60% | Check-in/out, chưa có QR code |
| Gói dịch vụ | 50% | Package booking, chưa có Package CRUD |
| Cộng đồng | 5% | Chỉ có DB model |
| AI | 25% | Chatbot + recommendation |
| Vai trò | 25% | JWT auth, chưa có role-based access |

**Tổng: ~35-40% hoàn thành**

---

## Cấu trúc src/

```
src/
├── api/                    # API Layer (12 controllers, 75 endpoints)
│   ├── controllers/
│   ├── schemas/            # Marshmallow validation
│   ├── middleware.py
│   ├── auth_middleware.py  # @jwt_required
│   ├── responses.py
│   ├── pagination.py
│   └── swagger.py
├── business/               # Business Logic Layer
│   ├── constants.py
│   ├── exceptions.py
│   └── models/
├── services/               # Service Layer (12 services)
├── database/               # Data Access Layer
│   ├── databases/          # PostgreSQL/MSSQL
│   ├── repositories/       # 10 repositories
│   └── models/             # 19 ORM models
├── tests/
├── uploads/
├── app.py                  # Entry point
├── config.py
└── requirements.txt
```

---

## Quick Start

```bash
cd src
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Configure .env with POSTGREE_DATABASE_URL
python app.py
# → http://localhost:9999/docs
```
