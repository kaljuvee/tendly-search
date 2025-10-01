"""
Simple search utility as fallback for Tendly Search application.
Provides basic search functionality using direct SQL queries when AI fails.
"""

import os
import pandas as pd
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from utils.db_util import DatabaseUtil

# Load environment variables
load_dotenv()

class SimpleSearchAgent:
    """Simple search agent using direct SQL queries."""
    
    def __init__(self):
        """Initialize the simple search agent."""
        self.db_util = DatabaseUtil()
    
    def search_construction_tenders(self, limit: int = 20) -> Dict[str, Any]:
        """Search for construction-related tenders."""
        try:
            query = """
            SELECT 
                title,
                description,
                estimated_value,
                deadline,
                organization_name,
                location
            FROM estonian_tenders 
            WHERE 
                LOWER(title) LIKE '%ehitus%' 
                OR LOWER(title) LIKE '%construction%'
                OR LOWER(title) LIKE '%building%'
                OR LOWER(description) LIKE '%ehitus%'
                OR LOWER(description) LIKE '%construction%'
                OR LOWER(description) LIKE '%building%'
            ORDER BY deadline DESC 
            LIMIT %s
            """
            
            result = self.db_util.execute_query(query, (limit,))
            
            return {
                "success": True,
                "results": result,
                "count": len(result) if result is not None else 0,
                "query_type": "construction_tenders"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": None
            }
    
    def search_harjumaa_tenders(self, limit: int = 20) -> Dict[str, Any]:
        """Search for tenders in Harjumaa region."""
        try:
            query = """
            SELECT 
                title,
                description,
                estimated_value,
                deadline,
                organization_name,
                location
            FROM estonian_tenders 
            WHERE 
                LOWER(location) LIKE '%harjumaa%'
                OR LOWER(location) LIKE '%harju%'
                OR LOWER(organization_name) LIKE '%tallinn%'
            ORDER BY deadline DESC 
            LIMIT %s
            """
            
            result = self.db_util.execute_query(query, (limit,))
            
            return {
                "success": True,
                "results": result,
                "count": len(result) if result is not None else 0,
                "query_type": "harjumaa_tenders"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": None
            }
    
    def search_high_value_tenders(self, min_value: int = 100000, limit: int = 20) -> Dict[str, Any]:
        """Search for high-value tenders."""
        try:
            query = """
            SELECT 
                title,
                description,
                estimated_value,
                deadline,
                organization_name,
                location
            FROM estonian_tenders 
            WHERE 
                estimated_value >= %s
            ORDER BY estimated_value DESC 
            LIMIT %s
            """
            
            result = self.db_util.execute_query(query, (min_value, limit))
            
            return {
                "success": True,
                "results": result,
                "count": len(result) if result is not None else 0,
                "query_type": "high_value_tenders"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": None
            }
    
    def search_recent_tenders(self, days: int = 30, limit: int = 20) -> Dict[str, Any]:
        """Search for recent tenders."""
        try:
            query = """
            SELECT 
                title,
                description,
                estimated_value,
                deadline,
                organization_name,
                location,
                published_date
            FROM estonian_tenders 
            WHERE 
                published_date >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY published_date DESC 
            LIMIT %s
            """
            
            result = self.db_util.execute_query(query, (days, limit))
            
            return {
                "success": True,
                "results": result,
                "count": len(result) if result is not None else 0,
                "query_type": "recent_tenders"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": None
            }
    
    def search_it_tenders(self, limit: int = 20) -> Dict[str, Any]:
        """Search for IT-related tenders."""
        try:
            query = """
            SELECT 
                title,
                description,
                estimated_value,
                deadline,
                organization_name,
                location
            FROM estonian_tenders 
            WHERE 
                LOWER(title) LIKE '%it%'
                OR LOWER(title) LIKE '%software%'
                OR LOWER(title) LIKE '%tarkvara%'
                OR LOWER(title) LIKE '%infotehnoloogia%'
                OR LOWER(description) LIKE '%software%'
                OR LOWER(description) LIKE '%tarkvara%'
                OR LOWER(description) LIKE '%infotehnoloogia%'
            ORDER BY deadline DESC 
            LIMIT %s
            """
            
            result = self.db_util.execute_query(query, (limit,))
            
            return {
                "success": True,
                "results": result,
                "count": len(result) if result is not None else 0,
                "query_type": "it_tenders"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": None
            }
    
    def search_active_tenders(self, limit: int = 20) -> Dict[str, Any]:
        """Search for active tenders (deadline in future)."""
        try:
            query = """
            SELECT 
                title,
                description,
                estimated_value,
                deadline,
                organization_name,
                location
            FROM estonian_tenders 
            WHERE 
                deadline >= CURRENT_DATE
            ORDER BY deadline ASC 
            LIMIT %s
            """
            
            result = self.db_util.execute_query(query, (limit,))
            
            return {
                "success": True,
                "results": result,
                "count": len(result) if result is not None else 0,
                "query_type": "active_tenders"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": None
            }
    
    def search_by_keyword(self, keyword: str, limit: int = 20) -> Dict[str, Any]:
        """Search tenders by keyword."""
        try:
            query = """
            SELECT 
                title,
                description,
                estimated_value,
                deadline,
                organization_name,
                location
            FROM estonian_tenders 
            WHERE 
                LOWER(title) LIKE %s
                OR LOWER(description) LIKE %s
                OR LOWER(organization_name) LIKE %s
            ORDER BY deadline DESC 
            LIMIT %s
            """
            
            search_term = f"%{keyword.lower()}%"
            result = self.db_util.execute_query(query, (search_term, search_term, search_term, limit))
            
            return {
                "success": True,
                "results": result,
                "count": len(result) if result is not None else 0,
                "query_type": "keyword_search",
                "keyword": keyword
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": None
            }
    
    def close(self):
        """Close database connection."""
        if self.db_util:
            self.db_util.close()

def get_simple_search_agent():
    """Factory function to create a simple search agent."""
    return SimpleSearchAgent()
