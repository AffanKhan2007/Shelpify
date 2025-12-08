🛒 Shelpify — Smart Inventory & Store Management System

Shelpify is a lightweight, modern, and modular inventory management application built with Streamlit.
It helps small and medium stores efficiently manage their products, stock levels, discounts, updates, and more — all from a clean and intuitive interface.

🚀 Features
🔹 Product Management

Add new products with:

Product ID

Name

Category

Type (Veg / Non-Veg / Other)

Price, Stock, and Value

Auto-generate IDs for new items

View, search, and edit existing products

🔹 Inventory Overview

Complete dashboard showing:

Total products

Total stock quantity

Total inventory value

Low-stock indicators

🔹 Discount Module

Apply discounts item-wise or category-wise

Supports custom % discounts on:

Products nearing expiry

Overstock situations

Includes an Auto Discount Dummy Tab where users can experiment without affecting live data

🔹 Updates Panel

Single location to show recent changes, including:

New items added

Stock changes

Discounts applied

Uses a built-in “Updates” icon for easy identification

🔹 Navigation System

Smooth page navigation using:

st.session_state.current_page = "add_product"
st.rerun()


Mimics multi-page behavior inside a single Streamlit script

🔹 User-Friendly UI

Clean welcome page with instructions

Simple sidebar navigation

Error handling for invalid inputs (negative dimensions, invalid coordinates, etc.)

Visual diagrams and plots for geometric/mathematical tools (if enabled)

🏗️ Project Structure
Shelpify/
│
├── app.py                    # Main application (navigation + pages)
├── pages/
│   ├── add_product.py        # Add new product page
│   ├── inventory.py          # Inventory overview
│   ├── discounts.py          # Auto discount dummy tab
│   ├── updates.py            # Update log
│   └── welcome.py            # Welcome page content
│
├── data/
│   └── products.csv          # Product database
│
├── utils/
│   ├── id_generator.py       # Automatic product ID generator
│   ├── database.py           # Read/write helpers
│   └── validators.py         # Input validation
│
└── README.md

⚙️ Installation
1️⃣ Clone the repository
git clone https://github.com/yourusername/shelpify.git
cd shelpify

2️⃣ Install dependencies
pip install -r requirements.txt

3️⃣ Run the application
streamlit run app.py

📘 How to Use
Welcome Page

Shows the purpose of Shelpify and links to all modules.

Add Product

Enter product details → Validate → Save to database.

Inventory

Displays all items in a searchable, sortable table with totals.

Discount Tab

Test or apply discounts category-wise or item-wise.

Updates

Shows the latest actions performed by the user.

🛠️ Tech Stack

Python 3.10+

Streamlit

Pandas

NumPy

Matplotlib (for diagrams if enabled)

🌱 Future Enhancements

Barcode scanning integration

GST & tax engine

Customer and purchase history tracking

Role-based login

Cloud sync and multi-store support
