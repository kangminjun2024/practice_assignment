from typing import Annotated, Literal
from pydantic import StringConstraints
from app.schemas.agent import Contract, Category, Source

# Direct RAG에서는 원 질문을 검색 질문으로 사용한다.
RagQuestion = Annotated[str, StringConstraints(
    strict=True, strip_whitespace=True, min_length=5, max_length=300
)]

class RagAskRequest(Contract):
    # BEGIN D31-B02-01
    # TODO D31-B02-01: question에 위에서 선언한 검증 타입을 지정하세요.
    question: Literal['UNIMPLEMENTED_D31-B02-01']
    # END D31-B02-01
    category_code: Category | None = None

class RagAskResponse(Contract):
    request_id: str
    status: Literal['completed', 'insufficient_evidence']
    answer: str
    sources: list[Source]
    latency_ms: float
