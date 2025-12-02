import streamlit as st
import requests
import pandas as pd

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
# 1. Try to get the key from "Secrets" (for the online version)
# 2. If that fails, look for it right here (for your local version)
try:
    API_KEY = st.secrets["RAPIDAPI_KEY"]
except:
    # PASTE YOUR KEY HERE FOR LOCAL TESTING
    API_KEY = "YOUR_RAPIDAPI_KEY_HERE"

# UPDATED: Correct endpoints for the APIs you are using
AMAZON_URL = "https://real-time-amazon-data.p.rapidapi.com/search"
WALMART_URL = "https://walmart-data.p.rapidapi.com/search"

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
                    "Price": float(str(item.get('product_price', '0')).replace('$', '').replace(',', '')),
                    "Link": item.get('product_url', '#')
                })
        return products
    except Exception as e:
        st.error(f"Amazon Error: {e}")
        return []

def search_walmart(query):
    if API_KEY == "YOUR_RAPIDAPI_KEY_HERE":
        return []

    # UPDATED: 'query' vs 'q' often varies, but this API typically uses 'query' or 'q'.
    # We also request JSON format explicitly.
    querystring = {"query": query, "page": "1", "country": "US"} 
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "walmart-data.p.rapidapi.com"
    }
    try:
        response = requests.get(WALMART_URL, headers=headers, params=querystring)
        data = response.json()
        
        products = []
        
        # DEBUG: If you still get 0 results, uncomment the line below to see what the API sent back
        # st.write(data) 

        # UPDATED: This specific API uses 'products', not 'items'
        if 'products' in data:
            for item in data['products'][:10]:
                # UPDATED: This API uses 'price', not 'salePrice'
                price_raw = item.get('price', 0)
                
                # Cleanup price (sometimes it comes as "$12.99" string, sometimes number)
                try:
                    price_val = float(str(price_raw).replace('$', '').replace(',', ''))
                except:
                    price_val = 0.0

                products.append({
                    "Store": "Walmart",
                    "Product": item.get('title', 'No Title'), # 'title' not 'name'
                    "Price": price_val,
                    "Link": item.get('link', '#') # 'link' not 'productUrl'
                })
        return products
    except Exception as e:
        st.error(f"Walmart Error: {e}")
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
            
            # Debugging Helpers
            if not amazon_data:
                st.warning("Amazon returned 0 results.")
            if not walmart_data:
                st.warning("Walmart returned 0 results.")

            all_data = amazon_data + walmart_data

            if all_data:
                df = pd.DataFrame(all_data)
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
