from website import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Open a connection
    with db.engine.connect() as conn:
        sql = text("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
                   "WHERE TABLE_TYPE='BASE TABLE' AND TABLE_SCHEMA='dbo';")
        result = conn.execute(sql)
        tables = [row[0] for row in result]
        print("Tables in dbo schema:", tables)

    # Check for the 4 expected tables
    expected_tables = {'Customer', 'Product', 'Cart', 'Order'}
    missing = expected_tables - set(tables)
    if missing:
        print("Missing tables:", missing)
    else:
        print("All 4 tables are present!")
