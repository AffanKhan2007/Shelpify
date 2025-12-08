# add_product_page.py

import streamlit as st
import pandas as pd
from datetime import timedelta

from data_model import (
    load_products,
    save_products,
    auto_detect_type,
    auto_expiry_days,
    generate_product_id,
    validate_manufacture_date,
    check_expired,
)


def render_add_product_page():
    st.title("➕ Add Product")

    df = load_products()

    # Get unique categories for dropdown
    category_options = sorted(df["Category"].astype(str).str.strip().unique())

    st.subheader("Enter Product Details")

    col1, col2 = st.columns(2)

    with col1:
        product_name = st.text_input("Product Name")

        # NEW: Category dropdown
        category = st.selectbox(
            "Category",
            category_options,
            key="category_dropdown"
        )

        quantity_str = st.text_input("Total Quantity")
        unit_price_str = st.text_input("Unit Price")

    detected_type = auto_detect_type(product_name)

    with col2:
        manu_date = st.date_input("Manufacture Date")

        product_type = st.selectbox(
            "Product Type (auto-filled but editable)",
            ["Veg", "Non-Veg", "Inedible"],
            index=["Veg", "Non-Veg", "Inedible"].index(
                detected_type if detected_type in ["Veg", "Non-Veg", "Inedible"] else "Veg"
            ),
        )

        default_exp_days = auto_expiry_days(product_name, product_type)
        expiry_days = st.number_input(
            "Expiry Days",
            min_value=1,
            value=int(default_exp_days),
            step=1,
        )

    try:
        pid_preview = generate_product_id(df, product_type)
        st.info(f"Product ID will be automatically assigned: **{pid_preview}**")
    except Exception as e:
        st.error(str(e))

    if st.button("Save Product", use_container_width=True, key="add_save"):
        errors = []

        if not product_name.strip():
            errors.append("Product Name is required.")

        try:
            quantity = float(quantity_str)
        except:
            errors.append("Total Quantity must be numeric.")

        try:
            unit_price = float(unit_price_str)
        except:
            errors.append("Unit Price must be numeric.")

        err_msg, warn_msg = validate_manufacture_date(manu_date)
        if err_msg:
            errors.append(err_msg)

        expired, expiry_date = check_expired(manu_date, expiry_days)
        if expired:
            errors.append(f"This product has already expired on {expiry_date}.")

        try:
            pid = generate_product_id(df, product_type)
        except Exception as e:
            errors.append(str(e))

        if errors:
            st.error("Cannot add product:")
            for e in errors:
                st.markdown(f"- {e}")
            return

        if warn_msg:
            st.warning(warn_msg)

        total_amount = quantity * unit_price

        new_row = {
            "Product ID": pid,
            "Product Name": product_name.strip(),
            "Category": category.strip(),
            "Type": product_type,
            "Unit Price": unit_price,
            "Total Quantity": quantity,
            "Total_Amount": total_amount,
            "Manufacture_Date": manu_date,
            "Expiry_Days": expiry_days,
            "Expiry_Date": expiry_date,
        }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_products(df)

        st.success(f"Product Added Successfully! (ID: {pid})")
        st.write("### Added Record")
        st.dataframe(pd.DataFrame([new_row]))

    st.markdown("---")
    if st.button("⬅ Back", key="add_back"):
        st.session_state.current_page = "home"
        st.rerun()
