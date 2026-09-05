import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from src.api.routes import api_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'super-secret-key'

    # Cho phép Kết nối Cross-Origin từ Next.js Frontend
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Route trả về file index.html nằm trong thư mục src
    @app.route('/')
    def serve_index():
        src_dir = os.path.dirname(os.path.abspath(__file__))
        return send_from_directory(src_dir, 'index.html')

    # Đăng ký Blueprint Router
    app.register_blueprint(api_bp)

    return app