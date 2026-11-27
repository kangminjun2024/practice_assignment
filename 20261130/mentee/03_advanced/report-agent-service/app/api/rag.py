from fastapi import APIRouter, Request
from app.schemas.rag import RagAskRequest, RagAskResponse
from app.rag.ids import explicit_ids

router = APIRouter(prefix='/api/v1')

# BEGIN D31-A02-03
# TODO D31-A02-03: RAG 응답 모델을 route의 response_model에 연결하세요.
@router.post('/rag/ask', response_model=None)  # UNIMPLEMENTED_D31-A02-03
# END D31-A02-03
def ask(body: RagAskRequest, request: Request):
    # Schema 검증을 통과한 뒤 요청 처리 함수가 호출된다.
    explicit_ids(body.question)  # 명시 ID 범위 오류를 AI 실행 전에 차단
    runtime = request.app.state.get_runtime()
    runtime.health()  # DB·CUDA·설정 준비 상태 검사
    # 현재 Pipeline은 동기 DB·GPU·HTTP 호출을 사용한다.
    return runtime.rag_service.ask(body)
