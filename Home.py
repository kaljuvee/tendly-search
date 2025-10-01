"""
Tendly Search - Main Streamlit Application
AI-powered tender database search and analysis platform.
"""

import streamlit as st
import pandas as pd
from utils.search_util import get_tender_search_agent
from utils.db_util import get_database_util
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Tendly Search",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .search-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'search_agent' not in st.session_state:
    with st.spinner("🚀 Initializing Tendly Search..."):
        try:
            st.session_state.search_agent = get_tender_search_agent()
            st.session_state.db_util = get_database_util()
        except Exception as e:
            st.error(f"Failed to initialize application: {str(e)}")
            st.stop()

# Header
st.markdown("""
<div class="main-header">
    <h1>🔍 Tendly Search</h1>
    <p>AI-Powered Tender Database Search & Analysis</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with navigation and info
with st.sidebar:
    st.header("🎯 Quick Actions")
    
    # Database statistics
    try:
        stats = st.session_state.search_agent.get_tender_statistics()
        
        st.subheader("📊 Database Overview")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Tenders", f"{stats.get('total_tenders', 0):,}")
        with col2:
            st.metric("Recent (30d)", f"{stats.get('recent_tenders', 0):,}")
        
        if stats.get('average_value', 0) > 0:
            st.metric("Avg. Value", f"€{stats.get('average_value', 0):,.0f}")
        
    except Exception as e:
        st.warning("Could not load database statistics")
    
    st.markdown("---")
    
    # Quick filters
    st.subheader("🔧 Quick Filters")
    
    # Time filter
    time_filter = st.selectbox(
        "Time Period",
        ["All time", "Last 7 days", "Last 30 days", "Last 90 days"]
    )
    
    # Value filter
    min_value = st.number_input(
        "Minimum Value (€)",
        min_value=0,
        value=0,
        step=1000,
        format="%d"
    )
    
    # Location filter
    location_filter = st.text_input(
        "Location",
        placeholder="e.g., Tallinn, Harjumaa"
    )

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔍 Search Tenders")
    
    # Predefined search buttons
    st.markdown("**Quick Search Options:**")
    
    predefined_searches = st.session_state.search_agent.get_predefined_searches()
    
    # Create buttons in a grid
    cols = st.columns(3)
    for i, search in enumerate(predefined_searches):
        with cols[i % 3]:
            if st.button(
                f"{search['icon']} {search['title']}", 
                key=f"predefined_{i}",
                help=search['description']
            ):
                st.session_state.current_search = search['query']
    
    st.markdown("---")
    
    # Custom search input
    search_query = st.text_input(
        "Or enter your own search:",
        value=st.session_state.get('current_search', ''),
        placeholder="e.g., Show me construction tenders in Tallinn with value over 50000 euros",
        key="search_input"
    )
    
    # Search button
    col_search, col_clear = st.columns([3, 1])
    with col_search:
        search_clicked = st.button("🔍 Search Tenders", type="primary", use_container_width=True)
    with col_clear:
        if st.button("🗑️ Clear"):
            st.session_state.current_search = ""
            st.rerun()

with col2:
    st.subheader("💡 Search Tips")
    st.markdown("""
    **Effective Search Examples:**
    
    🏗️ **Construction**: "construction tenders", "ehitus hanked"
    
    📍 **Location**: "tenders in Harjumaa", "Tallinn procurements"
    
    💰 **Value**: "high value tenders", "tenders over 100000 euros"
    
    🕒 **Time**: "recent tenders", "tenders from this month"
    
    🏢 **Organization**: "tenders from Tallinn city", "government tenders"
    
    💻 **Category**: "IT tenders", "software procurement"
    """)

# Process search
if search_clicked and search_query.strip():
    st.markdown("---")
    st.subheader("📋 Search Results")
    
    with st.spinner("🔍 Searching tender database..."):
        try:
            # Apply filters to search query if any
            enhanced_query = search_query
            
            if location_filter:
                enhanced_query += f" in {location_filter}"
            
            if min_value > 0:
                enhanced_query += f" with value over {min_value} euros"
            
            if time_filter != "All time":
                time_mapping = {
                    "Last 7 days": "from last 7 days",
                    "Last 30 days": "from last 30 days", 
                    "Last 90 days": "from last 90 days"
                }
                enhanced_query += f" {time_mapping[time_filter]}"
            
            # Try AI search first, fallback to simple search
            try:
                result = st.session_state.search_agent.search_tenders(enhanced_query, limit=50)
                
                if result["success"] and result.get("results"):
                    st.success(f"✅ AI Search completed successfully!")
                    
                    # Display results
                    st.markdown("### 📊 Results")
                    
                    # Try to parse and display structured results
                    if isinstance(result["results"], str):
                        st.markdown(result["results"])
                    else:
                        st.write(result["results"])
                else:
                    raise Exception("AI search returned no results")
                    
            except Exception as ai_error:
                # Fallback to simple search
                st.warning("🔄 AI search unavailable, using direct database search...")
                
                from utils.simple_search import SimpleSearchAgent
                simple_agent = SimpleSearchAgent()
                
                # Map search queries to simple search functions
                search_lower = search_query.lower()
                
                if any(word in search_lower for word in ['construction', 'ehitus', 'building']):
                    result = simple_agent.search_construction_tenders(limit=20)
                elif any(word in search_lower for word in ['harjumaa', 'harju', 'tallinn']):
                    result = simple_agent.search_harjumaa_tenders(limit=20)
                elif any(word in search_lower for word in ['high value', 'expensive', 'large']):
                    result = simple_agent.search_high_value_tenders(min_value=min_value or 100000, limit=20)
                elif any(word in search_lower for word in ['recent', 'new', 'latest']):
                    result = simple_agent.search_recent_tenders(limit=20)
                elif any(word in search_lower for word in ['it', 'software', 'tarkvara', 'technology']):
                    result = simple_agent.search_it_tenders(limit=20)
                elif any(word in search_lower for word in ['active', 'open', 'current']):
                    result = simple_agent.search_active_tenders(limit=20)
                else:
                    # Extract main keyword for general search
                    keywords = search_query.split()
                    main_keyword = keywords[0] if keywords else search_query
                    result = simple_agent.search_by_keyword(main_keyword, limit=20)
                
                simple_agent.close()
                
                if result["success"] and result.get("results") is not None and len(result["results"]) > 0:
                    st.success(f"✅ Found {result['count']} results using direct search!")
                    
                    # Display results as DataFrame
                    st.markdown("### 📊 Search Results")
                    df = pd.DataFrame(result["results"])
                    
                    # Format the dataframe for better display
                    if not df.empty:
                        # Format estimated_value if it exists
                        if 'estimated_value' in df.columns:
                            df['estimated_value'] = df['estimated_value'].apply(
                                lambda x: f"€{x:,.0f}" if pd.notnull(x) and x > 0 else "Not specified"
                            )
                        
                        st.dataframe(df, use_container_width=True)
                        
                        # Download button
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Results",
                            data=csv,
                            file_name=f"tender_search_results.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info("No results found for your search.")
                else:
                    st.error(f"❌ Search failed: {result.get('error', 'No results found')}")
                    st.info("💡 Try rephrasing your search or check the search tips.")
                
        except Exception as e:
            st.error(f"An error occurred during search: {str(e)}")

# Only show sample data when no search has been performed
if not search_clicked or not search_query.strip():
    st.markdown("---")
    st.info("💡 **Ready to search!** Use the buttons above or enter your own search query to find tenders in the database.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <h4>🔍 Tendly Search</h4>
    <p>AI-powered tender database search and analysis platform</p>
    <p><small>Built with Streamlit, LangChain, and OpenAI</small></p>
</div>
""", unsafe_allow_html=True)

# Clear current search from session state after processing
if 'current_search' in st.session_state and search_clicked:
    del st.session_state.current_search
