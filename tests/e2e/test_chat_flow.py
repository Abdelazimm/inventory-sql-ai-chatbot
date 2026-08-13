import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage
from app.agents.models import IntentResult, SQLGenerationResult


def test_auth_and_health_endpoints(client):
    # Health check
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

    # Ready check
    res = client.get("/ready")
    assert res.status_code == 200
    assert res.json()["database"] == "connected"

    # Login
    login_res = client.post("/auth/login", json={"username": "admin", "password": "admin123"})
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["role"] == "admin"


def test_chitchat_chat_flow(client):
    # Mock LLM intent classifier and chitchat response
    with patch("app.agents.nodes.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_structured = MagicMock()
        mock_structured.invoke.return_value = IntentResult(intent="chitchat", confidence=0.95)
        mock_llm.with_structured_output.return_value = mock_structured
        mock_llm.invoke.return_value = AIMessage(content="Hello! How can I assist with your inventory today?")
        mock_get_llm.return_value = mock_llm

        res = client.post("/chat", json={"message": "Hello!"})
        assert res.status_code == 200
        data = res.json()
        assert "inventory" in data["answer"].lower() or "hello" in data["answer"].lower()
        assert data["metadata"]["intent"] == "chitchat"
        assert data["session_id"] is not None


def test_database_query_chat_flow(client, admin_token):
    # Mock LLM generation and final response
    with patch("app.agents.nodes.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        
        # 1. Intent classifier mock
        mock_intent = MagicMock()
        mock_intent.invoke.return_value = IntentResult(intent="database_query", confidence=0.99)
        
        # 2. SQL generator mock
        mock_sql = MagicMock()
        mock_sql.invoke.return_value = SQLGenerationResult(query="SELECT AssetName, Cost FROM Assets ORDER BY Cost DESC LIMIT 1;", operation="select")
        
        mock_llm.with_structured_output.side_effect = [mock_intent, mock_sql]
        mock_llm.invoke.return_value = AIMessage(content="The most expensive asset is the ThinkPad X1 costing $1,500.00.")
        mock_get_llm.return_value = mock_llm

        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.post("/chat", json={"message": "What is the most expensive asset?"}, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "ThinkPad X1" in data["answer"]
        assert data["metadata"]["is_valid_sql"] is True
        assert data["metadata"]["generated_sql"] is not None
