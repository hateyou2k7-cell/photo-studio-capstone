import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, send_from_directory
from sqlalchemy import create_engine, Column, BigInteger, String, DateTime, Numeric, Integer, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime
import jwt
from functools import wraps
from flask import request, current_app

Base = declarative_base()
engine = create_engine('sqlite:///test.db', echo=False)
Session = sessionmaker(bind=engine)
db_session = Session()

# ---- Minimal Models ----
class AuthUserModel(Base):
    __tablename__ = 'auth_users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True)
    email = Column(String(100))
    password_hash = Column(String(255))

class SpaceModel(Base):
    __tablename__ = 'spaces'
    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(Integer, default=1)
    name = Column(String(255))
    type = Column(String(50))
    description = Column(Text)
    address = Column(String(255))
    max_capacity = Column(Integer)
    base_price_per_hour = Column(Float, default=0)
    status = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class ReservationModel(Base):
    __tablename__ = 'reservations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, default=1)
    provider_id = Column(Integer, default=1)
    space_id = Column(Integer)
    package_id = Column(Integer)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    total_price = Column(Float, default=0)
    status = Column(String(50), default='pending')
    qr_code = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class ReservationItemModel(Base):
    __tablename__ = 'reservation_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    reservation_id = Column(Integer)
    item_type = Column(String(50))
    item_id = Column(Integer)
    quantity = Column(Integer, default=1)
    price_at_booking = Column(Float, default=0)

class PaymentModel(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    reservation_id = Column(Integer)
    user_id = Column(Integer)
    amount = Column(Float)
    method = Column(String(50))
    status = Column(String(50), default='pending')
    transaction_ref = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

class ServiceSessionModel(Base):
    __tablename__ = 'service_sessions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    reservation_id = Column(Integer)
    checked_in_at = Column(DateTime)
    checked_out_at = Column(DateTime)
    actual_duration_minutes = Column(Integer)
    status = Column(String(50), default='in_progress')

class ReviewModel(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True, autoincrement=True)
    reservation_id = Column(Integer)
    user_id = Column(Integer)
    space_id = Column(Integer)
    rating = Column(Integer)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class SellCustomerModel(Base):
    __tablename__ = 'sell_customers'
    id = Column(Integer, primary_key=True)
    customer_name = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class SellProductModel(Base):
    __tablename__ = 'sell_products'
    id = Column(Integer, primary_key=True)
    product_name = Column(String(100))
    description = Column(String(255))
    product_code = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class SellInvoiceModel(Base):
    __tablename__ = 'sell_invoices'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer)
    invoice_date = Column(DateTime)
    total_amount = Column(Float, default=0)
    status = Column(String(50), default='pending')
    invoice_code = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    blank_amount = Column(Float, default=0)
    paid_amount = Column(Float, default=0)

class SellInvoiceItemModel(Base):
    __tablename__ = 'sell_invoice_items'
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer)
    product_id = Column(Integer)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0)
    total_price = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class PayTranModel(Base):
    __tablename__ = 'pay_trans'
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer)
    amount = Column(Float)
    payment_method = Column(String(50))
    transaction_date = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ---- Flask App ----
SECRET = 'test_secret_key'
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET

from werkzeug.security import generate_password_hash, check_password_hash

# Seed admin user
existing = db_session.query(AuthUserModel).filter_by(username='admin').first()
if not existing:
    u = AuthUserModel(username='admin', email='admin@test.com', password_hash=generate_password_hash('admin123'))
    db_session.add(u)
    db_session.commit()

# Seed a space
existing_space = db_session.query(SpaceModel).first()
if not existing_space:
    s = SpaceModel(name='Studio A', type='studio', description='Photo studio', max_capacity=10, base_price_per_hour=100)
    db_session.add(s)
    db_session.commit()

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'error': 'Missing token'}), 401
        try:
            payload = jwt.decode(token, SECRET, algorithms=['HS256'])
            request.current_user_id = payload.get('user_id')
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

# ---- AUTH ----
@app.route('/auth/check_router', methods=['GET'])
def check_router():
    return jsonify({'message': 'Router is working!'})

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Missing fields'}), 400
    user = db_session.query(AuthUserModel).filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid credentials'}), 401
    token = jwt.encode({'user_id': user.id, 'exp': datetime.utcnow().replace(hour=23, minute=59)}, SECRET, algorithm='HS256')
    return jsonify({'token': token, 'user_id': user.id})

@app.route('/auth/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    if not username or not password or not email:
        return jsonify({'error': 'Missing fields'}), 400
    if db_session.query(AuthUserModel).filter_by(username=username).first():
        return jsonify({'error': 'User exists'}), 400
    u = AuthUserModel(username=username, email=email, password_hash=generate_password_hash(password))
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return jsonify({'id': u.id, 'username': u.username, 'email': u.email}), 201

# ---- SPACES ----
@app.route('/spaces/', methods=['GET'])
def list_spaces():
    spaces = db_session.query(SpaceModel).all()
    return jsonify([{'id': s.id, 'name': s.name, 'type': s.type, 'description': s.description,
                     'max_capacity': s.max_capacity, 'base_price_per_hour': s.base_price_per_hour,
                     'status': s.status} for s in spaces])

@app.route('/spaces/<int:sid>', methods=['GET'])
def get_space(sid):
    s = db_session.query(SpaceModel).filter_by(id=sid).first()
    if not s:
        return jsonify({'message': 'Not found'}), 404
    return jsonify({'id': s.id, 'name': s.name, 'type': s.type})

@app.route('/spaces/', methods=['POST'])
@jwt_required
def create_space():
    data = request.get_json()
    s = SpaceModel(name=data['name'], type=data.get('type', 'studio'),
                   description=data.get('description'), max_capacity=data.get('max_capacity'),
                   base_price_per_hour=data.get('base_price_per_hour', 0))
    db_session.add(s)
    db_session.commit()
    db_session.refresh(s)
    return jsonify({'id': s.id, 'name': s.name, 'type': s.type}), 201

# ---- RESERVATIONS ----
@app.route('/v1/reservations/', methods=['GET'])
def list_reservations():
    reservations = db_session.query(ReservationModel).order_by(ReservationModel.created_at.desc()).all()
    return jsonify([{'id': r.id, 'user_id': r.user_id, 'space_id': r.space_id,
                     'start_time': str(r.start_time), 'end_time': str(r.end_time),
                     'total_price': r.total_price, 'status': r.status} for r in reservations])

@app.route('/v1/reservations/<int:rid>', methods=['GET'])
def get_reservation(rid):
    r = db_session.query(ReservationModel).filter_by(id=rid).first()
    if not r:
        return jsonify({'message': 'Not found'}), 404
    return jsonify({'id': r.id, 'status': r.status, 'total_price': r.total_price})

@app.route('/v1/reservations/', methods=['POST'])
@jwt_required
def create_reservation():
    data = request.get_json()
    from dateutil.parser import isoparse
    start = isoparse(data['start_time'])
    end = isoparse(data['end_time'])
    if start >= end:
        return jsonify({'message': 'start_time must be before end_time'}), 400
    space_id = data.get('space_id')
    if space_id:
        overlap = db_session.query(ReservationModel).filter(
            ReservationModel.space_id == space_id,
            ReservationModel.status != 'cancelled',
            ReservationModel.start_time < end,
            ReservationModel.end_time > start
        ).first()
        if overlap:
            return jsonify({'message': 'Space is already booked for this time period'}), 400
    r = ReservationModel(user_id=data['user_id'], provider_id=data.get('provider_id', 1),
                         space_id=space_id, start_time=start, end_time=end,
                         total_price=data.get('total_price', 0), status='pending')
    db_session.add(r)
    db_session.commit()
    db_session.refresh(r)
    return jsonify({'id': r.id, 'status': r.status, 'space_id': r.space_id}), 201

@app.route('/v1/reservations/<int:rid>/approve', methods=['POST'])
@jwt_required
def approve_reservation(rid):
    r = db_session.query(ReservationModel).filter_by(id=rid).first()
    if not r:
        return jsonify({'message': 'Not found'}), 404
    r.status = 'approved'
    db_session.commit()
    return jsonify({'id': r.id, 'status': r.status})

@app.route('/v1/reservations/<int:rid>/confirm', methods=['POST'])
@jwt_required
def confirm_reservation(rid):
    r = db_session.query(ReservationModel).filter_by(id=rid).first()
    if not r:
        return jsonify({'message': 'Not found'}), 404
    if r.status != 'approved':
        return jsonify({'message': f'Cannot transition from {r.status} to confirmed'}), 400
    r.status = 'confirmed'
    db_session.commit()
    return jsonify({'id': r.id, 'status': r.status})

@app.route('/v1/reservations/<int:rid>/cancel', methods=['POST'])
@jwt_required
def cancel_reservation(rid):
    r = db_session.query(ReservationModel).filter_by(id=rid).first()
    if not r:
        return jsonify({'message': 'Not found'}), 404
    r.status = 'cancelled'
    db_session.commit()
    return jsonify({'id': r.id, 'status': r.status})

@app.route('/v1/reservations/<int:rid>/checkin', methods=['POST'])
@jwt_required
def check_in(rid):
    r = db_session.query(ReservationModel).filter_by(id=rid).first()
    if not r:
        return jsonify({'message': 'Not found'}), 404
    if r.status not in ('confirmed', 'approved'):
        return jsonify({'message': f'Cannot check in from {r.status}'}), 400
    r.status = 'checked_in'
    session = ServiceSessionModel(reservation_id=rid, checked_in_at=datetime.utcnow(), status='in_progress')
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return jsonify({'id': session.id, 'reservation_id': rid, 'status': session.status,
                    'checked_in_at': str(session.checked_in_at)})

@app.route('/v1/reservations/<int:rid>/checkout', methods=['POST'])
@jwt_required
def check_out(rid):
    r = db_session.query(ReservationModel).filter_by(id=rid).first()
    if not r:
        return jsonify({'message': 'Not found'}), 404
    r.status = 'checked_out'
    session = db_session.query(ServiceSessionModel).filter_by(reservation_id=rid).first()
    if session:
        session.checked_out_at = datetime.utcnow()
        session.actual_duration_minutes = int((session.checked_out_at - session.checked_in_at).total_seconds() / 60)
        session.status = 'completed'
    db_session.commit()
    return jsonify({'id': session.id, 'status': session.status, 'duration': session.actual_duration_minutes})

@app.route('/v1/reservations/<int:rid>/items', methods=['POST'])
@jwt_required
def add_item(rid):
    data = request.get_json()
    item = ReservationItemModel(reservation_id=rid, item_type=data['item_type'],
                                 item_id=data['item_id'], quantity=data.get('quantity', 1),
                                 price_at_booking=data.get('price_at_booking', 0))
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return jsonify({'id': item.id, 'item_type': item.item_type, 'item_id': item.item_id}), 201

@app.route('/v1/reservations/<int:rid>/items', methods=['GET'])
def list_items(rid):
    items = db_session.query(ReservationItemModel).filter_by(reservation_id=rid).all()
    return jsonify([{'id': i.id, 'item_type': i.item_type, 'item_id': i.item_id, 'quantity': i.quantity} for i in items])

@app.route('/v1/reservations/<int:rid>/payment', methods=['POST'])
@jwt_required
def create_payment(rid):
    data = request.get_json()
    p = PaymentModel(reservation_id=rid, user_id=data['user_id'], amount=data['amount'],
                     method=data['method'], status='pending')
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return jsonify({'id': p.id, 'amount': p.amount, 'method': p.method, 'status': p.status}), 201

@app.route('/v1/reservations/<int:rid>/payment', methods=['GET'])
def get_payment(rid):
    p = db_session.query(PaymentModel).filter_by(reservation_id=rid).first()
    if not p:
        return jsonify({'message': 'No payment'}), 404
    return jsonify({'id': p.id, 'amount': p.amount, 'method': p.method, 'status': p.status})

@app.route('/v1/reservations/<int:rid>/payment/confirm', methods=['POST'])
@jwt_required
def confirm_payment(rid):
    p = db_session.query(PaymentModel).filter_by(reservation_id=rid).first()
    if not p:
        return jsonify({'message': 'No payment'}), 404
    p.status = 'success'
    db_session.commit()
    return jsonify({'id': p.id, 'status': p.status})

@app.route('/v1/reservations/<int:rid>/reviews', methods=['POST'])
@jwt_required
def add_review(rid):
    data = request.get_json()
    if not 1 <= data['rating'] <= 5:
        return jsonify({'message': 'rating must be 1-5'}), 400
    rev = ReviewModel(reservation_id=rid, user_id=data['user_id'], space_id=data.get('space_id'),
                      rating=data['rating'], comment=data.get('comment'))
    db_session.add(rev)
    db_session.commit()
    db_session.refresh(rev)
    return jsonify({'id': rev.id, 'rating': rev.rating, 'comment': rev.comment}), 201

# ---- BILLING ----
@app.route('/v1/billing/customers', methods=['GET'])
def list_customers():
    customers = db_session.query(SellCustomerModel).all()
    return jsonify([{'id': c.id, 'customer_name': c.customer_name, 'email': c.email} for c in customers])

@app.route('/v1/billing/customers', methods=['POST'])
@jwt_required
def create_customer():
    data = request.get_json()
    c = SellCustomerModel(customer_name=data['customer_name'], email=data.get('email'),
                          phone=data.get('phone'), address=data.get('address'))
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    return jsonify({'id': c.id, 'customer_name': c.customer_name}), 201

@app.route('/v1/billing/customers/<int:cid>', methods=['GET'])
def get_customer(cid):
    c = db_session.query(SellCustomerModel).filter_by(id=cid).first()
    if not c:
        return jsonify({'message': 'Not found'}), 404
    return jsonify({'id': c.id, 'customer_name': c.customer_name})

@app.route('/v1/billing/products', methods=['GET'])
def list_products():
    products = db_session.query(SellProductModel).all()
    return jsonify([{'id': p.id, 'product_name': p.product_name, 'product_code': p.product_code} for p in products])

@app.route('/v1/billing/products', methods=['POST'])
@jwt_required
def create_product():
    data = request.get_json()
    p = SellProductModel(product_name=data['product_name'], description=data.get('description'),
                         product_code=data.get('product_code'))
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return jsonify({'id': p.id, 'product_name': p.product_name}), 201

@app.route('/v1/billing/invoices', methods=['GET'])
def list_invoices():
    invoices = db_session.query(SellInvoiceModel).all()
    return jsonify([{'id': i.id, 'customer_id': i.customer_id, 'total_amount': i.total_amount,
                     'status': i.status, 'invoice_code': i.invoice_code} for i in invoices])

@app.route('/v1/billing/invoices', methods=['POST'])
@jwt_required
def create_invoice():
    data = request.get_json()
    import uuid
    inv = SellInvoiceModel(customer_id=data['customer_id'], total_amount=data.get('total_amount', 0),
                           status=data.get('status', 'pending'),
                           invoice_code=f'INV-{uuid.uuid4().hex[:8].upper()}')
    db_session.add(inv)
    db_session.commit()
    db_session.refresh(inv)
    return jsonify({'id': inv.id, 'invoice_code': inv.invoice_code, 'status': inv.status}), 201

@app.route('/v1/billing/invoices/<int:iid>', methods=['GET'])
def get_invoice(iid):
    i = db_session.query(SellInvoiceModel).filter_by(id=iid).first()
    if not i:
        return jsonify({'message': 'Not found'}), 404
    return jsonify({'id': i.id, 'invoice_code': i.invoice_code, 'status': i.status, 'total_amount': i.total_amount})

@app.route('/v1/billing/invoices/<int:iid>/items', methods=['POST'])
@jwt_required
def add_invoice_item(iid):
    data = request.get_json()
    item = SellInvoiceItemModel(invoice_id=iid, product_id=data['product_id'],
                                 quantity=data.get('quantity', 1), unit_price=data.get('unit_price', 0),
                                 total_price=data.get('quantity', 1) * data.get('unit_price', 0))
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    inv = db_session.query(SellInvoiceModel).filter_by(id=iid).first()
    if inv:
        inv.total_amount = sum(i.total_price or 0 for i in db_session.query(SellInvoiceItemModel).filter_by(invoice_id=iid).all())
        db_session.commit()
    return jsonify({'id': item.id, 'total_price': item.total_price}), 201

@app.route('/v1/billing/invoices/<int:iid>/payments', methods=['POST'])
@jwt_required
def add_invoice_payment(iid):
    data = request.get_json()
    p = PayTranModel(invoice_id=iid, amount=data['amount'], payment_method=data['payment_method'])
    db_session.add(p)
    db_session.commit()
    inv = db_session.query(SellInvoiceModel).filter_by(id=iid).first()
    if inv:
        inv.paid_amount = (inv.paid_amount or 0) + data['amount']
        inv.status = 'paid' if inv.paid_amount >= (inv.total_amount or 0) else 'partial'
        db_session.commit()
    return jsonify({'id': p.id, 'amount': p.amount, 'status': inv.status}), 201

@app.route('/v1/billing/invoices/<int:iid>/payments', methods=['GET'])
def list_invoice_payments(iid):
    payments = db_session.query(PayTranModel).filter_by(invoice_id=iid).all()
    return jsonify([{'id': p.id, 'amount': p.amount, 'method': p.payment_method} for p in payments])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999, debug=False)
