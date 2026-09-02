-- =====================================================
-- Photo Studio Capstone - Database Schema
-- PostgreSQL (Supabase)
-- =====================================================
-- WARNING: This schema is for reference only.
-- Run on empty DB or use Supabase Dashboard.

-- =====================================================
-- 1. ENUMS
-- =====================================================

CREATE TYPE user_role AS ENUM ('photographer', 'provider', 'expert', 'admin', 'user');
CREATE TYPE provider_status AS ENUM ('pending', 'approved', 'rejected');
CREATE TYPE space_type AS ENUM ('darkroom', 'studio');
CREATE TYPE equipment_type AS ENUM ('enlarger', 'camera', 'scanner', 'lighting', 'tripod', 'tank', 'other');
CREATE TYPE equipment_condition AS ENUM ('excellent', 'good', 'fair', 'poor', 'broken');
CREATE TYPE resource_category AS ENUM ('camera', 'lens', 'enlarger', 'scanner', 'lighting', 'tripod', 'background', 'darkroom_equipment');
CREATE TYPE item_type AS ENUM ('space', 'resource', 'consumable');
CREATE TYPE reservation_status AS ENUM ('pending', 'approved', 'confirmed', 'checked_in', 'checked_out', 'completed', 'cancelled');
CREATE TYPE payment_method AS ENUM ('vnpay', 'momo', 'cash');
CREATE TYPE payment_status AS ENUM ('pending', 'success', 'failed', 'refunded');
CREATE TYPE session_status AS ENUM ('in_progress', 'completed');
CREATE TYPE post_category AS ENUM ('article', 'tutorial', 'equipment_review', 'technique');
CREATE TYPE workshop_status AS ENUM ('open', 'full', 'cancelled', 'done');
CREATE TYPE booking_status AS ENUM ('pending', 'confirmed', 'cancelled', 'completed');

-- =====================================================
-- 2. TABLES (ordered by FK dependencies)
-- =====================================================

-- ========== AUTH ==========

CREATE TABLE public.auth_users (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR NOT NULL UNIQUE,
    email VARCHAR NOT NULL UNIQUE,
    password_hash VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE public.users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email VARCHAR NOT NULL UNIQUE,
    password_hash VARCHAR NOT NULL,
    full_name VARCHAR NOT NULL,
    phone VARCHAR,
    avatar_url VARCHAR,
    role user_role NOT NULL DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE public.auth_roles (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    description VARCHAR
);

CREATE TABLE public.auth_functions (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    url VARCHAR NOT NULL UNIQUE,
    description VARCHAR,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE public.auth_user_roles (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES public.auth_users(id),
    role_id INTEGER NOT NULL REFERENCES public.auth_roles(id)
);

CREATE TABLE public.auth_role_functions (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    role_id INTEGER NOT NULL REFERENCES public.auth_roles(id),
    function_id INTEGER NOT NULL REFERENCES public.auth_functions(id)
);

-- ========== PROVIDER ==========

CREATE TABLE public.provider_profiles (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE REFERENCES public.users(id),
    business_name VARCHAR NOT NULL,
    description TEXT,
    address VARCHAR,
    status provider_status DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========== SPACES ==========

CREATE TABLE public.spaces (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    provider_id BIGINT NOT NULL REFERENCES public.provider_profiles(id),
    name VARCHAR NOT NULL,
    type space_type NOT NULL,
    description TEXT,
    address VARCHAR,
    latitude NUMERIC,
    longitude NUMERIC,
    max_capacity INTEGER,
    dimensions VARCHAR,
    art_style VARCHAR,
    lighting VARCHAR,
    ventilation VARCHAR,
    acoustics VARCHAR,
    amenities TEXT,
    operating_hours VARCHAR,
    base_price_per_hour NUMERIC NOT NULL DEFAULT 0,
    status BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE public.space_images (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    space_id BIGINT NOT NULL REFERENCES public.spaces(id),
    url VARCHAR NOT NULL,
    is_primary BOOLEAN,
    sort_order INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE public.space_schedules (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    space_id BIGINT NOT NULL REFERENCES public.spaces(id),
    day_of_week INTEGER NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ========== RESOURCES ==========

CREATE TABLE public.resources (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    provider_id BIGINT NOT NULL REFERENCES public.provider_profiles(id),
    name VARCHAR NOT NULL,
    category resource_category NOT NULL,
    description TEXT,
    condition VARCHAR DEFAULT 'good',
    rental_price_per_hour NUMERIC NOT NULL DEFAULT 0,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE public.space_resources (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    space_id BIGINT NOT NULL REFERENCES public.spaces(id),
    resource_id BIGINT NOT NULL REFERENCES public.resources(id),
    quantity INTEGER DEFAULT 1
);

CREATE TABLE public.consumables (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    provider_id BIGINT NOT NULL REFERENCES public.provider_profiles(id),
    name VARCHAR NOT NULL,
    category VARCHAR DEFAULT 'chemical',
    unit VARCHAR,
    quantity_in_stock INTEGER DEFAULT 0,
    unit_price NUMERIC NOT NULL DEFAULT 0,
    is_available BOOLEAN DEFAULT TRUE
);

-- ========== EQUIPMENT ==========

CREATE TABLE public.equipments (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    provider_id BIGINT NOT NULL REFERENCES public.provider_profiles(id),
    space_id BIGINT REFERENCES public.spaces(id),
    name VARCHAR NOT NULL,
    model_name VARCHAR,
    type equipment_type NOT NULL,
    compatibility VARCHAR,
    condition equipment_condition,
    description TEXT,
    price_per_hour NUMERIC,
    is_available BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ========== SERVICE PACKAGES ==========

CREATE TABLE public.service_packages (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    provider_id BIGINT NOT NULL REFERENCES public.provider_profiles(id),
    name VARCHAR NOT NULL,
    description TEXT,
    price NUMERIC NOT NULL DEFAULT 0,
    status BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    duration_minutes INTEGER DEFAULT 60,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE public.package_items (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    package_id BIGINT NOT NULL REFERENCES public.service_packages(id),
    item_type item_type NOT NULL,
    item_id BIGINT NOT NULL,
    quantity INTEGER DEFAULT 1
);

CREATE TABLE public.package_equipments (
    package_id BIGINT NOT NULL REFERENCES public.service_packages(id),
    equipment_id BIGINT NOT NULL REFERENCES public.equipments(id),
    PRIMARY KEY (package_id, equipment_id)
);

-- ========== RESERVATIONS ==========

CREATE TABLE public.reservations (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES public.users(id),
    provider_id BIGINT NOT NULL REFERENCES public.provider_profiles(id),
    space_id BIGINT REFERENCES public.spaces(id),
    package_id BIGINT REFERENCES public.service_packages(id),
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    total_price NUMERIC NOT NULL DEFAULT 0,
    status reservation_status DEFAULT 'pending',
    qr_code VARCHAR,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE public.reservation_items (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    reservation_id BIGINT NOT NULL REFERENCES public.reservations(id),
    item_type item_type NOT NULL,
    item_id BIGINT NOT NULL,
    quantity INTEGER DEFAULT 1,
    price_at_booking NUMERIC NOT NULL DEFAULT 0
);

CREATE TABLE public.payments (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    reservation_id BIGINT NOT NULL REFERENCES public.reservations(id),
    user_id BIGINT NOT NULL REFERENCES public.users(id),
    amount NUMERIC NOT NULL,
    method payment_method NOT NULL,
    status payment_status DEFAULT 'pending',
    transaction_ref VARCHAR,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE public.service_sessions (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    reservation_id BIGINT NOT NULL REFERENCES public.reservations(id),
    checked_in_at TIMESTAMPTZ,
    checked_out_at TIMESTAMPTZ,
    actual_duration_minutes INTEGER,
    status session_status DEFAULT 'in_progress'
);

CREATE TABLE public.reviews (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    reservation_id BIGINT REFERENCES public.reservations(id),
    user_id BIGINT NOT NULL REFERENCES public.users(id),
    space_id BIGINT REFERENCES public.spaces(id),
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========== PACKAGE BOOKINGS ==========

CREATE TABLE public.package_bookings (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    package_id BIGINT NOT NULL REFERENCES public.service_packages(id),
    space_id BIGINT NOT NULL REFERENCES public.spaces(id),
    customer_id BIGINT NOT NULL REFERENCES public.users(id),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    status booking_status,
    total_price BIGINT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ========== COMMUNITY ==========

CREATE TABLE public.posts (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    author_id BIGINT NOT NULL REFERENCES public.users(id),
    title VARCHAR NOT NULL,
    content TEXT NOT NULL,
    category post_category NOT NULL DEFAULT 'article',
    is_published BOOLEAN DEFAULT TRUE,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE public.comments (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    post_id BIGINT NOT NULL REFERENCES public.posts(id),
    user_id BIGINT NOT NULL REFERENCES public.users(id),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========== WORKSHOPS ==========

CREATE TABLE public.workshops (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    expert_id BIGINT NOT NULL REFERENCES public.users(id),
    title VARCHAR NOT NULL,
    description TEXT,
    scheduled_at TIMESTAMPTZ NOT NULL,
    location VARCHAR,
    capacity INTEGER NOT NULL DEFAULT 10,
    price NUMERIC DEFAULT 0,
    status workshop_status DEFAULT 'open'
);

CREATE TABLE public.workshop_registrations (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    workshop_id BIGINT NOT NULL REFERENCES public.workshops(id),
    user_id BIGINT NOT NULL REFERENCES public.users(id),
    status VARCHAR DEFAULT 'registered',
    registered_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========== CHAT ==========

CREATE TABLE public.conversations (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES public.users(id),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE public.messages (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    conversation_id BIGINT NOT NULL REFERENCES public.conversations(id),
    sender_type VARCHAR NOT NULL CHECK (sender_type IN ('user', 'ai')),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========== BILLING ==========

CREATE TABLE public.sell_customers (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_name VARCHAR,
    email VARCHAR UNIQUE,
    phone VARCHAR,
    address VARCHAR,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE public.sell_products (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_name VARCHAR,
    description VARCHAR,
    product_code VARCHAR UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE public.sell_invoices (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id INTEGER REFERENCES public.sell_customers(id),
    invoice_date TIMESTAMP,
    total_amount DOUBLE PRECISION,
    status VARCHAR,
    invoice_code VARCHAR UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    blank_amount DOUBLE PRECISION,
    paid_amount DOUBLE PRECISION
);

CREATE TABLE public.sell_invoice_items (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    invoice_id INTEGER REFERENCES public.sell_invoices(id),
    product_id INTEGER REFERENCES public.sell_products(id),
    quantity INTEGER,
    unit_price DOUBLE PRECISION,
    total_price DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE public.pay_trans (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    invoice_id INTEGER NOT NULL REFERENCES public.sell_invoices(id),
    amount DOUBLE PRECISION NOT NULL,
    payment_method VARCHAR NOT NULL,
    transaction_date TIMESTAMP
);

-- ========== COURSES ==========

CREATE TABLE public.courses (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    course_name VARCHAR NOT NULL,
    description VARCHAR,
    status VARCHAR NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE public.course_register (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id INTEGER,
    course_id INTEGER,
    CONSTRAINT course_register_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id)
);

-- ========== LEGACY ==========

CREATE TABLE public.rooms (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    room_type VARCHAR NOT NULL,
    capacity INTEGER NOT NULL,
    price_per_hour NUMERIC NOT NULL,
    status VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE public.todos (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title VARCHAR NOT NULL,
    description VARCHAR,
    status VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE public.flask_user (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR NOT NULL UNIQUE,
    password VARCHAR NOT NULL,
    description VARCHAR,
    status BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE public.consultants (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    consultant_name VARCHAR NOT NULL,
    description VARCHAR,
    status VARCHAR NOT NULL,
    gender VARCHAR NOT NULL,
    age INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE public.programs (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title VARCHAR NOT NULL,
    description VARCHAR,
    status VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE public.surveys (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title VARCHAR NOT NULL,
    description VARCHAR,
    status VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE public.appointments (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    consultant_id INTEGER,
    user_id INTEGER,
    description VARCHAR,
    status VARCHAR NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    url_online VARCHAR,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT appointments_consultant_id_fkey FOREIGN KEY (consultant_id) REFERENCES public.consultants(id),
    CONSTRAINT appointments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.flask_user(id)
);

CREATE TABLE public.feedbacks (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    feedback_text VARCHAR,
    evaluation DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    course_id INTEGER,
    user_id INTEGER,
    CONSTRAINT feedbacks_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id),
    CONSTRAINT feedbacks_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.flask_user(id)
);
