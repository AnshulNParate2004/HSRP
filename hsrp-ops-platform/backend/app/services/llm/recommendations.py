"""LLM-generated operational recommendations via Azure OpenAI."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.services.llm.azure_client import get_azure_llm


def llm_recommendation(alert_type: str, context: dict, fallback: str) -> str:
    llm = get_azure_llm(temperature=0.3, max_tokens=200)
    if not llm:
        return fallback

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an HSRP operations expert for Real Industries India. "
            "Write ONE concise actionable recommendation (1-2 sentences) for management.",
        ),
        (
            "human",
            "Alert type: {alert_type}\nContext: {context}\nRecommendation:",
        ),
    ])
    chain = prompt | llm | StrOutputParser()
    try:
        text = chain.invoke({"alert_type": alert_type, "context": str(context)})
        return text.strip() or fallback
    except Exception:
        return fallback
