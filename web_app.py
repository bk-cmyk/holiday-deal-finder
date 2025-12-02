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
            link = item.get('
