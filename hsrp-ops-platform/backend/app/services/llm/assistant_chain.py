"""HSRP AI Assistant — Azure OpenAI + LangChain agent with live analytics tools."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.prebuilt import create_react_agent

from app.core.config import settings
from app.services.llm.azure_client import get_azure_llm
from app.services.llm.context import context_to_json
from app.services.llm.tools import build_analytics_tools

SYSTEM_PROMPT = """You are the AI Operations Assistant for National HSRP Enterprise (HSRP Ops).
You help executives and operations managers understand PAN India HSRP data: revenue, pendency, inventory, ESO performance, TAT, and forecasts.

Rules:
- ALWAYS use the provided tools to fetch live data before answering factual questions.
- Answer in clear, professional English. Use ₹ for Indian Rupee amounts.
- Cite specific numbers from tool results. If data is empty, say so.
- For strategic questions, combine multiple tool calls.
- Keep answers concise (2-5 sentences) unless the user asks for detail.
- Never invent statistics — only use tool output.

Initial context snapshot (may be stale — prefer tools for accuracy):
{context}
"""


def ask_with_langchain(db, question: str, vehicle_type: str | None = None) -> dict:
    q = question.strip()
    if not q:
        return {
            "answer": "Please ask a question about HSRP operations.",
            "sources": [],
            "llm_used": False,
        }

    llm = get_azure_llm(temperature=0.2, max_tokens=1200)
    if not llm:
        from app.services.assistant_fallback import ask as rule_ask

        result = rule_ask(db, q)
        result["llm_used"] = False
        result["warning"] = "Azure OpenAI not configured. Set AZURE_OPENAI_* in .env"
        return result

    tools = build_analytics_tools(db, vehicle_type)
    context = context_to_json(db, vehicle_type)

    try:
        agent = create_react_agent(llm, tools)
        result = agent.invoke(
            {
                "messages": [
                    SystemMessage(content=SYSTEM_PROMPT.format(context=context[:8000])),
                    HumanMessage(content=q),
                ]
            }
        )
        messages = result.get("messages", [])
        answer = ""
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and msg.content:
                answer = msg.content if isinstance(msg.content, str) else str(msg.content)
                break

        used_tools: list[str] = []
        for msg in messages:
            if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None):
                for tc in msg.tool_calls:
                    name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
                    if name and name not in used_tools:
                        used_tools.append(name)
            if isinstance(msg, ToolMessage) and msg.name and msg.name not in used_tools:
                used_tools.append(msg.name)

        return {
            "answer": answer or "I could not generate an answer. Please try rephrasing.",
            "sources": used_tools,
            "llm_used": True,
            "model": settings.azure_deployment,
        }
    except Exception as exc:
        return {
            "answer": f"AI assistant error: {exc}. Check Azure OpenAI configuration.",
            "sources": [],
            "llm_used": False,
            "error": str(exc),
        }


def generate_suggestions(db, vehicle_type: str | None = None) -> list[str]:
    """LLM-generated question suggestions based on live data."""
    llm = get_azure_llm(temperature=0.5, max_tokens=300)
    if not llm:
        return _default_suggestions(db)

    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate

    summary = context_to_json(db, vehicle_type)[:4000]
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Generate exactly 6 short questions a HSRP operations manager would ask. Return one per line, no numbering."),
        ("human", "Based on this data:\n{context}\n\nGenerate 6 relevant questions:"),
    ])
    chain = prompt | llm | StrOutputParser()
    try:
        text = chain.invoke({"context": summary})
        lines = [ln.strip().lstrip("0123456789.-) ") for ln in text.split("\n") if ln.strip()]
        return lines[:8] if lines else _default_suggestions(db)
    except Exception:
        return _default_suggestions(db)


def _default_suggestions(db) -> list[str]:
    from app.services import dashboard as dash

    s = dash.get_dashboard_summary(db)
    return [
        f"What is our total revenue across {s['total_orders']} orders?",
        f"How many orders are pending ({s['pending_orders']})?",
        "Which state has the highest revenue?",
        "Show critical pendency and SLA breaches",
        "Any stock shortage risks in the next 7 days?",
        "Which ESOs are underperforming?",
    ]
