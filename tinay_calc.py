import streamlit as st
import pandas as pd
import requests
import time

# APP CONFIGURATION
st.set_page_config(page_title="Tinay's Price Calculator", page_icon="🧮", layout="centered")
st.title("🧮 Tinay's Personal Retail Price Calculator")
st.markdown("Calculate wholesale item prices and manage your master store retail price book.")

tab1, tab2 = st.tabs(["📝 Price Calculator", "📊 Price Master List"])

# --- LIVE REFRESHING GOOGLE SHEETS VIEW ---
sheet_id = "14XUh3otWt1EoVM3RuLPceHhAaKF5iigOQO44mMcN2Fo"
# Appended an auto-updating time integer string to destroy old browser caches
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&t={int(time.time())}"

try:
    df_master = pd.read_csv(csv_url)
    df_master.columns = df_master.columns.str.strip()
except Exception as e:
    df_master = pd.DataFrame(columns=["Product Name", "Capital Cost", "Markup", "Profit", "Selling Price"])

# =========================================================
# TAB 1: SMART PRICE CALCULATOR
with tab1:
    st.subheader("Compute Product Pricing")
    
    with st.form("calculator_form", clear_on_submit=True):
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
        
        # ⚠️ REMEMBER TO REPLACE THIS WITH YOUR WEB APP URL GENERATED IN GOOGLE APPS SCRIPT:
        WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwm0XqttmJPpzw7YvWoC0m7ehfGVcPjU9VphzxHT5Zh9zXeaZpYZJ8ulQ-9HvexVaxrhg/exec
"
        
        submit_btn = st.form_submit_button("📥 Save to Master Price List", use_container_width=True)
        
        if submit_btn:
            if prod_name.strip():
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
                        st.toast(f"✅ Successfully saved '{prod_name}' directly to your Sheet!")
                        time.sleep(0.5) # Short rest interval to allow Google servers to finalize row additions
                        st.rerun()
                    else:
                        st.error("Failed to connect to the database pipeline.")
                except Exception as e:
                    st.error("Connection error. Make sure your Webhook URL is pasted correctly.")
            else:
                st.warning("Please type a valid Product Name before saving.")

# =========================================================
# TAB 2: PRICE MASTER LIST
with tab2:
    st.subheader("Your Cloud Price Master List")
    if df_master.empty or len(df_master) == 0:
        st.info("Your list is currently empty or loading live entries...")
    else:
        # Display the live table from your Google Sheet cleanly
        st.dataframe(df_master, use_container_width=True)
