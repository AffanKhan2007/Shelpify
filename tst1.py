import streamlit as st

# --- PAGE CONFIG ---
st.set_page_config(page_title="Shelpify – Inventory Management", page_icon="📦", layout="centered")

# --- SESSION STATES ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_page" not in st.session_state:
    st.session_state.current_page = "home"   # home, add_product, remove_product, find_product


# ---------------------------------------------------------
#  LOGIN PAGE
# ---------------------------------------------------------
def login_page():
    st.title("📦 Shelpify")
    st.subheader("Smart Inventory Management System")

    st.write("### Login to Continue")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        if username.strip() == "" or password.strip() == "":
            st.error("Please enter both username and password.")
        else:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()

    st.markdown(
        "<p style='color: gray; font-size: 13px;'>*Dummy login — username & password required*</p>",
        unsafe_allow_html=True
    )


# ---------------------------------------------------------
#  INVENTORY SUBPAGES
# ---------------------------------------------------------
def add_product_page():
    st.title("➕ Add Product")
    st.write("This is the add product page.")

    if st.button("⬅ Back to Inventory"):
        st.session_state.current_page = "home"
        st.rerun()


def remove_product_page():
    st.title("🗑 Remove Product")
    st.write("This is the remove product page.")

    if st.button("⬅ Back to Inventory"):
        st.session_state.current_page = "home"
        st.rerun()


def find_product_page():
    st.title("🔍 Find Product")
    st.write("This is the find product page.")

    if st.button("⬅ Back to Inventory"):
        st.session_state.current_page = "home"
        st.rerun()


# ---------------------------------------------------------
#  MAIN HOME PAGE (WITH 4 TABS)
# ---------------------------------------------------------
def home_page():
    st.title(f"Welcome to Shelpify, {st.session_state.username} 👋")
    st.write("### Your Dashboard")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📦 Inventory", "🛒 Sales", "📊 Analytics", "⚙️ Settings"
    ])

    # -------------------------------------------------
    # TAB 1 — INVENTORY
    # -------------------------------------------------
    with tab1:
        st.subheader("Inventory")

        st.write("Choose an action:")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("➕ Add Product"):
                st.session_state.current_page = "add_product"
                st.rerun()

        with col2:
            if st.button("🗑 Remove Product"):
                st.session_state.current_page = "remove_product"
                st.rerun()

        with col3:
            if st.button("🔍 Find Product"):
                st.session_state.current_page = "find_product"
                st.rerun()

    # -------------------------------------------------
    # OTHER TABS (PLACEHOLDERS)
    # -------------------------------------------------
    with tab2:
        st.subheader("Sales")
        st.info("Sales data and billing features will appear here.")

    with tab3:
        st.subheader("Analytics")
        st.info("Analytics, graphs, and insights will appear here.")

    with tab4:
        st.subheader("Settings")
        st.info("User settings and preferences.")

    st.markdown("---")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()


# ---------------------------------------------------------
#  PAGE ROUTER
# ---------------------------------------------------------
def page_router():
    page = st.session_state.current_page

    if page == "home":
        home_page()
    elif page == "add_product":
        add_product_page()
    elif page == "remove_product":
        remove_product_page()
    elif page == "find_product":
        find_product_page()


# ---------------------------------------------------------
#  MAIN APP LOGIC
# ---------------------------------------------------------
if not st.session_state.logged_in:
    login_page()
else:
    page_router()
    gyhififjv


