import os
import sys
import uuid
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage
from app.agents.graph import sql_agent_app
from app.config import settings


def run_cli():
    session_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}
    
    print("=" * 60)
    print("  Enterprise Inventory SQL AI Assistant (CLI Mode)")
    print(f"  Session ID: {session_id}")
    print("  Type 'exit', 'quit', or 'q' to end the session.")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSession ended.")
            break
            
        if not user_input:
            continue
            
        if user_input.lower() in ["exit", "quit", "q"]:
            print("Goodbye!")
            break
            
        inputs = {
            "messages": [HumanMessage(content=user_input)],
            "question": user_input,
            "session_id": session_id,
            "user_role": "admin",
            "retries": 0,
            "model_name": settings.MODEL_NAME
        }
        
        try:
            final_state = sql_agent_app.invoke(inputs, config=config)
            if final_state and "messages" in final_state and len(final_state["messages"]) > 0:
                print(f"\nAssistant: {final_state['messages'][-1].content}")
                if final_state.get("sql_query"):
                    print(f"\n[DEBUG - SQL]: {final_state['sql_query']}")
            else:
                print("\nAssistant: No response was generated.")
        except Exception as e:
            print(f"\n[Error]: {str(e)}")


if __name__ == "__main__":
    run_cli()
