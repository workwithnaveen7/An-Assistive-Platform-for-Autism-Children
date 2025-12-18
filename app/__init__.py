from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    socketio.init_app(app, cors_allowed_origins="*", async_mode='eventlet')
    
    # Register blueprints
    from app.auth import auth_bp
    from app.child_dashboard import child_bp
    from app.parent_dashboard import parent_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(child_bp, url_prefix='/child')
    app.register_blueprint(parent_bp, url_prefix='/parent')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

