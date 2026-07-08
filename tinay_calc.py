import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# PERSONALIZED APP CONFIGURATION
st.set_page_config(page_title="Tinay's Price Calculator", page_icon="🧮", layout="centered")
st.title("🧮 Tinay's Personal Retail Price Calculator")
st.markdown("Calculate wholesale item prices and manage your master store retail price book.")

tab1, tab2 = st.tabs(["📝 Price Calculator", "📊 Price Master List"])

# --- FIXED SECURE DIRECT CONNECTION ---
url = "https://google.com"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Replaced connection mapping to pull directly from your URL string
    df_master = conn.read(spreadsheet=url, ttl="0d")
    df_master.columns = df_master.columns.str.strip()
except Exception as e:
    # If the connection tool fails, pull the data as a clean public web reader
    try:
        sheet_id = "14XUh3otWt1EoVM3RuLPceHhAaKF5iigOQO44mMcN2Fo"
        csv_url = f"https://google.com{sheet_id}/export?format=csv"
        df_master = pd.read_csv(csv_url)
        df_master.columns = df_master.columns.str.strip()
    except:
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
    
    if prod_name:
        if st.button("📥 Save to Master Price List", use_container_width=True):
            new_entry = pd.DataFrame([{
                "Product Name": prod_name,
                "Capital Cost": capital,
                "Markup": f"{markup}%",
                "Profit": profit,
                "Selling Price": retail_price
            }])
            
            updated_df = pd.concat([df_master, new_entry], ignore_index=True)
            
            # Direct link fallback structure for updating rows safely
            try:
                conn.update(spreadsheet=url, data=updated_df)
                st.toast(f"✅ Successfully logged '{prod_name}' to cloud spreadsheet!")
                st.rerun()
            except Exception as update_error:
                st.error("🔒 Google API blocks remote writing without explicit credentials. Click below to add it directly:")
                sheet_id = "14XUh3otWt1EoVM3RuLPceHhAaKF5iigOQO44mMcN2Fo"
                form_url = f"https://google.com{sheet_id}/edit#gid=0"
                st.markdown(f"[🔗 Open Google Sheets to Log '{prod_name}' with Retail Price ₱{retail_price:,.2f}]({form_url})")
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
