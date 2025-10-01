"""
Database utility module for Tendly Search application.
Provides database connection and schema introspection functionality using SQLAlchemy.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, inspect, text
from sqlalchemy.orm import sessionmaker
import pandas as pd
from typing import Dict, List, Any

# Load environment variables
load_dotenv()

class DatabaseUtil:
    """Utility class for database operations and schema introspection."""
    
    def __init__(self):
        """Initialize database connection using environment variables."""
        self.db_url = os.getenv('DB_URL')
        if not self.db_url:
            raise ValueError("DB_URL environment variable is required")
        
        self.engine = create_engine(self.db_url)
        self.metadata = MetaData()
        self.inspector = inspect(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def get_table_names(self) -> List[str]:
        """Get all table names in the database."""
        return self.inspector.get_table_names()
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get detailed schema information for a specific table."""
        columns = self.inspector.get_columns(table_name)
        primary_keys = self.inspector.get_pk_constraint(table_name)
        foreign_keys = self.inspector.get_foreign_keys(table_name)
        indexes = self.inspector.get_indexes(table_name)
        
        return {
            'table_name': table_name,
            'columns': columns,
            'primary_keys': primary_keys,
            'foreign_keys': foreign_keys,
            'indexes': indexes
        }
    
    def get_all_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get schema information for all tables in the database."""
        schemas = {}
        for table_name in self.get_table_names():
            schemas[table_name] = self.get_table_schema(table_name)
        return schemas
    
    def get_sample_data(self, table_name: str, limit: int = 5) -> pd.DataFrame:
        """Get sample data from a table."""
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        return pd.read_sql(query, self.engine)
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a SQL query and return results as a DataFrame."""
        return pd.read_sql(query, self.engine)
    
    def get_table_info_for_langchain(self) -> str:
        """Get formatted table information suitable for LangChain SQL agents."""
        table_info = []
        
        for table_name in self.get_table_names():
            schema = self.get_table_schema(table_name)
            
            # Format column information
            columns_info = []
            for col in schema['columns']:
                col_info = f"  {col['name']} ({col['type']})"
                if col.get('nullable', True) == False:
                    col_info += " NOT NULL"
                if col.get('default') is not None:
                    col_info += f" DEFAULT {col['default']}"
                columns_info.append(col_info)
            
            # Format primary keys
            pk_info = ""
            if schema['primary_keys']['constrained_columns']:
                pk_info = f"  PRIMARY KEY: {', '.join(schema['primary_keys']['constrained_columns'])}"
            
            # Combine table information
            table_desc = f"Table: {table_name}\n"
            table_desc += "Columns:\n" + "\n".join(columns_info)
            if pk_info:
                table_desc += f"\n{pk_info}"
            
            table_info.append(table_desc)
        
        return "\n\n".join(table_info)
    
    def close(self):
        """Close database connections."""
        self.session.close()
        self.engine.dispose()

def get_database_util() -> DatabaseUtil:
    """Factory function to create and return a DatabaseUtil instance."""
    return DatabaseUtil()

if __name__ == "__main__":
    # Test the database utility
    db_util = DatabaseUtil()
    
    print("Available tables:")
    tables = db_util.get_table_names()
    for table in tables:
        print(f"- {table}")
    
    print("\nTable schemas:")
    schemas = db_util.get_all_schemas()
    for table_name, schema in schemas.items():
        print(f"\n{table_name}:")
        for col in schema['columns']:
            print(f"  {col['name']}: {col['type']}")
    
    print("\nLangChain formatted table info:")
    print(db_util.get_table_info_for_langchain())
    
    db_util.close()
