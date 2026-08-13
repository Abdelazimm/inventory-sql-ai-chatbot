from typing import Dict, Any, List
from sqlalchemy import inspect
from app.database.connection import engine


def get_dynamic_schema(engine_instance=None) -> str:
    """
    Introspects the relational database dynamically using SQLAlchemy Inspector.
    Extracts table names, column names, data types, primary keys, and foreign keys.
    Returns a comprehensive formatted schema string for the LLM prompt.
    """
    eng = engine_instance or engine
    inspector = inspect(eng)
    
    schema_parts = []
    
    # Tables to exclude from general inventory user queries (internal metadata/auth)
    exclude_tables = {"Users", "ChatSessions"}
    
    table_names = inspector.get_table_names()
    for table_name in table_names:
        if table_name in exclude_tables:
            continue
            
        columns = inspector.get_columns(table_name)
        pk_constraint = inspector.get_pk_constraint(table_name)
        pks = set(pk_constraint.get("constrained_columns", []) if pk_constraint else [])
        fks = inspector.get_foreign_keys(table_name)
        
        table_lines = [f"Table: {table_name}"]
        table_lines.append("Columns:")
        for col in columns:
            col_name = col["name"]
            col_type = str(col["type"])
            is_pk = " PRIMARY KEY" if col_name in pks else ""
            nullable = "" if col.get("nullable", True) else " NOT NULL"
            table_lines.append(f"  - {col_name} ({col_type}{is_pk}{nullable})")
            
        if fks:
            table_lines.append("Foreign Keys:")
            for fk in fks:
                constrained = ", ".join(fk.get("constrained_columns", []))
                referred_table = fk.get("referred_table", "")
                referred_cols = ", ".join(fk.get("referred_columns", []))
                table_lines.append(f"  - {table_name}.({constrained}) -> {referred_table}.({referred_cols})")
                
        schema_parts.append("\n".join(table_lines))
        
    return "\n\n".join(schema_parts)


def get_schema_dict(engine_instance=None) -> Dict[str, Any]:
    """Returns the introspected database schema as a structured dictionary."""
    eng = engine_instance or engine
    inspector = inspect(eng)
    
    schema_dict = {}
    exclude_tables = {"Users", "ChatSessions"}
    
    for table_name in inspector.get_table_names():
        if table_name in exclude_tables:
            continue
        columns = inspector.get_columns(table_name)
        pk_constraint = inspector.get_pk_constraint(table_name)
        fks = inspector.get_foreign_keys(table_name)
        schema_dict[table_name] = {
            "columns": [{"name": c["name"], "type": str(c["type"]), "nullable": c.get("nullable", True)} for c in columns],
            "primary_keys": pk_constraint.get("constrained_columns", []) if pk_constraint else [],
            "foreign_keys": fks
        }
    return schema_dict
