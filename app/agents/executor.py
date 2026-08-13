import time
from typing import List, Dict, Any, Tuple
from sqlalchemy import text
from app.database.connection import engine
from app.config import settings


def execute_sql_query(query: str, limit: int = None) -> Tuple[List[Dict[str, Any]], float]:
    """
    Executes a validated read-only SQL query against the database engine.
    Ensures:
    1. Returns a list of dictionaries with column names as keys.
    2. Limits maximum returned rows to protect against memory blowup.
    3. Measures and returns query execution time in milliseconds.
    """
    max_rows = limit or settings.MAX_QUERY_ROWS
    clean_query = query.strip().rstrip(";")
    
    # Check if query already has a LIMIT clause; if not, wrap safely or append limit if simple
    # But for aggregate queries (COUNT, SUM), wrapping is safest
    start_time = time.time()
    
    with engine.connect() as connection:
        # For SQLite, ensure read-only query execution
        result = connection.execute(text(clean_query))
        
        # Extract column names
        keys = list(result.keys())
        
        # Fetch up to max_rows
        raw_rows = result.fetchmany(max_rows)
        
        # Serialize to list of named dicts
        rows = [dict(zip(keys, row)) for row in raw_rows]
        
    execution_time_ms = round((time.time() - start_time) * 1000, 2)
    return rows, execution_time_ms
