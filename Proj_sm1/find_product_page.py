# find_product_page.py
import streamlit as st
import pandas as pd

from data_model import load_products


def render_find_product_page():
    st.title("🔍 Find Product")

    df = load_products()

    # Clean dataframe
    df["Product Name"] = df["Product Name"].astype(str).fillna("").str.strip()
    df["Product ID"] = pd.to_numeric(df["Product ID"], errors="coerce").fillna(-1).astype(int)

    if df.empty:
        st.warning("There are no products in the database yet.")
        if st.button("⬅ Back to Inventory", key="find_back_empty"):
            st.session_state.current_page = "home"
            st.rerun()
        return

    mode = st.radio("Search by:", ["Product ID", "Product Name"], key="find_mode")
    key = st.text_input(f"Enter {mode} to search", key="find_input")

    if st.button("Find", use_container_width=True, key="find_btn"):
        if not key.strip():
            st.error(f"Please enter a {mode}.")
            return

        # --------------------- ID SEARCH ---------------------
        if mode == "Product ID":
            if not key.isdigit():
                st.error("Product ID must be numeric.")
                return

            pid = int(key)
            mask = df["Product ID"] == pid

        # --------------------- NAME SEARCH ---------------------
        else:
            key_lower = key.lower().strip()
            mask = df["Product Name"].str.lower().str.contains(key_lower, na=False)

        if not mask.any():
            st.warning(
                "⚠ No matching product found.\n\n"
                "✔ Check spelling or ID\n"
                "✔ Try partial search (e.g., 'chick' instead of 'Chicken Breast')"
            )
            return

        results = df[mask].copy()

        st.success(f"Found {len(results)} matching product(s):")
        st.write("### Matching Record(s):")

        # DARK MODE FRIENDLY TABLE
        st.dataframe(
            results.style.set_properties(
                **{
                    "background-color": "#1e1e1e",
                    "color": "white"
                }
            )
        )

    st.markdown("---")
    if st.button("⬅ Back to Inventory", key="find_back"):
        st.session_state.current_page = "home"
        st.rerun()
