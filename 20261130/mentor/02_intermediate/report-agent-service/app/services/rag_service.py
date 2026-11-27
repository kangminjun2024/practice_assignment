from uuid import uuid4
import logging
from pydantic import ValidationError
from app.schemas.agent import RagResult
from app.schemas.rag import RagAskRequest, RagAskResponse
from app.services.metrics import Meter
from app.services.errors import ServiceError
from app.services.validator import check_tool_output
from app.rag.ids import explicit_ids

logger = logging.getLogger('uvicorn.error')

class RagService:
    def __init__(self, settings, pipeline):
        self.settings = settings
        self.pipeline = pipeline

    def run(self, question, query, category_code, k, meter):
        # HTTP와 분리된 업무 메서드. 내일 Tool에서도 호출할 수 있다.
        question_ids = explicit_ids(question)
        query_ids = explicit_ids(query)
        # 명시 ID를 포함한 질문을 다른 보고서 검색으로 바꿔 LLM에 넘기지 않는다.
        if question_ids and query_ids != question_ids:
            raise ServiceError('VALIDATION_ERROR', 'query_id_scope')
        requested_ids = question_ids or query_ids
        if type(k) is not int or not 1 <= k <= min(5, self.settings.retrieve_k):
            raise ServiceError('VALIDATION_ERROR')
        # BEGIN D31-I07-01
        # 해설 D31-I07-01: Agent Tool과 Direct API 모두 동일한 Pipeline을 사용한다.
        raw = self.pipeline.run(question, query, category_code, k, meter)
        # END D31-I07-01
        try:
            result = RagResult.model_validate(raw)
        except ValidationError:
            raise ServiceError('OUTPUT_CONTRACT_ERROR', 'invalid_rag_result') from None
        if result.status not in ('found', 'not_found'):
            raise ServiceError('OUTPUT_CONTRACT_ERROR', 'rag_status_rule')
        if (result.status == 'found') != bool(result.sources):
            raise ServiceError('OUTPUT_CONTRACT_ERROR', 'rag_sources_rule')
        # 공통 Service에서도 Source ID와 실제 검색 범위의 계약을 확인한다.
        # Pipeline 내부 Citation 검사(실제 Context와 대조)를 대신하는 검사는 아니다.
        try:
            check_tool_output('rag_search', result.model_dump())
        except ServiceError:
            raise ServiceError('OUTPUT_CONTRACT_ERROR', 'rag_result_citation') from None
        if result.query != query:
            raise ServiceError('OUTPUT_CONTRACT_ERROR', 'rag_query_mismatch')
        if any((requested_ids and s.report_id not in requested_ids)
               or (category_code is not None and s.category_code != category_code)
               for s in result.sources):
            raise ServiceError('OUTPUT_CONTRACT_ERROR', 'rag_source_scope')
        return result

    def ask(self, body: RagAskRequest) -> RagAskResponse:
        # 현재 요청 전용 ID와 Meter: 다른 요청과 공유하지 않는다.
        request_id = str(uuid4())
        meter = Meter(self.settings)
        try:
            # BEGIN D31-I07-02
            # 해설 D31-I07-02: Direct RAG에서는 원 질문을 검색 질문으로 사용한다.
            result = self.run(
                body.question, body.question, body.category_code,
                self.settings.context_k, meter,
            )
            # END D31-I07-02
        except ServiceError as exc:
            logger.warning('rag request=%s error=%s metrics=%s',
                           request_id, exc.code, meter.summary())
            raise
        # BEGIN D31-I07-05
        # 해설 D31-I07-05: 오류 상태는 run에서 이미 거절하므로 정상 업무 상태만 매핑한다.
        status = ('completed' if result.status == 'found'
                  else 'insufficient_evidence')
        # END D31-I07-05
        metrics = meter.summary()
        # 원문, 비밀, Query가 아닌 안전한 실행 수치만 기록한다.
        logger.info('rag request=%s status=%s metrics=%s',
                    request_id, status, metrics)
        return RagAskResponse(
            request_id=request_id, status=status,
            answer=result.answer, sources=result.sources,
            latency_ms=float(metrics['latency_ms']),
        )
