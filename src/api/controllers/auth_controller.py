from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from api.schemas.auth import RigisterUserRequestSchema,RigisterUserResponseSchema
from services.auth_service import AuthService
from database.repositories.auth_repository import AuthRepository
import jwt
from werkzeug.security import generate_password_hash
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
auth_service = AuthService(AuthRepository())
register_request = RigisterUserRequestSchema()
register_response = RigisterUserResponseSchema()
@auth_bp.route('/check_router', methods=['GET'])
def check_router():
    """
    Check router
    ---
    get:
      summary: Check router health
      tags:
        - Auth
      responses:
        200:
          description: Router is working
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
    """
    return jsonify({'message': 'Router is working!'}), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user
    ---
    post:
      summary: Login user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/LoginUserRequest'
      tags:
        - Auth
      responses:
        200:
          description: Successful login
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LoginUserResponse'
        401:
          description: Invalid credentials
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
    user = auth_service.login(username, password)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    payload = {
        'user_id': user.id,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(hours=2)
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

    provider_profile_id = None
    if user.role == 'provider':
        from database.databases.factory_database import FactoryDatabase
        from database.models.film_user_model import ProviderProfile
        session = FactoryDatabase.get_database('POSTGREE').session
        profile = session.query(ProviderProfile).filter_by(user_id=user.id).first()
        if profile:
            provider_profile_id = profile.id

    return jsonify({'token': token, 'user_id': user.id, 'role': user.role, 'provider_profile_id': provider_profile_id})


@auth_bp.route('/signup', methods=['POST'])
def register():
    """
    Register a new user
    ---
    post:
      summary: Register a new user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RigisterUserRequest'
      tags:
        - Auth
      responses:
        201:
          description: User registered successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RigisterUserResponse'
        400:
          description: Invalid input or user exists
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
    """
    ALLOWED_ROLES = {'user', 'photographer', 'provider', 'expert'}

    data = request.get_json()
    errors = register_request.validate(data)
    if errors:
      return jsonify(errors), 400
    # Lay thong tin tu nguoi dung truyen vao

    # Support JSON body and avoid KeyError by using .get()
    username = data.get('username') if isinstance(data, dict) else None
    password = data.get('password') if isinstance(data, dict) else None
    passwordconfirm = data.get('passwordconfirm') if isinstance(data, dict) else None
    email = data.get('email') if isinstance(data, dict) else None
    role = data.get('role', 'user') if isinstance(data, dict) else 'user'

    if not username or not password or not passwordconfirm or not email:
      return jsonify({'message': 'Missing required fields: username, password, passwordconfirm, email'}), 400

    if password != passwordconfirm:
      return jsonify({'message': 'Passwords do not match'}), 400

    if role not in ALLOWED_ROLES:
      return jsonify({'message': f'role must be one of {ALLOWED_ROLES}'}), 400

    if auth_service.check_exist(username):
      return jsonify({'message': 'User already exists. Please login.'}), 400
    #  vieets theo kien truc clean architecture
    # password_hashed = Str.encode()(password)
    password_hashed =generate_password_hash(password)
    new_user = auth_service.register(username, password_hashed, email, role=role)
    if not new_user:
      return jsonify({'message': 'Registration failed'}), 500 
    result = register_response.dump(new_user)
    return jsonify(result), 201

    #     return redirect(url_for('login'))

    # return render_template('register.html')