from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize SQLAlchemy
db = SQLAlchemy()

# Azure SQL credentials
SQL_USER = "urban_data"
SQL_PASSWORD = "admin001*"
SQL_SERVER = "urbanserver001db.database.windows.net"
SQL_DB = "historical_sales_data"


def create_database():
    """Create all tables in the Azure SQL database"""
    db.create_all()
    print('Database Created')


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # Azure SQL connection
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mssql+pyodbc://{SQL_USER}:{SQL_PASSWORD}@{SQL_SERVER}:1433/{SQL_DB}"
        "?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes&Connection+Timeout=30"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)

    # 404 page
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html')

    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Import models first
    from .models import Customer, Cart, Product, Order, HistoricSale

    # Import blueprints
    from .views import views
    from .auth import auth
    from .admin import admin

    # User loader
    @login_manager.user_loader
    def load_user(id):
        return Customer.query.get(int(id))

    # Register blueprints
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/')

    # Uncomment for first-time database creation
    # with app.app_context():
    #     create_database()

    return app