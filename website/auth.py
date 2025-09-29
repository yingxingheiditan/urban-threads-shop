from flask import Blueprint, render_template, redirect, url_for
from .forms import LoginForm, SignUpForm, PasswordChangeForm
from .models import Customer
from . import db
from flask_login import login_user, login_required, logout_user

auth = Blueprint('auth', __name__)

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password1 = form.password1.data
        password2 = form.password2.data

        if password1 == password2:
            new_customer = Customer(email=email, username=username, password=password2)
            try:
                db.session.add(new_customer)
                db.session.commit()
                return redirect(url_for('auth.login'))  # ✅ silent redirect
            except:
                pass
    return render_template('signup.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        customer = Customer.query.filter_by(email=email).first()

        if customer and customer.verify_password(password):
            login_user(customer, remember=True)
            return redirect(url_for('views.home'))  # ✅ silent login
    return render_template('login.html', form=form)


@auth.route('/logout')
@login_required
def log_out():
    logout_user()
    return redirect(url_for('views.home'))  # ✅ silent logout
