from flask import Blueprint, request, jsonify
import jwt
import datetime
from functools import wraps

api_bp = Blueprint('api', __name__, url_prefix='/api')
SECRET_KEY = 'super-secret-key'

# Middleware kiểm tra JWT Token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
        if not token:
            return jsonify({'message': 'Thiếu Token xác thực!'}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = data['username']
        except Exception:
            return jsonify({'message': 'Token không hợp lệ!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# 1. Auth (Đăng ký / Đăng nhập)
@api_bp.route('/auth/register', methods=['POST'])
@api_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Vui lòng điền đầy đủ Tên đăng nhập và Mật khẩu!'}), 400

    return jsonify({
        'message': f'Đăng ký tài khoản {username} thành công!',
        'user': {'username': username, 'email': email}
    }), 201

@api_bp.route('/auth/login', methods=['POST'])
@api_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username') or data.get('email')
    if not username:
        return jsonify({'message': 'Vui lòng nhập Username!'}), 400
        
    token = jwt.encode({
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, SECRET_KEY, algorithm="HS256")
    return jsonify({'access_token': token, 'username': username}), 200

# 2. Rooms
@api_bp.route('/rooms', methods=['GET', 'POST'])
def handle_rooms():
    if request.method == 'POST':
        return jsonify({'message': 'Tạo room thành công'}), 201
    return jsonify([
        {'id': 1, 'name': 'Phòng Studio A', 'capacity': 10, 'price_per_hour': 150000, 'type': 'Studio', 'status': 'Sẵn sàng'},
        {'id': 2, 'name': 'Phòng Studio B', 'capacity': 15, 'price_per_hour': 200000, 'type': 'VIP', 'status': 'Đang sử dụng'}
    ]), 200

# 3. Spaces
@api_bp.route('/spaces', methods=['GET', 'POST'])
def handle_spaces():
    if request.method == 'POST':
        return jsonify({'message': 'Tạo space thành công'}), 201
    return jsonify([{'id': 1, 'name': 'Không gian ngoài trời', 'type': 'Event', 'price_per_hour': 300000, 'capacity': 50, 'status': 'Sẵn sàng'}]), 200

@api_bp.route('/spaces/search', methods=['GET'])
def search_spaces():
    q = request.args.get('q', '')
    return jsonify([{'id': 1, 'name': f'Kết quả tìm kiếm cho: {q}', 'type': 'Event', 'price_per_hour': 300000, 'capacity': 50, 'status': 'Sẵn sàng'}]), 200

# 4. Equipment
@api_bp.route('/equipment', methods=['GET', 'POST'])
def handle_equipment():
    if request.method == 'POST':
        return jsonify({'message': 'Tạo thiết bị thành công'}), 201
    return jsonify([{'id': 1, 'name': 'Máy ảnh Sony A7III', 'type': 'Camera', 'price_per_hour': 50000, 'status': 'Sẵn sàng'}]), 200

# 5. Reservations (Cần JWT)
@api_bp.route('/reservations', methods=['GET', 'POST'])
@token_required
def handle_reservations(current_user):
    if request.method == 'POST':
        return jsonify({'message': 'Tạo đặt chỗ thành công'}), 201
    return jsonify([{'id': 1, 'user': current_user, 'space': 'Studio A', 'start': '08:00', 'end': '10:00', 'price': 300000, 'status': 'Đã xác nhận'}]), 200

# 6. Billing (Customers, Products, Invoices)
@api_bp.route('/customers', methods=['GET', 'POST'])
@token_required
def handle_customers(current_user):
    if request.method == 'POST':
        return jsonify({'message': 'Tạo khách hàng thành công'}), 201
    return jsonify([{'id': 1, 'name': 'Nguyễn Văn A', 'email': 'a@gmail.com', 'phone': '0901234567'}]), 200

@api_bp.route('/products', methods=['GET', 'POST'])
@token_required
def handle_products(current_user):
    if request.method == 'POST':
        return jsonify({'message': 'Tạo sản phẩm thành công'}), 201
    return jsonify([{'id': 1, 'name': 'Đèn Flash Godox', 'code': 'SP001'}]), 200

@api_bp.route('/invoices', methods=['GET'])
@token_required
def handle_invoices(current_user):
    return jsonify([{'id': 1, 'customer': 'Nguyễn Văn A', 'amount': 500000, 'status': 'Đã thanh toán'}]), 200

# 7. Package Bookings
@api_bp.route('/package-bookings', methods=['GET', 'POST'])
def handle_packages():
    if request.method == 'POST':
        return jsonify({'message': 'Tạo gói thành công'}), 201
    return jsonify([{'id': 1, 'package': 'Gói Chụp Cưới', 'space': 'Studio A', 'customer': 'Nguyễn Văn A', 'start': '08:00', 'end': '12:00', 'price': 1500000, 'status': 'Đã đặt'}]), 200

# 8. Courses
@api_bp.route('/courses', methods=['GET', 'POST'])
def handle_courses():
    if request.method == 'POST':
        return jsonify({'message': 'Tạo khóa học thành công'}), 201
    return jsonify([{'id': 1, 'name': 'Khóa học Nhiếp ảnh Cơ bản', 'description': 'Dành cho người mới', 'status': 'Đang mở'}]), 200

# 9. Chatbot AI
@api_bp.route('/chatbot', methods=['POST'])
def handle_chatbot():
    msg = request.get_json().get('message', '')
    return jsonify({'reply': f'Hệ thống AI đã nhận yêu cầu: "{msg}". Chúng tôi có thể giúp gì thêm cho bạn?'}), 200

# 10. Recommendations
@api_bp.route('/recommendations', methods=['GET'])
def handle_recommendations():
    return jsonify([
        {'id': 1, 'title': 'Gợi ý Studio A', 'reason': 'Phù hợp với nhóm 5-10 người'},
        {'id': 2, 'title': 'Gợi ý Đèn Godox V860III', 'reason': 'Thường được thuê cùng Studio A'}
    ]), 200