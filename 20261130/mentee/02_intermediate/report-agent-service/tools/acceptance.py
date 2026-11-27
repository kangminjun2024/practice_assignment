"""실제 HTTP 결과를 평가하는 객관적 계약 검사. 자연어 문장은 사람 검토."""
from tools.common import require
from app.schemas.rag import RagAskResponse
from app.schemas.agent import AskResponse
from app.rag.ids import explicit_ids
from app.services.validator import citation_ids
from app.schemas.agent import ModelAnswer


def validate_citation_contract(out):
    # 최종 응답의 인용과 Source 메타데이터 자체도 검사한다. 실제 Context 대조는 서버가 수행한다.
    ids = [s.source_id for s in out.sources]
    require(all(s.source_id == f'RPT-{s.report_id}' for s in out.sources), 'source_identity')
    require(citation_ids(ModelAnswer(status=out.status, answer=out.answer, source_ids=ids), set(ids)), 'citation_contract')


def validate_rag(response, report_id):
    require(response.status_code == 200, 'rag_http')
    out = RagAskResponse.model_validate(response.json())
    # 정상 요청의 구조 계약: 실제 요청 ID를 인용하고 완료해야 한다.
    # BEGIN D31-I08-01
    # TODO D31-I08-01: 응답 완료 상태와 실제 요청 보고서 ID 집합을 검사하세요.
    raise NotImplementedError('UNIMPLEMENTED_D31-I08-01')
    # END D31-I08-01
    validate_citation_contract(out)
    return out.model_dump()


def validate_agent(response, required, report_id, expected_status=None):
    require(response.status_code == 200, 'agent_http')
    out = AskResponse.model_validate(response.json())
    found = {trace.tool for trace in out.tool_trace if trace.status == 'found'}
    # BEGIN D31-I08-02
    # TODO D31-I08-02: Agent 완료 상태, 필요한 found Tool 포함 여부, 실행 검증 Flag를 확인하세요.
    raise NotImplementedError('UNIMPLEMENTED_D31-I08-02')
    # END D31-I08-02
    require(out.validation.citations_match_context, 'agent_citation')
    validate_citation_contract(out)
    call_ids = [trace.tool_call_id for trace in out.tool_trace]
    require(len(call_ids) == len(set(call_ids)) and all(call_ids), 'agent_trace_ids')
    if 'rag_search' in required:
        require({s.report_id for s in out.sources} == {report_id}, 'agent_expected_source')
    else:
        require(not out.sources, 'status_sources')
    if 'lookup_status' in required:
        require(expected_status is not None and expected_status.get('status') == 'found'
                and expected_status.get('report_id') == report_id, 'missing_db_reference')
        expected_line = f"보고서 {report_id}: index_status={expected_status['index_status']}, revision={expected_status['revision']}, embedding_fresh={str(expected_status['embedding_fresh']).lower()}"
        require(expected_line in out.answer.splitlines(), 'actual_db_status')
    return out.model_dump()


def validate_empty(response):
    require(response.status_code == 200, 'empty_http')
    out = RagAskResponse.model_validate(response.json())
    # BEGIN D31-I08-03
    # TODO D31-I08-03: 근거 부족 상태와 빈 출처를 검사하세요.
    raise NotImplementedError('UNIMPLEMENTED_D31-I08-03')
    # END D31-I08-03
    return out.model_dump()


def validate_snapshot(before, after):
    # 실습 외부 변경이 없어야 비교 가능하다. SHA-256 및 row count가 모두 일치해야 한다.
    require(bool(before) and before == after, 'db_snapshot_changed')
    return True
