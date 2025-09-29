from flask import Blueprint, render_template
from flask_login import current_user

views = Blueprint('views', __name__)

# ✅ Home Page
@views.route('/')
def home():
    return render_template("home.html", user=current_user)

# ✅ New Arrivals Page
@views.route('/new-arrivals')
def new_arrivals():
    items = [
        {"name": "Purple Black Hoodie", "price": 39.90, "image_url": "https://urbanthreads.blob.core.windows.net/new-arrivals/Model_1.jpg"},
        {"name": "Beige Hoodie", "price": 39.90, "image_url": "https://urbanthreads.blob.core.windows.net/new-arrivals/Model_2.jpg"},
        {"name": "Black White Hoodie", "price": 39.90, "image_url": "https://urbanthreads.blob.core.windows.net/new-arrivals/Model_3.jpg"},
        {"name": "Red Blue Hoodie", "price": 39.90, "image_url": "https://urbanthreads.blob.core.windows.net/new-arrivals/Model_4.jpg"},
        {"name": "Black Hoodie", "price": 39.90, "image_url": "https://urbanthreads.blob.core.windows.net/new-arrivals/Model_5.jpg"},
        {"name": "Red White Hoodie", "price": 39.90, "image_url": "https://urbanthreads.blob.core.windows.net/new-arrivals/Model_6.jpg"},
        {"name": "Green Blue Hoodie", "price": 39.90, "image_url": "https://urbanthreads.blob.core.windows.net/new-arrivals/Model_7.jpg"},
        {"name": "Blue Hoodie", "price": 39.90, "image_url": "https://urbanthreads.blob.core.windows.net/new-arrivals/Model_8.jpg"},
        {"name": "Red Hoodie", "price": 39.90, "image_url": "https://urbanthreads.blob.core.windows.net/new-arrivals/Model_9.jpg"},
    ]
    return render_template("new_arrivals.html", items=items, user=current_user)
