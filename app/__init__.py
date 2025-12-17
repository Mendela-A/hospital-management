from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Будь ласка, увійдіть для доступу до цієї сторінки.'
    login_manager.login_message_category = 'info'
    
    from app.routes.auth import auth
    from app.routes.patients import patients
    from app.routes.admin import admin
    
    app.register_blueprint(auth)
    app.register_blueprint(patients)
    app.register_blueprint(admin)
    
    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))