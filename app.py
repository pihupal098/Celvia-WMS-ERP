import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px
import base64

# --- CONFIG & CONNECTION ---
st.set_page_config(page_title="Celvia A-to-Z ERP", layout="wide")

@st.cache_resource
def init_connection():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

client = init_connection()
SHEET_ID = "1R9A5O1Z8Oh7t5K5En7GymT49GF5Mao9FyVjn26KzkDU"
sheet = client.open_by_key(SHEET_ID)

# --- SIDEBAR NAVIGATION ---
st.sidebar.image("https://via.placeholder.com/150?text=Celvia+Logo", width=100)
st.sidebar.title("Celvia Control Center")
page = st.sidebar.radio("Go To:", ["📊 Dashboard", "📦 Inventory & SKUs", "📑 Order Manager", "💰 PnL Insights"])

# --- SHARED DATA FETCHING ---
@st.cache_data(ttl=600) # 10 min cache for speed
def load_data(sheet_name):
    return pd.DataFrame(sheet.worksheet(sheet_name).get_all_records())

# --- PAGES ---
if page == "📊 Dashboard":
    st.header("Business Overview")
    prod_df = load_data("Products")
    # Dashboard Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Master SKUs", len(prod_df))
    c2.metric("Today's Dispatch", "Check PDF Portal")
    c3.metric("System Health", "Connected")
    
    # Graph: Inventory Distribution
    fig = px.pie(prod_df, names='SKU', title="SKU Share in Catalog")
    st.plotly_chart(fig)

elif page == "📦 Inventory & SKUs":
    st.header("Master Product Database")
    prod_df = load_data("Products")
    st.dataframe(prod_df, use_container_width=True)
    
    if st.button("➕ Add New SKU (Coming Soon)"):
        st.info("Form system build ho raha hai...")

elif page == "📑 Order Manager":
    st.header("Order Tracking & Dispatch")
    st.warning("Yahan hum Flipkart CSV upload ka system banayenge.")
    # Placeholder for file uploader
    order_file = st.file_uploader("Upload Flipkart Order CSV", type=["csv"])

elif page == "💰 PnL Insights":
    st.header("Net Profit Analytics")
    st.markdown("---")
    # Simple PnL Logic UI
    st.write("📈 Logic: `Selling Price - All Costs = Net Profit`")
    st.info("PnL tab ko auto-calculate karne ke liye hum agle step mein columns map karenge.")

# --- FOOTER ---
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Force Refresh Data"):
    st.cache_data.clear()
    st.rerun()
