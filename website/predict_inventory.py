# predictions.py
from . import create_app, db
from .models import HistoricSale, PredictedInventory
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

# ------------------- Flask App Context -------------------
app = create_app()
with app.app_context():

    # ------------------- Load Historic Sales -------------------
    sales = HistoricSale.query.all()
    
    if not sales:
        print("No historic sales found!")
        exit(1)

    # Convert to DataFrame (mirror SQL / Excel columns)
    data = pd.DataFrame([{
        "TransactionID": s.TransactionID,
        "DateTime": s.DateTime,   # optional, all Sep
        "ItemName": s.ItemName,
        "QuantitySold": s.QuantitySold,
        "StockBeforeSale": s.StockBeforeSale,
        "StockAfterSale": s.StockAfterSale,
        "Region": s.Region,
        "UnitPrice": s.UnitPrice,
        "PromotionApplied": 1 if str(s.PromotionApplied).lower() in ["yes", "true", "1"] else 0,
        "FinalPrice": s.FinalPrice
    } for s in sales])

    # ------------------- Aggregate per Item -------------------
    # 1. Lowest stock remaining in September = BalanceStock
    item_sales = data.groupby('ItemName').agg(
        BalanceStock=('StockAfterSale', 'min'),
        SepTotalSales=('QuantitySold', 'sum')
    ).reset_index()

    # ------------------- Simple ML Prediction -------------------
    # Here we use SepTotalSales as feature to predict October stock
    X = item_sales[['SepTotalSales']]
    y = item_sales['SepTotalSales']  # for demo, predicting similar sales
    model = LinearRegression()
    model.fit(X, y)
    item_sales['PredictedSales'] = model.predict(X).round().astype(int)

    # ------------------- Insert into PredictedInventory -------------------
    # Clear old predictions first (optional)
    db.session.query(PredictedInventory).delete()
    db.session.commit()

    for _, row in item_sales.iterrows():
        pred_row = PredictedInventory(
            item_name=row['ItemName'],
            predicted_sales=row['PredictedSales'],
            current_stock=row['BalanceStock']
        )
        db.session.add(pred_row)

    db.session.commit()
    print(f"Predictions inserted for {len(item_sales)} items!")
