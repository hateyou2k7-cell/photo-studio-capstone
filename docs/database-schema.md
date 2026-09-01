# Database Schema Documentation

Photo Studio Capstone sử dụng **PostgreSQL** (Supabase) với **SQLAlchemy ORM**.

---

## Bảng tổng quan

| # | Table | File ORM | Trạng thái API |
|---|---|---|---|
| 1 | users | `film_user_model.py` | Có API (qua auth + reservation) |
| 2 | provider_profiles | `film_user_model.py` | **Chưa có API** |
| 3 | spaces | `film_space_model.py` | Có API |
| 4 | resources | `film_space_model.py` | **Chưa có API** |
| 5 | space_resources | `film_space_model.py` | **Chưa có API** |
| 6 | consumables | `film_space_model.py` | **Chưa có API** |
| 7 | space_images | `space_management_model.py` | Có API |
| 8 | space_schedules | `space_management_model.py` | Có API |
| 9 | equipments | `equipment_model.py` | Có API |
| 10 | service_packages | `film_package_model.py` | Có API (qua package bookings) |
| 11 | package_items | `film_package_model.py` | **Chưa có API** |
| 12 | package_equipments | `equipment_model.py` | Liên kết M:N |
| 13 | reservations | `film_reservation_model.py` | Có API |
| 14 | reservation_items | `film_reservation_model.py` | Có API |
| 15 | payments | `film_reservation_model.py` | Có API |
| 16 | service_sessions | `film_reservation_model.py` | Có API (qua checkin/checkout) |
| 17 | reviews | `film_reservation_model.py` | Có API |
| 18 | package_bookings | `package_booking_model.py` | Có API |
| 19 | posts | `film_community_model.py` | **Chưa có API** |
| 20 | comments | `film_community_model.py` | **Chưa có API** |
| 21 | workshops | `film_community_model.py` | **Chưa có API** |
| 22 | workshop_registrations | `film_community_model.py` | **Chưa có API** |
| 23 | conversations | `film_ai_model.py` | **Chưa có API** |
| 24 | messages | `film_ai_model.py` | **Chưa có API** |
| 25 | rooms | `room_model.py` | Có API (legacy) |
| 26 | todos | - | Legacy, đã xóa ORM model |
| 27 | auth_users | `auth_user_model.py` | Có API (login) |
| 28 | auth_roles | `auth_role_model.py` | **Chưa có API** |
| 29 | auth_functions | `auth_funtion_model.py` | **Chưa có API** |
| 30 | sell_customers | `sell_customer_model.py` | Có API (billing) |
| 31 | sell_products | `sell_product_model.py` | Có API (billing) |
| 32 | sell_invoices | `sell_invoice_model.py` | Có API (billing) |
| 33 | sell_invoice_items | `sell_invoice_model.py` | Có API (billing) |
| 34 | pay_trans | `pay_tran_model.py` | Có API (billing) |
| 35 | flask_user | `user_model.py` | Legacy, không dùng |
| 36 | consultants | `consultant_model.py` | Orphaned, không dùng |
| 37 | feedbacks | `feedback_model.py` | Orphaned, không dùng |
| 38 | appointments | `appointment_model.py` | Orphaned, không dùng |
| 39 | programs | `program_model.py` | Orphaned, không dùng |
| 40 | surveys | `survey_model.py` | Orphaned, không dùng |
| 41 | courses | `course_model.py` | Có API (PostgreSQL) |
| 42 | course_register | `course_register_model.py` | Orphaned, không dùng |

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

> **Lưu ý**: Khi đăng ký qua API, user mới được tạo với role `user` (quyền cơ bản). Role `admin` chỉ được gán trực tiếp trong database.

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
