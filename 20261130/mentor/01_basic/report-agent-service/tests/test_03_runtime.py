from fastapi.testclient import TestClient
from app.main import create_app
from app.services.errors import ServiceError
import pytest

def test_lazy_di_and_lifespan():
    events=[]
    class Stub:
        def __init__(self):events.append('create')
        def health(self):return {'mode':'fixture'}
        def close(self):events.append('close')
    app=create_app(Stub)
    assert not events
    with TestClient(app) as c:
        assert c.get('/health').status_code==200
        assert c.get('/health').status_code==200
        assert events==['create']
    assert events==['create','close']

def test_actual_runtime_di(monkeypatch):
    pytest.importorskip('langchain');pytest.importorskip('langchain_openai')
    import app.core.runtime as module
    from app.core.settings import Settings
    s=Settings('','','');repo=object();embedder=object();reranker=object();factory=lambda:None
    monkeypatch.setattr(module,'preflight',lambda settings,repo_: {'mode':'fixture','same':repo_ is repo})
    r=module.Runtime(s,repo,embedder,reranker,factory)
    assert r.health()['same'] and r.rag_service.pipeline is r.pipeline
    assert r.agent.rag_service is r.rag_service and r.repo is repo and r.db is None
    assert r.model_factory is factory and r.pipeline.model_factory is factory
    r.close()
