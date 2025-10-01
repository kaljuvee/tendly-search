"""
SQL Chat utility for Tendly Search application.
Provides natural language to SQL conversion using LangChain and OpenAI.
"""

import os
from typing import Dict, List, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.agent_types import AgentType
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.schema import HumanMessage, SystemMessage
import pandas as pd
from utils.db_util import DatabaseUtil

# Load environment variables
load_dotenv()

class SQLChatAssistant:
    """Assistant for natural language database queries using LangChain."""
    
    def __init__(self, db_path=None):
        """Initialize the SQL chat assistant."""
        self.db_url = os.getenv('DB_URL')
        if not self.db_url:
            raise ValueError("DB_URL environment variable is required")
        
        # Initialize OpenAI client
        self.llm = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize SQL database connection
        self.db = SQLDatabase.from_uri(self.db_url)
        
        # Create SQL agent
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        self.agent = create_sql_agent(
            llm=self.llm,
            toolkit=self.toolkit,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True
        )
        
        # Initialize database utility for schema info
        self.db_util = DatabaseUtil()
    
    def get_database_schema(self) -> str:
        """Get a description of the database schema."""
        return self.db_util.get_table_info_for_langchain()
    
    def get_sample_queries(self) -> List[Dict[str, str]]:
        """Get sample queries users can try."""
        return [
            {
                "question": "Show me construction tenders",
                "category": "Tender Analysis"
            },
            {
                "question": "Tenders in Harjumaa",
                "category": "Geographic Analysis"
            },
            {
                "question": "What are the most recent tenders?",
                "category": "Tender Analysis"
            },
            {
                "question": "Show me tenders with highest value",
                "category": "Financial Analysis"
            },
            {
                "question": "Which organizations have the most tenders?",
                "category": "Organization Analysis"
            },
            {
                "question": "Show me expired tenders",
                "category": "Status Analysis"
            },
            {
                "question": "What types of procurement are most common?",
                "category": "Procurement Analysis"
            },
            {
                "question": "Show me tenders from this month",
                "category": "Time Analysis"
            },
            {
                "question": "Which regions have the most tender activity?",
                "category": "Geographic Analysis"
            },
            {
                "question": "Show me IT related tenders",
                "category": "Category Analysis"
            }
        ]
    
    def chat_with_database(self, question: str) -> Dict[str, Any]:
        """
        Process a natural language question and return SQL results.
        """
        try:
            # Add context about the database structure
            context_prompt = f"""
            You are a helpful AI assistant that can answer questions about a tender database.
            
            Database Schema:
            {self.get_database_schema()}
            
            Important Notes:
            - The database contains Estonian tender/procurement data
            - Use proper table joins when needed
            - Handle NULL values appropriately
            - Format monetary values with Euro symbol
            - Provide clear, business-friendly explanations
            
            Please answer the following question: {question}
            
            If you need to write SQL, make sure to:
            1. Use proper table joins when needed
            2. Handle NULL values appropriately
            3. Format monetary values with Euro symbol
            4. Provide clear, business-friendly explanations
            """
            
            # Execute the query using the agent
            result = self.agent.run(context_prompt)
            
            return {
                "success": True,
                "answer": result,
                "question": question,
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "answer": None,
                "question": question,
                "error": str(e)
            }
    
    def execute_direct_sql(self, sql_query: str) -> Dict[str, Any]:
        """
        Execute a direct SQL query (for advanced users).
        """
        try:
            result = self.db_util.execute_query(sql_query)
            
            return {
                "success": True,
                "data": result,
                "query": sql_query,
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "query": sql_query,
                "error": str(e)
            }
    
    def get_table_preview(self, table_name: str, limit: int = 5) -> pd.DataFrame:
        """Get a preview of data from a specific table."""
        return self.db_util.get_sample_data(table_name, limit)
    
    def get_available_tables(self) -> List[str]:
        """Get list of available tables in the database."""
        return self.db_util.get_table_names()

def get_sql_chat_assistant() -> SQLChatAssistant:
    """Factory function to create and return a SQLChatAssistant instance."""
    return SQLChatAssistant()

if __name__ == "__main__":
    # Test the SQL chat assistant
    assistant = SQLChatAssistant()
    
    print("Available tables:")
    tables = assistant.get_available_tables()
    for table in tables:
        print(f"- {table}")
    
    print("\nSample queries:")
    samples = assistant.get_sample_queries()
    for sample in samples[:3]:
        print(f"- {sample['question']} ({sample['category']})")
    
    print("\nDatabase schema:")
    print(assistant.get_database_schema())
