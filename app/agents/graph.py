import sqlite3
from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from app.agents.state import InventorySQLState
from app.agents.nodes import (
    intent_parser_node,
    chitchat_node,
    sql_generator_node,
    sql_validator_node,
    sql_executor_node,
    sql_corrector_node,
    final_response_node,
    error_response_node
)
from app.config import settings


def route_by_intent(state: InventorySQLState) -> Literal["chitchat", "sql_generator"]:
    intent = state.get("intent", "database_query")
    if intent == "chitchat":
        return "chitchat"
    return "sql_generator"


def route_after_validation(state: InventorySQLState) -> Literal["sql_executor", "sql_corrector", "error_response"]:
    if not state.get("is_valid", False):
        val_error = state.get("validation_error", "")
        # Do not retry severe security violations (e.g. DROP, DELETE)
        if any(sec in val_error.lower() for sec in ["forbidden", "only read-only", "detected", "multiple"]):
            return "error_response"
            
        retries = state.get("retries", 0)
        if retries < 3:
            return "sql_corrector"
        return "error_response"
    return "sql_executor"


def route_after_execution(state: InventorySQLState) -> Literal["final_response", "sql_corrector", "error_response"]:
    error = state.get("execution_error") or state.get("error")
    if error is None:
        return "final_response"
    
    retries = state.get("retries", 0)
    if retries < 3:
        return "sql_corrector"
    return "error_response"


def build_sql_graph(checkpointer=None):
    workflow = StateGraph(InventorySQLState)
    
    # Add Nodes
    workflow.add_node("intent_parser", intent_parser_node)
    workflow.add_node("chitchat", chitchat_node)
    workflow.add_node("sql_generator", sql_generator_node)
    workflow.add_node("sql_validator", sql_validator_node)
    workflow.add_node("sql_executor", sql_executor_node)
    workflow.add_node("sql_corrector", sql_corrector_node)
    workflow.add_node("final_response", final_response_node)
    workflow.add_node("error_response", error_response_node)
    
    # Set Entry Point
    workflow.set_entry_point("intent_parser")
    
    # Intent Branching
    workflow.add_conditional_edges(
        "intent_parser",
        route_by_intent,
        {
            "chitchat": "chitchat",
            "sql_generator": "sql_generator"
        }
    )
    
    workflow.add_edge("chitchat", END)
    
    # Generator -> Validator
    workflow.add_edge("sql_generator", "sql_validator")
    
    # Validator -> (Executor | Corrector | ErrorResponse)
    workflow.add_conditional_edges(
        "sql_validator",
        route_after_validation,
        {
            "sql_executor": "sql_executor",
            "sql_corrector": "sql_corrector",
            "error_response": "error_response"
        }
    )
    
    # Executor -> (FinalResponse | Corrector | ErrorResponse)
    workflow.add_conditional_edges(
        "sql_executor",
        route_after_execution,
        {
            "final_response": "final_response",
            "sql_corrector": "sql_corrector",
            "error_response": "error_response"
        }
    )
    
    # Corrector -> Validator (Always re-validate corrected queries!)
    workflow.add_edge("sql_corrector", "sql_validator")
    
    # Terminal edges
    workflow.add_edge("final_response", END)
    workflow.add_edge("error_response", END)
    
    return workflow.compile(checkpointer=checkpointer)


# Setup persistent SQLite checkpointer for session state
try:
    checkpointer_conn = sqlite3.connect(settings.CHECKPOINTS_DB_PATH, check_same_thread=False)
    sqlite_saver = SqliteSaver(checkpointer_conn)
    sqlite_saver.setup()
    sql_agent_app = build_sql_graph(checkpointer=sqlite_saver)
except Exception:
    # Fallback to in-memory/uncheckpointed if file lock
    sql_agent_app = build_sql_graph()
