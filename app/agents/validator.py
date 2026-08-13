import re
from typing import Tuple, Optional
import sqlglot
from sqlglot import exp


FORBIDDEN_EXPRESSIONS = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Drop,
    exp.Create,
    exp.Alter,
    exp.Command,
    exp.Transaction,
    exp.Commit,
    exp.Rollback,
    exp.Pragma,
)

FORBIDDEN_KEYWORDS = [
    "ATTACH", "DETACH", "PRAGMA", "VACUUM", "INTO OUTFILE", "LOAD_FILE", 
    "EXEC", "EXECUTE", "XP_CMDSHELL", "SHUTDOWN"
]


def validate_sql_query(query: str, dialect: str = "sqlite") -> Tuple[bool, Optional[str]]:
    """
    Validates a SQL query string for security and safety.
    1. Checks for empty query
    2. Uses sqlglot to parse the query AST
    3. Ensures exactly one statement is present (no stacked queries)
    4. Ensures the root statement is a SELECT or WITH ... SELECT
    5. Walks AST nodes to verify no forbidden mutation expressions exist
    6. Checks forbidden keywords regex
    """
    if not query or not query.strip():
        return False, "Query string is empty."
    
    clean_query = query.strip()
    
    # Strip markdown if present
    if clean_query.startswith("```sql"):
        clean_query = clean_query[6:]
    elif clean_query.startswith("```"):
        clean_query = clean_query[3:]
    if clean_query.endswith("```"):
        clean_query = clean_query[:-3]
    clean_query = clean_query.strip()
    
    # Check for forbidden keywords before parsing
    upper_query = clean_query.upper()
    for kw in FORBIDDEN_KEYWORDS:
        # Match whole keyword with word boundaries
        if re.search(rf"\b{kw}\b", upper_query):
            return False, f"Query contains forbidden keyword or command: '{kw}'"

    # AST Parse using sqlglot
    try:
        parsed_statements = sqlglot.parse(clean_query, read=dialect)
    except Exception as e:
        # If dialect parsing fails, try generic
        try:
            parsed_statements = sqlglot.parse(clean_query)
        except Exception as generic_err:
            return False, f"SQL Syntax/Parser Error: {str(generic_err)}"

    if not parsed_statements:
        return False, "Unable to parse SQL statement."

    if len(parsed_statements) > 1:
        return False, f"Multiple SQL statements detected ({len(parsed_statements)}). Only single queries are permitted."

    root_stmt = parsed_statements[0]
    if root_stmt is None:
        return False, "Invalid SQL statement."

    # Verify statement is a Select or Expression ending in Select
    is_select = isinstance(root_stmt, exp.Select)
    is_cte_select = False
    if isinstance(root_stmt, exp.Expression):
        # A CTE like WITH a AS (...) SELECT ...
        if root_stmt.find(exp.Select) is not None and not any(isinstance(root_stmt, f_type) for f_type in FORBIDDEN_EXPRESSIONS):
            is_cte_select = True

    if not (is_select or is_cte_select):
        stmt_type = root_stmt.key if hasattr(root_stmt, "key") else type(root_stmt).__name__
        return False, f"Only read-only SELECT queries are allowed. Attempted operation: {stmt_type}"

    # Walk AST and check for forbidden nodes anywhere in the tree
    for node in root_stmt.walk():
        if isinstance(node, FORBIDDEN_EXPRESSIONS):
            return False, f"Forbidden SQL operation detected: {type(node).__name__}"

    return True, None
