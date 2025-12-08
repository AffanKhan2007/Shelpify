# sales_page.py
import streamlit as st
import pandas as pd
from datetime import date
import altair as alt

# --------------------------
# IMPORTS FROM SALES MODEL
# --------------------------
from sales_model import (
    load_sales,
    save_sales,
    get_sales_aggregates,
    add_transaction,
    products_not_sold_for_days,
    apply_sales_to_inventory,
    load_sales as load_sales_df
)

# --------------------------
# IMPORTS FROM DATA MODEL
# --------------------------
from data_model import load_products, save_products


def _ensure_sales_date_is_date(sales_df: pd.DataFrame) -> pd.DataFrame:
    """Ensure 'Date of Sale' exists and is date-only (no time)."""
    if "Date of Sale" not in sales_df.columns:
        sales_df["Date of Sale"] = pd.NaT
        return sales_df
    sales_df = sales_df.copy()
    sales_df["Date of Sale"] = pd.to_datetime(sales_df["Date of Sale"], errors="coerce")
    # convert to date (remove time)
    sales_df["Date of Sale"] = sales_df["Date of Sale"].dt.date
    return sales_df


def render_sales_page():
    st.title("🧾 Sales & Transactions")

    tab1, tab2, tab3 = st.tabs([
        "Data & Stats",
        "View Transactions",
        "Add Transaction"
    ])

    # ----------------------
    # TAB 1 — DATA & STATISTICS
    # ----------------------
    with tab1:
        st.subheader("📊 Sales Summary & Statistics")

        sales_df = load_sales()
        sales_df = _ensure_sales_date_is_date(sales_df)
        prod_df = load_products()
        prod_snapshot = apply_sales_to_inventory(prod_df.copy())

        # Inventory snapshot
        st.write("### 🏷 Inventory Snapshot (After Sales Applied)")
        st.dataframe(prod_snapshot, use_container_width=True)

        st.markdown("---")

        # ---------- Total revenue metrics (by Type) ----------
        st.write("### 💰 Total Revenue Summary")

        if sales_df.empty:
            st.info("No sales recorded yet.")
        else:
            # Merge sales with product master to get Type (Veg / Non-Veg / Inedible)
            # Use left join: sales -> product to pick up Type values
            merged = sales_df.merge(
                prod_df[["Product ID", "Type"]],
                on="Product ID",
                how="left"
            )

            # Ensure numeric and presence of Total Sale Amount
            if "Total Sale Amount" not in merged.columns:
                merged["Total Sale Amount"] = 0.0
            merged["Total Sale Amount"] = pd.to_numeric(merged["Total Sale Amount"], errors="coerce").fillna(0.0)

            total_rev = merged["Total Sale Amount"].sum()
            veg_rev = merged[merged["Type"] == "Veg"]["Total Sale Amount"].sum()
            nonveg_rev = merged[merged["Type"] == "Non-Veg"]["Total Sale Amount"].sum()
            inedible_rev = merged[merged["Type"] == "Inedible"]["Total Sale Amount"].sum()

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Revenue", f"₹{total_rev:,.2f}")
            c2.metric("Veg Revenue", f"₹{veg_rev:,.2f}")
            c3.metric("Non-Veg Revenue", f"₹{nonveg_rev:,.2f}")
            c4.metric("Inedible Revenue", f"₹{inedible_rev:,.2f}")

        st.markdown("---")

        # ---------- Scatter: Transaction # vs Bill Amount (dotted avg line) ----------
        st.write("### 📈 Customer Bill Scatter (Transaction # vs Bill Amount)")

        if sales_df.empty:
            st.info("Not enough sales to plot bills.")
        else:
            # Group into bills: (Customer ID, Date of Sale) => one bill per customer per date
            bills = sales_df.groupby(["Customer ID", "Date of Sale"], dropna=False)["Total Sale Amount"] \
                            .sum().reset_index()

            # Ensure Date is datetime.date and sorted chronologically
            bills["Date of Sale"] = pd.to_datetime(bills["Date of Sale"], errors="coerce").dt.date
            bills = bills.sort_values("Date of Sale").reset_index(drop=True)

            bills["Transaction_Num"] = bills.index + 1
            bills["Total Sale Amount"] = pd.to_numeric(bills["Total Sale Amount"], errors="coerce").fillna(0.0)

            avg_bill = bills["Total Sale Amount"].mean()

            st.write(f"**Average Bill Amount → ₹{avg_bill:,.2f}**")

            scatter = alt.Chart(bills).mark_circle(size=70, color="#4EA8DE").encode(
                x=alt.X("Transaction_Num:Q", title="Transaction #"),
                y=alt.Y("Total Sale Amount:Q", title="Bill Amount (₹)"),
                tooltip=[
                    alt.Tooltip("Transaction_Num:Q", title="Txn #"),
                    alt.Tooltip("Customer ID:O", title="Customer"),
                    alt.Tooltip("Date of Sale:T", title="Date"),
                    alt.Tooltip("Total Sale Amount:Q", title="Bill (₹)", format=",.2f"),
                ]
            ).properties(height=320, width="container")

            avg_line = alt.Chart(pd.DataFrame({"y": [avg_bill]})).mark_rule(strokeDash=[6,6], color="red").encode(
                y="y:Q"
            )

            st.altair_chart((scatter + avg_line).interactive(), use_container_width=True)

        st.markdown("---")

        # ---------- Daily revenue line chart (date-wise, no time) ----------
        st.write("### 📉 Total Sales by Date (Date-wise)")

        if sales_df.empty:
            st.info("No sales to visualize.")
        else:
            daily = sales_df.groupby("Date of Sale", sort=True)["Total Sale Amount"].sum().reset_index()
            # Ensure Date column is datetime (with no time)
            daily["Date"] = pd.to_datetime(daily["Date of Sale"].astype(str), errors="coerce")
            daily["Total Sale Amount"] = pd.to_numeric(daily["Total Sale Amount"], errors="coerce").fillna(0.0)

            line = alt.Chart(daily).mark_line(point=True, color="#9B5DE5").encode(
                x=alt.X("Date:T", title="Date", axis=alt.Axis(format="%Y-%m-%d", labelAngle=-45)),
                y=alt.Y("Total Sale Amount:Q", title="Revenue (₹)")
            ).properties(height=320, width="container")

            st.altair_chart(line.interactive(), use_container_width=True)

        st.markdown("---")

        # ---------- Products not sold for N days ----------
        st.write("### 🕒 Products Not Sold for N Days")
        days = st.number_input("Enter days:", min_value=1, value=5, key="unsold_days_stats")
        prod_df_for_unsold = prod_df.copy()
        unsold = products_not_sold_for_days(prod_df_for_unsold, int(days))
        if unsold.empty:
            st.info(f"No products unsold for ≥ {days} days.")
        else:
            st.dataframe(unsold, use_container_width=True)

    # ----------------------
    # TAB 2 — VIEW TRANSACTIONS
    # ----------------------
    with tab2:
        st.subheader("📒 View Transactions")
        sales_df2 = load_sales_df()
        sales_df2 = _ensure_sales_date_is_date(sales_df2)

        if sales_df2.empty:
            st.info("No transactions recorded.")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                f_pid = st.text_input("Filter by Product ID:")
            with col2:
                f_cust = st.text_input("Filter by Customer ID:")
            with col3:
                f_date = st.date_input("Filter by Date:")

            filtered = sales_df2.copy()

            if f_pid.strip().isdigit():
                filtered = filtered[filtered["Product ID"] == int(f_pid)]

            if f_cust.strip().isdigit():
                filtered = filtered[filtered["Customer ID"] == int(f_cust)]

            if f_date:
                filtered = filtered[pd.to_datetime(filtered["Date of Sale"]).dt.date == f_date]

            st.write("### Filtered Transactions")
            st.dataframe(filtered, use_container_width=True)

            # total revenue for displayed results
            total_filtered_revenue = pd.to_numeric(filtered.get("Total Sale Amount", pd.Series([0.0])), errors="coerce").fillna(0.0).sum()
            st.success(f"Total Revenue for Displayed Transactions: ₹{total_filtered_revenue:,.2f}")

    # ----------------------
    # TAB 3 — ADD TRANSACTION
    # ----------------------
    with tab3:
        st.subheader("➕ Add New Transaction")

        prod_df = load_products()
        prod_df = apply_sales_to_inventory(prod_df.copy())

        options = prod_df.apply(
            lambda r: f"{int(r['Product ID'])} | {r['Product Name']} | Qty: {int(r['Total Quantity'])}",
            axis=1
        ).tolist()

        choice = st.selectbox("Select Product:", ["-- Select --"] + options, key="addtx_select")

        sel_pid = None
        sel_row = None
        if choice != "-- Select --":
            sel_pid = int(choice.split("|")[0].strip())
            sel_row = prod_df[prod_df["Product ID"] == sel_pid].iloc[0]
            st.success(f"{sel_row['Product Name']}  | Available: {int(sel_row['Total Quantity'])}")

        cust_id = st.text_input("Customer ID (optional):", key="addtx_cust")
        qty = st.number_input("Quantity Sold:", min_value=1, value=1, key="addtx_qty")
        unit_price = st.number_input("Unit Price (0 = auto):", min_value=0.0, value=0.0, key="addtx_price")
        sale_date = st.date_input("Date of Sale:", value=date.today(), key="addtx_date")

        if st.button("💾 Create Transaction", key="addtx_create"):
            if sel_pid is None:
                st.error("Please select a product.")
            else:
                available = int(sel_row["Total Quantity"])
                if qty > available:
                    st.error(f"Not enough stock. Available: {available}")
                else:
                    if unit_price == 0.0:
                        unit_price = float(sel_row.get("Unit Price", 0.0))

                    tx = add_transaction(
                        customer_id=int(cust_id) if cust_id.strip().isdigit() else None,
                        product_id=sel_pid,
                        product_name=sel_row["Product Name"],
                        date_of_sale=sale_date,
                        quantity_sold=int(qty),
                        unit_price=float(unit_price)
                    )

                    # update product inventory on disk
                    prod_full = load_products()
                    prod_full["Product ID"] = pd.to_numeric(prod_full["Product ID"], errors="coerce")
                    mask = prod_full["Product ID"] == sel_pid
                    if mask.any():
                        idx = prod_full[mask].index[0]
                        new_qty = max(0, int(prod_full.loc[idx, "Total Quantity"]) - int(qty))
                        prod_full.loc[idx, "Total Quantity"] = new_qty
                        prod_full.loc[idx, "Total_Amount"] = new_qty * float(prod_full.loc[idx].get("Unit Price", 0.0))
                        if "Applied_Sales_Total" not in prod_full.columns:
                            prod_full["Applied_Sales_Total"] = 0
                        prod_full.loc[idx, "Applied_Sales_Total"] = int(prod_full.loc[idx, "Applied_Sales_Total"] or 0) + int(qty)
                        save_products(prod_full)

                    st.success("Transaction created and inventory updated.")
                    st.json(tx)
