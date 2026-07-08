import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# PERSONALIZED APP CONFIGURATION
st.set_page_config(page_title="Tinay's Price Calculator", page_icon="🧮", layout="centered")
st.title("🧮 Tinay's Personal Retail Price Calculator")
st.markdown("Calculate wholesale item prices and manage your master store retail price book.")

tab1, tab2 = st.tabs(["📝 Price Calculator", "📊 Price Master List"])

# --- CLOUD GOOGLE SHEETS CONNECTION ---
# Establishes a secure pipeline to your online spreadsheet
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Read existing spreadsheet data rows safely
    url = "https://google.com"
    df_master = conn.read(spreadsheet=url)
    # Clean up column names to match Python expectations
    df_master.columns = df_master.columns.str.strip()
except Exception as e:
    st.error("Waiting for Cloud Setup Configuration link inside the Streamlit Dashboard...")
    df_master = pd.DataFrame(columns=["Product Name", "Capital Cost", "Markup", "Profit", "Final Retail Price"])

# =========================================================
# TAB 1: SMART PRICE CALCULATOR
with tab1:
    st.subheader("Compute Product Pricing")
    
    prod_name = st.text_input("Product Name", placeholder="e.g., Shampoo, Noodles, Soap")
    
    col1, col2 = st.columns(2)
    with col1:
        capital = st.number_input("Capital Cost (₱)", min_value=0.0, step=1.0, value=0.0)
    with col2:
        markup = st.number_input("Desired Markup (%)", min_value=0.0, step=1.0, value=10.0)
        
    profit = capital * (markup / 100.0)
    retail_price = capital + profit
    
    st.markdown("---")
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.metric(label="Profit per Unit", value=f"₱{profit:,.2f}")
    with res_col2:
        st.metric(label="Final Retail Selling Price", value=f"₱{retail_price:,.2f}")
        
    if not prod_name:
        st.info("Type a Product Name above to unlock the database save options.")

# =========================================================
# TAB 2: PRICE MASTER LIST
with tab2:
    st.subheader("Your Cloud Price Master List")
    if df_master.empty:
        st.info("Your list is currently empty or loading...")
    else:
        st.dataframe(df_master, use_container_width=True)







