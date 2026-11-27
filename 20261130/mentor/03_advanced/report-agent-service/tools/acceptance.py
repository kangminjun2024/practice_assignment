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
    # BEGIN D31-A08-01
    # 해설 D31-A08-01: HTTP 200만으로 성공을 판정하지 않는다.
    require(out.status == 'completed' and {s.report_id for s in out.sources} == {report_id}, 'rag_expected_source')
    # END D31-A08-01
    validate_citation_contract(out)
    return out.model_dump()


def validate_agent(response, required, report_id, expected_status=None):
    require(response.status_code == 200, 'agent_http')
    out = AskResponse.model_validate(response.json())
    found = {trace.tool for trace in out.tool_trace if trace.status == 'found'}
    # BEGIN D31-A08-02
    # 해설 D31-A08-02: 실제 Tool Trace의 found를 검사하며 호출 순서를 고정하지 않는다.
    require(out.status == 'completed' and required <= found and out.validation.required_tools_observed, 'agent_expected_tools')
    # END D31-A08-02
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
    # BEGIN D31-A08-03
    # 해설 D31-A08-03: 유효한 근거 없음은 시스템 실패와 다른 정상 업무 결과이다.
    require(out.status == 'insufficient_evidence' and not out.sources, 'empty_result')
    # END D31-A08-03
    return out.model_dump()


def validate_snapshot(before, after):
    # 실습 외부 변경이 없어야 비교 가능하다. SHA-256 및 row count가 모두 일치해야 한다.
    # BEGIN D31-A08-04
    # 해설 D31-A08-04: 같은 DB에서 외부 변경이 없을 때 데이터 불변성의 근거가 된다.
    require(bool(before) and before == after, 'db_snapshot_changed')
    # END D31-A08-04
    return True
