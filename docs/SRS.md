# Software Requirements Specification (SRS)

## Platform Connecting the Film Photography Community with Darkroom and Studio Services

**Phiên bản**: 1.0  
**Ngày**: 01/09/2026  
**Trạng thái**: Draft

---

## 1. Introduction

### 1.1 Purpose

Tài liệu này mô tả các yêu cầu chức năng và phi chức năng cho nền tảng kết nối cộng đồng nhiếp ảnh phim với các dịch vụ phòng tối và phòng chụp.

### 1.2 Scope

Hệ thống là multi-sided platform kết nối:
- **Photographer (Customer)**: Tìm kiếm, so sánh, đặt chỗ không gian nhiếp ảnh
- **Service Provider**: Quản lý không gian, thiết bị, dịch vụ
- **Photography Expert**: Chia sẻ kiến thức, tổ chức workshop
- **Administrator**: Quản lý nền tảng

### 1.3 Definitions

| Term | Definition |
|:---|:---|
| Darkroom | Phòng tối dùng để rửa phim |
| Studio | Phòng chụp ảnh |
| Space | Không gian nhiếp ảnh (darkroom hoặc studio) |
| Resource | Thiết bị, consumable, dịch vụ |
| Service Package | Gói dịch vụ kết hợp space + equipment + consumable |
| Reservation | Đặt chỗ không gian |
| Service Session | Phiên sử dụng thực tế (check-in → checkout) |

---

## 2. Overall Description

### 2.1 Product Perspective

```
┌─────────────────────────────────────────────────────┐
│                   PLATFORM                           │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ Mobile   │  │ Web      │  │ Admin Dashboard  │  │
│  │ (Flutter)│  │ (React)  │  │ (React)          │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────────────┘  │
│       │              │              │                │
│       └──────────────┼──────────────┘                │
│                      │                               │
│              ┌───────▼────────┐                      │
│              │  Backend API   │                      │
│              │  (Flask)       │                      │
│              └───────┬────────┘                      │
│                      │                               │
│       ┌──────────────┼──────────────┐                │
│       │              │              │                │
│  ┌────▼─────┐  ┌─────▼────┐  ┌─────▼─────┐         │
│  │PostgreSQL│  │ OpenAI   │  │ Storage   │         │
│  │(Supabase)│  │ API      │  │ (Azure)   │         │
│  └──────────┘  └──────────┘  └───────────┘         │
└─────────────────────────────────────────────────────┘
```

### 2.2 User Classes

| Role | Description | Priority |
|:---|:---|:---|
| Photographer | Người dùng đặt chỗ không gian | High |
| Service Provider | Chủ không gian, thiết bị | High |
| Photography Expert | Chuyên gia chia sẻ kiến thức | Medium |
| Administrator | Quản trị hệ thống | Medium |
| AI Assistant | Trợ lý AI thông minh | Low |

### 2.3 Operating Environment

- Backend: Python 3.12, Flask
- Database: PostgreSQL 15+ (Supabase)
- ORM: SQLAlchemy
- Auth: JWT (PyJWT)
- AI: OpenAI API (GPT-4)
- Deployment: Cloud (Render/Railway/Azure)

---

## 3. Functional Requirements

### 3.1 Authentication & Authorization (FR-AUTH)

| ID | Requirement | Priority | Status |
|:---|:---|:---|:---|
| FR-AUTH-01 | Đăng ký tài khoản mới | High | ✅ |
| FR-AUTH-02 | Đăng nhập với JWT token | High | ✅ |
| FR-AUTH-03 | Token hết hạn sau 2 giờ | High | ✅ |
| FR-AUTH-04 | Role-based access control | High | ❌ |
| FR-AUTH-05 | Đổi mật khẩu | Medium | ❌ |
| FR-AUTH-06 | Quên mật khẩu (email reset) | Low | ❌ |
| FR-AUTH-07 | Xác thực email | Low | ❌ |

### 3.2 Creative Space Management (FR-SPACE)

| ID | Requirement | Priority | Status |
|:---|:---|:---|:---|
| FR-SPACE-01 | Tạo không gian mới (darkroom/studio) | High | ✅ |
| FR-SPACE-02 | Cập nhật thông tin không gian | High | ✅ |
| FR-SPACE-03 | Xóa không gian | High | ✅ |
| FR-SPACE-04 | Tìm kiếm với filters (type, price, capacity) | High | ✅ |
| FR-SPACE-05 | Upload ảnh không gian | High | ✅ |
| FR-SPACE-06 | Quản lý lịch hoạt động theo ngày | High | ✅ |
| FR-SPACE-07 | Đặt làm ảnh chính (primary) | Medium | ✅ |
| FR-SPACE-08 | Thông tin chi tiết (art_style, lighting, ventilation) | Medium | ⚠️ |
| FR-SPACE-09 | Google Maps integration | Low | ❌ |

### 3.3 Resource & Equipment Management (FR-EQUIP)

| ID | Requirement | Priority | Status |
|:---|:---|:---|:---|
| FR-EQUIP-01 | Tạo thiết bị mới | High | ✅ |
| FR-EQUIP-02 | Cập nhật thông tin thiết bị | High | ✅ |
| FR-EQUIP-03 | Xóa thiết bị | High | ✅ |
| FR-EQUIP-04 | Theo dõi tình trạng (excellent/good/fair/poor) | High | ✅ |
| FR-EQUIP-05 | Quản lý consumable (hóa chất, giấy ảnh) | High | ❌ |
| FR-EQUIP-06 | Lên lịch bảo trì thiết bị | Medium | ❌ |
| FR-EQUIP-07 | Theo dõi vòng đời thiết bị | Medium | ❌ |

### 3.4 Reservation & Resource Allocation (FR-RES)

| ID | Requirement | Priority | Status |
|:---|:---|:---|:---|
| FR-RES-01 | Tạo đặt chỗ mới | High | ✅ |
| FR-RES-02 | Kiểm tra conflict detection | High | ✅ |
| FR-RES-03 | Duyệt đặt chỗ (Provider) | High | ✅ |
| FR-RES-04 | Xác nhận đặt chỗ (Customer) | High | ✅ |
| FR-RES-05 | Check-in / Checkout | High | ✅ |
| FR-RES-06 | Hủy đặt chỗ | High | ✅ |
| FR-RES-07 | Thêm items (equipment, consumable) | High | ✅ |
| FR-RES-08 | Thanh toán (payment) | High | ✅ |
| FR-RES-09 | Đánh giá (reviews) | Medium | ✅ |
| FR-RES-10 | QR Code check-in | Medium | ❌ |
| FR-RES-11 | Resource locking khi confirm | High | ✅ |
| FR-RES-12 | Concurrent reservation safety | High | ✅ |

### 3.5 Service Session Management (FR-SESSION)

| ID | Requirement | Priority | Status |
|:---|:---|:---|:---|
| FR-SESSION-01 | Ghi nhận thời gian check-in | High | ✅ |
| FR-SESSION-02 | Ghi nhận thời gian checkout | High | ✅ |
| FR-SESSION-03 | Tính thời gian sử dụng thực tế | High | ✅ |
| FR-SESSION-04 | Theo dõi equipment đã dùng | Medium | ❌ |
| FR-SESSION-05 | QR Code scan khi check-in | Medium | ❌ |

### 3.6 Service Package Management (FR-PKG)

| ID | Requirement | Priority | Status |
|:---|:---|:---|:---|
| FR-PKG-01 | Tạo service package | High | ❌ |
| FR-PKG-02 | Cập nhật service package | High | ❌ |
| FR-PKG-03 | Xóa service package | High | ❌ |
| FR-PKG-04 | Đặt service package | High | ✅ |
| FR-PKG-05 | Validate resource availability trước khi đặt | High | ✅ |
| FR-PKG-06 | Kết hợp space + equipment + consumable | Medium | ❌ |
| FR-PKG-07 | Pricing policy cho packages | Medium | ❌ |

### 3.7 Billing & Payment (FR-BILL)

| ID | Requirement | Priority | Status |
|:---|:---|:---|:---|
| FR-BILL-01 | Tạo invoice | High | ✅ |
| FR-BILL-02 | Thêm items vào invoice | High | ✅ |
| FR-BILL-03 | Auto-recalculate invoice total | High | ✅ |
| FR-BILL-04 | Tạo payment | High | ✅ |
| FR-BILL-05 | Xác nhận payment | High | ✅ |
| FR-BILL-06 | Quản lý customers | High | ✅ |
| FR-BILL-07 | Quản lý products | High | ✅ |
| FR-BILL-08 | VNPay integration | Medium | ❌ |
| FR-BILL-09 | MoMo integration | Medium | ❌ |
| FR-BILL-10 | Stripe integration | Low | ❌ |

### 3.8 Community (FR-COMM)

| ID | Requirement | Priority | Status |
|:---|:---|:---|:---|
| FR-COMM-01 | Đăng bài viết (posts) | High | ❌ |
| FR-COMM-02 | Bình luận (comments) | High | ❌ |
| FR-COMM-03 | Đăng ký workshop | High | ❌ |
| FR-COMM-04 | Chat messaging | Medium | ❌ |
| FR-COMM-05 | Feedback/Đánh giá dịch vụ | Medium | ❌ |
| FR-COMM-06 | Chia sẻ kiến thức | Medium | ❌ |

### 3.9 AI Features (FR-AI)

| ID | Requirement | Priority | Status |
|:---|:---|:---|:---|
| FR-AI-01 | Chatbot hỗ trợ nhiếp ảnh | Medium | ✅ |
| FR-AI-02 | Recommendation system | Medium | ✅ |
| FR-AI-03 | Image restoration | Low | ❌ |
| FR-AI-04 | Demand forecasting | Low | ❌ |
| FR-AI-05 | Dynamic pricing | Low | ❌ |
| FR-AI-06 | Semantic search | Low | ❌ |

### 3.10 Administration (FR-ADMIN)

| ID | Requirement | Priority | Status |
|:---|:---|:---|:---|
| FR-ADMIN-01 | Quản lý users | High | ❌ |
| FR-ADMIN-02 | Duyệt provider registrations | High | ❌ |
| FR-ADMIN-03 | Quản lý categories | Medium | ❌ |
| FR-ADMIN-04 | Monitor transactions | Medium | ❌ |
| FR-ADMIN-05 | System reports | Medium | ❌ |
| FR-ADMIN-06 | Manage AI services | Low | ❌ |

---

## 4. Non-Functional Requirements

### 4.1 Performance (NFR-PERF)

| ID | Requirement | Target | Status |
|:---|:---|:---|:---|
| NFR-PERF-01 | Average response time | < 3 seconds | ✅ |
| NFR-PERF-02 | Concurrent users support | 100+ | ⚠️ |
| NFR-PERF-03 | Database query optimization | Indexed queries | ✅ |

### 4.2 Security (NFR-SEC)

| ID | Requirement | Target | Status |
|:---|:---|:---|:---|
| NFR-SEC-01 | JWT authentication | HS256, 2h expiry | ✅ |
| NFR-SEC-02 | Password hashing | scrypt (Werkzeug) | ✅ |
| NFR-SEC-03 | HTTPS enforcement | TLS 1.2+ | ⚠️ |
| NFR-SEC-04 | Input validation | Marshmallow schemas | ✅ |
| NFR-SEC-05 | SQL injection prevention | SQLAlchemy ORM | ✅ |
| NFR-SEC-06 | CORS configuration | Configurable origins | ✅ |

### 4.3 Reliability (NFR-REL)

| ID | Requirement | Target | Status |
|:---|:---|:---|:---|
| NFR-REL-01 | Transaction safety | ACID compliance | ✅ |
| NFR-REL-02 | Concurrent reservation safety | Advisory locks | ✅ |
| NFR-REL-03 | Error handling | Graceful degradation | ✅ |
| NFR-REL-04 | Database backup | Daily automated | ⚠️ |

### 4.4 Scalability (NFR-SCALE)

| ID | Requirement | Target | Status |
|:---|:---|:---|:---|
| NFR-SCALE-01 | Horizontal scaling | Stateless backend | ✅ |
| NFR-SCALE-02 | Database scaling | Connection pooling | ⚠️ |
| NFR-SCALE-03 | Modular architecture | Clean Architecture | ✅ |

### 4.5 Maintainability (NFR-MAINT)

| ID | Requirement | Target | Status |
|:---|:---|:---|:---|
| NFR-MAINT-01 | Code modularity | 4-layer architecture | ✅ |
| NFR-MAINT-02 | API documentation | Swagger/OpenAPI | ✅ |
| NFR-MAINT-03 | Test coverage | 89% (48/54 tests) | ✅ |
| NFR-MAINT-04 | Code style | PEP 8 compliance | ✅ |

---

## 5. System Features Summary

### 5.1 Implemented Features

| Module | Endpoints | DB Tables | Status |
|:---|:---:|:---:|:---|
| Auth (Signup/Login) | 3 | auth_users, users | ✅ |
| Rooms Management | 5 | rooms | ✅ |
| Spaces Management | 6 | spaces | ✅ |
| Space Images | 4 | space_images | ✅ |
| Space Schedules | 4 | space_schedules | ✅ |
| Equipment Management | 5 | equipments | ✅ |
| Reservations | 17 | reservations, reservation_items, payments, service_sessions, reviews | ✅ |
| Package Bookings | 4 | package_bookings | ✅ |
| Billing (Invoices) | 19 | sell_customers, sell_products, sell_invoices, sell_invoice_items, pay_trans | ✅ |
| Courses | 5 | courses | ✅ |
| Chatbot (AI) | 2 | conversations, messages | ✅ |
| Recommendations (AI) | 1 | - | ✅ |
| **Total** | **75** | **28 tables** | |

### 5.2 Pending Features

| Module | Priority | Estimated Effort |
|:---|:---|:---|
| Service Package CRUD | High | 2-3 days |
| Community (Posts/Comments) | High | 3-4 days |
| Workshop Registration | High | 2-3 days |
| Role-based Access Control | High | 2-3 days |
| QR Code Generation | Medium | 1-2 days |
| Consumable Management | Medium | 2-3 days |
| Provider Dashboard | Medium | 3-4 days |
| Admin Panel | Medium | 3-4 days |
| Image Upload/Storage | Medium | 1-2 days |
| Payment Integration | Medium | 3-5 days |

---

## 6. Database Design

### 6.1 Entity Relationship Summary

**Total tables**: 44  
**Tables with ORM model**: 36  
**Tables with API**: 28  
**Legacy tables (no ORM)**: 8 (appointments, consultants, course_register, feedbacks, flask_user, programs, surveys, todos)  
**Total enums**: 11  
**Total foreign keys**: 50

### 6.2 Key Relationships

```
users (1) ──── (N) reservations ── (1:N) reservation_items
    │                  │
    │                  ├── (1:N) payments
    │                  ├── (1:N) service_sessions
    │                  └── (1:N) reviews
    │
    ├── (1:1) provider_profiles ── (1:N) spaces ── (1:N) space_images
    │              │                       │
    │              │                       └── (1:N) space_schedules
    │              │
    │              ├── (1:N) equipments
    │              ├── (1:N) resources ── (M:N via space_resources) spaces
    │              ├── (1:N) consumables
    │              └── (1:N) service_packages ── (1:N) package_items
    │                                           └── (M:N via package_equipments) equipments
    │
    ├── (1:N) posts ── (1:N) comments
    ├── (1:N) workshops ── (1:N) workshop_registrations
    ├── (1:N) conversations ── (1:N) messages
    └── (1:N) package_bookings

sell_customers (1) ──── (N) sell_invoices ── (1:N) sell_invoice_items
                                            └── (1:N) pay_trans
sell_products (1) ──── (N) sell_invoice_items

auth_users (M:N via auth_user_roles) auth_roles (M:N via auth_role_functions) auth_functions
```

### 6.3 Database Enums

| Enum | Values | Used By |
|---|---|---|
| `user_role` | photographer, provider, expert, admin, **user** | users.role |
| `provider_status` | pending, approved, rejected | provider_profiles.status |
| `space_type` | darkroom, studio | spaces.type |
| `equipment_type` | enlarger, camera, scanner, lighting, tripod, tank, other | equipments.type |
| `equipment_condition` | excellent, good, fair, poor, broken | equipments.condition |
| `resource_category` | camera, lens, enlarger, scanner, lighting, tripod, background, darkroom_equipment | resources.category |
| `item_type` | space, resource, consumable | reservation_items.item_type, package_items.item_type |
| `reservation_status` | pending, approved, confirmed, checked_in, checked_out, completed, cancelled | reservations.status |
| `payment_method` | vnpay, momo, cash | payments.method |
| `payment_status` | pending, success, failed, refunded | payments.status |
| `session_status` | in_progress, completed | service_sessions.status |
| `post_category` | article, tutorial, equipment_review, technique | posts.category |
| `workshop_status` | open, full, cancelled, done | workshops.status |
| `booking_status` | pending, confirmed, cancelled, completed | package_bookings.status |

---

## 7. API Design

### 7.1 Base URL

```
http://localhost:9999
```

### 7.2 Authentication

```http
Authorization: Bearer <jwt_token>
```

### 7.3 Response Format

**Success**:
```json
{
  "field1": "value1",
  "field2": "value2"
}
```

**Error**:
```json
{
  "message": "Error description",
  "error": "error_code"
}
```

### 7.4 Status Codes

| Code | Meaning |
|:---|:---|
| 200 | Success |
| 201 | Created |
| 204 | No Content (Deleted) |
| 400 | Bad Request (Validation error) |
| 401 | Unauthorized (Invalid/missing token) |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## 8. Glossary

| Term | Definition |
|:---|:---|
| JWT | JSON Web Token - phương thức xác thực |
| ORM | Object-Relational Mapping |
| CRUD | Create, Read, Update, Delete |
| ACID | Atomicity, Consistency, Isolation, Durability |
| Clean Architecture | Kiến trúc tách biệt layers |
| Repository Pattern | Pattern abstract data access |
| State Machine | Máy trạng thái cho reservation |
| Conflict Detection | Kiểm tra trùng lịch |
| Advisory Lock | PostgreSQL locking mechanism |

---

## 9. Appendices

### 9.1 Technology Stack

| Component | Technology |
|:---|:---|
| Backend | Flask (Python 3.12) |
| Database | PostgreSQL 15+ (Supabase) |
| ORM | SQLAlchemy |
| Auth | JWT (PyJWT) |
| Validation | Marshmallow |
| AI | OpenAI API (GPT-4) |
| API Docs | Swagger/Flasgger |
| Testing | pytest |
| Version Control | Git/GitHub |

### 9.2 Project Structure

```
src/
├── api/
│   ├── controllers/     # 12 Flask Blueprints
│   ├── schemas/         # 9 Marshmallow schemas
│   ├── middleware.py     # JWT, logging, CORS
│   ├── responses.py     # Standardized responses
│   └── swagger.py       # OpenAPI setup
├── services/            # 12 Business services
├── business/
│   ├── models/          # 21 Domain models + 11 repository interfaces
│   └── constants.py     # App constants
├── database/
│   ├── databases/       # DB connection factory (PostgreSQL/MSSQL)
│   ├── models/          # 36 ORM models (maps 36 DB tables)
│   └── repositories/    # 10 Repository implementations
├── app.py               # Flask app factory + inline GUI
├── config.py            # Configuration
├── test_all.py          # Full test suite (75 endpoints)
└── requirements.txt     # 15 dependencies
```

---

**End of SRS Document**
