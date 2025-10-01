"""
Interactive SQL Chat page for Tendly Search application.
Allows users to query the tender database using natural language.
"""

import streamlit as st
import pandas as pd
from utils.sql_chat import get_sql_chat_assistant
from utils.db_util import get_database_util
import time

# Page configuration
st.set_page_config(
    page_title="Tendly Search - Chat",
    page_icon="💬",
    layout="wide"
)

st.title("💬 Tender Database Chat")
st.markdown("Ask questions about tenders in natural language and get instant answers!")

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'sql_assistant' not in st.session_state:
    with st.spinner("Initializing AI assistant..."):
        st.session_state.sql_assistant = get_sql_chat_assistant()

# Sidebar with information
with st.sidebar:
    st.header("📊 Database Info")
    
    # Show available tables
    try:
        db_util = get_database_util()
        tables = db_util.get_table_names()
        st.subheader("Available Tables")
        for table in tables:
            st.write(f"• {table}")
        
        # Show sample data from first table if available
        if tables:
            st.subheader(f"Sample from {tables[0]}")
            sample_data = db_util.get_sample_data(tables[0], 3)
            st.dataframe(sample_data, use_container_width=True)
        
        db_util.close()
    except Exception as e:
        st.error(f"Error loading database info: {str(e)}")
    
    st.markdown("---")
    st.subheader("💡 Tips")
    st.markdown("""
    - Ask questions in Estonian or English
    - Be specific about what you want to know
    - Use terms like "tenders", "procurement", "organizations"
    - Ask about locations, dates, values, etc.
    """)

# Main chat interface
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("🤖 Ask a Question")
    
    # Sample question buttons
    st.markdown("**Quick Start - Try these questions:**")
    
    sample_questions = [
        "Show me construction tenders",
        "Tenders in Harjumaa", 
        "What are the most recent tenders?",
        "Show me tenders with highest value",
        "Which organizations have the most tenders?"
    ]
    
    # Create buttons in rows
    cols = st.columns(3)
    for i, question in enumerate(sample_questions):
        with cols[i % 3]:
            if st.button(question, key=f"sample_{i}"):
                st.session_state.current_question = question

# Chat input
user_question = st.text_input(
    "Your question:",
    value=st.session_state.get('current_question', ''),
    placeholder="e.g., Show me all construction tenders in Tallinn",
    key="question_input"
)

# Process question
if st.button("🔍 Search", type="primary") or user_question:
    if user_question.strip():
        # Add user question to chat history
        st.session_state.chat_history.append({
            "type": "user",
            "content": user_question,
            "timestamp": time.time()
        })
        
        # Show processing message
        with st.spinner("🤔 Thinking..."):
            try:
                # Get response from SQL assistant
                response = st.session_state.sql_assistant.chat_with_database(user_question)
                
                # Add assistant response to chat history
                st.session_state.chat_history.append({
                    "type": "assistant",
                    "content": response,
                    "timestamp": time.time()
                })
                
            except Exception as e:
                st.error(f"Error processing question: {str(e)}")
        
        # Clear the current question
        if 'current_question' in st.session_state:
            del st.session_state.current_question

# Display chat history
if st.session_state.chat_history:
    st.markdown("---")
    st.subheader("💬 Conversation History")
    
    for i, message in enumerate(reversed(st.session_state.chat_history[-10:])):  # Show last 10 messages
        if message["type"] == "user":
            with st.chat_message("user"):
                st.write(f"**You:** {message['content']}")
        
        elif message["type"] == "assistant":
            with st.chat_message("assistant"):
                response = message["content"]
                
                if response["success"]:
                    st.write(f"**AI Assistant:** {response['answer']}")
                    
                    # If the response contains structured data, try to display it as a table
                    if "SELECT" in str(response['answer']).upper():
                        try:
                            # Try to extract and display any tabular data
                            st.info("💡 The AI generated and executed a SQL query to answer your question.")
                        except:
                            pass
                else:
                    st.error(f"**Error:** {response['error']}")
                    st.info("💡 Try rephrasing your question or being more specific.")

# Advanced SQL section
with st.expander("🔧 Advanced: Direct SQL Query"):
    st.markdown("**For advanced users:** Execute SQL queries directly")
    
    sql_query = st.text_area(
        "SQL Query:",
        placeholder="SELECT * FROM tenders LIMIT 10;",
        height=100
    )
    
    if st.button("Execute SQL", type="secondary"):
        if sql_query.strip():
            try:
                with st.spinner("Executing query..."):
                    result = st.session_state.sql_assistant.execute_direct_sql(sql_query)
                
                if result["success"]:
                    st.success("Query executed successfully!")
                    if isinstance(result["data"], pd.DataFrame) and not result["data"].empty:
                        st.dataframe(result["data"], use_container_width=True)
                        
                        # Download button for results
                        csv = result["data"].to_csv(index=False)
                        st.download_button(
                            label="📥 Download Results as CSV",
                            data=csv,
                            file_name="query_results.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info("Query executed but returned no data.")
                else:
                    st.error(f"Query failed: {result['error']}")
                    
            except Exception as e:
                st.error(f"Error executing query: {str(e)}")

# Clear chat history button
if st.session_state.chat_history:
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <small>Tendly Search - AI-Powered Tender Database Query System</small>
    </div>
    """, 
    unsafe_allow_html=True
)
