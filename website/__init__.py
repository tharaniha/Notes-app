from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'jufrjowf'

    # Configure database path for compatibility with Vercel
    if os.getenv("VERCEL_ENV"):  # Check if running in Vercel
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:////tmp/{DB_NAME}"  # Use Vercel's writable directory
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"  # Local path for development

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Note
    create_database(app)

    # Set up Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):  
        return User.query.get(int(id))  # Flask-Login uses this to load the current user

    return app

def create_database(app):
    db_path = os.path.join('/tmp' if os.getenv("VERCEL_ENV") else 'website', DB_NAME)

    if not os.path.exists(db_path):
        with app.app_context():  
            db.create_all()
        print('Created Database!')
