import streamlit as st
import requests
import pandas as pd

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
# 1. Try to get the key from "Secrets" (for the online version)
try:
    API_KEY = st.secrets["RAPIDAPI_KEY"]
except:
    # 2. PASTE YOUR KEY HERE FOR LOCAL TESTING
    API_KEY = "YOUR_RAPIDAPI_KEY_HERE"

# UPDATED: New API Endpoints
AMAZON_URL = "https://real-time-amazon-data.p.rapidapi.com/search"
WALMART_URL = "https://realtime-walmart-data.p.rapidapi.com/search"

# ---------------------------------------------------------
# HELPER: TEXT CLEANER
# ---------------------------------------------------------
def clean_price(price_input):
    """Converts '$12.99' or 12.99 into the float 12.99"""
    try:
        # If it's already a number, just return it
        if isinstance(price_input, (int, float)):
            return float(price_input)
        # If it's a string, strip symbols
        clean_str = str(price_input).replace('$', '').replace(',', '').strip()
        return float(clean_str)
    except:
        return 0.0

# ---------------------------------------------------------
# FUNCTIONS
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
        print(f"Amazon Error: {e}")
        return []

def search_walmart(query):
    if API_KEY == "YOUR_RAPIDAPI_KEY_HERE":
        return []

    # UPDATED: Parameters for the 'jobykjoseph10' API
    querystring = {"query": query, "page": "1", "country": "US"}
    headers = {
        "X-RapidAPI-Key": API_KEY,
        # UPDATED: The new Host address
        "X-RapidAPI-Host": "realtime-walmart-data.p.rapidapi.com"
    }
    try:
        response = requests.get(WALMART_URL, headers=headers, params=querystring)
        data = response.json()
        
        products = []
        
        # This API usually puts items in data -> products
        # But we use a "Smart Finder" to look in likely places just in case
        items_list = []
        if 'data' in data and 'products' in data['data']:
            items_list = data['data']['products']
        elif 'data' in data: # Sometimes it's just directly in data
            items_list = data['data']
        elif 'products' in data:
            items_list = data['products']

        for item in items_list[:10]:
            # Smart find for Title
            title = item.get('product_title') or item.get('title') or item.get('name') or "No Title"
            
            # Smart find for Link
            link = item.get('product_url') or item.get('url') or item.get('link') or "#"
            
            # Smart find for Price
            price_raw = item.get('product_price') or item.get('price') or item.get('salePrice') or 0
            
            products.append({
                "Store": "Walmart",
                "Product": title,
                "Price": clean_price(price_raw),
                "Link": link
            })
            
        return products
    except Exception as e:
        print(f"Walmart Error: {e}")
        return []

# ---------------------------------------------------------
# THE WEBSITE LAYOUT
# ---------------------------------------------------------
st.set_page_config(page_title="Holiday Deal Finder", page_icon="🎁", layout="wide")

st.title("🎁 Holiday Deal Finder")
st.markdown("Compare prices across **Amazon** and **Walmart** instantly.")

# Input Section
col1, col2 = st.columns([3, 1])
with col1:
    product_name = st.text_input("What product are you looking for?", placeholder="e.g. PS5, Lego Star Wars, Air Fryer")
with col2:
    st.write("") 
    st.write("") 
    search_button = st.button("Find Deals", type="primary", use_container_width=True)

if search_button:
    if not product_name:
        st.warning("Please enter a product name first!")
    elif API_KEY == "YOUR_RAPIDAPI_KEY_HERE":
        st.error("❌ You forgot to paste your API Key in the code!")
    else:
        with st.spinner(f"Scanning stores for '{product_name}'..."):
            
            amazon_data = search_amazon(product_name)
            walmart_data = search_walmart(product_name)
            
            # Debugging Alerts
            if not amazon_data:
                st.warning("Amazon returned 0 results.")
            if not walmart_data:
                st.warning("Walmart returned 0 results.")

            all_data = amazon_data + walmart_data

            if all_data:
                df = pd.DataFrame(all_data)
                
                # Sort by price (Low to High)
                df = df.sort_values(by="Price") 
                
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
                st.error("No products found. Check your API subscription or try a different keyword.")