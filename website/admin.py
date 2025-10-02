from flask import Blueprint, render_template, flash, send_from_directory, redirect, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import calendar
from datetime import datetime
from sqlalchemy import func, extract
from .forms import ShopItemsForm, OrderForm
from .models import Product, Order, Customer, HistoricSale, PredictedInventory 
from . import db


admin = Blueprint('admin', __name__)


@admin.route('/media/<path:filename>')
def get_image(filename):
    return send_from_directory('../media', filename)


@admin.route('/add-shop-items', methods=['GET', 'POST'])
@login_required
def add_shop_items():
    if current_user.id == 1:
        form = ShopItemsForm()

        if form.validate_on_submit():
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data

            file = form.product_picture.data
            file_name = secure_filename(file.filename)
            file_path = f'./media/{file_name}'
            file.save(file_path)

            new_shop_item = Product(
                product_name=product_name,
                current_price=current_price,
                previous_price=previous_price,
                in_stock=in_stock,
                flash_sale=flash_sale,
                product_picture=file_path
            )

            try:
                db.session.add(new_shop_item)
                db.session.commit()
                flash(f'{product_name} added Successfully')
                print('Product Added')
                return render_template('add_shop_items.html', form=form)
            except Exception as e:
                print(e)
                flash('Product Not Added!!')

        return render_template('add_shop_items.html', form=form)

    return render_template('404.html')


@admin.route('/shop-items', methods=['GET', 'POST'])
@login_required
def shop_items():
    if current_user.id == 1:
        items = Product.query.order_by(Product.date_added).all()
        return render_template('shop_items.html', items=items)
    return render_template('404.html')


@admin.route('/update-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    if current_user.id == 1:
        form = ShopItemsForm()
        item_to_update = Product.query.get(item_id)

        form.product_name.render_kw = {'placeholder': item_to_update.product_name}
        form.previous_price.render_kw = {'placeholder': item_to_update.previous_price}
        form.current_price.render_kw = {'placeholder': item_to_update.current_price}
        form.in_stock.render_kw = {'placeholder': item_to_update.in_stock}
        form.flash_sale.render_kw = {'placeholder': item_to_update.flash_sale}

        if form.validate_on_submit():
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data

            file = form.product_picture.data
            file_name = secure_filename(file.filename)
            file_path = f'./media/{file_name}'
            file.save(file_path)

            try:
                Product.query.filter_by(id=item_id).update(dict(
                    product_name=product_name,
                    current_price=current_price,
                    previous_price=previous_price,
                    in_stock=in_stock,
                    flash_sale=flash_sale,
                    product_picture=file_path
                ))
                db.session.commit()
                flash(f'{product_name} updated Successfully')
                print('Product Updated')
                return redirect('/shop-items')
            except Exception as e:
                print('Product not Updated', e)
                flash('Item Not Updated!!!')

        return render_template('update_item.html', form=form)
    return render_template('404.html')


@admin.route('/delete-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def delete_item(item_id):
    if current_user.id == 1:
        try:
            item_to_delete = Product.query.get(item_id)
            db.session.delete(item_to_delete)
            db.session.commit()
            flash('One Item deleted')
            return redirect('/shop-items')
        except Exception as e:
            print('Item not deleted', e)
            flash('Item not deleted!!')
        return redirect('/shop-items')

    return render_template('404.html')


@admin.route('/view-orders')
@login_required
def order_view():
    if current_user.id == 1:
        orders = Order.query.order_by(Order.id.desc()).all()
        return render_template('view_orders.html', orders=orders)
    return render_template('404.html')


##########################  SQL #################################################
@admin.route('/history')
def history():
    page = request.args.get('page', 1, type=int)

    # Get filters from query string
    filters = {
        'TransactionID': request.args.get('TransactionID'),
        'DateTime': request.args.get('DateTime'),
        'ItemName': request.args.get('ItemName'),
        'QuantitySold': request.args.get('QuantitySold'),
        'StockBeforeSale': request.args.get('StockBeforeSale'),
        'StockAfterSale': request.args.get('StockAfterSale'),
        'Region': request.args.get('Region'),
        'UnitPrice': request.args.get('UnitPrice'),
        'PromotionApplied': request.args.get('PromotionApplied'),
        'FinalPrice': request.args.get('FinalPrice')
    }

    # Sorting parameters
    sort_col = request.args.get('sort_col', 'DateTime')
    sort_dir = request.args.get('sort_dir', 'desc')

    query = HistoricSale.query

    # Apply filters
    for col, value in filters.items():
        if value:
            if col == "PromotionApplied":
                query = query.filter(getattr(HistoricSale, col) == (value == "Yes"))
            elif col == "DateTime":
                month_number = list(calendar.month_name).index(value)
                query = query.filter(extract('month', HistoricSale.DateTime) == month_number)
            else:
                query = query.filter(getattr(HistoricSale, col) == value)

    # Apply sorting
    if hasattr(HistoricSale, sort_col):
        column = getattr(HistoricSale, sort_col)
        if sort_dir == 'asc':
            query = query.order_by(column.asc())
        else:
            query = query.order_by(column.desc())
    else:
        query = query.order_by(HistoricSale.DateTime.desc())

    # Count filtered rows
    filtered_count = query.count()

    # Pagination
    items = query.paginate(page=page, per_page=50)

    # Distinct values for dropdowns
    distinct_values = {}
    for col in filters.keys():
        if col == "DateTime":
            months = sorted(
                db.session.query(func.distinct(extract('month', HistoricSale.DateTime))).all(),
                key=lambda x: x[0]
            )
            distinct_values[col] = [calendar.month_name[int(m[0])] for m in months]
        elif col == "PromotionApplied":
            distinct_values[col] = ["Yes", "No"]
        else:
            vals = [v[0] for v in db.session.query(func.distinct(getattr(HistoricSale, col))).all()]
            try:
                vals = sorted(vals, key=lambda x: float(x))  # numeric
            except (ValueError, TypeError):
                vals = sorted(vals, key=lambda x: str(x).lower())  # text
            distinct_values[col] = vals

    return render_template(
        "history.html",
        items=items,
        distinct_values=distinct_values,
        filters=filters,
        filtered_count=filtered_count
    )




##########################  SQL #################################################


@admin.route('/update-order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def update_order(order_id):
    if current_user.id == 1:
        form = OrderForm()
        order = Order.query.get(order_id)

        if form.validate_on_submit():
            status = form.order_status.data
            order.status = status
            try:
                db.session.commit()
                flash(f'Order {order_id} Updated successfully')
                return redirect('/view-orders')
            except Exception as e:
                print(e)
                flash(f'Order {order_id} not updated')
                return redirect('/view-orders')

        return render_template('order_update.html', form=form)

    return render_template('404.html')


@admin.route('/customers')
@login_required
def display_customers():
    if current_user.id == 1:
        customers = Customer.query.all()
        return render_template('customers.html', customers=customers)
    return render_template('404.html')


@admin.route('/admin-page')
@login_required
def admin_page():
    if current_user.id == 1:
        return render_template('admin.html')
    return render_template('404.html')



############ Data Analysis - Pie Charts#####################################
@admin.route('/data_analysis')
def data_analysis():
    # Get month/year from query params
    month = request.args.get('month', default=9, type=int)   # default September
    year = request.args.get('year', default=2025, type=int)  # default 2025

    # Total items sold
    total_items = db.session.query(func.sum(HistoricSale.QuantitySold))\
        .filter(extract('month', HistoricSale.DateTime)==month,
                extract('year', HistoricSale.DateTime)==year).scalar() or 0

    # Total profit (sum of FinalPrice)
    total_profit = db.session.query(func.sum(HistoricSale.FinalPrice))\
        .filter(extract('month', HistoricSale.DateTime)==month,
                extract('year', HistoricSale.DateTime)==year).scalar() or 0

    # Region (SG vs HK)
    region_data = db.session.query(
        HistoricSale.Region,
        func.sum(HistoricSale.QuantitySold)
    ).filter(extract('month', HistoricSale.DateTime)==month,
             extract('year', HistoricSale.DateTime)==year)\
     .group_by(HistoricSale.Region).all()

    region_labels = [r[0] for r in region_data]
    region_values = [r[1] for r in region_data]

    # Top 10 items
    top10 = db.session.query(
        HistoricSale.ItemName,
        func.sum(HistoricSale.QuantitySold)
    ).filter(extract('month', HistoricSale.DateTime)==month,
             extract('year', HistoricSale.DateTime)==year)\
     .group_by(HistoricSale.ItemName)\
     .order_by(func.sum(HistoricSale.QuantitySold).desc())\
     .limit(10).all()

    top10_items_labels = [t[0] for t in top10]
    top10_items_values = [t[1] for t in top10]

    return render_template(
        'data_analysis.html',
        total_items=total_items,
        total_profit=total_profit,
        region_labels=region_labels,
        region_values=region_values,
        top10_items_labels=top10_items_labels,
        top10_items_values=top10_items_values
    )


############ Data Analysis -Pie Charts#####################################





##########################  Prediction #################################################
@admin.route('/predicted_inventory')
@login_required
def predicted_inventory():
    if current_user.id == 1:  # Admin only
        items = PredictedInventory.query.all()
        return render_template('predicted_inventory.html', items=items)
    return render_template('404.html')
##########################  Prediction #################################################