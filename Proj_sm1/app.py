# app.py
import streamlit as st

from HomePage import render_home_info
from add_product_page import render_add_product_page
from remove_product_page import render_remove_product_page
from find_product_page import render_find_product_page
from analytics_page import render_analytics_page
from updates_page import render_updates_page
from sales_page import render_sales_page
from updates_page import render_updates_page
from discount_page import render_discount_page
from ui_components import render_header


# -------------------------
# Session init
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"
if "username" not in st.session_state:
    st.session_state.username = ""


# -------------------------
# Login
# -------------------------

def login_page():
    render_header()
    """### 👋 Welcome to Shelpify

Shelpify is your intelligent, all-in-one inventory and sales management system designed to help stores operate with accuracy, speed, and clarity.

### 🧠 What Shelpify Does
Shelpify brings together inventory control, expiry tracking, sales logging, and analytics into one smooth, automated platform. The system updates stock in real time, highlights products that are nearing expiry, tracks transactions, and provides meaningful insights into product performance and revenue trends.

### 🔍 Why Shelpify?
- Reduce waste through expiry alerts  
- Maintain accurate stock levels  
- Track sales instantly and automatically  
- Identify slow-moving and fast-moving products  
- Make smarter decisions with visual analytics  
- Enjoy a clean, modern dashboard experience  

### 🚀 How to Use This Dashboard
Use the tabs above to navigate through Shelpify:
- **Recent Updates:** Expired & near-expiry alerts  
- **Inventory Management:** Add, remove, and find products  
- **Inventory Analytics:** Stock levels, filters, trends  
- **Sales:** Create transactions and analyze customer behavior  
- **Auto Discounts:** Apply discounts to near-expiry products  

### ✔ Your Store, Smarter.
Shelpify helps you run your inventory the smart way — organized, automated, and always in your control.
"""
    st.title("📦 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        if not username.strip() or not password.strip():
            st.error("Both username and password are required.")
        else:
            st.session_state.logged_in = True
            st.session_state.username = username.strip()
            st.rerun()   # FIXED


def home_page():
    render_header()
    st.title(f"Welcome to Shelpify, {st.session_state.username} 👋")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        ["🏡 Home", "🔄 Recent Updates", "📦 Inventory Management", "📊 Inventory Analytics", "🛒 Sales", "💸 Auto Discounts","⚙️ Settings"]
    )

    # ---------------- TAB 1 : Home Page ----------------
    with tab1:
        render_home_info()

    # ---------------- TAB 2 : Recent Updates ----------------
    with tab2:
        render_updates_page()

    # ---------------- TAB 3 : Inventory Management ----------------
    with tab3:
        st.subheader("Inventory Actions")
        c1, c2, c3 = st.columns(3)

        with c1:
            if st.button("➕ Add Product", key="home_add"):
                st.session_state.current_page = "add_product"
                st.rerun()

        with c2:
            if st.button("🗑 Remove Product", key="home_remove"):
                st.session_state.current_page = "remove_product"
                st.rerun()

        with c3:
            if st.button("🔍 Find Product", key="home_find"):
                st.session_state.current_page = "find_product"
                st.rerun()

    # ---------------- TAB 4 : Analytics ----------------
    with tab4:
        render_analytics_page()

    # ---------------- TAB 5 : Sales ----------------
    with tab5:
        render_sales_page()

    # ---------------- TAB 5 : Auto Discounts ----------------
    with tab6:
        render_discount_page()

    # ---------------- TAB 6 : Settings ----------------
    with tab7:
        st.subheader("⚙️ Settings")
        st.info("User preferences and system controls will appear here.")

        # Logout button ONLY here
        if st.button("Logout", key="settings_logout"):
            st.session_state.logged_in = False
            st.rerun()


# -------------------------
# Router
# -------------------------
def router():
    page = st.session_state.current_page
    if page == "home":
        home_page()
    elif page == "add_product":
        render_add_product_page()
    elif page == "remove_product":
        render_remove_product_page()
    elif page == "find_product":
        render_find_product_page()
    else:
        st.write("Unknown page, going back home.")
        st.session_state.current_page = "home"
        st.experimental_rerun()


# -------------------------
# Main
# -------------------------
def main():
    st.set_page_config(page_title="Shelpify", page_icon="📦", layout="wide")

    if not st.session_state.logged_in:
        login_page()
    else:
        router()


if __name__ == "__main__":
    main()
