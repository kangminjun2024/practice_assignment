import pytest
pytest.importorskip('langchain_core')
from tests.sdk_helpers import make_pipeline,answer
from langchain_core.messages import AIMessage
from app.services.metrics import Meter
from app.services.errors import ServiceError

Q='보고서 63번의 핵심 내용'

def test_actual_lcel_stub_model():
    p=make_pipeline();m=Meter(p.settings)
    out=p.run(Q,Q,None,3,m)
    assert out['status']=='found' and out['sources'][0]['source_id']=='RPT-63' and m.model_calls==1

def test_empty_skips_model():
    p=make_pipeline(empty=True);m=Meter(p.settings)
    def forbidden():raise AssertionError('LLM must not run')
    p.model_factory=forbidden
    assert p.run(Q,Q,None,3,m)['status']=='not_found' and m.model_calls==0

@pytest.mark.parametrize('content',['not-json',answer('RPT-999999')])
def test_model_output_error(content):
    p=make_pipeline([AIMessage(content=content)])
    with pytest.raises(ServiceError,match='OUTPUT_CONTRACT_ERROR'):p.run(Q,Q,None,3,Meter(p.settings))

def test_model_initialization_timeout():
    p=make_pipeline()
    def fail():raise TimeoutError('fixture secret')
    p.model_factory=fail
    with pytest.raises(ServiceError,match='LLM_TIMEOUT') as e:p.run(Q,Q,None,3,Meter(p.settings))
    assert 'fixture secret' not in str(e.value.envelope())
