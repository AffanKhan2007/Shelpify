# data_model.py
import pandas as pd
import os
from datetime import datetime, timedelta

CSV_FILE = "product_data_manufacture_expiry.csv"  # <-- change here if your file name is different

COLUMNS = [
    "Product ID", "Product Name", "Category", "Type",
    "Unit Price", "Total Quantity", "Total_Amount",
    "Manufacture_Date", "Expiry_Days", "Expiry_Date",
]


# ---------------------------
# Loading / Saving
# ---------------------------
def load_products() -> pd.DataFrame:
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(CSV_FILE, index=False)
        return df

    df = pd.read_csv(CSV_FILE)

    # Ensure columns exist
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA

    # Keep only expected columns & order
    df = df[COLUMNS]

    # Convert types
    df["Product ID"] = pd.to_numeric(df["Product ID"], errors="coerce").astype("Int64")
    df["Unit Price"] = pd.to_numeric(df["Unit Price"], errors="coerce")
    df["Total Quantity"] = pd.to_numeric(df["Total Quantity"], errors="coerce")
    df["Total_Amount"] = pd.to_numeric(df["Total_Amount"], errors="coerce")

    df["Manufacture_Date"] = pd.to_datetime(df["Manufacture_Date"], errors="coerce").dt.date
    df["Expiry_Date"] = pd.to_datetime(df["Expiry_Date"], errors="coerce").dt.date

    return df


def save_products(df: pd.DataFrame) -> None:
    df.to_csv(CSV_FILE, index=False)


# ---------------------------
# Auto Type Detection
# ---------------------------
def auto_detect_type(product_name: str) -> str:
    name = (product_name or "").lower()

    nonveg_keywords = [
        "chicken", "fish", "meat", "mutton", "prawn", "prawns",
        "nugget", "sausage", "ham", "salami", "cold cut", "bacon"
    ]
    veg_keywords = ["fruit", "vegetable", "veg", "tomato", "potato", "greens"]
    inedible_keywords = [
        "detergent", "cleaner", "liquid", "soap", "tissue",
        "paste", "sanitizer", "shampoo", "toothpaste"
    ]

    if any(k in name for k in nonveg_keywords):
        return "Non-Veg"
    if any(k in name for k in veg_keywords):
        return "Veg"
    if any(k in name for k in inedible_keywords):
        return "Inedible"
    return "Veg"  # default edible


# ---------------------------
# Auto Expiry Days
# ---------------------------
def auto_expiry_days(product_name: str, product_type: str) -> int:
    name = (product_name or "").lower()
    pt = (product_type or "").lower()

    if pt == "inedible":
        return 548  # 1.5 years approx

    nonveg_keywords = ["chicken", "meat", "fish", "prawn", "mutton"]
    coldcut_keywords = ["sausage", "ham", "salami", "cold cut", "bacon"]
    fruitveg_keywords = ["fruit", "veg", "vegetable", "tomato", "potato"]
    juice_keywords = ["juice"]
    grain_keywords = ["rice", "wheat", "cereal", "grain", "dal", "lentil"]

    if any(k in name for k in nonveg_keywords):
        return 7
    if any(k in name for k in coldcut_keywords):
        return 365
    if any(k in name for k in fruitveg_keywords):
        return 7
    if any(k in name for k in juice_keywords):
        return 180
    if any(k in name for k in grain_keywords):
        return 365

    return 7  # default edible expiry


# ---------------------------
# Product ID Generation
# ---------------------------
def _range_for_type(product_type: str) -> tuple[int, int]:
    pt = product_type.lower()
    if pt == "non-veg":
        return 4200, 4299
    if pt == "veg":
        return 4700, 4899  # you allowed 4800 too
    if pt == "inedible":
        return 5700, 5799
    # default: treat as veg
    return 4700, 4899


def generate_product_id(df: pd.DataFrame, product_type: str) -> int:
    start, end = _range_for_type(product_type)
    existing = df["Product ID"].dropna().astype(int)
    in_range = existing[(existing >= start) & (existing <= end)]

    if in_range.empty:
        candidate = start + 1
    else:
        candidate = int(in_range.max()) + 1

    if candidate > end:
        raise ValueError(
            f"No more Product IDs available for type '{product_type}' "
            f"in range {start}-{end}."
        )
    return candidate


# ---------------------------
# Validation Helpers
# ---------------------------
def validate_manufacture_date(manu_date) -> tuple[str | None, str | None]:
    """
    Returns (error_msg, warning_msg).
    error_msg != None => block.
    warning_msg != None => show but allow.
    """
    today = datetime.now().date()
    if manu_date > today:
        return "Manufacture date cannot be in the future.", None

    if (today - manu_date).days > 182:  # ~6 months
        return None, (
            "This product was manufactured over 6 months ago. "
            "It might be too old for certain purposes."
        )

    return None, None


def check_expired(manu_date, expiry_days: int) -> tuple[bool, datetime.date]:
    expiry_date = manu_date + timedelta(days=int(expiry_days))
    today = datetime.now().date()
    return expiry_date < today, expiry_date
