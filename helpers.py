from db_init import SessionLocal
from models import Items
from sqlalchemy import and_


def profit_for_each_item(items=None):
    """
        Compute the profit for each item in the given list of items and return a report.

        Args:
            items: A list of items for which to compute the profit.

        Returns:
            A list of dictionaries, where each dictionary represents a row in the report.
            The first row contains the column headers, the last row contains the total profit,
            and the other rows contain the profit information for each item.

            Each dictionary has the following keys:
            - "product_name": The name of the product.
            - "total_quantity": The total quantity of the product (i.e., quantity + sold_units).
            - "total_price": The total price of the product (i.e., total_quantity * price).
            - "units_sold": The number of units sold.
            - "per_unit_cost": The cost per unit.
            - "per_unit_price": The price per unit.
            - "units_sold_price": The total price of the units sold.
            - "product_profit": The profit for the product (i.e., units_sold_price - (cost * sold_units)).

        Raises:
            None.
        """
    total_profit = 0
    report = [
        {
            "product_name": "Product Name",
            "total_quantity": "Total Quantity",
            "total_price": "Total Price",
            "units_sold": "Units Sold",
            "per_unit_cost": "Per Unit Cost",
            "per_unit_price": "Per Unit Price",
            "units_sold_price": "Units Sold Price",
            "product_profit": "Product Profit",
        },
        {"Total Profit": total_profit}
    ]
    report += [{"product_name": item.name, "total_quantity": item.quantity + item.sold_units,
                "total_price": (item.quantity + item.sold_units) * item.price, "units_sold": item.sold_units,
                "per_unit_cost": item.cost, "per_unit_price": item.price,
                "units_sold_price": item.sold_units * item.price,
                "product_profit": (item.sold_units * item.price) - (item.cost * item.sold_units), } for item in items]
    total_profit = sum(item["product_profit"] for item in report[2:])
    report[1]["Total Profit"] = total_profit
    return report[1:]

#
# def fetch_items(start_date=None, end_date=None):
#     if start_date and end_date:
#         items = get_items_between_dates(start_date=start_date, end_date=end_date)
#     elif start_date:
#         items = get_items_from_date(date=start_date, operator='>=')
#     elif end_date:
#         # Filter items up to end_date
#         items = get_items_from_date(date=end_date, operator='<=')
#     else:
#         return False
#
#     return {"items": items}
#
#
# def get_items_from_date(date=None, operator=None):
#     # Filter items based on start_date
#     with SessionLocal() as db:
#         if ">" in operator:
#             return db.query(Items).filter(Items.date >= date).all()
#         elif "<" in operator:
#             return db.query(Items).filter(Items.date <= date).all()
#
#
# def get_items_between_dates(start_date=None, end_date=None):
#     with SessionLocal() as db:
#         return db.query(Items).filter(and_(Items.date >= start_date, Items.date <= end_date)).all()
