import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

st.set_page_config(page_title="Celvia Cloud ERP", page_icon="☁️", layout="wide")
st.title("☁️ Celvia ERP - Live Connection Test")

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    # Secrets se JSON ki details aayengi
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # Aapki Sheet ID
    SHEET_ID = "1R9A5O1Z8Oh7t5K5En7GymT49Gf5Mao9FyVjn26KzkDU"
    
    st.info("Connecting to Google Cloud Servers... ⏳")
    sheet = client.open_by_key(SHEET_ID)
    st.success("✅ SUCCESS! Cloud Bot connected to Google Sheet securely!")
    
    st.subheader("📦 Live Data from 'Products' Tab:")
    worksheet = sheet.worksheet("Products") 
    data = worksheet.get_all_records()
    st.dataframe(pd.DataFrame(data))

except Exception as e:
    st.error(f"❌ Connection Fail: {e}")
