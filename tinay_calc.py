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
csv_url = f"https://google.com{sheet_id}/export?format=csv&t={int(time.time())}"

try:
    df_master = pd.read_csv(csv_url)
    df_master.columns = df_master.columns.str.strip()
except Exception as e:
    df_master = pd.DataFrame(columns=["Product Name", "Capital Cost", "Markup", "Profit", "Selling Price"])

# Helper function to check if a product already exists case-insensitively
def check_exists(name):
    if not df_master.empty and "Product Name" in df_master.columns:
        return name.strip().lower() in df_master["Product Name"].astype(str).str.strip().str.lower().values
    return False

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
        WEBHOOK_URL = "https://google.com"
        
        submit_btn = st.form_submit_button("📥 Save to Master Price List", use_container_width=True)
        
        if submit_btn:
            if prod_name.strip():
                # Store the data payload layout ready for submission actions
                st.session_state["pending_payload"] = {
                    "action": "save",
                    "product": prod_name.strip(),
                    "capital": capital,
                    "markup": f"{markup}%",
                    "profit": profit,
                    "selling": retail_price
                }
                
                # Check if it already exists to determine if we trigger a confirmation prompt
                if check_exists(prod_name):
                    st.session_state["show_overwrite_dialog"] = True
                    st.session_state["duplicate_product_name"] = prod_name.strip()
                else:
                    # Clear modal trigger state and direct save for fresh items
                    st.session_state["show_overwrite_dialog"] = False
                    try:
                        response = requests.post(WEBHOOK_URL, json=st.session_state["pending_payload"])
                        if response.status_code == 200:
                            st.toast(f"✅ Successfully saved '{prod_name}' directly to your Sheet!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("Failed to connect to the database pipeline.")
                    except Exception as e:
                        st.error("Connection error. Make sure your Webhook URL is pasted correctly.")
            else:
                st.warning("Please type a valid Product Name before saving.")

    # 🚨 INTERACTIVE OVERWRITE POPUP SYSTEM (Placed outside the form to allow secondary click tracking options)
    if st.session_state.get("show_overwrite_dialog", False):
        dup_name = st.session_state.get("duplicate_product_name", "This item")
        st.markdown("---")
        st.warning(f"⚠️ **Notice:** '{dup_name}' already exists in your Master Price List. Do you want to overwrite it?")
        
        choice_col1, choice_col2 = st.columns(2)
        with choice_col1:
            if st.button("Yes, Overwrite Existing", use_container_width=True, type="danger", key="confirm_overwrite_btn"):
                try:
                    response = requests.post(WEBHOOK_URL, json=st.session_state["pending_payload"])
                    if response.status_code == 200:
                        st.toast(f"🔄 Correctly updated '{dup_name}' in your Sheet!")
                        st.session_state["show_overwrite_dialog"] = False
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Failed to update entry.")
                except Exception as e:
                    st.error("Connection error.")
        with choice_col2:
            if st.button("Cancel", use_container_width=True, key="cancel_overwrite_btn"):
                st.session_state["show_overwrite_dialog"] = False
                st.rerun()

# =========================================================
# TAB 2: PRICE MASTER LIST
with tab2:
    st.subheader("Your Cloud Price Master List")
    if df_master.empty or len(df_master) == 0:
        st.info("Your list is currently empty or loading live entries...")
    else:
        # Display the live table from your Google Sheet cleanly
        st.dataframe(df_master, use_container_width=True)
