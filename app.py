import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIG ---
st.set_page_config(page_title="PihuKaart Command Center", layout="wide", page_icon="🛒")

# --- DATABASE CONNECTION ---
@st.cache_resource
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

try:
    client = get_gspread_client()
    SHEET_ID = "1R9A5O1Z8Oh7t5K5En7GymT49GF5Mao9FyVjn26KzkDU"
    sheet = client.open_by_key(SHEET_ID)
except Exception as e:
    st.error(f"Database Connection Error: {e}")
    st.stop()

# --- CACHED DATA FETCHING ---
@st.cache_data(ttl=300) # 5 min auto-refresh
def fetch_data(worksheet_name):
    try:
        ws = sheet.worksheet(worksheet_name)
        return pd.DataFrame(ws.get_all_records())
    except Exception:
        return pd.DataFrame() # Return empty if sheet not found yet

# --- PIHUKAART SIDEBAR MENU (Exact AppSheet Replica) ---
st.sidebar.markdown("""
    <h2 style='text-align: center; color: #10b981; font-weight: 900;'>🛒 PihuKaart ERP</h2>
    <hr style='margin-top: 0; margin-bottom: 15px;'>
""", unsafe_allow_html=True)

menu_category = st.sidebar.radio("Main Navigation", [
    "📦 Products Manager",
    "🖨️ Packing Center",
    "📑 Orders & Returns",
    "💰 Cashflow & Expenses",
    "🛒 Stock & Packaging",
    "⚙️ Command Center"
])

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Force Refresh All Data"):
    st.cache_data.clear()
    st.rerun()

# ==========================================
#        MODULE 1: PRODUCTS MANAGER
# ==========================================
if menu_category == "📦 Products Manager":
    st.title("📦 Master Product Catalog")
    
    # Sub-tabs for Product section
    p_tab1, p_tab2, p_tab3 = st.tabs(["Products List", "Low Stock Alerts 🚨", "SKU Errors ⚠️"])
    
    with p_tab1:
        prod_df = fetch_data("Products")
        
        if not prod_df.empty:
            total_prods = len(prod_df)
            st.markdown(f"**Showing {total_prods} Active Products**")
            
            # Creating AppSheet Style Cards in Streamlit
            for index, row in prod_df.iterrows():
                name = row.get("Product Name", "Unknown")
                stock = row.get("Stock", 0)
                buy_price = row.get("Buy", 0)
                # Auto Calculate Value
                try:
                    value = int(stock) * float(buy_price)
                except:
                    value = 0
                
                img_url = str(row.get("Product Image", "https://via.placeholder.com/100?text=No+Img"))
                
                # Dynamic Red Color for Low Stock
                stock_color = "#ef4444" if isinstance(stock, (int, float)) and stock < 10 else "#64748b"
                title_color = "#ef4444" if isinstance(stock, (int, float)) and stock < 10 else "#1e293b"

                st.markdown(f"""
                <div style="background: white; border-radius: 12px; padding: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px; border-left: 5px solid {stock_color}; display: flex; align-items: center; gap: 20px;">
                    <img src="{img_url}" width="80" height="80" style="object-fit: contain; border-radius: 8px; border: 1px solid #e2e8f0; padding: 2px;">
                    <div style="flex-grow: 1;">
                        <h4 style="margin: 0 0 5px 0; color: {title_color}; font-size: 18px;">{name}</h4>
                        <p style="margin: 0; font-size: 14px; color: #64748b; font-weight: 600;">
                            Stock: <span style="color: {stock_color};">{stock}</span> | 
                            Buy: ₹{buy_price} | 
                            <span style="color: #10b981;">Value: ₹{value}</span>
                        </p>
                    </div>
                    <div style="cursor: pointer; font-size: 20px; color: #94a3b8;">⋮</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ 'Products' tab not found in Google Sheet or it is empty.")

    with p_tab2:
        st.subheader("🚨 Low Stock Alerts")
        st.info("Items with stock less than 10 will automatically appear here.")
        # Logic to filter prod_df where Stock < 10

    with p_tab3:
        st.subheader("⚠️ SKU Error / Flipkart Mapping")
        st.info("Unmapped SKUs from your Flipkart reports will be flagged here.")

# ==========================================
#        MODULE 2: PACKING CENTER
# ==========================================
elif menu_category == "🖨️ Packing Center":
    st.title("🖨️ Label Processing & Packing")
    st.success("✅ Yahan humara PDF Crop aur Multi-Upload wala code aayega jo pehle banaya tha.")
    # (Print portal code goes here)

# ==========================================
#        MODULE 3: ORDERS & RETURNS
# ==========================================
elif menu_category == "📑 Orders & Returns":
    st.title("📑 Orders & Returns Management")
    o_tab1, o_tab2 = st.tabs(["Orders Detail", "Returns Order 🔄"])
    
    with o_tab1:
        st.subheader("Upload Flipkart Dispatch File")
        st.file_uploader("Upload CSV", type=['csv'])
        
    with o_tab2:
        st.subheader("Process Customer Returns")
        with st.form("return_form"):
            st.text_input("Order ID")
            st.selectbox("Return Reason", ["Customer Return", "Courier Return", "Damaged"])
            st.form_submit_button("Log Return")

# ==========================================
#      MODULE 4: CASHFLOW & EXPENSES
# ==========================================
elif menu_category == "💰 Cashflow & Expenses":
    st.title("💰 Finance & Accounting")
    f_tab1, f_tab2, f_tab3 = st.tabs(["💸 Expenses", "💵 Add Cashflow", "📢 Ads Spend Entry"])
    
    with f_tab1:
        st.subheader("Record Daily Expense")
        with st.form("expense_form"):
            st.date_input("Date")
            st.selectbox("Category", ["Salary", "Office Rent", "Tea/Snacks", "Stationery", "Other"])
            st.number_input("Amount (₹)", min_value=0)
            st.text_input("Description")
            st.form_submit_button("Save Expense")
            
    with f_tab2:
        st.subheader("Log Incoming Cashflow")
        st.info("Form to record incoming settlements from Flipkart/Amazon.")
        
    with f_tab3:
        st.subheader("Advertising Spend")
        st.info("Log daily ad spends to accurately calculate PnL.")

# ==========================================
#      MODULE 5: STOCK & PACKAGING
# ==========================================
elif menu_category == "🛒 Stock & Packaging":
    st.title("🛒 Procurement & Inwarding")
    s_tab1, s_tab2, s_tab3 = st.tabs(["📦 New Stock Purchases", "🏷️ Packaging Purchase", "📦 Packaging Inventory"])
    
    with s_tab1:
        st.subheader("Inward New Stock")
        st.write("Add newly purchased items to inventory.")
        # Form for new stock

# ==========================================
#      MODULE 6: COMMAND CENTER
# ==========================================
elif menu_category == "⚙️ Command Center":
    st.title("⚙️ Danger Zone & System About")
    st.warning("☢️ Danger Zone: Admin settings, delete records, clear cache.")
    st.write("**App Version:** 2.0 (Streamlit Native)")
    st.write("**Database:** Connected & Active")
