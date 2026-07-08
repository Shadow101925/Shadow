import streamlit as st
import pandas as pd

# PERSONALIZED APP CONFIGURATION
st.set_page_config(page_title="Tinay's Price Calculator", page_icon="🧮", layout="centered")
st.title("🧮 Tinay's Personal Retail Price Calculator")
st.markdown("Calculate wholesale item prices and manage your master store retail price book.")

tab1, tab2 = st.tabs(["📝 Price Calculator", "📊 Price Master List"])

# --- DIRECT LIVE GOOGLE SHEETS CONNECTION ---
# Formats your Google Sheets link to export cleanly as a public CSV reader
sheet_id = "14XUh3otWt1EoVM3RuLPceHhAaKF5iigOQO44mMcN2Fo"
csv_url = f"https://google.com{sheet_id}/export?format=csv"

try:
    # Pull live data rows instantly without requiring local Secrets configuration
    df_master = pd.read_csv(csv_url)
    df_master.columns = df_master.columns.str.strip()
except Exception as e:
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
        
    st.markdown("---")
    
    # Unlocks action option dynamically when a string value is passed into the entry field
    if prod_name:
        # Created a public submission reference link for easy tracking
        form_url = f"https://google.com{sheet_id}/edit#gid=0"
        st.success(f"✨ Ready to save **{prod_name}** to your online database!")
        st.markdown(f"[🔗 Open Google Sheets to View or Edit Data Records]({form_url})")
    else:
        st.info("Type a Product Name above to unlock the database save options.")

# =========================================================
# TAB 2: PRICE MASTER LIST
with tab2:
    st.subheader("Your Cloud Price Master List")
    if df_master.empty:
        st.info("Your list is currently empty or loading...")
    else:
        # Display the live table from your Google Sheet cleanly
        st.dataframe(df_master, use_container_width=True)
