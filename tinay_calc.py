import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# PERSONALIZED APP CONFIGURATION
st.set_page_config(page_title="Tinay's Price Calculator", page_icon="🧮", layout="centered")
st.title("🧮 Tinay's Personal Retail Price Calculator")
st.markdown("Calculate wholesale item prices and manage your master store retail price book layout.")

tab1, tab2 = st.tabs(["🧮 Price Calculator", "📋 Price Master List"])

# --- CLOUD GOOGLE SHEETS CONNECTION ---
# Establishes a secure pipeline to your online spreadsheet
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Read existing spreadsheet data rows safely
    df_master = conn.read(ttl="0d") # 0d ensures it pulls live data every refresh
    # Clean up column names to match Python expectations
    df_master.columns = df_master.columns.str.strip()
except Exception as e:
    st.error("Waiting for Cloud Setup Configuration link inside the Streamlit Dashboard Dashboard...")
    df_master = pd.DataFrame(columns=["Product Name", "Capital Cost", "Markup", "Profit", "Selling Price"])

# =========================================================
# TAB 1: SMART PRICE CALCULATOR
# =========================================================
with tab1:
    st.subheader("Calculate & Save Retail Prices")
    st.markdown("Enter item details below to automatically compute your retail price.")
    
    item_name = st.text_input("Product Name (e.g., Coke Litro, Sardines):", key="p_name").strip()
    capital = st.number_input("Wholesale Capital / Cost (PHP):", min_value=0.0, value=None, step=1.0, key="p_cap")
    markup_percent = st.number_input("Target Markup Percentage (%):", min_value=0.0, value=None, step=1.0, key="p_mark")
    
    valid_capital = capital if capital is not None else 0.0
    valid_markup = markup_percent if markup_percent is not None else 0.0
    
    profit_amount = valid_capital * (valid_markup / 100)
    final_retail_price = valid_capital + profit_amount
    
    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a: st.metric("Profit per Unit", f"₱{profit_amount:,.2f}")
    with col_b: st.metric("Final Retail Selling Price", f"₱{final_retail_price:,.2f}")
    st.markdown("---")

    if item_name:
        # Check if the product already exists inside the Google Sheet rows
        is_existing = item_name.lower() in df_master["Product Name"].astype(str).str.lower().values
        
        if is_existing:
            st.warning(f"⚠️ **'{item_name}' already exists in your Master List!**")
            overwrite_confirm = st.checkbox("Yes, I want to overwrite/update this item's price information.")
            
            if overwrite_confirm:
                if st.button("🔄 Update Existing Price", use_container_width=True, type="primary"):
                    # Remove the old row profile from memory dataframe
                    df_master = df_master[df_master["Product Name"].astype(str).str.lower() != item_name.lower()]
                    # Append updated row data dictionary entries
                    new_row = pd.DataFrame([{
                        "Product Name": item_name, "Capital Cost": valid_capital,
                        "Markup": valid_markup, "Profit": profit_amount, "Selling Price": final_retail_price
                    }])
                    df_master = pd.concat([df_master, new_row], ignore_index=True)
                    # Push memory dataset back up to the online cloud sheet file
                    conn.update(data=df_master)
                    st.toast(f"🎉 UPDATED: {item_name} is now ₱{final_retail_price:,.2f}")
                    st.session_state["p_name"] = ""
                    st.session_state["p_cap"] = None
                    st.session_state["p_mark"] = None
                    st.rerun()
        else:
            if valid_capital > 0:
                if st.button("💾 Save to Price Master List", use_container_width=True):
                    new_row = pd.DataFrame([{
                        "Product Name": item_name, "Capital Cost": valid_capital,
                        "Markup": valid_markup, "Profit": profit_amount, "Selling Price": final_retail_price
                    }])
                    df_master = pd.concat([df_master, new_row], ignore_index=True)
                    conn.update(data=df_master)
                    st.toast(f"✅ SAVED: {item_name} added at ₱{final_retail_price:,.2f}")
                    st.session_state["p_name"] = ""
                    st.session_state["p_cap"] = None
                    st.session_state["p_mark"] = None
                    st.rerun()
            else:
                st.caption("⚠️ Enter a wholesale capital cost higher than ₱0.00 to save.")
    else:
        st.info("Type a Product Name above to unlock the database save options.")


# =========================================================
# TAB 2: PRICE MASTER LIST (Live Google Sheet Sync)
# =========================================================
with tab2:
    st.subheader("📋 Registered Retail Price Directory")
    st.markdown("Search items or check rows below to delete them from your master online ledger.")
    
    if not df_master.empty and df_master["Product Name"].notna().any():
        search_query = st.text_input("🔍 Search for a product name:", "").strip().lower()
        
        if search_query:
            df_master = df_master[df_master["Product Name"].astype(str).str.lower().str.contains(search_query)]

        df_master.insert(0, "Select", False)
        
        edited_df = st.data_editor(
            df_master,
            use_container_width=True,
            hide_index=True,
            column_config={"Select": st.column_config.CheckboxColumn(required=True)}
        )
        
        selected_rows = edited_df[edited_df["Select"] == True]
        
        if not selected_rows.empty:
            st.markdown("---")
            st.subheader("⚙️ Actions for Selected Items")
            
            if st.button("🗑️ Delete Selected Rows", use_container_width=True, type="secondary"):
                # Filter out the items selected for deletion from the main sheet model dataset
                targets = selected_rows["Product Name"].tolist()
                df_master = df_master[~df_master["Product Name"].isin(targets)]
                df_master = df_master.drop(columns=["Select"], errors="ignore")
                conn.update(data=df_master)
                st.toast(f"🗑️ Deleted product entries from cloud data sheet.")
                st.rerun()
                    
    else:
        st.info("Your Cloud Price Master List is empty. Go to the Calculator tab to log your products.")
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Title of your app
st.title("Google Sheets Connection App")

# Create a connection object
conn = st.connection("gsheets", type=GSheetsConnection)

# Read the data from your spreadsheet
# Replace the URL below with your actual Google Sheet URL
url = "https://google.com"
df = conn.read(spreadsheet=url)

# Display the data in your app
st.dataframe(df)


