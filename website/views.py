from flask import Blueprint, render_template, flash, redirect, request, jsonify, url_for
from .models import Product, Cart, Order
from flask_login import login_required, current_user
from . import db
from intasend import APIService

views = Blueprint('views', __name__)

API_PUBLISHABLE_KEY = 'YOUR_PUBLISHABLE_KEY'
API_TOKEN = 'YOUR_API_TOKEN'
FLAT_SHIPPING_FEE = 30  # 💰 Flat S$30 shipping

# ======================
# 🏠 HOME
# ======================
@views.route('/')
def home():
    return render_template("home.html", user=current_user)

# ======================
# 🆕 NEW ARRIVALS PAGE
# ======================
@views.route('/new-arrivals')
def new_arrivals():
    items = [
        {"name": "Purple Rain Hoodie", "price": 159.90, "image_url": "https://urbanthreads.blob.core.windows.net/new-arrivals/Model_1.jpg", "in_stock": 10},
        {"name": "Mood Camo Hoodie", "price": 159.90, "image_url": "https://urbanthreads.blob.core.windows.net/new-arrivals/Model_2.jpg", "in_stock": 10},
        {"name": "Life In Mono Hoodie", "price": 159.90, "image_url": "https://urbanthreads.blob.core.windows.net/new-arrivals/Model_3.jpg", "in_stock": 10},
        {"name": "UT Classic Hoodie", "price": 159.90, "image_url": "https://urbanthreads.blob.core.windows.net/new-arrivals/Model_4.jpg", "in_stock": 10},
        {"name": "Darkness Avenger Hoodie", "price": 159.90, "image_url": "https://urbanthreads.blob.core.windows.net/new-arrivals/Model_5.jpg", "in_stock": 10},
        {"name": "Local Patriot Hoodie", "price": 159.90, "image_url": "https://urbanthreads.blob.core.windows.net/new-arrivals/Model_6.jpg", "in_stock": 10},
        {"name": "Blend Essence Hoodie", "price": 159.90, "image_url": "https://urbanthreads.blob.core.windows.net/new-arrivals/Model_7.jpg", "in_stock": 10},
        {"name": "Oceanic Hoodie", "price": 159.90, "image_url": "https://urbanthreads.blob.core.windows.net/new-arrivals/Model_8.jpg", "in_stock": 10},
        {"name": "Crimson Hoodie", "price": 159.90, "image_url": "https://urbanthreads.blob.core.windows.net/new-arrivals/Model_9.jpg", "in_stock": 10},
    ]
    return render_template("new_arrivals.html", items=items, user=current_user)

# ======================
# 👕 ALL PRODUCTS
# ======================
@views.route('/all')
def all():
    items = Product.query.order_by(Product.flash_sale.desc()).all()
    return render_template(
        'all.html',
        items=items,
        cart=Cart.query.filter_by(customer_link=current_user.id).all() if current_user.is_authenticated else []
    )

# ======================
# ➕ ADD TO CART
# ======================
@views.route('/add-to-cart/<int:item_id>', methods=['POST'])
@login_required
def add_to_cart(item_id):
    item_to_add = Product.query.get(item_id)
    if not item_to_add:
        flash('Item not found.', 'danger')
        return redirect(request.referrer)

    existing_item = Cart.query.filter_by(product_link=item_id, customer_link=current_user.id).first()
    if existing_item:
        existing_item.quantity += 1
        db.session.commit()
        flash(f'Quantity of {item_to_add.product_name} updated.', 'info')
    else:
        new_cart_item = Cart(quantity=1, product_link=item_to_add.id, customer_link=current_user.id)
        db.session.add(new_cart_item)
        db.session.commit()
        flash(f'{item_to_add.product_name} added to cart.', 'success')

    return redirect(url_for('views.show_cart'))

# ======================
# 🛒 SHOW CART
# ======================
@views.route('/cart')
@login_required
def show_cart():
    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    amount = sum(item.product.current_price * item.quantity for item in cart)
    return render_template('cart.html', cart=cart, amount=amount, total=amount + FLAT_SHIPPING_FEE)

# ======================
# ➕ INCREASE QUANTITY
# ======================
@views.route('/pluscart')
@login_required
def plus_cart():
    cart_id = request.args.get('cart_id')
    cart_item = Cart.query.get(cart_id)
    cart_item.quantity += 1
    db.session.commit()

    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    amount = sum(item.product.current_price * item.quantity for item in cart)

    data = {
        'quantity': cart_item.quantity,
        'amount': amount,
        'total': amount + FLAT_SHIPPING_FEE
    }
    return jsonify(data)

# ======================
# ➖ DECREASE QUANTITY
# ======================
@views.route('/minuscart')
@login_required
def minus_cart():
    cart_id = request.args.get('cart_id')
    cart_item = Cart.query.get(cart_id)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
    else:
        db.session.delete(cart_item)
    db.session.commit()

    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    amount = sum(item.product.current_price * item.quantity for item in cart)

    data = {
        'quantity': cart_item.quantity if cart_item.quantity > 0 else 0,
        'amount': amount,
        'total': amount + FLAT_SHIPPING_FEE
    }
    return jsonify(data)

# ======================
# ❌ REMOVE CART ITEM
# ======================
@views.route('/removecart/<int:cart_id>', methods=['POST'])
@login_required
def remove_cart(cart_id):
    cart_item = Cart.query.get_or_404(cart_id)

    if cart_item.customer_link != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('views.show_cart'))

    product_name = cart_item.product.product_name
    db.session.delete(cart_item)
    db.session.commit()

    flash(f'{product_name} removed from cart.', 'info')
    return redirect(url_for('views.show_cart'))

    # ======================
# 💳 CHECKOUT PAGE
# ======================
@views.route('/checkout')
@login_required
def checkout():
    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('views.show_cart'))

    subtotal = sum(item.product.current_price * item.quantity for item in cart)
    total = subtotal + FLAT_SHIPPING_FEE

    return render_template('checkout.html', cart=cart, subtotal=subtotal, shipping=FLAT_SHIPPING_FEE, total=total)

# ======================
# 🧾 PLACE ORDER
# ======================
@views.route('/place-order', methods=['POST'])
@login_required
def place_order():
    customer_cart = Cart.query.filter_by(customer_link=current_user.id)
    if customer_cart:
        try:
            total = sum(item.product.current_price * item.quantity for item in customer_cart)

            service = APIService(token=API_TOKEN, publishable_key=API_PUBLISHABLE_KEY, test=True)
            create_order_response = service.collect.mpesa_stk_push(
                phone_number='YOUR_NUMBER',
                email=current_user.email,
                amount=total + FLAT_SHIPPING_FEE,
                narrative='Purchase of goods'
            )

            for item in customer_cart:
                new_order = Order(
                    quantity=item.quantity,
                    price=item.product.current_price,
                    status=create_order_response['invoice']['state'].capitalize(),
                    payment_id=create_order_response['id'],
                    product_link=item.product_link,
                    customer_link=item.customer_link
                )
                db.session.add(new_order)
                product = Product.query.get(item.product_link)
                product.in_stock -= item.quantity
                db.session.delete(item)
                db.session.commit()

            flash('Order Placed Successfully', 'success')
            return redirect('/orders')
        except Exception as e:
            print(e)
            flash('Order not placed', 'danger')
            return redirect('/')
    else:
        flash('Your cart is empty.', 'warning')
        return redirect('/')

# ======================
# 📦 ORDERS PAGE
# ======================
@views.route('/orders')
@login_required
def order():
    orders = Order.query.filter_by(customer_link=current_user.id).all()
    return render_template('orders.html', orders=orders)

# ======================
# 🔍 SEARCH
# ======================
@views.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search')
        items = Product.query.filter(Product.product_name.ilike(f'%{search_query}%')).all()
        return render_template(
            'search.html',
            items=items,
            cart=Cart.query.filter_by(customer_link=current_user.id).all() if current_user.is_authenticated else []
        )
    return render_template('search.html')
