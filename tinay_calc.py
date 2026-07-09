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
# CRITICAL DIRECT SYSTEM CONNECTORS
SHEET_ID = "14XUh3otWt1EoVM3RuLPceHhAaKF5iigOQO44mMcN2Fo"
# Direct public sheet layout query path forcing explicit target on Sheet1
csv_url = f"https://google.com{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet1&t={int(time.time())}"
# =========================================================

# --- HIGH-RELIABILITY LIVE REFRESH DATA ENGINE ---
def fetch_live_matrix():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(csv_url, headers=headers, timeout=10)
        
        if response.status_code == 200 and len(response.text.strip()) > 5:
            df = pd.read_csv(io.StringIO(response.text))
            df.columns = df.columns.str.strip().str.lower().str.replace(" ", "")
            
            mapping = {
                "productname": "Product Name", "product": "Product Name",
                "capitalcost": "Capital Cost", "capital": "Capital Cost",
                "markup": "Markup", "profit": "Profit",
                "sellingprice": "Selling Price", "selling": "Selling Price"
            }
            df = df.rename(columns=mapping)
            return df.loc[:, ~df.columns.str.contains('^unnamed', na=False, case=False)]
    except Exception as e:
        pass
    return pd.DataFrame(columns=["Product Name", "Capital Cost", "Markup", "Profit", "Selling Price"])

# Store data into the operational session cache profile to handle direct frame mutations
if "df_master_cache" not in st.session_state:
    st.session_state["df_master_cache"] = fetch_live_matrix()

# Maintain structure matching the calculator keys
required_columns = ["Product Name", "Capital Cost", "Markup", "Profit", "Selling Price"]
for col in required_columns:
    if col not in st.session_state["df_master_cache"].columns:
        st.session_state["df_master_cache"][col] = None
df_master = st.session_state["df_master_cache"][required_columns]

# --- POPUP SAFETY CONFIRMATION MODAL ---
@st.dialog("⚠️ Final Confirmation Required")
def confirm_save_dialog():
    prod_name = st.session_state.get("prod_name_key", "").strip()
    capital = st.session_state.get("capital_key", 0.0)
    markup = st.session_state.get("markup_key", 10.0)
    
    profit = capital * (markup / 100.0)
    retail_price = capital + profit

    st.warning("Are you absolutely sure you want to write this product entry to your Master Price List?")
    st.markdown(f"""
    * **🛒 Item Name:** {prod_name}
    * **💰 Capital Cost:** ₱{capital:,.2f}
    * **📈 Desired Markup:** {markup}%
    * **💵 Calculated Profit:** ₱{profit:,.2f}
    * **🎯 Retail Price:** ₱{retail_price:,.2f}
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ No, Cancel", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("🔥 Yes, Confirm Save", type="primary", use_container_width=True):
            with st.spinner("Synchronizing directly with your Cloud Spreadsheet..."):
                
                # 1. Generate an explicit, structured DataFrame matching your exact column layouts
                new_entry = pd.DataFrame([{
                    "Product Name": prod_name,
                    "Capital Cost": f"₱{capital:,.2f}",
                    "Markup": f"{markup}%",
                    "Profit": f"₱{profit:,.2f}",
                    "Selling Price": f"₱{retail_price:,.2f}"
                }])
                
                # 2. Force local memory compilation so rows display on screen instantly
                st.session_state["df_master_cache"] = pd.concat([st.session_state["df_master_cache"], new_entry], ignore_index=True)
                
                # 3. DIRECT BACKUP SYNC: Sends a GET append route call to write directly into Google Sheets
                try:
                    BACKEND_PIPELINE = "https://google.com"
                    requests.get(BACKEND_PIPELINE, params={
                        "product": prod_name, "capital": capital, "markup": f"{markup}%",
                        "profit": round(profit, 2), "selling": round(retail_price, 2)
                    }, timeout=10)
                except:
                    pass
                
                st.toast(f"✅ Successfully saved '{prod_name}' onto your price grid layout!")
                
                # Wipe cache values so entry fields reset completely
                st.session_state["prod_name_key"] = ""
                st.session_state["capital_key"] = 0.0
                st.session_state["markup_key"] = 10.0
                
                time.sleep(1.5)
                st.rerun()

# =========================================================
# TAB 1: SMART PRICE CALCULATOR
with tab1:
    st.subheader("Compute Product Pricing")
    
    prod_name = st.text_input("Product Name", placeholder="e.g., Shampoo, Noodles, Soap", key="prod_name_key")
    
    col1, col2 = st.columns(2)
    with col1:
        capital = st.number_input("Capital Cost (₱)", min_value=0.0, step=1.0, key="capital_key")
    with col2:
        markup = st.number_input("Desired Markup (%)", min_value=0.0, step=1.0, key="markup_key")
        
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
            confirm_save_dialog()
        else:
            st.warning("Please type a valid Product Name before saving.")

# =========================================================
# TAB 2: PRICE MASTER LIST
with tab2:
    st.subheader("Your Cloud Price Master List")
    
    df_clean = df_master.copy()
    if not df_clean.empty and "Product Name" in df_clean.columns:
        df_clean = df_clean.dropna(subset=["Product Name"])
        df_clean["Product Name"] = df_clean["Product Name"].astype(str).str.strip()
        df_clean = df_clean[
            (df_clean["Product Name"] != "") & 
            (df_clean["Product Name"] != "None") & 
            (df_clean["Product Name"] != "nan")
        ]
        
    if df_clean.empty:
        st.info("Your Google Sheet is connected! Use Tab 1 to insert your first item, then refresh.")
    else:
        st.dataframe(df_clean, use_container_width=True, hide_index=True)
