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

**Controllers hiện có** (13 files):

| Controller | File | Blueprint prefix |
|---|---|---|
| todo | `todo_controller.py` | `/todos` |
| auth | `auth_controller.py` | `/auth` |
| room | `room_controller.py` | `/rooms` |
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
| RoomRequest/Response | `schemas/room.py` | Room CRUD |
| SpaceRequest/Response | `schemas/space.py` | Space CRUD |
| SpaceImageResponse | `schemas/space_image.py` | Image metadata |
| SpaceScheduleRequest/Response | `schemas/space_schedule.py` | Schedule slots |
| ReservationRequest/Response | `schemas/reservation.py` | Reservation, items, payments, reviews |
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
| RoomService | `room_service.py` | CRUD rooms, name uniqueness |
| SpaceService | `space_service.py` | CRUD spaces, search, validate space_type |
| SpaceImageService | `space_image_service.py` | File upload, UUID naming, primary image logic |
| SpaceScheduleService | `space_schedule_service.py` | Schedule CRUD, time validation |
| ReservationService | `reservation_service.py` | State machine, overlap check, payments, reviews |
| EquipmentService | `equipment_service.py` | CRUD, type/condition validation |
| PackageBookingService | `package_booking_service.py` | Booking + resource conflict detection + advisory locks |
| BillingService | `billing_service.py` | Invoice/item/customer/product/payment CRUD |
| CourseService | `course_service.py` | CRUD courses |
| chatbot_service | `chatbot_service.py` | OpenAI integration, function calling, FAQ fallback |
| recommendation_service | `recommendation_service.py` | Content-based filtering, user profiling |

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
    ├── room.py            # RoomDomain
    ├── space.py           # SpaceDomain
    ├── space_image.py     # SpaceImageDomain
    ├── space_schedule.py  # SpaceScheduleDomain
    ├── reservation.py     # ReservationDomain, ReservationItemDomain, PaymentDomain, ServiceSessionDomain, ReviewDomain
    ├── equipment.py       # EquipmentDomain
    ├── billing.py         # InvoiceDomain, InvoiceItemDomain, CustomerDomain, ProductDomain, PayTransactionDomain
    ├── package_booking.py # PackageBookingDomain
    ├── course.py          # CourseDomain
    ├── itodo_repository.py
    ├── iauth_repository.py
    ├── iroom_repository.py
    ├── ispace_repository.py
    ├── ispace_image_repository.py
    ├── ispace_schedule_repository.py
    ├── ireservation_repository.py
    ├── ibilling_repository.py
    ├── iequipment_repository.py
    ├── ipackage_booking_repository.py
    └── icourse_repository.py
```

**Repository Interfaces** (ABC):

| Interface | Methods |
|---|---|
| ITodoRepository | add, get_by_id, list, update, delete |
| IAuthRepository | login, register, check_exist |
| IRoomRepository | add, get_by_id, find_by_name, list, update, delete |
| ISpaceRepository | add, get_by_id, list, search, update, delete |
| ISpaceImageRepository | add, get_by_id, list, update, delete, clear_primary |
| ISpaceScheduleRepository | add, get_by_id, list, update, delete |
| IReservationRepository | add, get_by_id, list, update, delete, update_status, add_item, list_items, add_payment, get_payment, check_in, check_out, add_review, list_reviews, check_overlap |
| IInvoiceRepository | add, get_by_id, list, update, delete, add_item, list_items, delete_item, add_customer, get_customer, list_customers, update_customer, delete_customer, add_product, get_product, list_products, update_product, delete_product, add_payment, list_payments |
| IEquipmentRepository | add, get_by_id, list, update, delete |
| IPackageBookingRepository | add, get_by_id, list, update, find_conflicts, find_equipment_conflicts |
| ICourseRepository | add, get_by_id, list, update, delete |

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
├── room_repository.py
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
├── room_model.py             # RoomModel (legacy)
├── todo_model.py             # TodoModel (legacy)
├── auth/
│   ├── auth_user_model.py    # AuthUserModel
│   ├── auth_role_model.py    # AuthRoleModel
│   └── auth_funtion_model.py # AuthFuntionModel
├── sell/
│   ├── sell_customer_model.py
│   ├── sell_product_model.py
│   └── sell_invoice_model.py
└── pay/
    └── pay_tran_model.py
```

---

## Data Flow Example

### Tạo Reservation

```
1. POST /v1/reservations/
   │
   ▼
2. reservation_controller.py:create_reservation()
   │  - Parse request JSON
   │  - Validate with ReservationRequestSchema
   │  - Check @jwt_required
   │
   ▼
3. reservation_service.py:create()
   │  - Check overlap: reservation_repo.check_overlap(space_id, start_time, end_time)
   │  - Create ReservationDomain object
   │
   ▼
4. reservation_repository.py:add()
   │  - Convert to Reservation ORM model
   │  - db_session.add(), db_session.commit()
   │
   ▼
5. PostgreSQL reservations table
   │
   ▼
6. Return JSON response
```

---

## Authentication Flow

```
1. POST /auth/login { username, password }
   │
   ▼
2. auth_service.py:login()
   │  - Query auth_users table
   │  - Verify password (bcrypt)
   │  - Generate JWT (HS256, SECRET_KEY)
   │
   ▼
3. Return { token, username }
   │
   ▼
4. Client adds header: Authorization: Bearer <token>
   │
   ▼
5. @jwt_required decorator
   │  - Extract token from header
   │  - jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
   │  - Set request.current_user_id
   │  - Return 401 if invalid/expired
   │
   ▼
6. Controller accesses request.current_user_id
```

**Lưu ý**: Hiện tại JWT chỉ check token valid, chưa check role-based access control.

---

## Known Issues

| Issue | Mô tả |
|---|---|
| Duplicate user systems | `auth_users` (login) và `users` (reservations) không liên kết |
| Duplicate space systems | `rooms` (RoomController) và `spaces` (SpaceController) riêng biệt |
| No role-based access | `jwt_required` chỉ check token, chưa check role |
| Empty files | `schemas/user.py`, `dependency_container.py`, `api/requests.py` |
| Legacy code | `todo_*`, `course_repository.py` (in-memory) |
| Swagger title | Vẫn ghi "Todo API" thay vì "Photo Studio API" |
| Unused models | `survey_model.py`, `consultant_model.py`, `program_model.py`, `appointment_model.py` |
