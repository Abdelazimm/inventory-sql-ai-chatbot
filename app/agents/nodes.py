import os
import json
import logging
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from app.config import settings
from app.agents.state import InventorySQLState
from app.agents.models import IntentResult, SQLGenerationResult, SQLCorrectionResult
from app.agents.schema import get_dynamic_schema
from app.agents.validator import validate_sql_query
from app.agents.executor import execute_sql_query
from app.agents.prompts import (
    INTENT_SYSTEM_PROMPT, CHITCHAT_SYSTEM_PROMPT,
    SQL_GENERATOR_SYSTEM_PROMPT, SQL_CORRECTOR_SYSTEM_PROMPT,
    RESPONSE_SYSTEM_PROMPT
)

logger = logging.getLogger(__name__)


def get_llm():
    """Instantiates the ChatOpenAI client."""
    return ChatOpenAI(
        model=settings.MODEL_NAME,
        temperature=settings.TEMPERATURE,
        api_key=settings.OPENAI_API_KEY
    )


def intent_parser_node(state: InventorySQLState) -> Dict[str, Any]:
    """Classifies user message intent into structured IntentResult."""
    question = state.get("question", "")
    recent_messages = state.get("messages", [])[-6:]
    
    # Try structured LLM classification
    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(IntentResult)
        result: IntentResult = structured_llm.invoke(
            [SystemMessage(content=INTENT_SYSTEM_PROMPT)] +
            recent_messages +
            [HumanMessage(content=f"Classify this message: '{question}'")]
        )
        return {
            "intent": result.intent,
            "intent_confidence": result.confidence,
            "error": None
        }
    except Exception as e:
        logger.warning(f"Intent parser fallback triggered due to: {e}")
        # Heuristic fallback if LLM offline / mocked
        q_lower = question.lower()
        if any(greet in q_lower for greet in ["hello", "hi", "hey", "good morning", "good afternoon", "who are you", "what can you do"]):
            return {"intent": "chitchat", "intent_confidence": 0.9, "error": None}
        if any(mut in q_lower for mut in ["delete", "remove", "insert", "create asset", "add asset", "update vendor"]):
            return {"intent": "mutation", "intent_confidence": 0.85, "error": None}
        return {"intent": "database_query", "intent_confidence": 0.9, "error": None}


def chitchat_node(state: InventorySQLState) -> Dict[str, Any]:
    """Handles general conversational chitchat."""
    question = state.get("question", "")
    recent_messages = state.get("messages", [])[-4:]
    
    try:
        llm = get_llm()
        response = llm.invoke(
            [SystemMessage(content=CHITCHAT_SYSTEM_PROMPT)] +
            recent_messages +
            [HumanMessage(content=question)]
        )
        content = response.content
    except Exception as e:
        content = "Hello! I am your AI Inventory Analytics Assistant. You can ask me questions about assets, vendors, purchase orders, sales orders, sites, and stock levels."
        
    return {
        "messages": [AIMessage(content=content)]
    }


def sql_generator_node(state: InventorySQLState) -> Dict[str, Any]:
    """Generates a structured SQL query from question & dynamic schema."""
    question = state.get("question", "")
    schema = get_dynamic_schema()
    recent_messages = state.get("messages", [])[-6:]
    
    prompt = SQL_GENERATOR_SYSTEM_PROMPT.format(schema=schema)
    
    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(SQLGenerationResult)
        result: SQLGenerationResult = structured_llm.invoke(
            [SystemMessage(content=prompt)] +
            recent_messages +
            [HumanMessage(content=question)]
        )
        query = result.query
    except Exception as e:
        # Fallback to direct raw invocation if structured output fails
        try:
            llm = get_llm()
            resp = llm.invoke(
                [SystemMessage(content=prompt + "\nReturn ONLY the raw SQL query, no markdown.")] +
                recent_messages +
                [HumanMessage(content=question)]
            )
            query = resp.content.strip()
        except Exception as e2:
            query = "SELECT * FROM Assets LIMIT 5;"
            
    return {
        "sql_query": query,
        "is_valid": None,
        "validation_error": None,
        "execution_error": None,
        "error": None
    }


def sql_validator_node(state: InventorySQLState) -> Dict[str, Any]:
    """Validates the generated SQL query for AST safety and read-only compliance."""
    query = state.get("sql_query", "")
    is_valid, validation_error = validate_sql_query(query)
    
    return {
        "is_valid": is_valid,
        "validation_error": validation_error,
        "error": validation_error if not is_valid else None
    }


def sql_executor_node(state: InventorySQLState) -> Dict[str, Any]:
    """Executes the validated SQL query against the database engine."""
    query = state.get("sql_query", "")
    
    # If not valid from validator, skip execution
    if not state.get("is_valid", False):
        return {
            "error": state.get("validation_error", "SQL validation failed."),
            "execution_error": state.get("validation_error", "SQL validation failed.")
        }
        
    try:
        rows, exec_time = execute_sql_query(query)
        return {
            "sql_result": rows,
            "execution_time_ms": exec_time,
            "execution_error": None,
            "error": None
        }
    except Exception as e:
        return {
            "execution_error": str(e),
            "error": str(e),
            "retries": state.get("retries", 0) + 1
        }


def sql_corrector_node(state: InventorySQLState) -> Dict[str, Any]:
    """Corrects a failed SQL query using schema and error diagnostic."""
    schema = get_dynamic_schema()
    query = state.get("sql_query", "")
    error_msg = state.get("error", "Unknown error")
    question = state.get("question", "")
    recent_messages = state.get("messages", [])[-4:]
    
    prompt = SQL_CORRECTOR_SYSTEM_PROMPT.format(
        schema=schema,
        sql_query=query,
        error=error_msg
    )
    
    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(SQLCorrectionResult)
        result: SQLCorrectionResult = structured_llm.invoke(
            [SystemMessage(content=prompt)] +
            recent_messages +
            [HumanMessage(content=f"Fix query for: {question}")]
        )
        fixed_query = result.query
    except Exception:
        try:
            llm = get_llm()
            resp = llm.invoke(
                [SystemMessage(content=prompt + "\nReturn ONLY the fixed raw SQL query.")] +
                recent_messages +
                [HumanMessage(content=f"Fix query for: {question}")]
            )
            fixed_query = resp.content.strip()
        except Exception:
            fixed_query = "SELECT * FROM Assets LIMIT 5;"
            
    return {
        "sql_query": fixed_query,
        "is_valid": None,
        "validation_error": None,
        "error": None
    }


def final_response_node(state: InventorySQLState) -> Dict[str, Any]:
    """Generates a natural, grounded response based on SQL results."""
    question = state.get("question", "")
    sql_result = state.get("sql_result", [])
    recent_messages = state.get("messages", [])[-4:]
    
    result_str = json.dumps(sql_result, default=str) if isinstance(sql_result, (list, dict)) else str(sql_result)
    
    prompt = f"{RESPONSE_SYSTEM_PROMPT}\n\nUser Question: {question}\n\nSQL Results Data:\n{result_str}"
    
    try:
        llm = get_llm()
        response = llm.invoke(
            [SystemMessage(content=prompt)] +
            recent_messages +
            [HumanMessage(content=f"Answer the question based on the data: {question}")]
        )
        content = response.content
    except Exception as e:
        # Fallback formatting
        if not sql_result:
            content = "No matching records were found in the database."
        else:
            content = f"Here are the results retrieved from the inventory database:\n{result_str}"
            
    return {
        "messages": [AIMessage(content=content)]
    }


def error_response_node(state: InventorySQLState) -> Dict[str, Any]:
    """Provides a graceful failure message after max retries or security violation."""
    error_msg = state.get("error", "Unable to complete query.")
    
    if "forbidden" in error_msg.lower() or "read-only" in error_msg.lower():
        msg = f"Security Notice: The requested operation could not be performed. {error_msg}"
    else:
        msg = "I was unable to retrieve the requested data after multiple attempts. Please try rephrasing your question or specifying different criteria."
        
    return {
        "messages": [AIMessage(content=msg)]
    }
