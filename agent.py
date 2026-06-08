"""
agent.py — LangChain SQL Agent powered by Groq (Llama 3).

The agent receives a plain-English question, generates SQL,
runs it against the SQLite database, and returns a formatted answer.
"""

import os
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()


# System prompt
AGENT_PREFIX = """
You are a senior logistics operations analyst at LoadShare India.
You help operations teams, product managers, and leadership understand
delivery performance by querying the logistics database.

Database schema:
- orders: order_id, customer_id, origin_city, destination_city,
          delivery_partner, category, status, amount, weight_kg,
          created_at, expected_at, delivered_at, delay_reason
  status values: delivered | pending | cancelled | delayed | in_transit | returned
  Dates stored as TEXT 'YYYY-MM-DD HH:MM:SS'

- delivery_partners: partner_id, name, base_city, rating, active_orders

- cities: city_id, name, state, zone
  zone values: North | South | East | West | Central

- daily_metrics: metric_id, date (TEXT 'YYYY-MM-DD'), city,
                 total_orders, delivered_orders, cancelled_orders,
                 delayed_orders, avg_delivery_time_hrs

Rules:
1. Use strftime('%Y-%m-%d', created_at) for date comparisons.
2. "Last 30 days" means created_at >= date('now', '-30 days').
3. "Last week" means created_at >= date('now', '-7 days').
4. Always JOIN cities or delivery_partners when zone/state/rating is needed.
5. Round all percentages to 1 decimal place.
6. Return a clear, concise answer — no raw SQL in the final response.
7. If the question is ambiguous, answer the most useful interpretation.
"""


def build_agent():
    """Build and return the LangChain SQL agent. Called once at startup."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY not found. "
        )

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",  
        temperature=0,                    
        groq_api_key=api_key,
    )

    db = SQLDatabase.from_uri(
        "sqlite:///logistics.db",
        include_tables=["orders", "delivery_partners", "cities", "daily_metrics"],
        sample_rows_in_table_info=3,  
    )

    agent = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools",   
        verbose=True,                
        max_iterations=15,
        handle_parsing_errors=True,
        prefix=AGENT_PREFIX,
    )

    return agent


# Singleton
_agent = None


def get_agent():
    global _agent
    if _agent is None:
        print("🔧  Initialising agent (first call only)…")
        _agent = build_agent()
    return _agent


def ask(question: str) -> str:
    """
    Public interface used by main.py.
    Returns the agent's plain-English answer.
    """
    result = get_agent().invoke({"input": question})
    return result["output"]


if __name__ == "__main__":
    test_q = "Which city had the most delayed orders?"
    print(f"\nQuestion: {test_q}\n")
    print(ask(test_q))
