"""Day31 07-B: 기존 RAG Tool을 RagService.run()에 연결한다."""
import json
from langchain.tools import tool
from langchain_core.tools import InjectedToolCallId, ToolException
from typing import Annotated
from pydantic import BaseModel, ConfigDict, ValidationError
from app.schemas.agent import Query, Category, K
from app.services.validator import check_tool_output
from app.services.errors import ServiceError
from app.rag.ids import explicit_ids

class RagInput(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    query: Query
    category_code: Category | None = None
    k: K = 3


class RagToolInput(RagInput):
    # 서버가 주입하는 호출 ID. 모델이 선택하는 업무 인수에는 포함되지 않는다.
    tool_call_id: Annotated[str, InjectedToolCallId]


def resolve_search_args(question, category, query, category_code, k, retrieve_k):
    """사용자 검색 범위를 보존한다. 모델이 요청한 인수 오류는 Tool 오류로 전달한다."""
    original_ids = explicit_ids(question)  # 사용자 오류는 ServiceError(422)
    try:
        args = RagInput.model_validate({'query':query, 'category_code':category_code, 'k':k})
        if args.k > retrieve_k or (category is not None and args.category_code not in (None, category)):
            raise ValueError()
        try:
            query_ids = explicit_ids(args.query)
        except ServiceError as exc:
            if exc.code == 'VALIDATION_ERROR':
                raise ValueError() from None
            raise
        if original_ids and not query_ids <= original_ids:
            raise ValueError()
        effective_category = category if category is not None else args.category_code
        # 일부 ID만 누락해도 복원한다. 다른 ID로 바꾸지 않는다.
        missing = original_ids - query_ids
        effective_query = (' '.join(f'RPT-{i}' for i in sorted(missing))+' '+args.query) if missing else args.query
        if len(effective_query) > 300:
            raise ValueError()
        return effective_query, effective_category, args.k
    except (ValidationError, ValueError):
        raise ToolException('invalid_input') from None


def make_rag_tool(rag_service, settings, question, category, meter):
    @tool(args_schema=RagToolInput)
    def rag_search(query: Query, tool_call_id: Annotated[str, InjectedToolCallId], category_code: Category | None = None, k: K = 3) -> str:
        """보고서의 기술적 내용, 근거, 요약을 실제 검색한다. query 1~300자, category_code는 6개 코드 또는 null, k는 1~5. 지정 보고서 번호를 보존한다. 상태 조회는 별도 도구다."""
        meter.reserve('tool')
        try:
            effective_query, effective_category, effective_k = resolve_search_args(
                question, category, query, category_code, k, settings.retrieve_k)
            # Agent 요청의 Meter를 그대로 전달한다. ask()가 아닌 run()을 공유한다.
            # BEGIN D31-I07-03
            # 해설 D31-I07-03: Agent의 현재 Meter를 내부 RAG에 넘겨 생성 모델 호출도 같은 예산에 포함한다.
            result = rag_service.run(question, effective_query, effective_category, effective_k, meter).model_dump()
            # END D31-I07-03
            result = check_tool_output('rag_search', result)
        except ServiceError as exc:
            meter.fatal = exc
            raise
        meter.save_tool(tool_call_id, 'rag_search', result,
                        {'category_code':effective_category, 'k':effective_k})
        return json.dumps(result, ensure_ascii=False)
    rag_search.handle_tool_error = True
    rag_search.handle_validation_error = 'invalid_input'
    return rag_search
