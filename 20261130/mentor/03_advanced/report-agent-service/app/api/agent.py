"""Day31 07-B: FastAPI와 기존 LangChain Agent의 연결."""
from uuid import uuid4
import logging
from fastapi import APIRouter, Request
from app.schemas.agent import AskRequest, AskResponse
from app.services.metrics import Meter
from app.services.errors import ServiceError
from app.rag.ids import explicit_ids

router = APIRouter(prefix='/api/v1')
logger = logging.getLogger('uvicorn.error')

@router.post('/agent/ask', response_model=AskResponse)
def ask(body: AskRequest, request: Request):
    # 유효하지 않은 사용자 ID는 GPU·DB·LLM 실행 전에 거절한다.
    explicit_ids(body.question)
    runtime = request.app.state.get_runtime()
    runtime.health()
    request_id = str(uuid4())
    meter = Meter(runtime.settings)
    try:
        # BEGIN D31-A07-04
        # 해설 D31-A07-04: 실제 Agent의 Tool 선택과 실행은 create_agent 내부에서 이루어진다.
        result = runtime.agent.ask(request_id, body, meter)
        # END D31-A07-04
    except ServiceError as exc:
        logger.warning('agent request=%s error=%s metrics=%s', request_id, exc.code, meter.summary())
        raise
    # Ledger 원문이나 Prompt가 아닌 안전한 수치만 기록한다.
    logger.info('agent request=%s status=%s metrics=%s', request_id, result['status'], meter.summary())
    return result
