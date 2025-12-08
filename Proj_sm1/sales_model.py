# sales_model.py
import pandas as pd
import os
from datetime import datetime, date, timedelta

SALES_CSV = "Sales_log.csv"   # ensure this exists in project folder

def _ensure_sales_file():
    if not os.path.exists(SALES_CSV):
        # create empty sales file with common columns
        df = pd.DataFrame(columns=[
            "Customer ID", "Product ID", "Product Name",
            "Date of Sale", "Quantity Sold", "Unit Price", "Total Sale Amount"
        ])
        df.to_csv(SALES_CSV, index=False)

def load_sales():
    _ensure_sales_file()
    df = pd.read_csv(SALES_CSV)
    # Clean column names (strip)
    df.columns = [c.strip() for c in df.columns]
    # Normalize expected columns
    # If old columns had trailing spaces, above strips them
    # Parse dates:
    if "Date of Sale" in df.columns:
        df["Date of Sale"] = pd.to_datetime(df["Date of Sale"], errors="coerce").dt.date
    # Numeric
    if "Quantity Sold" in df.columns:
        df["Quantity Sold"] = pd.to_numeric(df["Quantity Sold"], errors="coerce").fillna(0).astype(int)
    if "Unit Price" in df.columns:
        df["Unit Price"] = pd.to_numeric(df["Unit Price"], errors="coerce").fillna(0.0)
    if "Total Sale Amount" in df.columns:
        df["Total Sale Amount"] = pd.to_numeric(df["Total Sale Amount"], errors="coerce").fillna(0.0)
    return df

def save_sales(df: pd.DataFrame):
    # ensure normalized column names before saving
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    # Ensure date formatting
    if "Date of Sale" in df.columns:
        df["Date of Sale"] = pd.to_datetime(df["Date of Sale"]).dt.strftime("%Y-%m-%d")
    df.to_csv(SALES_CSV, index=False)

def get_sales_aggregates():
    """
    Returns a DataFrame grouped by Product ID with total units sold and last sold date.
    """
    df = load_sales()
    if df.empty:
        return pd.DataFrame(columns=["Product ID", "Total_Sold", "Last_Sold_Date"])
    grp = df.groupby("Product ID").agg(
        Total_Sold=("Quantity Sold", "sum"),
        Last_Sold_Date=("Date of Sale", lambda s: pd.to_datetime(s).max())
    ).reset_index()
    grp["Last_Sold_Date"] = pd.to_datetime(grp["Last_Sold_Date"]).dt.date
    return grp

def get_last_sold_date_map():
    df = get_sales_aggregates()
    return dict(zip(df["Product ID"].astype(int), df["Last_Sold_Date"]))

def get_total_sold_map():
    df = get_sales_aggregates()
    return dict(zip(df["Product ID"].astype(int), df["Total_Sold"]))

def apply_sales_to_inventory(product_df: pd.DataFrame) -> pd.DataFrame:
    """
    Subtracts sold quantities (from Sales_log.csv) from product_df['Total Quantity'].
    This is idempotent: it stores and updates 'Applied_Sales_Total' column in product_df
    to avoid double application. Returns the updated product_df (and does not save it).
    """
    prod = product_df.copy()
    sales = load_sales()
    # Normalize types
    prod["Product ID"] = pd.to_numeric(prod["Product ID"], errors="coerce")
    prod["Total Quantity"] = pd.to_numeric(prod["Total Quantity"], errors="coerce").fillna(0).astype(int)

    # compute total sold per product from sales df
    if sales.empty:
        # ensure Applied_Sales_Total exists
        if "Applied_Sales_Total" not in prod.columns:
            prod["Applied_Sales_Total"] = 0
        return prod

    sales_grp = sales.groupby("Product ID")["Quantity Sold"].sum().to_dict()

    # ensure column exists
    if "Applied_Sales_Total" not in prod.columns:
        prod["Applied_Sales_Total"] = 0

    # iterate and apply differences
    def apply_row(row):
        pid = int(row["Product ID"]) if not pd.isna(row["Product ID"]) else None
        applied = int(row.get("Applied_Sales_Total", 0) or 0)
        sold_total = int(sales_grp.get(pid, 0)) if pid is not None else 0
        delta = sold_total - applied
        if delta != 0:
            # subtract delta from Total Quantity (ensure not negative)
            new_qty = int(row["Total Quantity"]) - int(delta)
            if new_qty < 0:
                new_qty = 0
            row["Total Quantity"] = new_qty
            row["Applied_Sales_Total"] = sold_total
        return row

    prod = prod.apply(apply_row, axis=1)

    return prod

def products_not_sold_for_days(product_df: pd.DataFrame, days: int):
    """
    Returns products whose last sold date is older than today - days,
    or never sold.
    """
    prod = product_df.copy()
    sales = load_sales()
    # build last sold map
    last_map = get_last_sold_date_map()
    today = date.today()
    threshold = today - timedelta(days=days)
    results = []
    for _, row in prod.iterrows():
        pid = int(row["Product ID"]) if not pd.isna(row["Product ID"]) else None
        last = last_map.get(pid, None)
        if last is None:
            # never sold -> include
            results.append(row)
        else:
            # include if last <= threshold
            if pd.to_datetime(last).date() <= threshold:
                results.append(row)
    if results:
        return pd.DataFrame(results)
    else:
        return pd.DataFrame(columns=prod.columns)

def add_transaction(customer_id, product_id, product_name, date_of_sale, quantity_sold, unit_price=None):
    """
    Adds a sale record to Sales_log.csv. Unit price and total sale amount computed if not provided.
    Returns the new sales row (dict). Does NOT update product CSV here; caller should update inventory.
    """
    df = load_sales()
    # normalize date
    if isinstance(date_of_sale, str):
        ds = pd.to_datetime(date_of_sale, errors="coerce").date()
    elif isinstance(date_of_sale, (datetime, pd.Timestamp)):
        ds = date_of_sale.date()
    elif isinstance(date_of_sale, date):
        ds = date_of_sale
    else:
        ds = date.today()

    # compute unit price if not given
    if unit_price is None:
        # try to find last unit price for product in sales log
        prev = df[df["Product ID"] == product_id].sort_values("Date of Sale", ascending=False)
        if not prev.empty and "Unit Price" in prev.columns:
            unit_price = float(prev.iloc[0]["Unit Price"])
        else:
            unit_price = 0.0

    total_sale = float(quantity_sold) * float(unit_price)

    new_row = {
        "Customer ID": customer_id,
        "Product ID": int(product_id),
        "Product Name": product_name,
        "Date of Sale": ds.strftime("%Y-%m-%d"),
        "Quantity Sold": int(quantity_sold),
        "Unit Price": float(unit_price),
        "Total Sale Amount": float(total_sale),
    }

    df2 = df.copy()
    df2 = pd.concat([df2, pd.DataFrame([new_row])], ignore_index=True)
    save_sales(df2)
    return new_row
