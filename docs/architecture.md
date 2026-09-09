# Architecture Documentation

Photo Studio Capstone sử dụng **Clean Architecture** với Flask.

---

## Kiến trúc tổng quan

```
HTTP Request
    │
    ▼
┌─────────────────────────────────────────────┐
│  API Layer (api/)                           │
│  - Controllers (Flask Blueprints)           │
│  - Schemas (Marshmallow validation)         │
│  - Middleware (JWT, logging, CORS)          │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  Service Layer (services/)                  │
│  - Business logic                           │
│  - Validation rules                         │
│  - State transitions                        │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  Business Layer (business/)                 │
│  - Domain models (dataclasses)              │
│  - Repository interfaces (ABC)              │
│  - Exceptions                               │
└──────────────────┬──────────────────────────┘
                   │ implements
                   ▼
┌─────────────────────────────────────────────┐
│  Database Layer (database/)                 │
│  - Repository implementations               │
│  - ORM models (SQLAlchemy)                  │
│  - Database adapters (PostgreSQL/MSSQL)     │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
              PostgreSQL
```

---

## Các Layer chi tiết

### 1. API Layer

**Files**: `api/controllers/`, `api/schemas/`, `api/middleware.py`, `api/auth_middleware.py`

**Trách nhiệm**:
- Route definitions (Flask Blueprints)
- Request parsing
- Input validation (Marshmallow)
- Response formatting
- JWT authentication

**Controllers hiện có** (12 files):

| Controller | File | Blueprint prefix |
|---|---|---|
| todo | `todo_controller.py` | `/todos` |
| auth | `auth_controller.py` | `/auth` |
| space | `space_controller.py` | `/spaces` |
| space_image | `space_image_controller.py` | `/spaces/{id}/images` |
| space_schedule | `space_schedule_controller.py` | `/spaces/{id}/schedule` |
| reservation | `reservation_controller.py` | `/v1/reservations` |
| equipment | `equipment_controller.py` | `/api/v1/equipment` |
| package_booking | `package_booking_controller.py` | `/api/v1/package-bookings` |
| billing | `billing_controller.py` | `/v1/billing` |
| chatbot | `chatbot_controller.py` | `/api/v1/chatbot` |
| recommendation | `recommendation_controller.py` | `/api/v1/recommendations` |
| course | `course_controller.py` | `/courses` |

> **Lưu ý**: `room_controller.py` đã bị deprecated. Dùng `space_controller.py` thay thế.

**Middleware**:
- `middleware.py`: Request logging, error handling, CORS headers
- `auth_middleware.py`: `@jwt_required`, `@jwt_optional` (decorators)
- `responses.py`: Standardized JSON response helpers
- `pagination.py`: Pagination utility

**Schemas** (marshmallow):

| Schema | File | Validates |
|---|---|---|
| TodoRequest/Response | `schemas/todo.py` | Todo CRUD |
| Auth (Login/Register) | `schemas/auth.py` | Username, password, email |
| SpaceRequest/Response | `schemas/space.py` | Space CRUD |
| SpaceImageResponse | `schemas/space_image.py` | Image metadata |
| SpaceScheduleRequest/Response | `schemas/space_schedule.py` | Schedule slots |
| ReservationRequest/Response | `schemas/reservation.py` | Reservation + customer info + equipment_ids, items, payments, reviews |
| EquipmentRequest/Response | `schemas/equipment.py` | Equipment, PackageBooking |
| Billing (Invoice/Customer/Product) | `schemas/billing.py` | Billing CRUD |
| User | `schemas/user.py` | **EMPTY** |

---

### 2. Service Layer

**Files**: `services/`

| Service | File | Trách nhiệm |
|---|---|---|
| TodoService | `todo_service.py` | CRUD todos (legacy) |
| AuthService | `auth_service.py` | Login, register, JWT generation |
| SpaceService | `space_service.py` | CRUD spaces, search, validate space_type (5 types) |
| SpaceImageService | `space_image_service.py` | File upload, UUID naming, primary image logic |
| SpaceScheduleService | `space_schedule_service.py` | Schedule CRUD, time validation |
| ReservationService | `reservation_service.py` | State machine, overlap check, payments, reviews |
| EquipmentService | `equipment_service.py` | CRUD, type/condition validation |
| PackageBookingService | `package_booking_service.py` | Booking + resource conflict detection + advisory locks |
| BillingService | `billing_service.py` | Invoice/item/customer/product/payment CRUD |
| CourseService | `course_service.py` | CRUD courses |
| chatbot_service | `chatbot_service.py` | OpenAI integration, function calling, FAQ fallback |
| recommendation_service | `recommendation_service.py` | Content-based filtering, user profiling |

> **Lưu ý**: `RoomService` đã bị deprecated. Dùng `SpaceService` thay thế.

**Reservation State Machine**:
```
pending → approved → confirmed → checked_in → checked_out → completed
    └────────────────┴────────────────┴────────────────┘
                  cancelled
```

**Key patterns**:
- Overlap detection: `ReservationRepository.check_overlap(space_id, start_time, end_time)`
- Resource locking: `PackageBookingService` uses PostgreSQL advisory locks (`pg_advisory_xact_lock`)
- Auto-recalculate: `BillingService` recalculates invoice totals on item/payment changes

---

### 3. Business Layer

**Files**: `business/`

```
business/
├── constants.py           # API_VERSION, PAGE_SIZE
├── exceptions.py          # NotFoundError, ValidationError, ConflictError, UnauthorizedError
└── models/
    ├── todo.py            # TodoDomain
    ├── auth.py            # AuthDomain
    ├── user.py            # UserDomain
    ├── space.py           # SpaceDomain (5 types: darkroom, studio, standard, vip, conference)
    ├── space_image.py     # SpaceImageDomain
    ├── space_schedule.py  # SpaceScheduleDomain
    ├── reservation.py     # ReservationDomain, ReservationItemDomain, PaymentDomain, ServiceSessionDomain, ReviewDomain
    ├── equipment.py       # EquipmentDomain
    ├── billing.py         # InvoiceDomain, InvoiceItemDomain, CustomerDomain, ProductDomain, PayTransactionDomain
    ├── package_booking.py # PackageBookingDomain
    ├── course.py          # CourseDomain
    ├── itodo_repository.py
    ├── iauth_repository.py
    ├── ispace_repository.py
    ├── ispace_image_repository.py
    ├── ispace_schedule_repository.py
    ├── ireservation_repository.py
    ├── ibilling_repository.py
    ├── iequipment_repository.py
    ├── ipackage_booking_repository.py
    └── icourse_repository.py
```

> **Lưu ý**: `room.py`, `iroom_repository.py` đã bị deprecated.

**Repository Interfaces** (ABC):

| Interface | Methods |
|---|---|
| ITodoRepository | add, get_by_id, list, update, delete |
| IAuthRepository | login, register, check_exist |
| ISpaceRepository | add, get_by_id, list, search, update, delete |
| ISpaceImageRepository | add, get_by_id, list, update, delete, clear_primary |
| ISpaceScheduleRepository | add, get_by_id, list, update, delete |
| IReservationRepository | add, get_by_id, list, update, delete, update_status, add_item, list_items, add_payment, get_payment, check_in, check_out, add_review, list_reviews, check_overlap |
| IInvoiceRepository | add, get_by_id, list, update, delete, add_item, list_items, delete_item, add_customer, get_customer, list_customers, update_customer, delete_customer, add_product, get_product, list_products, update_product, delete_product, add_payment, list_payments |
| IEquipmentRepository | add, get_by_id, list, update, delete |
| IPackageBookingRepository | add, get_by_id, list, update, find_conflicts, find_equipment_conflicts |
| ICourseRepository | add, get_by_id, list, update, delete |

> **Lưu ý**: `IRoomRepository` đã bị deprecated.

---

### 4. Database Layer

**Files**: `database/`

#### Databases

```
database/databases/
├── __init__.py              # init_db() - creates all tables
├── base.py                  # SQLAlchemy declarative_base
├── abstract_database.py     # AbstractDatabase ABC
├── factory_database.py      # FactoryDatabase (MSSQL/POSTGREE)
├── database_postgres.py     # PostgreSQL implementation
├── database_mssql.py        # MSSQL implementation (legacy)
└── postgres.py              # Engine/session setup
```

**Factory Pattern**:
```python
# factory_database.py
class FactoryDatabase:
    @staticmethod
    def get_database(db_type: str):
        if db_type == 'POSTGREE':
            return DatabasePostgres()
        elif db_type == 'MSSQL':
            return DatabaseMSSQL()
```

#### Repositories

```
database/repositories/
├── todo_repository.py
├── auth_repository.py
├── space_repository.py
├── space_image_repository.py
├── space_schedule_repository.py
├── reservation_repository.py
├── equipment_repository.py
├── billing_repository.py
├── package_booking_repository.py
├── course_repository.py      # In-memory (chưa dùng DB)
└── user_repository.py        # Skeleton
```

> **Lưu ý**: `room_repository.py` đã bị deprecated.

#### ORM Models

```
database/models/
├── film_user_model.py        # User, ProviderProfile
├── film_space_model.py       # Space, Resource, SpaceResource, Consumable
├── film_package_model.py     # ServicePackage, PackageItem
├── film_reservation_model.py # Reservation, ReservationItem, Payment, ServiceSession, Review
├── film_community_model.py   # Post, Comment, Workshop, WorkshopRegistration
├── film_ai_model.py          # Conversation, Message
├── space_management_model.py # SpaceImage, SpaceSchedule
├── equipment_model.py        # Equipment, package_equipments
├── package_booking_model.py  # PackageBooking
├── todo_model.py             # TodoModel (legacy)
├── auth/
│   ├── auth_role_model.py    # AuthRoleModel
│   └── auth_funtion_model.py # AuthFuntionModel
├── sell/
│   ├── sell_customer_model.py
│   ├── sell_product_model.py
│   └── sell_invoice_model.py
└── pay/
    └── pay_tran_model.py
```

> **Lưu ý**: `room_model.py`, `auth_user_model.py` đã bị deprecated. User giờ dùng `film_user_model.py`.

---

## Data Flow Example

### Tạo Reservation + Invoice

```
1. POST /v1/reservations/
   { customer_name, customer_email, customer_phone,
     space_id, equipment_ids: [1,2,3],
     start_time, end_time }
   │
   ▼
2. reservation_controller.py:create_reservation()
   │  - Parse request JSON
   │  - Validate with ReservationRequestSchema
   │  - Check @jwt_required
   │  - Get space info for pricing
   │
   ▼
3. Tính giá
   │  - space_cost = space.base_price_per_hour × hours
   │  - equipment_cost = sum(eq.price_per_hour × hours)
   │  - total = space_cost + equipment_cost
   │
   ▼
4. Tạo Reservation (status=pending)
   │  - reservation_service.create()
   │  - reservation_service.add_item() cho space + equipment
   │
   ▼
5. Tạo Invoice trong Billing
   │  - billing_service.create_customer()
   │  - billing_service.create_invoice()
   │  - billing_service.add_item() cho space rental
   │  - billing_service.add_item() cho equipment rental
   │
   ▼
6. Return response với breakdown chi tiết
```

---

## Authentication Flow

```
1. POST /auth/login { username, password }
   │
   ▼
2. auth_service.py:login()
   │  - Query users table (by username)
   │  - Verify password (bcrypt)
   │  - Generate JWT (HS256, SECRET_KEY)
   │
   ▼
3. Return { token, user_id }
   │
   ▼
4. Client adds header: Authorization: Bearer <token>
   │
   ▼
5. @jwt_required decorator
   │  - Extract token from header
   │  - jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
   │  - Set request.current_user_id, request.current_user_role
   │  - Return 401 if invalid/expired
   │
   ▼
6. Controller accesses request.current_user_id
```

**Lưu ý**: JWT chứa `user_id` và `role` trong payload. Admin role bypass tất cả JWT validation.
Bảng `auth_users` đã bị deprecated, mọi logic dùng `users` table.

---

## Known Issues

| Issue | Mô tả | Trạng thái |
|---|---|---|
| ~~Duplicate user systems~~ | `auth_users` + `users` không liên kết | ✅ Đã gộp vào `users` |
| ~~Duplicate space systems~~ | `rooms` + `spaces` riêng biệt | ✅ Đã gộp vào `spaces` |
| ~~Swagger title~~ | Ghi "Todo API" | ✅ Đã sửa "Photo Studio API" |
| Admin bypass | Admin role có unconditional access – cần sửa RBAC | ⚠️ Còn tồn tại |
| Empty files | `schemas/user.py`, `dependency_container.py` | ⚠️ Còn tồn tại |
| Legacy code | `todo_*`, `course_repository.py` (in-memory) | ⚠️ Còn tồn tại |
| Unused models | `survey_model.py`, `consultant_model.py`... | ⚠️ Còn tồn tại |
