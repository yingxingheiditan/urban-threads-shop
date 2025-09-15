from flask import Flask
from dotenv import load_dotenv
import os

# Load environment variables from the .env file (if present)
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    return app