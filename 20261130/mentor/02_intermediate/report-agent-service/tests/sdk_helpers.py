"""테스트 전용 Fixture; 실제 서비스에는 import하지 않는다."""
import json
from langchain_core.messages import AIMessage
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from app.core.settings import Settings
from app.rag.documents import to_document

class FakeToolModel(FakeMessagesListChatModel):
    def bind_tools(self,tools,**kwargs):return self

class Repo:
    def __init__(self,empty=False):self.empty=empty
    def lookup(self,rid):return {'status':'found','report_id':rid,'category_code':'RESEARCH_PLAN','index_status':'ready','revision':1,'embedding_fresh':True}
    def candidates(self,vector,category,k,rid):
        if self.empty:return []
        ids=[63,64] if rid is None else [rid] if rid==63 else []
        return [{'report_id':i,'title':'fixture','content':'fixture 근거','overview':'fixture','category_code':'RESEARCH_PLAN','revision':1,'distance':0.1+(i-63)*0.1} for i in ids][:k]
    def preflight(self):return {'eligible_vectors':1,'db':'ready'}
class Emb:
    def encode(self,q,m):return [1.0]+[0.0]*383
class Rank:
    def rank(self,q,docs,m):return [d.model_copy(update={'metadata':{**d.metadata,'reranker_score':1.0}}) for d in reversed(docs)]

def answer(source='RPT-63'):
    return json.dumps({'status':'completed','answer':'fixture ['+source+']','source_ids':[source]})

def make_pipeline(messages=None,empty=False,ranker=None,context_chars=9000):
    from app.rag.pipeline import RagPipeline
    from app.rag.retriever import Retriever
    s=Settings('','fixture','fixture',context_chars=context_chars)
    return RagPipeline(s,Retriever(Repo(empty),Emb()),ranker or Rank(),lambda:FakeToolModel(responses=messages or [AIMessage(content=answer())]))
