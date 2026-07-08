import streamlit as st
import pandas as pd
import requests
import time

# APP CONFIGURATION
st.set_page_config(page_title="Tinay's Price Calculator", page_icon="🧮", layout="centered")
st.title("🧮 Tinay's Personal Retail Price Calculator")
st.markdown("Calculate wholesale item prices and manage your master store retail price book.")

# Webhook configuration pipeline
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwm0XqttmJPpzw7YvWoC0m7ehfGVcPjU9VphzxHT5Zh9zXeaZpYZJ8ulQ-9HvexVaxrhg/exec"

tab1, tab2 = st.tabs(["📝 Price Calculator", "📊 Price Master List"])

# --- LIVE REFRESHING GOOGLE SHEETS VIEW ---
sheet_id = "14XUh3otWt1EoVM3RuLPceHhAaKF5iigOQO44mMcN2Fo"
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&t={int(time.time())}"

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
    
    # 1. Input Section (Moved outside a traditional Form to handle multi-step confirmation popups)
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
    
    # Main action button
    submit_btn = st.button("📥 Save to Master Price List", use_container_width=True, type="primary")
    
    # Check states when the user tries to save
    if submit_btn:
        if not prod_name.strip():
            st.warning("Please type a valid Product Name before saving.")
        else:
            # Check if product is already in the spreadsheet
            if check_exists(prod_name):
                st.session_state["show_overwrite_dialog"] = True
                st.session_state["pending_payload"] = {
                    "action": "save",
                    "product": prod_name.strip(),
                    "capital": capital,
                    "markup": f"{markup}%",
                    "profit": profit,
                    "selling": retail_price
                }
            else:
                # Direct save if it is a completely new item
                payload = {
                    "action": "save",
                    "product": prod_name.strip(),
                    "capital": capital,
                    "markup": f"{markup}%",
                    "profit": profit,
                    "selling": retail_price
                }
                try:
                    response = requests.post(WEBHOOK_URL, json=payload)
                    if response.status_code == 200:
                        st.toast(f"✅ Successfully saved '{prod_name}' directly to your Sheet!")
                        time.sleep(1.0)
                        st.rerun()
                    else:
                        st.error("Failed to connect to the database pipeline.")
                except Exception as e:
                    st.error("Connection error. Make sure your Webhook URL is pasted correctly.")

    # OVERWRITE POPUP / DIALOG CONTAINER
    if st.session_state.get("show_overwrite_dialog", False):
        st.markdown("---")
        st.warning(f"⚠️ **Notice:** '{prod_name}' already exists in your Master Price List. Do you want to overwrite it?")
        
        choice_col1, choice_col2 = st.columns(2)
        with choice_col1:
            if st.button("Yes, Overwrite Existing", use_container_width=True, type="danger"):
                try:
                    response = requests.post(WEBHOOK_URL, json=st.session_state["pending_payload"])
                    if response.status_code == 200:
                        st.toast(f"🔄 Correctly updated '{prod_name}' in your Sheet!")
                        st.session_state["show_overwrite_dialog"] = False
                        time.sleep(1.0)
                        st.rerun()
                    else:
                        st.error("Failed to update entry.")
                except Exception as e:
                    st.error("Connection error.")
        with choice_col2:
            if st.button("Cancel", use_container_width=True):
                st.session_state["show_overwrite_dialog"] = False
                st.rerun()

# =========================================================
# TAB 2: PRICE MASTER LIST & DELETION INTERFACE
with tab2:
    st.subheader("Your Cloud Price Master List")
    if df_master.empty or len(df_master) == 0:
        st.info("Your list is currently empty or loading live entries...")
    else:
        st.markdown("Select item rows below to remove them from your spreadsheet database.")
        
        # Create an interactive grid using checkboxes alongside the rows
        to_delete = []
        
        # Display Header Row
        head_col1, head_col2, head_col3 = st.columns([1, 4, 2])
        head_col1.markdown("**Delete**")
        head_col2.markdown("**Product Name**")
        head_col3.markdown("**Retail Price**")
        st.markdown("---")
        
        # Render check box rows manually for precise selective deletion operations
        for index, row in df_master.iterrows():
            p_name = row.get("Product Name", "Unknown")
            p_price = row.get("Selling Price", "0.0")
            
            c1, c2, c3 = st.columns([1, 4, 2])
            # Checkbox key must be unique per product row element
            if c1.checkbox("🗑️", key=f"del_{index}_{p_name}"):
                to_delete.append(p_name)
            c2.text(p_name)
            c3.text(f"₱{p_price}")
            
        st.markdown("---")
        
        # Multi-Item Action Button for Deletion
        if len(to_delete) > 0:
            st.error(f"Ready to remove {len(to_delete)} item(s) from your data records.")
            if st.button("🚨 Permanently Delete Selected Products", use_container_width=True, type="primary"):
                success_count = 0
                for delete_target in to_delete:
                    try:
                        del_payload = {"action": "delete", "product": delete_target}
                        response = requests.post(WEBHOOK_URL, json=del_payload)
                        if response.status_code == 200:
                            success_count += 1
                    except Exception:
                        pass
                
                if success_count > 0:
                    st.toast(f"🗑️ Successfully removed {success_count} item(s) from Google Sheets!")
                    time.sleep(1.0)
                    st.rerun()
                else:
                    st.error("Failed to delete entries. Please try again.")
