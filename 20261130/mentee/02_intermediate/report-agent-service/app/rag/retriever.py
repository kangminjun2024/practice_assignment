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
        # TODO D31-I04-01: 현재 질문과 Meter를 사용해 E5 인코딩을 호출하세요.
        raise ServiceError('NOT_IMPLEMENTED', 'UNIMPLEMENTED_D31-I04-01')
        # END D31-I04-01
        start=perf_counter()
        rows=[]
        # ID 지정 시 다른 보고서로 대체하지 않는다. 지정하지 않았다면 일반 의미 검색.
        for rid in ids or [None]:
            # BEGIN D31-I04-02
            # TODO D31-I04-02: Repository 후보 조회 결과를 rows에 추가하세요.
            raise ServiceError('NOT_IMPLEMENTED', 'UNIMPLEMENTED_D31-I04-02')
            # END D31-I04-02
        meter.record('pgvector_retrieval',start)
        # BEGIN D31-I04-03
        # TODO D31-I04-03: 거리 오름차순·ID 동점 기준으로 최대 top_k개를 정렬하고 Document로 반환하세요.
        raise ServiceError('NOT_IMPLEMENTED', 'UNIMPLEMENTED_D31-I04-03')
        # END D31-I04-03
