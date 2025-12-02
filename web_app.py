import streamlit as st
import requests
import pandas as pd

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
try:
    API_KEY = st.secrets["RAPIDAPI_KEY"]
except:
    API_KEY = "YOUR_RAPIDAPI_KEY_HERE"

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
        
    # Amazon API uses 'query'
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

    # FIXED: Changed 'query' to 'keyword' based on the error message
    querystring = {"keyword": query, "page": "1", "country": "US", "sort_by": "best_match"}
    
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "realtime-walmart-data.p.rapidapi.com"
    }
    try:
        response = requests.get(WALMART_URL, headers=headers, params=querystring)
        data = response.json()
        
        products = []
        
        # This API returns data -> products -> list
        items_list = []
        if 'data' in data and 'products' in data['data']:
            items_list = data['data']['products']
            
        for item in items_list[:10]:
            products.append({
                "Store": "Walmart",
                "Product": item.get('product_title', 'No Title'),
                "Price": clean_price(item.get('product_price', 0)),
                "Link": item.get('product_url', '#')
            })
            
        return products
    except Exception as e:
        st.error(f"Walmart Error: {e}")
        return []

# ---------------------------------------------------------
# WEBSITE LAYOUT
# ---------------------------------------------------------
st.set_page_config(page_title="Holiday Deal Finder", page_icon="🎁", layout="wide")
st.title("🎁 Holiday Deal Finder")

col1, col2 = st.columns([3, 1])
with col1:
    product_name = st.text_input("What product are you looking for?", placeholder="e.g. PS5, Lego Star Wars")
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
                st.error("No results found. (If Amazon worked but Walmart failed, check if the Walmart API is down)")