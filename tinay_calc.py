import streamlit as st
import pandas as pd
import requests
import time
import io

# APP CONFIGURATION
st.set_page_config(page_title="Tinay's Price Calculator", page_icon="🧮", layout="centered")
st.title("🧮 Tinay's Personal Retail Price Calculator")
st.markdown("Calculate wholesale item prices and manage your master store retail price book.")

tab1, tab2 = st.tabs(["📝 Price Calculator", "📊 Price Master List"])

# --- LIVE REFRESHING GOOGLE SHEETS VIEW ---
sheet_id = "14XUh3otWt1EoVM3RuLPceHhAaKF5iigOQO44mMcN2Fo"
# Bulletproof direct CSV export URL pattern that bypasses Google script blockades
csv_url = f"https://google.com{sheet_id}/export?format=csv&id={sheet_id}&gid=0&t={int(time.time())}"

try:
    # Mimics an official browser profile to stop Google from throwing empty frames
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(csv_url, headers=headers)
    
    if response.status_code == 200 and len(response.text.strip()) > 0:
        df_master = pd.read_csv(io.StringIO(response.text))
        df_master.columns = df_master.columns.str.strip()
    else:
        # Fallback if connection succeeds but sheet data returns blank
        df_master = pd.DataFrame(columns=["Product Name", "Capital Cost", "Markup", "Profit", "Selling Price"])
except Exception as e:
    # Structural fallback database schema
    df_master = pd.DataFrame(columns=["Product Name", "Capital Cost", "Markup", "Profit", "Selling Price"])

# =========================================================
# TAB 1: SMART PRICE CALCULATOR
with tab1:
    st.subheader("Compute Product Pricing")
    
    # Form structures ensure data variables are locked into session memory cleanly
    with st.form("calculator_form", clear_on_submit=False):
        prod_name = st.text_input("Product Name", placeholder="e.g., Shampoo, Noodles, Soap")
        
        col1, col2 = st.columns(2)
        with col1:
            capital = st.number_input("Capital Cost (₱)", min_value=0.0, step=1.0, value=0.0)
        with col2:
            markup = st.number_input("Desired Markup (%)", min_value=0.0, step=1.0, value=10.0)
            
        # Safe explicit math engine runtime
        profit = capital * (markup / 100.0)
        retail_price = capital + profit
        
        st.markdown("---")
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.metric(label="Profit per Unit", value=f"₱{profit:,.2f}")
        with res_col2:
            st.metric(label="Final Retail Selling Price", value=f"₱{retail_price:,.2f}")
        
        st.markdown("---")
        
        # FIX FOR ACCIDENTAL ENTER KEY SELECTION: Explicit safety switch verification requirement
        authorize_save = st.checkbox("Confirm: I am ready to push this calculation to the Cloud Sheet registry")
        
        submit_btn = st.form_submit_button("📥 Save to Master Price List", use_container_width=True)
        
        if submit_btn:
            if not prod_name.strip():
                st.warning("Please type a valid Product Name before saving.")
            elif not authorize_save:
                st.error("⚠️ Data blocked! You must check the confirmation box above before clicking save.")
            else:
                payload = {
                    "product": prod_name,
                    "capital": capital,
                    "markup": f"{markup}%",
                    "profit": round(profit, 2),
                    "selling": round(retail_price, 2)
                }
                
                WEBHOOK_URL = "https://google.com"
                
                with st.spinner("Uploading row entry directly to your cloud data books..."):
                    try:
                        response = requests.post(WEBHOOK_URL, json=payload)
                        if response.status_code == 200:
                            st.toast(f"✅ Successfully saved '{prod_name}' to your Master Sheet!")
                            time.sleep(1.0)
                            st.rerun()
                        else:
                            st.error(f"Failed to connect to pipeline. Server status: {response.status_code}")
                    except Exception as e:
                        st.error("Connection error. Make sure your Apps Script Webhook is active.")

# =========================================================
# TAB 2: PRICE MASTER LIST
with tab2:
    st.subheader("Your Cloud Price Master List")
    if df_master.empty or len(df_master) == 0:
        st.info("Your list is currently empty or loading live entries...")
        st.markdown("💡 *If your entries are not appearing, double check that your Google Sheet access settings are changed from 'Restricted' to 'Anyone with the link can view'.*")
    else:
        st.dataframe(df_master, use_container_width=True)
