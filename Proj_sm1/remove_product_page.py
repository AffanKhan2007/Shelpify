# remove_product_page.py
import streamlit as st
import pandas as pd

from data_model import load_products, save_products


def render_remove_product_page():
    st.title("🗑 Remove Product")

    df = load_products()

    if df.empty:
        st.warning("There are no products in the database yet.")
        if st.button("⬅ Back to Inventory"):
            st.session_state.current_page = "home"
            st.rerun()
        return

    mode = st.radio("Delete by:", ["Product ID", "Product Name"])
    key = st.text_input(f"Enter {mode}")

    if st.button("Delete Product", use_container_width=True, key="remove_delete"):
        if not key.strip():
            st.error(f"Please enter a {mode}.")
            return

        if mode == "Product ID":
            if not key.isdigit():
                st.error("Product ID must be numeric.")
                return
            pid = int(key)
            mask = df["Product ID"] == pid
        else:
            key_lower = key.strip().lower()
            mask = df["Product Name"].str.lower() == key_lower

        if not mask.any():
            st.warning(
                "⚠ No matching product found to delete. "
                "Check the ID or name and try again."
            )
        else:
            deleted = df[mask].copy()
            df = df[~mask]
            save_products(df)

            st.success(f"✅ Deleted {len(deleted)} record(s).")
            st.write("### Deleted Record(s)")
            st.dataframe(deleted)

    st.markdown("---")
    if st.button("⬅ Back to Inventory", key="remove_back"):
        st.session_state.current_page = "home"
        st.rerun()   # FIXED

