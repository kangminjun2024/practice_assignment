from langchain_openai import ChatOpenAI
from app.services.errors import ServiceError

def make_model(settings):
    # 객체를 구성하는 시점과 실제 API 호출 시점은 다르다.
    if not settings.llm_configured:
        raise ServiceError('LLM_UNAVAILABLE', 'not_configured')
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.api_key,
        timeout=settings.llm_timeout_seconds,
        max_retries=0,
        max_tokens=1200,
    )
