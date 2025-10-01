"""
Search utility for Tendly Search application.
Provides advanced search functionality using LangChain text-to-SQL agents.
"""

import os
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.agent_types import AgentType
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.prompts import PromptTemplate
import pandas as pd
from utils.db_util import DatabaseUtil

# Load environment variables
load_dotenv()

class TenderSearchAgent:
    """Advanced search agent for tender database queries."""
    
    def __init__(self):
        """Initialize the tender search agent."""
        self.db_url = os.getenv('DB_URL')
        if not self.db_url:
            raise ValueError("DB_URL environment variable is required")
        
        # Initialize OpenAI client
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize SQL database connection
        self.db = SQLDatabase.from_uri(self.db_url)
        
        # Create SQL toolkit and agent
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        
        # Custom prompt for tender-specific queries
        self.custom_prompt = PromptTemplate(
            input_variables=["input", "agent_scratchpad", "table_info"],
            template="""
            You are an expert assistant for querying a tender/procurement database.
            
            Database Information:
            {table_info}
            
            Guidelines for tender queries:
            1. When users ask about "construction tenders", look for construction-related keywords in tender titles or descriptions
            2. For location queries like "Harjumaa", search in location/region fields
            3. Always provide clear, business-friendly explanations
            4. Format monetary values appropriately (use Euro symbol if applicable)
            5. Handle Estonian language terms appropriately
            6. When showing results, include key fields like title, organization, value, deadline
            7. Sort results by relevance (recent dates, higher values, etc.)
            
            Common Estonian terms:
            - "hanked" = tenders/procurements
            - "Harjumaa" = Harju County (includes Tallinn)
            - "ehitus" = construction
            - "IT" = information technology
            
            Question: {input}
            
            {agent_scratchpad}
            """
        )
        
        # Create the agent with custom prompt
        self.agent = create_sql_agent(
            llm=self.llm,
            toolkit=self.toolkit,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True
        )
        
        # Initialize database utility
        self.db_util = DatabaseUtil()
    
    def search_tenders(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """
        Search tenders using natural language query.
        
        Args:
            query: Natural language search query
            limit: Maximum number of results to return
            
        Returns:
            Dictionary with search results and metadata
        """
        try:
            # Enhance the query with context and limits
            enhanced_query = f"""
            {query}
            
            Please limit results to {limit} items and include the most relevant information.
            Format the response to show key tender details like title, organization, value, and deadline.
            """
            
            # Execute search using the agent
            result = self.agent.run(enhanced_query)
            
            return {
                "success": True,
                "results": result,
                "query": query,
                "count": "Multiple results" if "SELECT" in str(result) else "1",
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "results": None,
                "query": query,
                "count": 0,
                "error": str(e)
            }
    
    def get_construction_tenders(self, limit: int = 10) -> pd.DataFrame:
        """Get construction-related tenders."""
        try:
            query = f"""
            SELECT et.*, etd.tender_name, etd.short_description, etd.estimated_cost
            FROM estonian_tenders et
            LEFT JOIN estonian_tender_details etd ON et.procurement_id = etd.procurement_id
            WHERE LOWER(et.procurement_name) LIKE '%construction%' 
               OR LOWER(et.procurement_name) LIKE '%ehitus%'
               OR LOWER(etd.short_description) LIKE '%construction%'
               OR LOWER(etd.short_description) LIKE '%ehitus%'
            ORDER BY et.created_at DESC
            LIMIT {limit}
            """
            return self.db_util.execute_query(query)
        except Exception as e:
            print(f"Error getting construction tenders: {e}")
            return pd.DataFrame()
    
    def get_tenders_by_location(self, location: str, limit: int = 10) -> pd.DataFrame:
        """Get tenders by location/region."""
        try:
            query = f"""
            SELECT et.*, etd.tender_name, etd.short_description, etd.estimated_cost, etd.nuts_code
            FROM estonian_tenders et
            LEFT JOIN estonian_tender_details etd ON et.procurement_id = etd.procurement_id
            WHERE LOWER(etd.nuts_code) LIKE '%{location.lower()}%'
               OR LOWER(etd.location_additional_info) LIKE '%{location.lower()}%'
               OR LOWER(et.contracting_authority_name) LIKE '%{location.lower()}%'
            ORDER BY et.created_at DESC
            LIMIT {limit}
            """
            return self.db_util.execute_query(query)
        except Exception as e:
            print(f"Error getting tenders by location: {e}")
            return pd.DataFrame()
    
    def get_recent_tenders(self, days: int = 30, limit: int = 10) -> pd.DataFrame:
        """Get recent tenders from the last N days."""
        try:
            query = f"""
            SELECT et.*, etd.tender_name, etd.short_description, etd.estimated_cost
            FROM estonian_tenders et
            LEFT JOIN estonian_tender_details etd ON et.procurement_id = etd.procurement_id
            WHERE et.created_at >= CURRENT_DATE - INTERVAL '{days} days'
            ORDER BY et.created_at DESC
            LIMIT {limit}
            """
            return self.db_util.execute_query(query)
        except Exception as e:
            print(f"Error getting recent tenders: {e}")
            return pd.DataFrame()
    
    def get_high_value_tenders(self, min_value: float = 100000, limit: int = 10) -> pd.DataFrame:
        """Get high-value tenders above specified amount."""
        try:
            query = f"""
            SELECT et.*, etd.tender_name, etd.short_description, etd.estimated_cost
            FROM estonian_tenders et
            LEFT JOIN estonian_tender_details etd ON et.procurement_id = etd.procurement_id
            WHERE etd.estimated_cost >= {min_value}
            ORDER BY etd.estimated_cost DESC
            LIMIT {limit}
            """
            return self.db_util.execute_query(query)
        except Exception as e:
            print(f"Error getting high-value tenders: {e}")
            return pd.DataFrame()
    
    def search_by_organization(self, organization: str, limit: int = 10) -> pd.DataFrame:
        """Search tenders by organization name."""
        try:
            query = f"""
            SELECT et.*, etd.tender_name, etd.short_description, etd.estimated_cost
            FROM estonian_tenders et
            LEFT JOIN estonian_tender_details etd ON et.procurement_id = etd.procurement_id
            WHERE LOWER(et.contracting_authority_name) LIKE '%{organization.lower()}%'
            ORDER BY et.created_at DESC
            LIMIT {limit}
            """
            return self.db_util.execute_query(query)
        except Exception as e:
            print(f"Error searching by organization: {e}")
            return pd.DataFrame()
    
    def get_tender_statistics(self) -> Dict[str, Any]:
        """Get basic statistics about the tender database."""
        try:
            stats = {}
            
            # Total tenders
            total_query = "SELECT COUNT(*) as total FROM estonian_tenders"
            total_result = self.db_util.execute_query(total_query)
            stats['total_tenders'] = total_result.iloc[0]['total'] if not total_result.empty else 0
            
            # Recent tenders (last 30 days)
            recent_query = """
            SELECT COUNT(*) as recent FROM estonian_tenders 
            WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
            """
            recent_result = self.db_util.execute_query(recent_query)
            stats['recent_tenders'] = recent_result.iloc[0]['recent'] if not recent_result.empty else 0
            
            # Average value
            avg_query = """
            SELECT AVG(etd.estimated_cost) as avg_value 
            FROM estonian_tender_details etd 
            WHERE etd.estimated_cost > 0
            """
            avg_result = self.db_util.execute_query(avg_query)
            stats['average_value'] = avg_result.iloc[0]['avg_value'] if not avg_result.empty else 0
            
            # Top organizations
            org_query = """
            SELECT contracting_authority_name, COUNT(*) as tender_count 
            FROM estonian_tenders 
            WHERE contracting_authority_name IS NOT NULL
            GROUP BY contracting_authority_name 
            ORDER BY tender_count DESC 
            LIMIT 5
            """
            org_result = self.db_util.execute_query(org_query)
            stats['top_organizations'] = org_result.to_dict('records') if not org_result.empty else []
            
            return stats
            
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}
    
    def get_predefined_searches(self) -> List[Dict[str, str]]:
        """Get list of predefined search options."""
        return [
            {
                "title": "Construction Tenders",
                "description": "Find all construction and building related tenders",
                "query": "show me construction tenders",
                "icon": "🏗️"
            },
            {
                "title": "Tenders in Harjumaa",
                "description": "Tenders in Harju County (including Tallinn)",
                "query": "tenders in Harjumaa",
                "icon": "📍"
            },
            {
                "title": "Recent Tenders",
                "description": "Most recently published tenders",
                "query": "show me the most recent tenders",
                "icon": "🕒"
            },
            {
                "title": "High Value Tenders",
                "description": "Tenders with highest estimated values",
                "query": "show me tenders with highest value",
                "icon": "💰"
            },
            {
                "title": "IT Tenders",
                "description": "Information technology related tenders",
                "query": "show me IT related tenders",
                "icon": "💻"
            },
            {
                "title": "Active Tenders",
                "description": "Currently active tenders with open deadlines",
                "query": "show me active tenders that are still open",
                "icon": "✅"
            }
        ]

def get_tender_search_agent() -> TenderSearchAgent:
    """Factory function to create and return a TenderSearchAgent instance."""
    return TenderSearchAgent()

if __name__ == "__main__":
    # Test the search agent
    agent = TenderSearchAgent()
    
    print("Testing Tender Search Agent...")
    
    # Test basic search
    result = agent.search_tenders("show me construction tenders")
    print(f"Search result: {result['success']}")
    
    # Test statistics
    stats = agent.get_tender_statistics()
    print(f"Database statistics: {stats}")
    
    # Test predefined searches
    searches = agent.get_predefined_searches()
    print(f"Available predefined searches: {len(searches)}")
