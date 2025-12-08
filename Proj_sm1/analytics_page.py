# analytics_page.py

import streamlit as st
import pandas as pd
from datetime import datetime

from data_model import load_products


# ---------- Overstock Rules You Defined ----------
OVERSTOCK_THRESHOLDS = {
    "Canned/Processed": 100,
    "Car Care": 50,
    "Cleaning": 80,
    "Dairy/Eggs": 200,
    "Dry Fruit/Nuts": 50,
    "Frozen/Processed": 100,
    "Fruit": 150,
    "Grain/Staple": 200,
    "Household/Care": 100,
    "Meat/Protein": 75,
    "Paper Products": 100,
    "Personal Care": 70,
    "Seafood": 50,
    "Snack/Confectionery": 80,
    "Vegetable": 250,
    "Beverage": 100,
}


# ---------- Near-Expiry Rules ----------
def get_near_expiry_window(category, product_name, expiry_days):
    name = product_name.lower()

    # Dairy special classification
    if category == "Dairy/Eggs":
        if any(x in name for x in ["milk", "curd", "yogurt", "cream"]):
            return 2
        if any(x in name for x in ["cheese", "paneer", "butter"]):
            return 30
        return 7

    # Fruits & Vegetables
    if category in ["Fruit", "Vegetable"]:
        return 2

    # Fresh Meat / Seafood
    if category in ["Meat/Protein", "Seafood"]:
        if expiry_days <= 7:
            return 2
        return 7

    # Medium-expiry food-based items
    if category in [
        "Snack/Confectionery",
        "Grain/Staple",
        "Canned/Processed",
        "Frozen/Processed",
        "Beverage",
    ]:
        return 30

    # Long expiry
    if category in ["Household/Care", "Cleaning", "Car Care", "Paper Products"]:
        return 15

    return 30


# ---------- Stock Classification ----------
def classify_stock(qty, category):
    if pd.isna(qty):
        return "Unknown"
    q = float(qty)

    if q == 0:
        return "Out of Stock"
    if q <= 25:
        return "Understock"
    if q > OVERSTOCK_THRESHOLDS.get(category, 100):
        return "Overstock"
    return "Normal"


# ---------- Expiry Classification ----------
def classify_expiry(expiry_date, near_window):
    today = datetime.today().date()

    if expiry_date < today:
        return "Expired"

    days_left = (expiry_date - today).days

    if days_left <= near_window:
        return "Near Expiry"

    return "Good"


# ---------- Row Coloring ----------
def color_rows(row):
    status = row["Expiry_Status"]
    stock = row["Stock_Status"]

    if status == "Expired":
        return ["background-color: #4d0000; color: white"] * len(row)
    if status == "Near Expiry":
        return ["background-color: #663c00; color: white"] * len(row)
    if stock == "Understock":
        return ["background-color: #002147; color: white"] * len(row)
    if stock == "Overstock":
        return ["background-color: #003300; color: white"] * len(row)

    return ["background-color: #1e1e1e; color: white"] * len(row)


# ---------- Main Analytics Page ----------
def render_analytics_page():
    st.title("📊 Advanced Inventory Analytics")

    df = load_products().copy()

    if df.empty:
        st.warning("No products available.")
        return

    df["Expiry_Date"] = pd.to_datetime(df["Expiry_Date"]).dt.date

    # Add statuses
    df["Stock_Status"] = df.apply(
        lambda r: classify_stock(r["Total Quantity"], r["Category"]), axis=1
    )

    df["Expiry_Status"] = df.apply(
        lambda r: classify_expiry(
            r["Expiry_Date"],
            get_near_expiry_window(r["Category"], r["Product Name"], r["Expiry_Days"]),
        ),
        axis=1,
    )

    # ---------- KPI Cards ----------
    total = len(df)
    expired = (df["Expiry_Status"] == "Expired").sum()
    near = (df["Expiry_Status"] == "Near Expiry").sum()
    under = (df["Stock_Status"] == "Understock").sum()
    over = (df["Stock_Status"] == "Overstock").sum()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Products", total)
    c2.metric("Expired", expired)
    c3.metric("Near Expiry", near)
    c4.metric("Understock", under)
    c5.metric("Overstock", over)

    st.markdown("---")

    # ---------- FILTERS ----------
    st.subheader("🧰 Filters")
    filtered_df = df.copy()

    # Category filter
    categories = ["(All)"] + sorted(df["Category"].unique())
    selected_cat = st.selectbox("Category", categories)
    if selected_cat != "(All)":
        filtered_df = filtered_df[filtered_df["Category"] == selected_cat]

    # Stock filter
    stock_options = ["(All)", "Understock", "Overstock", "Out of Stock", "Normal"]
    selected_stock = st.selectbox("Stock Status", stock_options)
    if selected_stock != "(All)":
        filtered_df = filtered_df[filtered_df["Stock_Status"] == selected_stock]

    # Expiry filter
    expiry_options = ["(All)", "Expired", "Near Expiry", "Good"]
    selected_exp = st.selectbox("Expiry Status", expiry_options)
    if selected_exp != "(All)":
        filtered_df = filtered_df[filtered_df["Expiry_Status"] == selected_exp]

    # Price filter
    min_p = float(df["Unit Price"].min())
    max_p = float(df["Unit Price"].max())

    col1, col2 = st.columns(2)
    with col1:
        pmin = st.number_input("Min Price", value=min_p, min_value=0.0)
    with col2:
        pmax = st.number_input("Max Price", value=max_p, min_value=0.0)

    if pmin <= pmax:
        filtered_df = filtered_df[
            (filtered_df["Unit Price"] >= pmin) &
            (filtered_df["Unit Price"] <= pmax)
        ]

    st.markdown("---")

    # ---------- FINAL TABLE ----------
    st.subheader(f"📄 Filtered Results ({len(filtered_df)} items)")
    styled = filtered_df.style.apply(color_rows, axis=1)
    st.dataframe(styled, use_container_width=True)
