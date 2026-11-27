from fastapi import APIRouter, Request
from app.schemas.rag import RagAskRequest, RagAskResponse
from app.rag.ids import explicit_ids

router = APIRouter(prefix='/api/v1')

# BEGIN D31-I02-03
# 해설 D31-I02-03: FastAPI가 반환값을 응답 Schema에 맞춰 검증하고 OpenAPI에 표시한다.
@router.post('/rag/ask', response_model=RagAskResponse)
# END D31-I02-03
def ask(body: RagAskRequest, request: Request):
    # Schema 검증을 통과한 뒤 요청 처리 함수가 호출된다.
    explicit_ids(body.question)  # 명시 ID 범위 오류를 AI 실행 전에 차단
    runtime = request.app.state.get_runtime()
    runtime.health()  # DB·CUDA·설정 준비 상태 검사
    # 현재 Pipeline은 동기 DB·GPU·HTTP 호출을 사용한다.
    return runtime.rag_service.ask(body)
