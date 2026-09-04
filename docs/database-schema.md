# Database Schema Documentation

Photo Studio Capstone sử dụng **PostgreSQL** (Supabase) với **SQLAlchemy ORM**.

**Database URL**: Supabase PostgreSQL (cloud)  
**Tổng tables**: 44 | **Tổng enums**: 11 | **Tổng FKs**: 50

---

## Bảng tổng quan

| # | Table | Columns | Rows | ORM Model | API |
|---|---|:---:|:---:|---|:---:|
| 1 | users | 10 | 11 | `film_user_model.py` | ✅ |
| 2 | provider_profiles | 7 | 1 | `film_user_model.py` | ✅ (internal) |
| 3 | spaces | 20 | 4 | `film_space_model.py` | ✅ |
| 4 | resources | 10 | 0 | `film_space_model.py` | ❌ |
| 5 | space_resources | 4 | 0 | `film_space_model.py` | ❌ |
| 6 | consumables | 8 | 0 | `film_space_model.py` | ❌ |
| 7 | space_images | 6 | 0 | `space_management_model.py` | ✅ |
| 8 | space_schedules | 8 | 0 | `space_management_model.py` | ✅ |
| 9 | equipments | 13 | 3 | `equipment_model.py` | ✅ |
| 10 | service_packages | 9 | 0 | `film_package_model.py` | ❌ |
| 11 | package_items | 5 | 0 | `film_package_model.py` | ❌ |
| 12 | package_equipments | 2 | 0 | `equipment_model.py` | ❌ |
| 13 | reservations | 12 | 2 | `film_reservation_model.py` | ✅ |
| 14 | reservation_items | 6 | 1 | `film_reservation_model.py` | ✅ |
| 15 | payments | 8 | 1 | `film_reservation_model.py` | ✅ |
| 16 | service_sessions | 6 | 1 | `film_reservation_model.py` | ✅ |
| 17 | reviews | 7 | 1 | `film_reservation_model.py` | ✅ |
| 18 | package_bookings | 10 | 0 | `package_booking_model.py` | ✅ |
| 19 | posts | 9 | 0 | `film_community_model.py` | ❌ |
| 20 | comments | 5 | 0 | `film_community_model.py` | ❌ |
| 21 | workshops | 9 | 0 | `film_community_model.py` | ❌ |
| 22 | workshop_registrations | 5 | 0 | `film_community_model.py` | ❌ |
| 23 | conversations | 4 | 0 | `film_ai_model.py` | ❌ |
| 24 | messages | 5 | 0 | `film_ai_model.py` | ❌ |
| 25 | rooms | 9 | 3 | `room_model.py` | ✅ (legacy) |
| 26 | todos | 6 | 0 | - | ❌ (legacy) |
| 27 | auth_users | 6 | 11 | `auth_user_model.py` | ✅ |
| 28 | auth_roles | 3 | 0 | `auth_role_model.py` | ❌ |
| 29 | auth_functions | 6 | 0 | `auth_funtion_model.py` | ❌ |
| 30 | auth_user_roles | 3 | 0 | `auth_role_model.py` | ❌ |
| 31 | auth_role_functions | 3 | 0 | `auth_role_model.py` | ❌ |
| 32 | sell_customers | 7 | 14 | `sell_customer_model.py` | ✅ |
| 33 | sell_products | 6 | 15 | `sell_product_model.py` | ✅ |
| 34 | sell_invoices | 10 | 12 | `sell_invoice_model.py` | ✅ |
| 35 | sell_invoice_items | 8 | 10 | `sell_invoice_model.py` | ✅ |
| 36 | pay_trans | 5 | 3 | `pay_tran_model.py` | ✅ |
| 37 | flask_user | 7 | 0 | `user_model.py` | ❌ (legacy) |
| 38 | consultants | 8 | 0 | `consultant_model.py` | ❌ |
| 39 | feedbacks | 7 | 0 | `feedback_model.py` | ❌ |
| 40 | appointments | 10 | 0 | `appointment_model.py` | ❌ |
| 41 | programs | 6 | 0 | `program_model.py` | ❌ |
| 42 | surveys | 6 | 0 | `survey_model.py` | ❌ |
| 43 | courses | 8 | 10 | `course_model.py` | ✅ |
| 44 | course_register | 3 | 0 | `course_register_model.py` | ❌ |

---

## Enums (11 types)

| Enum | Values |
|---|---|
| `user_role` | photographer, provider, expert, admin, **user** |
| `provider_status` | pending, approved, rejected |
| `space_type` | darkroom, studio |
| `equipment_type` | enlarger, camera, scanner, lighting, tripod, tank, other |
| `equipment_condition` | excellent, good, fair, poor, broken |
| `resource_category` | camera, lens, enlarger, scanner, lighting, tripod, background, darkroom_equipment |
| `item_type` | space, resource, consumable |
| `reservation_status` | pending, approved, confirmed, checked_in, checked_out, completed, cancelled |
| `payment_method` | vnpay, momo, cash |
| `payment_status` | pending, success, failed, refunded |
| `session_status` | in_progress, completed |
| `post_category` | article, tutorial, equipment_review, technique |
| `workshop_status` | open, full, cancelled, done |
| `booking_status` | pending, confirmed, cancelled, completed |

---

## Foreign Keys (50 relationships)

### Core Business Flow
```
users ──(1:N)──> reservations ──(1:N)──> reservation_items
    │                 │
    │                 ├──(1:N)──> payments
    │                 ├──(1:N)──> service_sessions
    │                 └──(1:N)──> reviews
    │
    └──(1:1)──> provider_profiles ──(1:N)──> spaces ──(1:N)──> space_images
                        │                       │
                        │                       └──(1:N)──> space_schedules
                        │
                        ├──(1:N)──> equipments
                        ├──(1:N)──> resources ──(M:N)──> space_resources
                        ├──(1:N)──> consumables
                        └──(1:N)──> service_packages ──(1:N)──> package_items
                                                    │
                                                    └──(M:N)──> package_equipments
```

### Community
```
users ──(1:N)──> posts ──(1:N)──> comments
users ──(1:N)──> workshops ──(1:N)──> workshop_registrations
users ──(1:N)──> conversations ──(1:N)──> messages
```

### Auth
```
auth_users ──(M:N)──> auth_roles ──(M:N)──> auth_functions
```

### Billing
```
sell_customers ──(1:N)──> sell_invoices ──(1:N)──> sell_invoice_items
                                        └──(1:N)──> pay_trans
sell_products ──(1:N)──> sell_invoice_items
```

### Legacy
```
flask_user ──(1:N)──> course_register ──(N:1)──> courses
flask_user ──(1:N)──> appointments ──(N:1)──> consultants
flask_user ──(1:N)──> feedbacks ──(N:1)──> courses
```

---

## Bảng chi tiết (chỉ các bảng liên quan đến đề tài)

### 1. users

Bảng người dùng chính.

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    avatar_url VARCHAR(500),
    role VARCHAR(50) NOT NULL DEFAULT 'photographer',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Enums**: `role` = `user` | `photographer` | `provider` | `expert` | `admin`

> **Lưu ý**: Khi đăng ký qua API, user có thể chọn role (`user`, `photographer`, `provider`, `expert`). Role `admin` bị từ chối khi signup. Nếu role=provider, tự tạo `provider_profiles` record (status=pending).

---

### 2. provider_profiles

Hồ sơ nhà cung cấp (1:1 với users).

```sql
CREATE TABLE provider_profiles (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) NOT NULL,
    business_name VARCHAR(255) NOT NULL,
    description TEXT,
    address VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Enums**: `status` = `pending` | `approved` | `rejected`

---

### 3. spaces

Không gian nhiếp ảnh.

```sql
CREATE TABLE spaces (
    id BIGSERIAL PRIMARY KEY,
    provider_id BIGINT REFERENCES provider_profiles(id) NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    address VARCHAR(255),
    latitude NUMERIC(10,7),
    longitude NUMERIC(10,7),
    max_capacity INTEGER,
    dimensions VARCHAR(100),
    art_style VARCHAR(100),
    lighting VARCHAR(100),
    ventilation VARCHAR(100),
    acoustics VARCHAR(100),
    amenities TEXT,
    operating_hours VARCHAR(100),
    base_price_per_hour NUMERIC(12,2) NOT NULL DEFAULT 0,
    status BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Enums**: `type` = `darkroom` | `studio`

**Relationships**:
- `provider_id` → provider_profiles.id
- 1:N → space_images, space_schedules, equipments
- M:N → resources (qua space_resources)

---

### 4. resources

Thiết bị cho thuê (chưa có API).

```sql
CREATE TABLE resources (
    id BIGSERIAL PRIMARY KEY,
    provider_id BIGINT REFERENCES provider_profiles(id) NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    condition VARCHAR(20) DEFAULT 'good',
    rental_price_per_hour NUMERIC(12,2) NOT NULL DEFAULT 0,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Enums**: `category` = `camera` | `lens` | `enlarger` | `scanner` | `lighting` | `tripod` | `background` | `darkroom_equipment`

---

### 5. space_resources

Liên kết N:N spaces ↔ resources.

```sql
CREATE TABLE space_resources (
    id BIGSERIAL PRIMARY KEY,
    space_id BIGINT REFERENCES spaces(id) ON DELETE CASCADE NOT NULL,
    resource_id BIGINT REFERENCES resources(id) ON DELETE CASCADE NOT NULL,
    quantity INTEGER DEFAULT 1
);
```

---

### 6. consumables

Vật tư tiêu hao (chưa có API).

```sql
CREATE TABLE consumables (
    id BIGSERIAL PRIMARY KEY,
    provider_id BIGINT REFERENCES provider_profiles(id) NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50) DEFAULT 'chemical',
    unit VARCHAR(20),
    quantity_in_stock INTEGER DEFAULT 0,
    unit_price NUMERIC(12,2) NOT NULL DEFAULT 0,
    is_available BOOLEAN DEFAULT TRUE
);
```

---

### 7. space_images

Hình ảnh không gian.

```sql
CREATE TABLE space_images (
    id BIGSERIAL PRIMARY KEY,
    space_id BIGINT REFERENCES spaces(id) ON DELETE CASCADE NOT NULL,
    url VARCHAR(500) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### 8. space_schedules

Lịch hoạt động theo ngày.

```sql
CREATE TABLE space_schedules (
    id BIGSERIAL PRIMARY KEY,
    space_id BIGINT REFERENCES spaces(id) ON DELETE CASCADE NOT NULL,
    day_of_week INTEGER NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

`day_of_week`: 0=Chủ nhật, 1=Thứ 2, ..., 7=Thứ 7

---

### 9. equipments

Thiết bị nhiếp ảnh.

```sql
CREATE TABLE equipments (
    id BIGSERIAL PRIMARY KEY,
    provider_id BIGINT REFERENCES provider_profiles(id) NOT NULL,
    space_id BIGINT REFERENCES spaces(id),
    name VARCHAR(255) NOT NULL,
    model_name VARCHAR(255),
    type VARCHAR(50) NOT NULL,
    compatibility VARCHAR(255),
    condition VARCHAR(50),
    description TEXT,
    price_per_hour NUMERIC,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Indexes**: `ix_equipment_space_id`, `ix_equipment_provider_id`

**Enums**: `type` = `enlarger` | `camera` | `scanner` | `lighting` | `tripod` | `tank` | `other`

---

### 10. service_packages

Gói dịch vụ.

```sql
CREATE TABLE service_packages (
    id BIGSERIAL PRIMARY KEY,
    provider_id BIGINT REFERENCES provider_profiles(id) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price NUMERIC(12,2) NOT NULL DEFAULT 0,
    duration_minutes INTEGER DEFAULT 60,
    status BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

### 11. package_items

Chi tiết gói dịch vụ (chưa có API).

```sql
CREATE TABLE package_items (
    id BIGSERIAL PRIMARY KEY,
    package_id BIGINT REFERENCES service_packages(id) ON DELETE CASCADE NOT NULL,
    item_type VARCHAR(50) NOT NULL,
    item_id BIGINT NOT NULL,
    quantity INTEGER DEFAULT 1
);
```

---

### 12. package_equipments

Liên kết N:N service_packages ↔ equipments.

```sql
CREATE TABLE package_equipments (
    package_id BIGINT REFERENCES service_packages(id) ON DELETE CASCADE,
    equipment_id BIGINT REFERENCES equipments(id) ON DELETE CASCADE,
    PRIMARY KEY (package_id, equipment_id)
);
```

---

### 13. reservations

Đặt chỗ.

```sql
CREATE TABLE reservations (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) NOT NULL,
    provider_id BIGINT REFERENCES provider_profiles(id) NOT NULL,
    space_id BIGINT REFERENCES spaces(id),
    package_id BIGINT REFERENCES service_packages(id),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    total_price NUMERIC(12,2) NOT NULL DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending',
    qr_code VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Status flow**: `pending` → `approved` → `confirmed` → `checked_in` → `checked_out` → `completed` | `cancelled`

---

### 14. reservation_items

Chi tiết mục trong đặt chỗ.

```sql
CREATE TABLE reservation_items (
    id BIGSERIAL PRIMARY KEY,
    reservation_id BIGINT REFERENCES reservations(id) ON DELETE CASCADE NOT NULL,
    item_type VARCHAR(50) NOT NULL,
    item_id BIGINT NOT NULL,
    quantity INTEGER DEFAULT 1,
    price_at_booking NUMERIC(12,2) NOT NULL DEFAULT 0
);
```

---

### 15. payments

Thanh toán đặt chỗ.

```sql
CREATE TABLE payments (
    id BIGSERIAL PRIMARY KEY,
    reservation_id BIGINT REFERENCES reservations(id) NOT NULL,
    user_id BIGINT REFERENCES users(id) NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    method VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    transaction_ref VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Enums**: `method` = `vnpay` | `momo` | `cash`
**Enums**: `status` = `pending` | `success` | `failed` | `refunded`

---

### 16. service_sessions

Phiên sử dụng (check-in/out).

```sql
CREATE TABLE service_sessions (
    id BIGSERIAL PRIMARY KEY,
    reservation_id BIGINT REFERENCES reservations(id) NOT NULL UNIQUE,
    checked_in_at TIMESTAMPTZ,
    checked_out_at TIMESTAMPTZ,
    actual_duration_minutes INTEGER,
    status VARCHAR(50) DEFAULT 'in_progress'
);
```

---

### 17. reviews

Đánh giá.

```sql
CREATE TABLE reviews (
    id BIGSERIAL PRIMARY KEY,
    reservation_id BIGINT REFERENCES reservations(id),
    user_id BIGINT REFERENCES users(id) NOT NULL,
    space_id BIGINT REFERENCES spaces(id),
    rating INTEGER NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### 18. package_bookings

Đặt gói dịch vụ.

```sql
CREATE TABLE package_bookings (
    id BIGSERIAL PRIMARY KEY,
    package_id BIGINT REFERENCES service_packages(id) NOT NULL,
    space_id BIGINT REFERENCES spaces(id) NOT NULL,
    customer_id BIGINT REFERENCES users(id) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    status VARCHAR(50),
    total_price BIGINT DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Indexes**: `ix_pkg_booking_package_time`, `ix_pkg_booking_space_time`, `ix_pkg_booking_customer`

---

### 19-22. Community Tables (chưa có API)

```sql
CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    author_id BIGINT REFERENCES users(id) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50) NOT NULL DEFAULT 'article',
    is_published BOOLEAN DEFAULT TRUE,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE comments (
    id BIGSERIAL PRIMARY KEY,
    post_id BIGINT REFERENCES posts(id) ON DELETE CASCADE NOT NULL,
    user_id BIGINT REFERENCES users(id) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE workshops (
    id BIGSERIAL PRIMARY KEY,
    expert_id BIGINT REFERENCES users(id) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    scheduled_at TIMESTAMP NOT NULL,
    location VARCHAR(255),
    capacity INTEGER NOT NULL DEFAULT 10,
    price INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'open'
);

CREATE TABLE workshop_registrations (
    id BIGSERIAL PRIMARY KEY,
    workshop_id BIGINT REFERENCES workshops(id) ON DELETE CASCADE NOT NULL,
    user_id BIGINT REFERENCES users(id) NOT NULL,
    status VARCHAR(20) DEFAULT 'registered',
    registered_at TIMESTAMP DEFAULT NOW()
);
```

---

### 23-24. AI Tables (chưa có API)

```sql
CREATE TABLE conversations (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) NOT NULL,
    started_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    conversation_id BIGINT REFERENCES conversations(id) ON DELETE CASCADE NOT NULL,
    sender_type VARCHAR(10) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### 25. rooms (Legacy)

```sql
CREATE TABLE rooms (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    room_type VARCHAR(50) NOT NULL,
    capacity INTEGER NOT NULL,
    price_per_hour NUMERIC NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Enums**: `room_type` = `standard` | `vip` | `studio` | `conference`

---

### 26. auth_users

```sql
CREATE TABLE auth_users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Mối quan hệ chính

```
users 1──1 provider_profiles 1──N spaces
                               1──N resources
                               1──N consumables
                               1──N service_packages
                               1──N equipments

spaces N──N resources (qua space_resources)
spaces 1──N space_images
spaces 1──N space_schedules
spaces 1──N equipments
spaces 1──N reservations
spaces 1──N reviews

reservations 1──N reservation_items
reservations 1──1 payments
reservations 1──1 service_sessions
reservations 1──N reviews

service_packages 1──N package_items
service_packages N──N equipments (qua package_equipments)

users 1──N reservations
users 1──N posts
users 1──N comments
users 1──N workshop_registrations
users 1──N conversations

posts 1──N comments
workshops 1──N workshop_registrations
conversations 1──N messages
```
