from typing import Annotated, Literal
from pydantic import StringConstraints
from app.schemas.agent import Contract, Category, Source

# Direct RAG에서는 원 질문을 검색 질문으로 사용한다.
RagQuestion = Annotated[str, StringConstraints(
    strict=True, strip_whitespace=True, min_length=5, max_length=300
)]

class RagAskRequest(Contract):
    # BEGIN D31-B02-01
    # 해설 D31-B02-01: RagQuestion은 공백 제거 및 5~300자 제한을 포함한 타입이다.
    question: RagQuestion
    # END D31-B02-01
    category_code: Category | None = None

class RagAskResponse(Contract):
    request_id: str
    status: Literal['completed', 'insufficient_evidence']
    answer: str
    sources: list[Source]
    latency_ms: float
