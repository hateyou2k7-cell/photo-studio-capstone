# 📸 Photo Studio Capstone

**Platform Connecting the Film Photography Community with Darkroom and Studio Services**
*Nền tảng kết nối cộng đồng nhiếp ảnh phim với các dịch vụ phòng tối và phòng chụp*

---

## 📑 Mục lục

- [Giới thiệu](#-giới-thiệu)
- [Nhiệm vụ & Phân công (Team Responsibilities)](#-nhiệm-vụ--phân-công-team-responsibilities)
- [Lộ trình phát triển (Timeline)](#-lộ-trình-phát-triển-timeline)
- [Kiến trúc hệ thống (Architecture)](#-kiến-trúc-hệ-thống-architecture)
- [Công nghệ sử dụng (Tech Stack)](#-công-nghệ-sử-dụng-tech-stack)
- [Cài đặt & Chạy dự án](#-cài-đặt--chạy-dự-án)
- [Sequence Diagram](#-sequence-diagram)

---

## 🎯 Giới thiệu

Phong trào nhiếp ảnh phim đang hồi sinh mạnh mẽ, kéo theo nhu cầu ngày càng lớn về phòng tối, phòng chụp, thiết bị chuyên dụng và các dịch vụ hỗ trợ. Tuy nhiên, các nguồn lực này hiện vẫn phân mảnh: người chụp phải tìm kiếm qua mạng xã hội hoặc liên hệ cá nhân, trong khi các đơn vị cung cấp dịch vụ quản lý bằng spreadsheet hoặc nhiều công cụ rời rạc, dẫn đến hiệu suất sử dụng tài nguyên thấp và khó phân tích vận hành.

**Photo Studio Capstone** là một nền tảng đa phía (multi-sided platform) kết nối nhiếp ảnh gia phim với các đơn vị cung cấp phòng tối, phòng chụp, thiết bị và dịch vụ sáng tạo liên quan — hỗ trợ chia sẻ tài nguyên thông minh, quản lý đặt chỗ, tương tác cộng đồng và quản lý vận hành kinh doanh trong một hệ sinh thái thống nhất.

### Vai trò trong hệ thống

| Vai trò | Mô tả |
|---|---|
| **Photographer (Customer)** | Tìm kiếm, so sánh, đặt phòng/thiết bị, thanh toán, tham gia cộng đồng |
| **Service Provider** | Quản lý phòng tối/studio, thiết bị, gói dịch vụ, đơn đặt, doanh thu |
| **Photography Expert** | Chia sẻ kiến thức, tổ chức workshop, đánh giá thiết bị |
| **Administrator** | Quản trị người dùng, provider, nội dung, giao dịch, báo cáo hệ thống |
| **AI Assistant** | Gợi ý cá nhân hoá, phục hồi/nâng cấp ảnh scan, trả lời câu hỏi nhiếp ảnh |

---

## 👥 Nhiệm vụ & Phân công (Team Responsibilities)

Dự án được triển khai theo mô hình **Scrum rút gọn** trong **10 tuần (5 Sprint x 2 tuần)**, với 5 thành viên phụ trách các module Backend độc lập nhưng tích hợp chặt chẽ theo 6 Core Business Flow của hệ thống.

| Thành viên | Vai trò chính | Module Backend phụ trách | Phạm vi công việc |
|---|---|---|---|
| **Người 1 (Lead)** | Điều phối dự án (PM/BA) | Auth & User | Thiết kế kiến trúc tổng thể, RBAC/JWT, quản lý Sprint, tài liệu SRS/SDD, điều phối tích hợp giữa các module, đảm bảo tiến độ & chất lượng chung |
| **Người 2** | Role Provider | Creative Space (Room) Management | Quản lý phòng tối/studio: CRUD, tìm kiếm/lọc, lịch trống, hình ảnh; tích hợp Billing & Payment |
| **Người 3** | Role Photographer | Reservation & Booking *(module lõi quan trọng nhất)* | Đặt chỗ, kiểm tra & khoá tài nguyên chống trùng lịch, check-in/checkout (Service Session), phát triển ứng dụng Mobile (Flutter) |
| **Người 4** | Role Expert | Community & Review | Chia sẻ kiến thức, đánh giá/bình luận, kiểm duyệt nội dung; phát triển Web Portal (Provider/Admin dashboard), Reporting & Analytics |
| **Người 5** | Role AI | Equipment & Service Package | Quản lý thiết bị & gói dịch vụ, đảm bảo tài nguyên hợp lệ trước khi xác nhận đặt; nghiên cứu & tích hợp các tính năng AI (gợi ý, trợ lý ảo, phục hồi ảnh) |

> 📋 Danh sách task chi tiết theo từng tuần (Summary, Priority, Epic, Timeline) được quản lý trên **Jira** — xem file import tại `docs/jira/Jira_Import_Tuan*.xlsx` trong repo.

---

## 🗓 Lộ trình phát triển (Timeline)

Dự án bắt đầu từ **22/07/2026**, chia thành 5 Sprint, mỗi Sprint 2 tuần (14 ngày):

| Sprint | Tuần | Trọng tâm |
|---|---|---|
| 1 | 1 – 2 | Project Charter, SRS, kiến trúc hệ thống, thiết kế CSDL |
| 2 | 3 – 4 | Setup hạ tầng, Auth/RBAC, module Creative Space |
| 3 | 5 – 6 | Module Reservation & Service Package, Service Session, tích hợp core |
| 4 | 7 – 8 | Billing/Payment, Reporting, Unit & Integration Test |
| 5 | 9 – 10 | System Test/UAT, Deployment, tài liệu & báo cáo Final |

---

## 🏗 Kiến trúc hệ thống (Architecture)

Backend triển khai theo mô hình **Clean Architecture**, tách biệt rõ ràng giữa tầng nghiệp vụ (Domain), tầng dịch vụ (Services) và tầng hạ tầng (Infrastructure):

```bash
    ├── migrations
    ├── scripts
    │   └── run_postgres.sh
    ├── src
    │   ├── api
    │   │   ├── controllers
    │   │   │   └── ...  # controllers for the api (Room, Reservation, Package, Community, Auth...)
    │   │   ├── schemas
    │   │   │   └── ...  # Marshmallow schemas
    │   │   ├── middleware.py
    │   │   ├── responses.py
    │   │   └── requests.py
    │   ├── infrastructure
    │   │   ├── services
    │   │   │   └── ...  # Services that use third party libraries (payment gateway, cloud storage, OpenAI...)
    │   │   ├── databases
    │   │   │   └── ...  # Database adapters and initialization
    │   │   ├── repositories
    │   │   │   └── ...  # Repositories for interacting with the databases
    │   │   └── models
    │   │       └── ...  # Database models
    │   ├── domain
    │   │   ├── constants.py
    │   │   ├── exceptions.py
    │   │   └── models
    │   │       └── ...  # Business logic models (Room, Reservation, Package, Review...)
    │   ├── services
    │   │   └── ...  # Services for interacting with the domain (business logic)
    │   ├── app.py
    │   ├── config.py
    │   ├── cors.py
    │   ├── create_app.py
    │   ├── dependency_container.py
    │   ├── error_handler.py
    │   └── logging.py
```

### Domain Layer
Chứa các entity nghiệp vụ cốt lõi: `Room`, `Reservation`, `Equipment`, `ServicePackage`, `Review`, `User` cùng các quy tắc nghiệp vụ (VD: kiểm tra trùng lịch, khoá tài nguyên).

### Services Layer
Điều phối logic nghiệp vụ giữa Domain và Infrastructure, xử lý các use case chính: đặt phòng, thanh toán, gợi ý AI.

### Infrastructure Layer
Triển khai cụ thể việc kết nối cơ sở dữ liệu, cổng thanh toán (VNPay/MoMo/Stripe), lưu trữ đám mây (Azure Blob/Firebase Storage) và OpenAI API.

---

## 🧰 Công nghệ sử dụng (Tech Stack)

| Thành phần | Công nghệ |
|---|---|
| Mobile Application | Flutter (Android & iOS) |
| Web Portal | ReactJS / Next.js |
| Backend | Flask (Clean Architecture) / ASP.NET Core Web API |
| Database | PostgreSQL / MSSQL Server |
| Cloud Storage | Microsoft Azure Blob Storage / Firebase Storage |
| Authentication | JWT & OAuth 2.0 (RBAC) |
| AI Integration | OpenAI API, Recommendation Systems, Computer Vision |
| Maps & Location | Google Maps API |
| Online Payment | VNPay, MoMo, Stripe |
| Cloud Deployment | Microsoft Azure / Firebase |
| Version Control | GitHub |

---

## ⚙️ Cài đặt & Chạy dự án

### Download source code
```bash
git clone https://github.com/hateyou2k7-cell/photo-studio-capstone.git
```

### Kiểm tra Python đã cài đặt trên máy chưa
```bash
python --version
```

### Bước 1: Tạo môi trường ảo Python (phiên bản 3.x)
**Windows:**
```bash
py -m venv .venv
```
**Unix/MacOS:**
```bash
python3 -m venv .venv
```

### Bước 2: Kích hoạt môi trường
**Windows:**
```bash
.venv\Scripts\activate.ps1
```
> Nếu xảy ra lỗi active `.venv` trên Windows, mở PowerShell với quyền **Administrator** và chạy:
> ```powershell
> Set-ExecutionPolicy RemoteSigned -Force
> ```
**Unix/MacOS:**
```bash
source .venv/bin/activate
```

### Bước 3: Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```

### Bước 4: Chạy ứng dụng
```bash
python app.py
```

Truy cập tài liệu API tại:
- http://localhost:6868/docs
- http://localhost:9999/docs

### Tạo file `.env` trong thư mục `/src/.env`
```env
# Flask settings
FLASK_ENV=development
SECRET_KEY=your_secret_key

# SQL Server settings
DB_USER=sa
DB_PASSWORD=Aa@123456
DB_HOST=127.0.0.1
DB_PORT=1433
DB_NAME=PhotoStudioDB

DATABASE_URI = "mssql+pymssql://sa:Aa%40123456@127.0.0.1:1433/PhotoStudioDB"
```

### Pull image MS SQL Server
```bash
docker pull mcr.microsoft.com/mssql/server:2025-latest
```

### Cài đặt MS SQL Server trong Docker
```bash
docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=Aa123456" -p 1433:1433 --name sql1 --hostname sql1 -d mcr.microsoft.com/mssql/server:2025-latest
```

### ORM Flask (SQLAlchemy ORM)
Ánh xạ class (OOP) trong `src/infrastructure/models` → bảng trong Database, cùng các mối quan hệ khoá ngoại (bao gồm quan hệ many-to-many, ví dụ: `Room` ↔ `Equipment` qua bảng trung gian `RoomEquipment`).

---

## 🔄 Sequence Diagram

```plantuml
@startuml
title Clean Architecture Sequence Diagram - Photo Studio Capstone

actor Actor
participant "Web/Mobile App"
participant "Controller"
participant "Services"
participant "Domain"
participant "Infrastructure"
database "Database"

Actor -> "Web/Mobile App": Request (VD: Đặt phòng)
activate "Web/Mobile App"

"Web/Mobile App" -> "Controller"
activate "Controller"

"Controller" -> "Services"
activate "Services"

"Services" -> "Domain"
activate "Domain"
note over Domain: Kiểm tra quy tắc nghiệp vụ (VD: chống trùng lịch)

"Domain" -> "Infrastructure"
activate "Infrastructure"
note over Infrastructure: Repository / Payment / Cloud Storage

"Infrastructure" -> "Database"
activate "Database"

"Database" --> "Infrastructure"
deactivate "Database"

"Infrastructure" --> "Domain"
deactivate "Infrastructure"

"Domain" --> "Services"
deactivate "Domain"

"Services" --> "Controller"
deactivate "Services"

"Controller" --> "Web/Mobile App"
deactivate "Controller"

"Web/Mobile App" --> Actor
note left of "Web/Mobile App"
  Render data (xác nhận đặt phòng)
end note
deactivate "Web/Mobile App"

@enduml
```

---

## 📄 License

Dự án phục vụ mục đích học tập – Đồ án tốt nghiệp (Capstone Project).
