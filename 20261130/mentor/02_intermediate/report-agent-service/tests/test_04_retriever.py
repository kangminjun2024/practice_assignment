import pytest
from app.rag.ids import explicit_ids
from app.services.errors import ServiceError
from app.core.settings import Settings
from app.services.metrics import Meter

@pytest.mark.parametrize('question',['보고서 0번','RPT--1','report id 9223372036854775808'])
def test_invalid_explicit_ids(question):
    with pytest.raises(ServiceError,match='VALIDATION_ERROR'):explicit_ids(question)

def test_retriever_uses_ids_and_metadata():
    pytest.importorskip('langchain_core')
    from app.rag.retriever import Retriever
    class Emb:
        def encode(self,q,meter):self.q=q;return [1.0]+[0.0]*383
    class Repo:
        def __init__(self):self.calls=[]
        def candidates(self,vector,category,k,rid):
            self.calls.append((vector,category,k,rid))
            return [{'report_id':rid,'title':'fixture','content':'근거','overview':'overview','category_code':'RESEARCH_PLAN','revision':2,'distance':0.2}]
    e=Emb();repo=Repo();r=Retriever(repo,e);m=Meter(Settings('','',''))
    q='보고서 63번의 내용을 알려줘.';docs=r.search(q,'RESEARCH_PLAN',3,m)
    assert e.q==q and repo.calls[0][1:]==('RESEARCH_PLAN',3,63)
    assert len(repo.calls[0][0])==384 and len(docs)==1
    assert docs[0].metadata['source_id']=='RPT-63' and docs[0].metadata['revision']==2 and docs[0].page_content=='근거'
    assert any(s['stage']=='pgvector_retrieval' for s in m.stages)
