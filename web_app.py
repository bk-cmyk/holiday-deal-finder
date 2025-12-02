import streamlit as st
import requests
import pandas as pd
import json # Added for debug printing

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
try:
    API_KEY = st.secrets["RAPIDAPI_KEY"]
except:
    API_KEY = "YOUR_RAPIDAPI_KEY_HERE"

# UPDATED: Verified Endpoint for jobykjoseph10
AMAZON_URL = "https://real-time-amazon-data.p.rapidapi.com/search"
WALMART_URL = "https://realtime-walmart-data.p.rapidapi.com/search"

# ---------------------------------------------------------
# HELPER: PRICE CLEANER
# ---------------------------------------------------------
def clean_price(price_input):
    try:
        if isinstance(price_input, (int, float)):
            return float(price_input)
        # Remove '$', ',' and whitespace
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
    except Exception as e:
        return []

def search_walmart(query):
    if API_KEY == "YOUR_RAPIDAPI_KEY_HERE":
        return []

    # UPDATED: Parameters for jobykjoseph10
    querystring = {"query": query, "page": "1", "country": "US", "sort_by": "best_match"}
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "realtime-walmart-data.p.rapidapi.com"
    }
    try:
        response = requests.get(WALMART_URL, headers=headers, params=querystring)
        data = response.json()
        
        products = []
        
        # --- DIAGNOSTIC BLOCK ---
        # If we can't find data, we save the raw response to look at later
        if 'data' not in data:
            st.error("⚠️ WALMART DEBUG: No 'data' folder found in response.")
            with st.expander("See Raw Walmart Response (Click to open)"):
                st.json(data)
        
        # This API usually returns: data -> products -> [list]
        items_list = []
        if 'data' in data and 'products' in data['data']:
            items_list = data['data']['products']
        
        # Fallback: Sometimes it is just data -> [list]
        elif 'data' in data and isinstance(data['data'], list):
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
st.title("🎁 Holiday Deal Finder (Diagnostic Mode)")

col1, col2 = st.columns([3, 1])
with col1:
    product_name = st.text_input("Product Search", placeholder="e.g. PS5")
with col2:
    st.write("") 
    st.write("") 
    search_button = st.button("Find Deals", type="primary", use_container_width=True)

if search_button:
    if API_KEY == "YOUR_RAPIDAPI_KEY_HERE":
        st.error("❌ API Key missing.")
    else:
        with st.spinner(f"Scanning for '{product_name}'..."):
            
            amazon_data = search_amazon(product_name)
            walmart_data = search_walmart(product_name)
            
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
                st.warning("No results found.")