# ui_components.py
import streamlit as st

def render_header():
    logo_url = "https://www.vhv.rs/dpng/d/502-5023490_warehouse-vector-svg-inventory-management-system-logo-hd.png"   

    st.markdown(
        f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 18px;
            padding: 8px 4px;
        ">
            <img src="{logo_url}" style="width: 60px; height: 60px; border-radius: 8px;" />
            <h1 style="
                margin: 0;
                padding: 0;
                font-size: 42px;
                font-weight: 700;
                color: #333;
            ">Shelpify</h1>
        </div>
        <hr style="margin-top: 2px; margin-bottom: 20px;">
        """,
        unsafe_allow_html=True
    )
