"""Direct RAG HTTP·Service 연결 검증. 실제 GPU/LLM 대신 명시적 Stub."""
import pytest
from fastapi.testclient import TestClient
from app.core.settings import Settings
from app.main import create_app
from app.services.rag_service import RagService
from app.services.errors import ServiceError
from app.services.metrics import Meter
from app.schemas.rag import RagAskRequest

SOURCE={'source_id':'RPT-63','report_id':63,'title':'fixture','category_code':'RESEARCH_PLAN','revision':1}
Q='보고서 63번의 핵심 내용'
class Pipe:
    def __init__(self,status='found'):self.status=status;self.meters=[]
    def run(self,q,query,cat,k,m):
        self.meters.append(m)
        return {'status':self.status,'query':query,'answer':'근거 [RPT-63]' if self.status=='found' else '근거 부족','sources':[SOURCE] if self.status=='found' else []}
class Runtime:
    def __init__(self,pipeline=None):self.settings=Settings('','','');self.rag_service=RagService(self.settings,pipeline or Pipe())
    def health(self):return {'mode':'fixture'}
    def close(self):pass

def test_rag_http_and_meter_scope():
    r=Runtime()
    with TestClient(create_app(lambda:r),raise_server_exceptions=False) as c:
        a=c.post('/api/v1/rag/ask',json={'question':Q});b=c.post('/api/v1/rag/ask',json={'question':Q})
        assert a.status_code==b.status_code==200
        assert a.json()['status']=='completed' and a.json()['sources'][0]['report_id']==63
        assert a.json()['request_id']!=b.json()['request_id']
        assert r.rag_service.pipeline.meters[0] is not r.rag_service.pipeline.meters[1]

def test_empty_and_bad_output():
    for state,code,status in [('not_found',200,'insufficient_evidence'),('error',500,'OUTPUT_CONTRACT_ERROR')]:
        with TestClient(create_app(lambda:Runtime(Pipe(state))),raise_server_exceptions=False) as c:
            out=c.post('/api/v1/rag/ask',json={'question':Q})
            assert out.status_code==code
            assert (out.json()['status'] if code==200 else out.json()['error']['code'])==status

@pytest.mark.parametrize('k',[True,1.0,0,6])
def test_k_strict(k):
    r=Runtime()
    with pytest.raises(ServiceError,match='VALIDATION_ERROR'):r.rag_service.run(Q,Q,None,k,Meter(r.settings))
    assert not r.rag_service.pipeline.meters

@pytest.mark.parametrize('code,http',[('DB_UNAVAILABLE',503),('GPU_UNAVAILABLE',503),('LLM_UNAVAILABLE',503),('LLM_TIMEOUT',504),('EMBEDDING_UNAVAILABLE',503)])
def test_failure_contract(code,http):
    class Broken(Runtime):
        def health(self):raise ServiceError(code)
    with TestClient(create_app(Broken),raise_server_exceptions=False) as c:
        out=c.post('/api/v1/rag/ask',json={'question':Q})
        assert out.status_code==http and out.json()['error']['code']==code


@pytest.mark.parametrize('patch,category',[
    ({'sources':[dict(SOURCE,source_id='RPT-64')],'answer':'근거 [RPT-64]'},None),
    ({'sources':[dict(SOURCE,report_id=64,source_id='RPT-64')],'answer':'근거 [RPT-64]'},None),
    ({'sources':[SOURCE,SOURCE]},None),
    ({'answer':'근거 [RPT-999]'},None),
    ({'query':'다른 검색 질문'},None),
    ({},'EXPERIMENT'),
    ({'status':'not_found','answer':'잘못된 인용 RPT-63','sources':[]},None),
])
def test_shared_service_rejects_inconsistent_result(patch,category):
    class BadPipe(Pipe):
        def run(self,*args):return dict(super().run(*args),**patch)
    r=Runtime(BadPipe())
    with pytest.raises(ServiceError,match='OUTPUT_CONTRACT_ERROR'):
        r.rag_service.run(Q,Q,category,1,Meter(r.settings))


def test_unexpected_http_exception_is_sanitized(caplog):
    class Broken(Runtime):
        def health(self):raise RuntimeError('fixture-secret-raw-exception')
    # raise_server_exceptions=True에서도 서버 쪽 원본 예외가 밖으로 전파되지 않는다.
    with TestClient(create_app(Broken)) as client:
        out=client.post('/api/v1/rag/ask',json={'question':Q})
        assert out.status_code==500 and out.json()['error']['code']=='INTERNAL_ERROR'
    assert 'fixture-secret-raw-exception' not in out.text and 'fixture-secret-raw-exception' not in caplog.text


@pytest.mark.parametrize('query',['일반적인 질문입니다','보고서 64번의 핵심 내용','RPT-63과 RPT-64 내용'])
def test_rewritten_query_preserves_explicit_ids_before_pipeline(query):
    r=Runtime()
    with pytest.raises(ServiceError,match='VALIDATION_ERROR'):
        r.rag_service.run(Q,query,None,1,Meter(r.settings))
    assert not r.rag_service.pipeline.meters
