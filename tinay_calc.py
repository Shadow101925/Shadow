import streamlit as st
import pandas as pd
import requests

# APP CONFIGURATION
st.set_page_config(page_title="Tinay's Price Calculator", page_icon="🧮", layout="centered")
st.title("🧮 Tinay's Personal Retail Price Calculator")
st.markdown("Calculate wholesale item prices and manage your master store retail price book.")

tab1, tab2 = st.tabs(["📝 Price Calculator", "📊 Price Master List"])

# --- LIVE GOOGLE SHEETS VIEW CONNECTION ---
sheet_id = "14XUh3otWt1EoVM3RuLPceHhAaKF5iigOQO44mMcN2Fo"
csv_url = f"https://google.com{sheet_id}/export?format=csv"

try:
    df_master = pd.read_csv(csv_url)
    df_master.columns = df_master.columns.str.strip()
except Exception as e:
    df_master = pd.DataFrame(columns=["Product Name", "Capital Cost", "Markup", "Profit", "Selling Price"])

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
        
    st.markdown("---")
    
    # ⚠️ PASTE YOUR COPIED WEB APP URL INSIDE THE QUOTES BELOW:
    WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwn8dPZgJgb4nVMI9tXzc4RidlCLGX2N5uILXCwl7OfxelXvU4ytC_89J4A3UQnG85cjQ/exec"
    
    if prod_name:
        if st.button("📥 Save to Master Price List", use_container_width=True):
            payload = {
                "product": prod_name,
                "capital": capital,
                "markup": f"{markup}%",
                "profit": profit,
                "selling": retail_price
            }
            try:
                response = requests.post(WEBHOOK_URL, json=payload)
                if response.status_code == 200:
                    st.success(f"✅ Successfully saved '{prod_name}' directly to your Sheet!")
                    st.rerun()
                else:
                    st.error("Failed to connect to the database pipeline.")
            except Exception as e:
                st.error("Connection error. Make sure your Webhook URL is pasted correctly.")
    else:
        st.info("Type a Product Name above to unlock the database save options.")

# =========================================================
# TAB 2: PRICE MASTER LIST
with tab2:
    st.subheader("Your Cloud Price Master List")
    if df_master.empty:
        st.info("Your list is currently empty or loading...")
    else:
        st.dataframe(df_master, use_container_width=True)
