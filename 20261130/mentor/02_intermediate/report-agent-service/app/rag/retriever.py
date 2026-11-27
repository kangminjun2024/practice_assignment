"""B-05/I-03: 검색 질문과 원래 질문은 구별한다. 명시 ID는 정확히 제한."""
import re
from time import perf_counter
from app.rag.documents import to_document

from app.rag.ids import explicit_ids

class Retriever:
    def __init__(self, repo, embedder):
        self.repo=repo; self.embedder=embedder
    def search(self, query, category_code, top_k, meter, exact_ids=None):
        ids=sorted(explicit_ids(query) if exact_ids is None else exact_ids)
        # BEGIN D31-I04-01
        # 해설 D31-I04-01: 실제 E5는 cuda:0에서 query prefix와 정규화를 사용하여 384차원 Vector를 만든다.
        vector=self.embedder.encode(query,meter)
        # END D31-I04-01
        start=perf_counter()
        rows=[]
        # ID 지정 시 다른 보고서로 대체하지 않는다. 지정하지 않았다면 일반 의미 검색.
        for rid in ids or [None]:
            # BEGIN D31-I04-02
            # 해설 D31-I04-02: 각 명시 ID 또는 일반 검색에 동일한 Vector, Category, top_k를 전달한다.
            rows.extend(self.repo.candidates(vector,category_code,top_k,rid))
            # END D31-I04-02
        meter.record('pgvector_retrieval',start)
        # BEGIN D31-I04-03
        # 해설 D31-I04-03: DB Row에서 본문과 Metadata를 보존하여 LangChain에 연결한다.
        return [to_document(r) for r in sorted(rows,key=lambda r:(r['distance'],r['report_id']))[:top_k]]
        # END D31-I04-03
