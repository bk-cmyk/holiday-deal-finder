import streamlit as st
import requests
import pandas as pd

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
# PASTE YOUR RAPIDAPI KEY HERE
# detailed instructions on where to find this are coming in the next step!
import os
# Try to get the key from Streamlit secrets, or fallback to an empty string
try:
    API_KEY = st.secrets["RAPIDAPI_KEY"]
except:
    API_KEY = ""

AMAZON_URL = "https://real-time-amazon-data.p.rapidapi.com/search"
WALMART_URL = "https://walmart-data.p.rapidapi.com/walmart/search"

# ---------------------------------------------------------
# FUNCTIONS (The logic from your old script)
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
            for item in data['data']['products'][:5]:
                products.append({
                    "Store": "Amazon",
                    "Product": item.get('product_title', 'No Title'),
                    "Price": item.get('product_price', 'N/A'),
                    "Link": item.get('product_url', '#')
                })
        return products
    except:
        return []

def search_walmart(query):
    if API_KEY == "YOUR_RAPIDAPI_KEY_HERE":
        return []

    querystring = {"query": query, "page": "1"} 
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "walmart-data.p.rapidapi.com"
    }
    try:
        response = requests.get(WALMART_URL, headers=headers, params=querystring)
        data = response.json()
        products = []
        if 'items' in data:
            for item in data['items'][:5]:
                products.append({
                    "Store": "Walmart",
                    "Product": item.get('name', 'No Title'),
                    "Price": f"${item.get('salePrice', 'N/A')}",
                    "Link": item.get('productUrl', '#')
                })
        return products
    except:
        return []

# ---------------------------------------------------------
# THE WEBSITE LAYOUT
# ---------------------------------------------------------
st.set_page_config(page_title="Holiday Deal Finder", page_icon="🎁")

st.title("🎁 Holiday Deal Finder")
st.markdown("Compare prices across **Amazon** and **Walmart** instantly.")

# 1. The Input Box
product_name = st.text_input("What product are you looking for?", placeholder="e.g. PS5, Lego Star Wars, Air Fryer")

# 2. The Button
if st.button("Find Deals"):
    if not product_name:
        st.warning("Please enter a product name first!")
    elif API_KEY == "YOUR_RAPIDAPI_KEY_HERE":
        st.error("❌ You forgot to paste your API Key in the code!")
    else:
        with st.spinner(f"Scanning stores for '{product_name}'..."):
            
            # Fetch Data
            amazon_data = search_amazon(product_name)
            walmart_data = search_walmart(product_name)
            all_data = amazon_data + walmart_data

            if all_data:
                # Convert to a nice table
                df = pd.DataFrame(all_data)
                
                # Display the table
                st.success(f"Found {len(all_data)} items!")
                st.dataframe(
                    df, 
                    column_config={
                        "Link": st.column_config.LinkColumn("Product Link")
                    },
                    hide_index=True
                )
            else:
                st.error("No products found. Check your API subscription or try a different keyword.")