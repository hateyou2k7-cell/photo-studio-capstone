from api.controllers.auth_controller import auth_bp as auth_bp
from api.controllers.room_controller import bp as room_bp

def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(room_bp)
