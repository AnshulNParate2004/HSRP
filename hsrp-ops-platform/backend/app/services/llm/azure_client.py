"""Azure OpenAI via LangChain — shared LLM client."""

from langchain_openai import AzureChatOpenAI

from app.core.config import settings


def get_azure_llm(*, temperature: float = 0.2, max_tokens: int = 1500) -> AzureChatOpenAI | None:
    if not settings.azure_configured:
        return None
    return AzureChatOpenAI(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=settings.azure_api_version,
        azure_deployment=settings.azure_deployment,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=60,
    )
