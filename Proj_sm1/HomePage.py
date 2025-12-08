# HomePage.py
import streamlit as st

def render_home_info():
    """
    User-defined function to display general information 
    without rendering a duplicate header.
    """
    st.title("🏠 Welcome to Shelpify Dashboard")

    st.write("""
        ## What is Shelpify?

        **Shelpify** is an intelligent inventory and sales management
        system designed to help businesses automate stock tracking,
        sales logging, analytics, and expiry monitoring.

        ### 🌟 Key Features
        - Real-time inventory management
        - Automated sales-to-stock updates
        - Expiry & near-expiry alerts
        - Visual analytics & revenue reports
        - Customer transaction tracking
        - Fast, clean UI with smart automation

        ### 🚀 Getting Started
        Use the tabs above to access all modules.
    """)
