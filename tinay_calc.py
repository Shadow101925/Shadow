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
# Uses the Visualization API endpoint and a timestamp to bypass caching and script blockades
csv_url = f"https://google.com{sheet_id}/gviz/tq?tqx=out:csv&t={int(time.time())}"

try:
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(csv_url, headers=headers)
    df_master = pd.read_csv(io.StringIO(response.text))
    df_master.columns = df_master.columns.str.strip()
except Exception as e:
    df_master = pd.DataFrame(columns=["Product Name", "Capital Cost", "Markup", "Profit", "Selling Price"])

# --- POPUP CONFIRMATION DIALOG ---
@st.dialog("Confirm Save to Master List")
def confirm_save_dialog(prod_name, capital, markup, profit, retail_price):
    st.write(f"Are you sure you want to add **{prod_name}**?")
    st.write(f"💰 **Capital Cost:** ₱{capital:,.2f}")
    st.write(f"📈 **Markup:** {markup}%")
    st.write(f"💵 **Profit:** ₱{profit:,.2f}")
    st.write(f"🎯 **Selling Price:** ₱{retail_price:,.2f}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ Cancel", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("🔥 Confirm & Save", type="primary", use_container_width=True):
            payload = {
                "product": prod_name,
                "capital": capital,
                "markup": f"{markup}%",
                "profit": round(profit, 2),
                "selling": round(retail_price, 2)
            }
            WEBHOOK_URL = "https://google.com"
            
            with st.spinner("Saving to cloud..."):
                try:
                    response = requests.post(WEBHOOK_URL, json=payload)
                    if response.status_code == 200:
                        st.toast(f"✅ Successfully saved '{prod_name}'!")
                        time.sleep(1.0)
                        st.rerun()
                    else:
                        st.error("Failed to connect to the database pipeline.")
                except Exception as e:
                    st.error("Connection error. Check your Webhook URL.")

# =========================================================
# TAB 1: SMART PRICE CALCULATOR
with tab1:
    st.subheader("Compute Product Pricing")
    
    # Form layout removed so values calculate and display dynamically
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
    
    submit_btn = st.button("📥 Save to Master Price List", use_container_width=True, type="primary")
    
    if submit_btn:
        if prod_name.strip():
            # Intercepts the workflow and triggers confirmation window
            confirm_save_dialog(prod_name, capital, markup, profit, retail_price)
        else:
            st.warning("Please type a valid Product Name before saving.")

# =========================================================
# TAB 2: PRICE MASTER LIST
with tab2:
    st.subheader("Your Cloud Price Master List")
    if df_master.empty or len(df_master) == 0:
        st.info("Your list is currently empty or loading live entries...")
    else:
        st.dataframe(df_master, use_container_width=True)
