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

# =========================================================
# CRITICAL DIRECT LINK CONFIGURATION
WEBHOOK_URL = "https://google.com"
SHEET_ID = "14XUh3otWt1EoVM3RuLPceHhAaKF5iigOQO44mMcN2Fo"
# =========================================================

# --- HIGH-RELIABILITY LIVE REFRESH DATA ENGINE ---
def fetch_live_matrix():
    try:
        # Standard format to force Google Sheets to output text records cleanly
        export_url = f"https://google.com{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet1&t={int(time.time())}"
        
        # Pull text tables straight into memory bypassing cache filters
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(export_url, headers=headers, timeout=10)
        
        if response.status_code == 200 and len(response.text.strip()) > 5:
            df = pd.read_csv(io.StringIO(response.text))
            
            # Standardize column headers to handle layout mapping variances
            df.columns = df.columns.str.strip().str.lower().str.replace(" ", "")
            
            mapping = {
                "productname": "Product Name", "product": "Product Name",
                "capitalcost": "Capital Cost", "capital": "Capital Cost",
                "markup": "Markup", "profit": "Profit",
                "sellingprice": "Selling Price", "selling": "Selling Price"
            }
            df = df.rename(columns=mapping)
            df = df.loc[:, ~df.columns.str.contains('^unnamed', na=False, case=False)]
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
                payload = {
                    "product": prod_name,
                    "capital": capital,
                    "markup": f"{markup}%",
                    "profit": round(profit, 2),
                    "selling": round(retail_price, 2)
                }
                
                with st.spinner("Writing direct row entry to database ledger..."):
                    try:
                        response = requests.post(WEBHOOK_URL, json=payload, timeout=15)
                        if response.status_code == 200 or "Success" in response.text:
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
    
    if not df_clean.empty and "Product Name" in df_clean.columns:
        df_clean["Product Name"] = df_clean["Product Name"].astype(str).str.strip()
        # Drop completely blank artifact noise rows cleanly
        df_clean = df_clean[
            (df_clean["Product Name"] != "") & 
            (df_clean["Product Name"] != "None") & 
            (df_clean["Product Name"].notna())
        ]
    
    if df_clean.empty:
        st.info("Your Google Sheet is connected! Use Tab 1 to insert your first item, then refresh.")
    else:
        st.dataframe(df_clean, use_container_width=True, hide_index=True)
