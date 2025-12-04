import streamlit as st
import requests
import pandas as pd
import json

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
try:
    API_KEY = st.secrets["RAPIDAPI_KEY"]
except:
    API_KEY = "YOUR_RAPIDAPI_KEY_HERE"

# UPDATED: Verified Endpoints
AMAZON_URL = "https://real-time-amazon-data.p.rapidapi.com/search"
WALMART_URL = "https://realtime-walmart-data.p.rapidapi.com/search"

# ---------------------------------------------------------
# HELPER: PRICE CLEANER
# ---------------------------------------------------------
def clean_price(price_input):
    try:
        if isinstance(price_input, (int, float)):
            return float(price_input)
        clean_str = str(price_input).replace('$', '').replace(',', '').strip()
        return float(clean_str)
    except:
        return 0.0

# ---------------------------------------------------------
# SEARCH FUNCTIONS
# ---------------------------------------------------------
def search_amazon(query):
    if API_KEY == "YOUR_RAPIDAPI_KEY_HERE":
        return []
        
    querystring = {"query": query, "country": "US", "sort_by": "RELEVANCE"}
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "real-time-amazon-data.p.rapidapi.com"
    }
    try:
        response = requests.get(AMAZON_URL, headers=headers, params=querystring)
        data = response.json()
        
        products = []
        if 'data' in data and 'products' in data['data']:
            for item in data['data']['products'][:10]:
                products.append({
                    "Store": "Amazon",
                    "Product": item.get('product_title', 'No Title'),
                    "Price": clean_price(item.get('product_price', 0)),
                    "Link": item.get('product_url', '#')
                })
        return products
    except:
        return []

def search_walmart(query):
    if API_KEY == "YOUR_RAPIDAPI_KEY_HERE":
        return []

    # FIX: The API demands 'keyword', not 'query'
    querystring = {"keyword": query, "page": "1", "country": "US", "sort_by": "best_match"}
    
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "realtime-walmart-data.p.rapidapi.com"
    }
    try:
        response = requests.get(WALMART_URL, headers=headers, params=querystring)
        data = response.json()
        
        # --- DIAGNOSTIC BLOCK ---
        # If the standard "data -> products" path fails, we print the raw JSON
        # so you can see EXACTLY what the API sent back.
        if 'data' not in data or 'products' not in data['data']:
            st.warning(f"⚠️ Walmart Debug: API connected but returned unexpected structure.")
            with st.expander("🔎 Click here to see the RAW Walmart data"):
                st.json(data)

        products = []
        
        # "Smart Parse" - tries to find the list of items
        items_list = []
        if 'data' in data and 'products' in data['data']:
            items_list = data['data']['products']
        elif 'data' in data:
            items_list = data['data']
            
        for item in items_list[:10]:
            products.append({
                "Store": "Walmart",
                "Product": item.get('product_title', 'No Title'),
                "Price": clean_price(item.get('product_price', 0)),
                "Link": item.get('product_url', '#')
            })
            
        return products
    except Exception as e:
        st.error(f"Walmart Connection Error: {e}")
        return []

# ---------------------------------------------------------
# WEBSITE LAYOUT
# ---------------------------------------------------------
st.set_page_config(page_title="Holiday Deal Finder", page_icon="🎁", layout="wide")
st.title("🎁 Holiday Deal Finder")

col1, col2 = st.columns([3, 1])
with col1:
    product_name = st.text_input("What product are you looking for?", placeholder="e.g. Lego Star Wars")
with col2:
    st.write("") 
    st.write("") 
    search_button = st.button("Find Deals", type="primary", use_container_width=True)

if search_button:
    if not product_name:
        st.warning("Please enter a product name first!")
    elif API_KEY == "YOUR_RAPIDAPI_KEY_HERE":
        st.error("❌ API Key missing.")
    else:
        with st.spinner(f"Scanning for '{product_name}'..."):
            
            amazon_data = search_amazon(product_name)
            walmart_data = search_walmart(product_name)
            
            if not amazon_data:
                st.warning("Amazon returned 0 results.")
            if not walmart_data:
                st.warning("Walmart returned 0 results (Check the Debug Expander above).")

            all_data = amazon_data + walmart_data

            if all_data:
                df = pd.DataFrame(all_data).sort_values(by="Price")
                st.success(f"Found {len(all_data)} items!")
                st.dataframe(
                    df, 
                    column_config={
                        "Link": st.column_config.LinkColumn("Product Link"),
                        "Price": st.column_config.NumberColumn("Price", format="$%.2f")
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.error("No results found.")