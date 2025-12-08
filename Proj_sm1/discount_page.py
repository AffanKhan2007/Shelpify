# discount_page.py
import streamlit as st
import pandas as pd
from data_model import load_products


def render_discount_page():
    st.title("💸 Auto Discounts – Expiry-Based Pricing")

    df = load_products()

    if df.empty:
        st.warning("No products available.")
        return

    # Convert dates
    df["Expiry_Date"] = pd.to_datetime(df["Expiry_Date"], errors="coerce")
    df["Manufacture_Date"] = pd.to_datetime(df["Manufacture_Date"], errors="coerce")
    df["Days_Left"] = (df["Expiry_Date"] - pd.Timestamp.now().normalize()).dt.days

    # -----------------------
    # 1️⃣ NEAR-EXPIRY LIST
    # -----------------------
    st.subheader("📅 Near-Expiry Items")

    near = df[df["Days_Left"] <= 7].sort_values("Days_Left")

    if near.empty:
        st.info("No items expiring within 7 days.")
    else:
        st.dataframe(near, use_container_width=True)

    st.markdown("---")

    # -----------------------
    # 2️⃣ CATEGORY-WISE DISCOUNT
    # -----------------------
    st.subheader("🏷 Apply Discount (Category-Wise)")

    categories = sorted(df["Category"].unique().tolist())
    sel_cat = st.selectbox("Select Category", ["-- Select --"] + categories)

    discount_cat = st.number_input("Discount %", min_value=0, max_value=90, value=10)

    if st.button("Apply Category Discount"):
        if sel_cat == "-- Select --":
            st.error("Select a valid category.")
        else:
            filtered = df[df["Category"] == sel_cat].copy()
            filtered["Discounted Price"] = filtered["Unit Price"] * (1 - discount_cat / 100)
            st.success(f"Applied {discount_cat}% discount to category: {sel_cat}")
            st.dataframe(filtered[[
                "Product ID", "Product Name", "Category", "Unit Price", "Discounted Price"
            ]], use_container_width=True)

    st.markdown("---")

    # -----------------------
    # 3️⃣ ITEM-WISE DISCOUNT
    # -----------------------
    st.subheader("🎯 Apply Discount (Item-Wise)")

    item_options = df.apply(
        lambda r: f"{int(r['Product ID'])} | {r['Product Name']} | ₹{r['Unit Price']}",
        axis=1
    ).tolist()

    sel_item = st.selectbox("Select Product", ["-- Select --"] + item_options)

    discount_item = st.number_input("Item Discount %", min_value=0, max_value=90, value=5)

    if st.button("Apply Item Discount"):
        if sel_item == "-- Select --":
            st.error("Select a valid product.")
        else:
            pid = int(sel_item.split("|")[0].strip())
            row = df[df["Product ID"] == pid].iloc[0]

            new_price = row["Unit Price"] * (1 - discount_item / 100)

            st.success(f"Applied {discount_item}% discount to {row['Product Name']}")
            st.write(f"### Before: ₹{row['Unit Price']}")
            st.write(f"### After: ₹{new_price:.2f}")
