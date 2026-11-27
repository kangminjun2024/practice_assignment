"""실습 07 실행기 계약을 HTTP Fixture로 검사. 실제 DB·LLM 실행 아님."""
from types import SimpleNamespace
import httpx
import pytest
from app.services.errors import ServiceError
from tools import run_lab
from tests.test_07a_service import SOURCE

HTTPX_CLIENT=httpx.Client

STATE={'status':'found','report_id':63,'category_code':'RESEARCH_PLAN','index_status':'ready','revision':1,'embedding_fresh':True}
RAG={'request_id':'fixture','status':'completed','answer':'근거 [RPT-63]','sources':[SOURCE],'latency_ms':1.0}
COMPOUND={**RAG,'answer':'근거 [RPT-63]\n\n[실제 DB 상태]\n보고서 63: index_status=ready, revision=1, embedding_fresh=true',
          'tool_trace':[{'tool_call_id':'r','tool':'rag_search','status':'found'},{'tool_call_id':'s','tool':'lookup_status','status':'found'}],
          'validation':{'citations_match_context':True,'required_tools_observed':True}}


def run_fixture(monkeypatch,part,rag=None,agent=None):
    monkeypatch.setattr(run_lab,'actual_db',lambda *args:({}, {'lookup_status':STATE}))
    def handler(request):
        if request.url.path=='/openapi.json':return httpx.Response(200,json={'info':{'title':'Day31 Report Agent Service'}})
        if request.url.path=='/health':return httpx.Response(200,json={'database':'report_agent_lab','gpu':'cuda:0'})
        if request.url.path=='/api/v1/rag/ask':return httpx.Response(200,json=RAG if rag is None else rag)
        if request.url.path=='/api/v1/agent/ask':return httpx.Response(200,json=COMPOUND if agent is None else agent)
        raise AssertionError(request.url.path)
    monkeypatch.setattr(httpx,'Client',lambda **kwargs:HTTPX_CLIENT(transport=httpx.MockTransport(handler),**kwargs))
    return run_lab.live(7,SimpleNamespace(report_id=63,missing_id=999999,port=8000,http_timeout=10,part=part))


def test_07a_checks_expected_source(monkeypatch):
    assert run_fixture(monkeypatch,'A')['checks']['direct_rag']['status']=='completed'
    wrong={**RAG,'answer':'근거 [RPT-64]','sources':[dict(SOURCE,source_id='RPT-64',report_id=64)]}
    with pytest.raises(ServiceError,match='OUTPUT_CONTRACT_ERROR'):run_fixture(monkeypatch,'A',rag=wrong)
