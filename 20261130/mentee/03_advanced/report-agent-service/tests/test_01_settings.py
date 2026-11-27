import pytest
from app.core.settings import Settings, MODEL, RERANKER, ROOT
from app.services.errors import ServiceError
from app.core import preflight as pf


def settings(**kw):
    return Settings('postgresql+psycopg://local:dummy@localhost:5432/report_agent_lab','fixture','fixture',**kw)

def test_configuration_contract():
    s=settings().validate()
    assert s.embedding_model==MODEL and s.reranker_model==RERANKER and s.context_k<=s.retrieve_k
    assert 'dummy' not in repr(s) and 'database_url' not in repr(s) and 'api_key' not in repr(s)
    assert ROOT.name=='report-agent-service'

@pytest.mark.parametrize('kw',[{'context_k':6},{'retrieve_k':0},{'embedding_model':'other'},{'max_tool_calls':0}])
def test_invalid_config(kw):
    with pytest.raises(ServiceError):settings(**kw).validate()

def test_preflight_no_live_model(monkeypatch):
    class Repo:
        def preflight(self):return {'eligible_vectors':1,'db':'ready'}
    monkeypatch.setattr(pf,'require_cuda',lambda:'cuda:0')
    out=pf.preflight(settings(),Repo())
    assert out['llm_live_verified'] is False
    class Empty:
        def preflight(self):return {'eligible_vectors':0}
    with pytest.raises(ServiceError,match='EMBEDDING_UNAVAILABLE'):pf.preflight(settings(),Empty())
