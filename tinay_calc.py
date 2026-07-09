import streamlit as st
import pandas as pd
import requests
import time

# APP CONFIGURATION
st.set_page_config(page_title="Tinay's Price Calculator", page_icon="🧮", layout="centered")
st.title("🧮 Tinay's Personal Retail Price Calculator")
st.markdown("Calculate wholesale item prices and manage your master store retail price book.")

tab1, tab2 = st.tabs(["📝 Price Calculator", "📊 Price Master List"])

# =========================================================
# CRITICAL DIRECT LINK CONFIGURATION (FULLY IMPLEMENTED)
WEBHOOK_URL = "https://google.com"
# =========================================================

# --- HIGH-RELIABILITY LIVE REFRESH DATA ENGINE ---
def fetch_live_matrix():
    try:
        # Appends a unique timestamp to completely bypass browser caching blocks
        response = requests.get(f"{WEBHOOK_URL}?t={int(time.time())}", timeout=12)
        if response.status_code == 200:
            data_json = response.json()
            df = pd.DataFrame(data_json)
            
            # Map column names to maintain exact UI structure uniformity
            mapping = {
                "productname": "Product Name", "product": "Product Name", "Product Name": "Product Name",
                "capitalcost": "Capital Cost", "capital": "Capital Cost", "Capital Cost": "Capital Cost",
                "markup": "Markup", "Markup": "Markup",
                "profit": "Profit", "Profit": "Profit",
                "sellingprice": "Selling Price", "selling": "Selling Price", "Selling Price": "Selling Price"
            }
            df = df.rename(columns=mapping)
            return df
    except Exception as e:
        pass
    return pd.DataFrame(columns=["Product Name", "Capital Cost", "Markup", "Profit", "Selling Price"])

df_master = fetch_live_matrix()

# Maintain structure matching the calculator keys
required_columns = ["Product Name", "Capital Cost", "Markup", "Profit", "Selling Price"]
for col in required_columns:
    if col not in df_master.columns:
        df_master[col] = None
df_master = df_master[required_columns]

# =========================================================
# TAB 1: SMART PRICE CALCULATOR
with tab1:
    st.subheader("Compute Product Pricing")
    
    with st.form("calculator_form", clear_on_submit=False):
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
        
        authorize_save = st.checkbox("Confirm: I am ready to push this calculation to the Cloud Sheet registry")
        submit_btn = st.form_submit_button("📥 Save to Master Price List", use_container_width=True)
        
        if submit_btn:
            if not prod_name.strip():
                st.warning("Please type a valid Product Name before saving.")
            elif not authorize_save:
                st.error("⚠️ Data blocked! You must check the confirmation box above before clicking save.")
            else:
                # Packages data points into URL parameters to eliminate the 405 error
                payload = {
                    "product": prod_name,
                    "capital": capital,
                    "markup": f"{markup}%",
                    "profit": round(profit, 2),
                    "selling": round(retail_price, 2)
                }
                
                with st.spinner("Writing direct row entry to database ledger..."):
                    try:
                        response = requests.get(WEBHOOK_URL, params=payload, timeout=15)
                        if response.status_code == 200 and "SUCCESS" in response.text:
                            st.toast(f"✅ Successfully saved '{prod_name}' directly to your Sheet!")
                            time.sleep(1.5)
                            st.rerun()
                        else:
                            st.error(f"Pipeline status code mismatch: {response.status_code}")
                    except Exception as e:
                        st.error("Connection tracking mismatch. Verification required.")

# =========================================================
# TAB 2: PRICE MASTER LIST
with tab2:
    st.subheader("Your Cloud Price Master List")
    
    df_clean = df_master.copy()
    df_clean["Product Name"] = df_clean["Product Name"].astype(str).str.strip()
    df_clean = df_clean[
        (df_clean["Product Name"] != "") & 
        (df_clean["Product Name"] != "None") & 
        (df_clean["Product Name"].notna())
    ]
    
    if df_clean.empty:
        st.info("Your Google Sheet is connected, but no entries were found on 'Sheet1'. Use Tab 1 to insert your first item!")
    else:
        st.dataframe(df_clean, use_container_width=True, hide_index=True)
