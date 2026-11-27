import json
import pytest
from app.main import create_app
from app.core.settings import Settings
from fastapi.testclient import TestClient
from app.services.errors import ServiceError

Q='보고서 63번의 현재 인덱싱 상태'

def test_agent_route_and_invalid_id():
    class Stub:
        settings=Settings('','','')
        def __init__(self):self.agent=self
        def health(self):return {'mode':'fixture'}
        def close(self):pass
        def ask(self,rid,body,meter):
            return {'request_id':rid,'status':'incomplete','answer':'fixture','sources':[],'tool_trace':[], 'validation':{'citations_match_context':True,'required_tools_observed':False},'latency_ms':1.0}
    with TestClient(create_app(Stub),raise_server_exceptions=False) as c:
        r=c.post('/api/v1/agent/ask',json={'question':Q});assert r.status_code==200 and r.json()['status']=='incomplete'
    with TestClient(create_app(lambda: (_ for _ in ()).throw(AssertionError())),raise_server_exceptions=False) as c:
        assert c.post('/api/v1/agent/ask',json={'question':'보고서 0번의 상태'}).status_code==422


def test_real_create_agent_with_stub_llm(monkeypatch):
    pytest.importorskip('langchain');pytest.importorskip('langchain_openai')
    from tests.sdk_helpers import FakeToolModel,Repo,Emb,Rank,answer
    from langchain_core.messages import AIMessage
    from app.core.runtime import Runtime
    from app.schemas.agent import AskRequest
    from app.services.metrics import Meter
    calls=[{'id':'r1','name':'rag_search','args':{'query':'보고서 63 핵심 내용','k':1},'type':'tool_call'},
           {'id':'s1','name':'lookup_status','args':{'report_id':63},'type':'tool_call'}]
    agent_model=FakeToolModel(responses=[AIMessage(content='',tool_calls=calls),AIMessage(content=answer())])
    rag_model=FakeToolModel(responses=[AIMessage(content=answer())]);models=iter([agent_model,rag_model])
    r=Runtime(Settings('','fixture','fixture'),Repo(),Emb(),Rank(),lambda:next(models))
    m=Meter(r.settings)
    out=r.agent.ask('fixture',AskRequest(question='보고서 63번의 핵심 내용과 인덱싱 상태를 알려줘.'),m)
    assert out['status']=='completed' and {x['tool'] for x in out['tool_trace']}=={'rag_search','lookup_status'}
    assert m.model_calls==3 and m.tool_calls==2 and set(m.ledger)=={'r1','s1'}
    assert 'revision=1' in out['answer']


def test_tool_id_scope_and_shared_meter():
    pytest.importorskip('langchain');pytest.importorskip('langchain_openai')
    from app.tools.rag_tool import make_rag_tool,resolve_search_args
    from langchain_core.tools import ToolException
    from app.services.metrics import Meter
    from app.schemas.agent import RagResult
    s=Settings('','','');m=Meter(s)
    question='보고서 63과 RPT-64의 핵심 내용'
    query,cat,k=resolve_search_args(question,'RESEARCH_PLAN','RPT-63 내용',None,1,8)
    assert 'RPT-64' in query and cat=='RESEARCH_PLAN'
    for bad in ['RPT-0 내용','RPT-999 내용']:
        with pytest.raises(ToolException):resolve_search_args(question,None,bad,None,1,8)
    with pytest.raises(ServiceError):resolve_search_args('보고서 0 내용',None,'내용',None,1,8)
    class Service:
        def run(self,q,query,cat,k,meter):
            assert meter is m
            meter.reserve('model')
            return RagResult(status='not_found',query=query,answer='근거 부족',sources=[])
    tool=make_rag_tool(Service(),s,question,'RESEARCH_PLAN',m)
    msg=tool.invoke({'name':'rag_search','args':{'query':'RPT-63 내용','k':1},'id':'r1','type':'tool_call'})
    assert json.loads(msg.content)['status']=='not_found' and 'r1' in m.ledger and m.model_calls==1 and m.tool_calls==1
    assert 'tool_call_id' not in tool.tool_call_schema.model_json_schema()['properties']


@pytest.mark.parametrize('name,args',[
    ('rag_search',{'query':'보고서 63 핵심 내용','k':True}),
    ('rag_search',{'query':'보고서 63 핵심 내용','k':1,'sql':'SELECT 1'}),
    ('lookup_status',{'report_id':'63'}),
    ('lookup_status',{'report_id':63,'sql':'SELECT 1'}),
])
def test_explicit_tool_schema_rejects_invalid_args(name,args):
    pytest.importorskip('langchain');pytest.importorskip('langchain_openai')
    from app.tools.rag_tool import make_rag_tool
    from app.tools.db_tool import make_db_tool
    from app.services.metrics import Meter
    s=Settings('','','');m=Meter(s)
    class Forbidden:
        def run(self,*args):raise AssertionError('invalid input entered RAG')
        def lookup(self,*args):raise AssertionError('invalid input entered DB')
    tool=(make_rag_tool(Forbidden(),s,Q,None,m) if name=='rag_search' else make_db_tool(Forbidden(),Q,m))
    assert 'tool_call_id' not in tool.tool_call_schema.model_json_schema()['properties']
    message=tool.invoke({'name':name,'args':args,'id':'invalid-1','type':'tool_call'})
    assert message.status=='error' and not m.ledger and m.tool_calls==0
