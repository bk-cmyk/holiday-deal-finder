import streamlit as st
import requests
import pandas as pd
import os

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
        # UPDATED: Changed limit from [:5] to [:10]
        if 'data' in data and 'products' in data['data']:
            for item in data['data']['products'][:10]:
                products.append({
                    "Store": "Amazon",
                    "Product": item.get('product_title', 'No Title'),
                    # Clean up price to ensure it sorts correctly later
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

    querystring = {"query": query, "page": "1"} 
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "walmart-data.p.rapidapi.com"
    }
    try:
        response = requests.get(WALMART_URL, headers=headers, params=querystring)
        data = response.json()
        
        products = []
        # UPDATED: Changed limit from [:5] to [:10]
        if 'items' in data:
            for item in data['items'][:10]:
                price_raw = item.get('salePrice', 0)
                products.append({
                    "Store": "Walmart",
                    "Product": item.get('name', 'No Title'),
                    "Price": float(str(price_raw).replace('$', '').replace(',', '')),
                    "Link": item.get('productUrl', '#')
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
    st.write("") # Spacer
    st.write("") # Spacer
    search_button = st.button("Find Deals", type="primary", use_container_width=True)

if search_button:
    if not product_name:
        st.warning("Please enter a product name first!")
    elif API_KEY == "YOUR_RAPIDAPI_KEY_HERE":
        st.error("❌ You forgot to paste your API Key in the code!")
    else:
        with st.spinner(f"Scanning stores for '{product_name}'..."):
            
            # Fetch Data from both
            amazon_data = search_amazon(product_name)
            walmart_data = search_walmart(product_name)
            
            # Debugging: Show user if one store returned 0 items
            if not amazon_data:
                st.warning("Amazon returned 0 results. (Check API Quota?)")
            if not walmart_data:
                st.warning("Walmart returned 0 results. (Check API Quota?)")

            # Combine
            all_data = amazon_data + walmart_data

            if all_data:
                # Create DataFrame
                df = pd.DataFrame(all_data)
                
                # Format Price column nicely ($123.45)
                df = df.sort_values(by="Price") # Sort by cheapest first
                
                # Display the table
                st.success(f"Found {len(all_data)} items!")
                
                # Specialized column config for clickable links and price format
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
