"""07-B의 실제 실행기는 두 Tool 검증을 요구한다. HTTP Fixture로 실패 재현."""
import pytest
from app.services.errors import ServiceError
from tests.test_07a_runner import run_fixture, COMPOUND


def test_07b_checks_both_tools_and_db_value(monkeypatch):
    assert run_fixture(monkeypatch,'B')['checks']['agent_both']['status']=='completed'

@pytest.mark.parametrize('patch',[
    {'tool_trace':[COMPOUND['tool_trace'][1]]},
    {'answer':'근거 [RPT-63]\n보고서 63: index_status=ready, revision=999, embedding_fresh=true'},
    {'validation':{'citations_match_context':False,'required_tools_observed':True}},
])
def test_07b_rejects_partial_or_wrong_evidence(monkeypatch,patch):
    with pytest.raises(ServiceError,match='OUTPUT_CONTRACT_ERROR'):
        run_fixture(monkeypatch,'B',agent={**COMPOUND,**patch})
