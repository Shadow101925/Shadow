import streamlit as st
import pandas as pd
import requests
import time
import io

# APP CONFIGURATION
st.set_page_config(page_title="Tinay's Price Calculator", page_icon="🧮", layout="centered")

# --- PINAKABAGONG VISIBILITY THEME STYLING (FIXED) ---
st.markdown("""
    <style>
    /* Binabago ang background ng buong app */
    .stApp {
        background-color: #FFF0F5; /* Soft Lavender Pink */
    }
    
    /* Pwersahang ginagawang madilim ang text sa labas para readable sa pink background */
    h1, h2, h3, p, label, .stMarkdown, span {
        color: #1E1E1E !important; /* Dark Charcoal Text */
    }
    
    /* 🚀 TARGETING NEW DIALOG: Puwersahang ginagawang Puti ang background ng bagong Pop-up containers */
    .stDialog > div, div[data-testid="stDialog"] > div, div[role="dialog"] {
        background-color: #FFFFFF !important; /* Pure White Background para sa Pop-up */
        border-radius: 12px !important;
        box-shadow: 0px 10px 25px rgba(0,0,0,0.3) !important;
    }
    
    /* Siguraduhing madilim at malinaw ang lahat ng text sa loob ng bagong Pop-up model layout */
    .stDialog h1, .stDialog h2, .stDialog h3, .stDialog p, .stDialog li, .stDialog span, .stDialog div,
    div[data-testid="stDialog"] h1, div[data-testid="stDialog"] h2, div[data-testid="stDialog"] h3, 
    div[data-testid="stDialog"] p, div[data-testid="stDialog"] li, div[data-testid="stDialog"] span, div[data-testid="stDialog"] div {
        color: #1E1E1E !important; /* Dark Charcoal para kitang-kita sa puting pop-up */
    }
    
    /* Disenyo ng buong Tab Section */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
    }
    
    /* Disenyo para sa LAHAT ng Tabs kapag hindi pa kiniclick */
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        background-color: #FFD1DC !important; /* Soft Pastel Baby Pink para sa inactive tab */
        border-radius: 8px 8px 0px 0px;
        padding: 10px 24px;
        color: #444444 !important;
        font-weight: normal;
        border: none !important;
        transition: all 0.3s ease;
    }
    
    /* Disenyo para sa SELECTED o ACTIVE Tab */
    .stTabs [aria-selected="true"] {
        background-color: #FF69B4 !important; /* Matingkad na Hot Pink para sa Selected Tab */
        color: #FFFFFF !important; /* Puting text para litaw */
        font-weight: bold !important;
        box-shadow: 0px 4px 10px rgba(255, 105, 180, 0.3);
    }
    
    /* Tinatanggal ang pulang underline line sa ilalim ng tabs */
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🧮 Tinay's Personal Retail Price Calculator")
st.markdown("Calculate wholesale item prices and manage your master store retail price book.")

tab1, tab2 = st.tabs(["📝 Price Calculator", "📊 Price Master List"])

# =========================================================
# CRITICAL DIRECT SYSTEM CONNECTORS
SHEET_ID = "14XUh3otWt1EoVM3RuLPceHhAaKF5iigOQO44mMcN2Fo"
WEBHOOK_URL = "https://google.com"
# =========================================================

# --- HIGH-RELIABILITY LIVE REFRESH DATA ENGINE ---
def fetch_live_matrix():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(f"{WEBHOOK_URL}?t={int(time.time())}", headers=headers, timeout=12)
        if response.status_code == 200:
            data_json = response.json()
            if not data_json or len(data_json) == 0 or isinstance(data_json, dict):
                return pd.DataFrame(columns=["Product Name", "Capital Cost", "Markup", "Profit", "Selling Price"])
                
            df = pd.DataFrame(data_json)
            df.columns = df.columns.str.strip().str.lower().str.replace(" ", "")
            
            mapping = {
                "productname": "Product Name", "product": "Product Name", "product name": "Product Name",
                "capitalcost": "Capital Cost", "capital": "Capital Cost", "capital cost": "Capital Cost",
                "markup": "Markup", "markup": "Markup",
                "profit": "Profit", "profit": "Profit",
                "sellingprice": "Selling Price", "selling": "Selling Price", "selling price": "Selling Price"
            }
            df = df.rename(columns=mapping)
            return df.loc[:, ~df.columns.str.contains('^unnamed', na=False, case=False)]
    except Exception as e:
        pass
    return pd.DataFrame(columns=["Product Name", "Capital Cost", "Markup", "Profit", "Selling Price"])

if "df_master_cache" not in st.session_state:
    st.session_state["df_master_cache"] = fetch_live_matrix()

required_columns = ["Product Name", "Capital Cost", "Markup", "Profit", "Selling Price"]
for col in required_columns:
    if col not in st.session_state["df_master_cache"].columns:
        st.session_state["df_master_cache"][col] = None
df_master = st.session_state["df_master_cache"][required_columns]

# --- POPUP SAFETY CONFIRMATION MODAL WITH DUPLICATE DETECTION ---
@st.dialog("⚠️ Final Confirmation Required")
def confirm_save_dialog():
    prod_name = st.session_state.get("prod_name_key", "").strip()
    capital = st.session_state.get("capital_key", 0.0)
    markup = st.session_state.get("markup_key", 10.0)
    
    profit = capital * (markup / 100.0)
    retail_price = capital + profit

    existing_df = st.session_state["df_master_cache"]
    is_duplicate = False
    if not existing_df.empty and "Product Name" in existing_df.columns:
        is_duplicate = prod_name.lower() in existing_df["Product Name"].astype(str).str.lower().str.strip().values

    if is_duplicate:
        st.error(f"🔄 **DUPLICATE DETECTED**: '{prod_name}' already exists in your master list!")
        st.write("Confirming below will **overwrite and change** its current price logs with your new values.")
    else:
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
                
                new_row_data = {
                    "Product Name": prod_name,
                    "Capital Cost": f"₱{capital:,.2f}",
                    "Markup": f"{markup}%",
                    "Profit": f"₱{profit:,.2f}",
                    "Selling Price": f"₱{retail_price:,.2f}"
                }
                
                if is_duplicate:
                    idx_match = st.session_state["df_master_cache"][
                        st.session_state["df_master_cache"]["Product Name"].astype(str).str.lower().str.strip() == prod_name.lower()
                    ].index
                    for col in required_columns:
                        st.session_state["df_master_cache"].loc[idx_match, col] = new_row_data[col]
                else:
                    new_entry = pd.DataFrame([new_row_data])
                    st.session_state["df_master_cache"] = pd.concat([st.session_state["df_master_cache"], new_entry], ignore_index=True)
                
                try:
                    requests.get(WEBHOOK_URL, params={
                        "product": prod_name, "capital": capital, "markup": f"{markup}%",
                        "profit": round(profit, 2), "selling": round(retail_price, 2)
                    }, timeout=15)
                except:
                    pass
                
                if is_duplicate:
                    st.toast(f"🔄 Successfully updated pricing for '{prod_name}'!")
                else:
                    st.toast(f"✅ Successfully saved '{prod_name}' onto your price grid layout!")
                
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
        # INTERACTIVE SEARCH BAR
        search_query = st.text_input("🔍 Search Product Name...", placeholder="Type to filter list live...")
        
        if search_query.strip():
            df_display = df_clean[df_clean["Product Name"].str.contains(search_query.strip(), case=False, na=False)]
        else:
            df_display = df_clean.copy()
            
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # SECURE DELETING FUNCTION PANEL
        st.markdown("---")
        with st.expander("🛠️ Admin Controls: Remove Items From Database List"):
            all_products_list = df_clean["Product Name"].unique().tolist()
            product_to_delete = st.selectbox("Select a product name item to permanently delete:", options=["-- Choose Product --"] + all_products_list)
            
            delete_btn = st.button("❌ Execute Delete Selected Product", type="secondary", use_container_width=True)
            
            if delete_btn:
                if product_to_delete != "-- Choose Product --":
                    st.session_state["df_master_cache"] = st.session_state["df_master_cache"][
                        st.session_state["df_master_cache"]["Product Name"].astype(str).str.strip() != product_to_delete
                    ]
                    st.toast(f"🗑️ Cleaned '{product_to_delete}' out of your active memory list registers!")
                    time.sleep(1.0)
                    st.rerun()
                else:
                    st.warning("Please choose a valid product name choice tracking element row above first.")
