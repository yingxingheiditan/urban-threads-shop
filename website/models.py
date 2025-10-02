from . import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Customer(db.Model, UserMixin):
    __tablename__ = 'Customer'  # ✅ explicitly set
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String(500))
    date_joined = db.Column(db.DateTime(), default=datetime.utcnow)

    cart_items = db.relationship('Cart', backref=db.backref('customer', lazy=True))
    orders = db.relationship('Order', backref=db.backref('customer', lazy=True))

    @property
    def password(self):
        raise AttributeError('Password is not a readable Attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password=password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password=password)

    def __str__(self):
        return f"<Customer {self.id}>"

class Product(db.Model):
    __tablename__ = 'Product'  # ✅ explicitly set
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    previous_price = db.Column(db.Float, nullable=False)
    in_stock = db.Column(db.Integer, nullable=False)
    product_picture = db.Column(db.String(1000), nullable=False)
    flash_sale = db.Column(db.Boolean, default=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    carts = db.relationship('Cart', backref=db.backref('product', lazy=True))
    orders = db.relationship('Order', backref=db.backref('product', lazy=True))

    def __str__(self):
        return f"<Product {self.product_name}>"

class Cart(db.Model):
    __tablename__ = 'Cart'  # ✅ explicitly set
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    customer_link = db.Column(db.Integer, db.ForeignKey('Customer.id'), nullable=False)
    product_link = db.Column(db.Integer, db.ForeignKey('Product.id'), nullable=False)

    def __str__(self):
        return f"<Cart {self.id}>"

class Order(db.Model):
    __tablename__ = 'Order'  # ✅ explicitly set
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(100), nullable=False)
    payment_id = db.Column(db.String(1000), nullable=False)

    customer_link = db.Column(db.Integer, db.ForeignKey('Customer.id'), nullable=False)
    product_link = db.Column(db.Integer, db.ForeignKey('Product.id'), nullable=False)

    def __str__(self):
        return f"<Order {self.id}>"

# ✅ History table: do not touch
class HistoricSale(db.Model):
    __tablename__ = 'Final_urbanthreads_transactions_full_4000.xlsx - Sheet1'   # ⚠️ adjust if your CSV import used another name

    TransactionID = db.Column(db.Integer, primary_key=True)
    DateTime = db.Column(db.DateTime, nullable=False)
    ItemName = db.Column(db.String(100), nullable=False)
    QuantitySold = db.Column(db.Integer, nullable=False)
    StockBeforeSale = db.Column(db.Integer, nullable=False)
    StockAfterSale = db.Column(db.Integer, nullable=False)
    Region = db.Column(db.String(50), nullable=False)
    UnitPrice = db.Column(db.Float, nullable=False)
    PromotionApplied = db.Column(db.String(50), nullable=False)
    FinalPrice = db.Column(db.Float, nullable=False)


#######$
class PredictedInventory(db.Model):
    __tablename__ = 'PredictedInventory'
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(500))
    predicted_sales = db.Column(db.Float)
    current_stock = db.Column(db.Integer)
    def __str__(self):
        return f"<PredictedInventory {self.item_name}: Predicted={self.predicted_sales}, Stock={self.current_stock}>"
#######$