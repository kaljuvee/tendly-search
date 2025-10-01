"""
Simple test version of Tendly Search application.
"""

import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Tendly Search - Test",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Tendly Search - Test Version")
st.markdown("Testing basic functionality...")

# Test database connection
try:
    from utils.db_util import DatabaseUtil
    
    st.success("✅ Database utility imported successfully")
    
    db_util = DatabaseUtil()
    tables = db_util.get_table_names()
    
    st.success(f"✅ Connected to database. Found {len(tables)} tables:")
    for table in tables[:5]:  # Show first 5 tables
        st.write(f"- {table}")
    
    if tables:
        sample_data = db_util.get_sample_data(tables[0], 3)
        st.subheader(f"Sample data from {tables[0]}:")
        st.dataframe(sample_data)
    
    db_util.close()
    
except Exception as e:
    st.error(f"❌ Database connection failed: {str(e)}")

# Test search utility
try:
    from utils.search_util import TenderSearchAgent
    
    st.success("✅ Search utility imported successfully")
    
    # Don't initialize the full agent in test mode to avoid OpenAI calls
    st.info("Search agent ready (not initialized to avoid API calls)")
    
except Exception as e:
    st.error(f"❌ Search utility import failed: {str(e)}")

# Test environment variables
st.subheader("Environment Variables")
db_url = os.getenv('DB_URL')
openai_key = os.getenv('OPENAI_API_KEY')

if db_url:
    st.success("✅ DB_URL is set")
else:
    st.error("❌ DB_URL not found")

if openai_key:
    st.success("✅ OPENAI_API_KEY is set")
else:
    st.error("❌ OPENAI_API_KEY not found")

st.markdown("---")
st.markdown("**Test completed!** If all checks pass, the main application should work.")
