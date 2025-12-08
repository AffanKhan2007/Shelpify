# updates_page.py (adjusted)
import streamlit as st
import pandas as pd
from datetime import datetime
from data_model import load_products
from sales_model import apply_sales_to_inventory, products_not_sold_for_days, load_sales

from analytics_page import get_near_expiry_window, classify_expiry

def render_updates_page():
    st.title("🔔 Updates")

    prod_df = load_products().copy()
    # apply historical sales to get current snapshot (does not save)
    prod_snapshot = apply_sales_to_inventory(prod_df)

    if prod_snapshot.empty:
        st.warning("No products available.")
        return

    prod_snapshot["Expiry_Date"] = pd.to_datetime(prod_snapshot["Expiry_Date"]).dt.date

    # compute expiry statuses
    prod_snapshot["Expiry_Status"] = prod_snapshot.apply(
        lambda r: classify_expiry(
            r["Expiry_Date"],
            get_near_expiry_window(r["Category"], r["Product Name"], r["Expiry_Days"])
        ), axis=1
    )

    # Expired table
    expired_df = prod_snapshot[prod_snapshot["Expiry_Status"] == "Expired"]
    st.subheader(f"🟥 Expired Products ({len(expired_df)})")
    if expired_df.empty:
        st.info("No expired products.")
    else:
        st.dataframe(expired_df, use_container_width=True)

    st.markdown("---")

    # Near expiry table
    near_df = prod_snapshot[prod_snapshot["Expiry_Status"] == "Near Expiry"]
    st.subheader(f"🟧 Near-Expiry Products ({len(near_df)})")
    if near_df.empty:
        st.info("No near-expiry products.")
    else:
        st.dataframe(near_df, use_container_width=True)

    st.markdown("---")

    # Products not sold for N days
    st.subheader("Products not sold for N days")
    days = st.number_input("Show products not sold for at least (days)", min_value=1, value=5, key="updates_not_sold_days")
    ns_df = products_not_sold_for_days(prod_df, int(days))
    if ns_df.empty:
        st.info("No products matched the filter.")
    else:
        st.write(f"Products not sold for >= {days} days (or never sold): {len(ns_df)}")
        st.dataframe(ns_df, use_container_width=True)
