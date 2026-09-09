# Báo cáo tiến độ dự án

**Dự án**: Photo Studio Capstone  
**Ngày**: 09/09/2026  
**Phiên bản**: 1.0

## Tóm tắt

- Kiến trúc sạch, chia bốn lớp: API, Service, Business, Database.
- Backend Python 3.12 + Flask, database PostgreSQL trên Supabase, xác thực bằng JWT (HS256).

## Những gì đã làm xong

| Mô-đun | Trạng thái | Ghi chú |
|--------|------------|---------|
| Đăng nhập / Đăng ký | ✅ | Dùng bảng `users`, JWT thời hạn 2 giờ |
| Không gian (CRUD + tìm kiếm) | ✅ | Nhập rooms vào spaces |
| Ảnh và lịch của không gian | ✅ | Upload, ảnh chính, khung giờ |
| Quản lý thiết bị | ✅ | CRUD, phân loại, tình trạng |
| Đặt chỗ và hóa đơn | ✅ | Máy trạng thái, phát hiện xung đột, tự động xuất hóa đơn |
| Đặt gói dịch vụ | ✅ | Đặt chỗ + khóa tài nguyên |
| Thanh toán (hóa đơn/khách hàng/sản phẩm) | ✅ | 19 endpoint, tự động tính lại tổng |
| Khóa học | ✅ | CRUD |
| Chatbot AI | ✅ | Gọi function OpenAI, dự phòng FAQ |
| Gợi ý thông minh | ✅ | Lọc dựa trên nội dung |

## Những việc còn lại

| Tính năng | Ưu tiên | Ghi chú |
|-----------|----------|---------|
| CRUD gói dịch vụ | Cao | Mới chỉ có đặt, chưa có quản lý gói |
| Cộng đ��ng (bài viết, bình luận, hội thảo) | Cao | Mới chỉ có model DB, chưa có API |
| Phân quyền theo vai trò | Cao | Admin bypass vẫn tồn tại |
| QR Code check-in | Trung bình | Chưa làm |
| Quản lý vật tư tiêu hao | Trung bình | Bảng consumables chưa có API |
| Tích hợp thanh toán VNPay/MoMo | Trung bình | Mới chỉ là placeholder |
| Dashboard quản trị | Trung bình | Chưa có frontend |
| Dọn dẹp code cũ | Trung bình | Còn bảng rooms, auth_users,... |

## Vấn đề đang gặp

1. **Bypass admin**: Middleware JWT không kiểm tra quyền ngoài admin – cần sửa lại.
2. **File rỗng**: `schemas/user.py` và `dependency_container.py` chưa có nội dung.
3. **Code thừa**: Các module `todo_*`, `room_*`, `auth_user_*` chưa được xóa.
4. **Session dùng chung**: PostgreSQL session dùng toàn cục, nên tách theo từng request.
5. **CORS**: Thiếu header `Access-Control-Allow-Origin` – đã sửa ở middleware.

## Con số

- Tổng endpoint: 65 (25 cần JWT)
- Số bảng: 44 (28 có API)
- ORM model: 36
- Độ phủ test: ~89% (48/54 tests)

## Nên làm tiếp

1. Hoàn thiện RBAC thay vì dùng admin bypass.
2. Làm CRUD cho gói dịch vụ.
3. Xây dựng API cho cộng đồng (bài viết, bình luận, hội thảo).
4. Tách session riêng cho mỗi request.
5. Xóa bảng cũ và đồng bộ lại ORM.

---
*Báo cáo này được tổng hợp từ mã nguồn và tài liệu.*