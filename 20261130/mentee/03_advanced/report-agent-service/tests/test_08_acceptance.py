import pytest
from tools.acceptance import validate_rag,validate_agent,validate_empty,validate_snapshot
from app.services.errors import ServiceError
class Response:
    status_code=200
    def __init__(self,body):self.body=body
    def json(self):return self.body
SOURCE={'source_id':'RPT-63','report_id':63,'title':'fixture','category_code':'RESEARCH_PLAN','revision':1}
RAG={'request_id':'fixture','status':'completed','answer':'근거 [RPT-63]','sources':[SOURCE],'latency_ms':1.0}
AGENT={**RAG,'tool_trace':[{'tool_call_id':'r','tool':'rag_search','status':'found'}],'validation':{'citations_match_context':True,'required_tools_observed':True}}

def test_rag_acceptance():
    assert validate_rag(Response(RAG),63)['status']=='completed'
    with pytest.raises(ServiceError):validate_rag(Response(RAG),64)

def test_agent_acceptance():
    assert validate_agent(Response(AGENT),{'rag_search'},63)['status']=='completed'
    with pytest.raises(ServiceError):validate_agent(Response(AGENT),{'lookup_status'},63)

def test_empty_acceptance():
    assert validate_empty(Response({**RAG,'status':'insufficient_evidence','sources':[],'answer':'없음'}))['status']=='insufficient_evidence'
    with pytest.raises(ServiceError):validate_empty(Response(RAG))

def test_snapshot_acceptance():
    assert validate_snapshot({'reports':{'count':1,'sha256':'a'}},{'reports':{'count':1,'sha256':'a'}})
    with pytest.raises(ServiceError):validate_snapshot({'reports':1},{'reports':2})


@pytest.mark.parametrize('patch',[
    {'answer':'허위 [RPT-999]'},
    {'sources':[dict(SOURCE,source_id='RPT-64')],'answer':'근거 [RPT-64]'},
    {'sources':[SOURCE,SOURCE]},
    {'tool_trace':[AGENT['tool_trace'][0],AGENT['tool_trace'][0]]},
])
def test_agent_acceptance_rechecks_actual_response(patch):
    with pytest.raises(ServiceError):validate_agent(Response({**AGENT,**patch}),{'rag_search'},63)


def test_status_reference_is_checked():
    state={'status':'found','report_id':63,'index_status':'ready','revision':1,'embedding_fresh':True}
    out={**AGENT,'answer':'보고서 63: index_status=ready, revision=1, embedding_fresh=true','sources':[],
         'tool_trace':[{'tool_call_id':'s','tool':'lookup_status','status':'found'}]}
    assert validate_agent(Response(out),{'lookup_status'},63,state)['status']=='completed'
    with pytest.raises(ServiceError):validate_agent(Response(out),{'lookup_status'},63,dict(state,report_id=64))
