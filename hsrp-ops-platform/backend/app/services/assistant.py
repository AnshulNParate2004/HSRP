"""AI Assistant — delegates to LangChain + Azure OpenAI."""

from sqlalchemy.orm import Session

from app.services.llm.assistant_chain import ask_with_langchain, generate_suggestions


def ask(db: Session, question: str, vehicle_type: str | None = None) -> dict:
    return ask_with_langchain(db, question, vehicle_type)


def get_suggestions(db: Session, vehicle_type: str | None = None) -> list[str]:
    return generate_suggestions(db, vehicle_type)
