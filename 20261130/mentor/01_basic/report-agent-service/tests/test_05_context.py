import json
import pytest
pytest.importorskip('langchain_core')
from tests.sdk_helpers import make_pipeline,Rank
from app.services.metrics import Meter
from app.services.errors import ServiceError

def test_rank_then_context():
    p=make_pipeline();m=Meter(p.settings)
    docs,info=p.retrieve('검색 품질을 개선하는 연구',None,3,m)
    assert [x['report_id'] for x in info['before']]==[63,64]
    assert [x['report_id'] for x in info['after']]==[64,63]
    context,sources=p.build_context(docs,1)
    assert json.loads(context)[0]['source_id']=='RPT-64' and [s['report_id'] for s in sources]==[64]

def test_budget_and_candidate_preservation():
    p=make_pipeline(context_chars=1000);docs,_=p.retrieve('보고서 63 내용',None,3,Meter(p.settings))
    docs=[docs[0].model_copy(update={'page_content':'한글 '*2000})]
    context,sources=p.build_context(docs,3)
    assert len(context)<=1000 and len(sources)==1 and len(json.loads(context)[0]['content'])<3000
    class Broken(Rank):
        def rank(self,q,docs,m):return []
    broken=make_pipeline(ranker=Broken())
    with pytest.raises(ServiceError,match='OUTPUT_CONTRACT_ERROR'):broken.retrieve('검색 품질 연구',None,3,Meter(broken.settings))
