"""실제 FastAPI TestClient. Stub Service는 HTTP 계약만 확인."""
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.core.settings import Settings
from app.services.errors import ServiceError

class StubRuntime:
    settings=Settings('','','')
    def __init__(self):self.rag_service=self;self.calls=0
    def health(self):return {'mode':'fixture'}
    def close(self):pass
    def ask(self,body):
        self.calls+=1
        return {'request_id':'fixture','status':'insufficient_evidence','answer':'테스트용 응답','sources':[],'latency_ms':1.0}

def test_route_and_trim():
    from app.schemas.rag import RagAskRequest
    assert RagAskRequest(question='  정상 질문입니다.  ').question=='정상 질문입니다.'
    with TestClient(create_app(StubRuntime),raise_server_exceptions=False) as c:
        r=c.post('/api/v1/rag/ask',json={'question':'정상 질문입니다.'})
        assert r.status_code==200 and r.json()['status']=='insufficient_evidence'
        spec=c.get('/openapi.json').json()
        assert 'RagAskResponse' in spec['components']['schemas']
        assert '/api/v1/rag/ask' in spec['paths']

@pytest.mark.parametrize('body',[{'question':'abc'},{'question':'  '},{'question':12},{'question':'x'*301},{'question':'정상 질문입니다.','category_code':'WRONG'},{'question':'정상 질문입니다.','k':10}])
def test_schema_422_without_runtime(body):
    def no_runtime():raise AssertionError('Runtime must not run')
    with TestClient(create_app(no_runtime),raise_server_exceptions=False) as c:
        r=c.post('/api/v1/rag/ask',json=body)
        assert r.status_code==422 and r.json()['error']['code']=='VALIDATION_ERROR'

def test_http_edges_and_response_model():
    class Bad(StubRuntime):
        def ask(self,body):return {'status':'unexpected'}
    with TestClient(create_app(Bad),raise_server_exceptions=False) as c:
        assert c.get('/api/v1/rag/ask').status_code==405
        assert c.get('/unknown').status_code==404
        assert c.post('/api/v1/rag/ask',content='{',headers={'Content-Type':'application/json'}).status_code==422
        assert c.post('/api/v1/rag/ask',json={'question':'정상 질문입니다.'}).status_code==500
